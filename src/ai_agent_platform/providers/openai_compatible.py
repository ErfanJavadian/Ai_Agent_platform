"""OpenAI-compatible Chat Completions provider using only the Python standard library."""

from __future__ import annotations

import json
import os
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_agent_platform.core.errors import ProviderConfigurationError, ProviderRequestError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest


class OpenAICompatibleProvider:
    """Calls a model endpoint that implements the OpenAI Chat Completions format.

    The endpoint and credentials are supplied at runtime. No SDK or third-party
    HTTP dependency is required.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        api_base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ProviderConfigurationError("AI_AGENT_API_KEY must be configured")
        if not model or not model.strip():
            raise ProviderConfigurationError("AI_AGENT_MODEL must be configured")
        if not api_base_url or not api_base_url.strip():
            raise ProviderConfigurationError("AI_AGENT_API_BASE_URL must not be empty")
        if timeout <= 0:
            raise ProviderConfigurationError("Provider timeout must be greater than zero")

        base = api_base_url.strip().rstrip("/")
        self._endpoint = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
        self._api_key = api_key.strip()
        self._model = model.strip()
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "openai_compatible"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "OpenAICompatibleProvider":
        """Build a provider from environment variables without exposing secrets."""
        values = os.environ if environ is None else environ
        raw_timeout = values.get("AI_AGENT_TIMEOUT_SECONDS", "30")
        try:
            timeout = float(raw_timeout)
        except (TypeError, ValueError) as exc:
            raise ProviderConfigurationError(
                "AI_AGENT_TIMEOUT_SECONDS must be a number"
            ) from exc

        return cls(
            api_key=values.get("AI_AGENT_API_KEY", ""),
            model=values.get("AI_AGENT_MODEL", ""),
            api_base_url=values.get(
                "AI_AGENT_API_BASE_URL", "https://api.openai.com/v1"
            ),
            timeout=timeout,
        )

    def generate(self, agent: AgentDefinition, request: AgentRequest) -> str:
        system_parts = [agent.instructions.strip()]
        if agent.description.strip():
            system_parts.append(f"Agent description: {agent.description.strip()}")
        if request.context:
            system_parts.append(
                "Additional context (JSON):\n"
                + json.dumps(request.context, ensure_ascii=False, sort_keys=True)
            )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": "\n\n".join(system_parts)},
                {"role": "user", "content": request.task},
            ],
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = Request(
            self._endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(http_request, timeout=self._timeout) as response:
                raw_response = response.read()
        except HTTPError as exc:
            # Do not include request headers or credentials in surfaced errors.
            try:
                detail = exc.read(500).decode("utf-8", errors="replace")
            except Exception:
                detail = ""
            suffix = f": {detail}" if detail else ""
            raise ProviderRequestError(
                f"Model provider returned HTTP {exc.code}{suffix}"
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderRequestError(
                f"Could not reach the model provider: {type(exc).__name__}"
            ) from exc

        try:
            data = json.loads(raw_response.decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise ProviderRequestError(
                "Model provider returned an invalid Chat Completions response"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestError("Model provider returned empty message content")
        return content.strip()
