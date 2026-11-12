"""OpenAI-compatible Chat Completions provider with function/tool calling."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_agent_platform.core.errors import ProviderConfigurationError, ProviderRequestError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest, ProviderTurn, ToolCall


class OpenAICompatibleProvider:
    """Calls an endpoint implementing OpenAI Chat Completions and tools format."""

    def __init__(self, *, api_key: str, model: str,
                 api_base_url: str = "https://api.openai.com/v1",
                 timeout: float = 30.0) -> None:
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
        self._api_key, self._model, self._timeout = api_key.strip(), model.strip(), timeout

    @property
    def name(self) -> str:
        return "openai_compatible"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "OpenAICompatibleProvider":
        values = os.environ if environ is None else environ
        try:
            timeout = float(values.get("AI_AGENT_TIMEOUT_SECONDS", "30"))
        except (TypeError, ValueError) as exc:
            raise ProviderConfigurationError("AI_AGENT_TIMEOUT_SECONDS must be a number") from exc
        return cls(
            api_key=values.get("AI_AGENT_API_KEY", ""),
            model=values.get("AI_AGENT_MODEL", ""),
            api_base_url=values.get("AI_AGENT_API_BASE_URL", "https://api.openai.com/v1"),
            timeout=timeout,
        )

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            self._endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            try:
                detail = exc.read(500).decode("utf-8", errors="replace")
            except Exception:
                detail = ""
            raise ProviderRequestError(
                f"Model provider returned HTTP {exc.code}" + (f": {detail}" if detail else "")
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderRequestError(
                f"Could not reach the model provider: {type(exc).__name__}"
            ) from exc
        try:
            data = json.loads(raw.decode("utf-8"))
            message = data["choices"][0]["message"]
            if not isinstance(message, dict):
                raise TypeError("message must be an object")
            return message
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise ProviderRequestError(
                "Model provider returned an invalid Chat Completions response"
            ) from exc

    def _system_message(self, agent: AgentDefinition, request: AgentRequest) -> str:
        parts = [agent.instructions.strip()]
        if agent.description.strip():
            parts.append(f"Agent description: {agent.description.strip()}")
        if request.context:
            parts.append("Additional context (JSON):\n" +
                         json.dumps(request.context, ensure_ascii=False, sort_keys=True))
        return "\n\n".join(parts)

    def generate(self, agent: AgentDefinition, request: AgentRequest) -> str:
        message = self._request({
            "model": self._model,
            "messages": [
                {"role": "system", "content": self._system_message(agent, request)},
                {"role": "user", "content": request.task},
            ],
        })
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestError("Model provider returned empty message content")
        return content.strip()

    def generate_turn(self, agent: AgentDefinition, request: AgentRequest,
                      messages: list[dict[str, Any]],
                      tools: list[dict[str, Any]]) -> ProviderTurn:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role":"system","content":self._system_message(agent, request)}, *messages],
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        message = self._request(payload)
        content = message.get("content")
        if content is not None and not isinstance(content, str):
            raise ProviderRequestError("Model returned invalid message content")
        raw_calls = message.get("tool_calls", [])
        if not isinstance(raw_calls, list):
            raise ProviderRequestError("Model returned invalid tool_calls")
        calls: list[ToolCall] = []
        for item in raw_calls:
            try:
                function = item["function"]
                name = function["name"]
                arguments = json.loads(function["arguments"])
                call_id = item["id"]
                if not isinstance(name, str) or not isinstance(call_id, str) or not isinstance(arguments, dict):
                    raise TypeError
                calls.append(ToolCall(call_id=call_id, name=name, arguments=arguments))
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ProviderRequestError("Model returned a malformed tool call") from exc
        if not calls and (not isinstance(content, str) or not content.strip()):
            raise ProviderRequestError("Model returned neither content nor tool calls")
        return ProviderTurn(content=content.strip() if isinstance(content, str) and content.strip() else None,
                            tool_calls=tuple(calls))
