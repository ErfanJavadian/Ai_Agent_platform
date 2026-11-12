"""Environment-driven selection of model provider implementations."""

from __future__ import annotations

import os
from typing import Mapping

from ai_agent_platform.core.errors import ProviderConfigurationError
from ai_agent_platform.providers.base import ModelProvider
from ai_agent_platform.providers.fake import FakeProvider
from ai_agent_platform.providers.openai_compatible import OpenAICompatibleProvider


def create_provider(
    environ: Mapping[str, str] | None = None,
) -> ModelProvider:
    """Create the configured provider.

    AI_AGENT_PROVIDER defaults to fake so local development and tests do
    not require credentials or network access. Supported values are
    fake and openai_compatible.
    """
    values = os.environ if environ is None else environ
    provider_name = values.get("AI_AGENT_PROVIDER", "fake").strip().lower()

    if provider_name == "fake":
        return FakeProvider()
    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider.from_env(values)

    raise ProviderConfigurationError(
        "Unsupported AI_AGENT_PROVIDER. Supported values: fake, openai_compatible"
    )
