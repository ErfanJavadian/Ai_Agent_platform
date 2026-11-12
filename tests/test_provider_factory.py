"""Tests for environment-driven provider selection."""

import pytest

from ai_agent_platform.core.errors import ProviderConfigurationError
from ai_agent_platform.providers.fake import FakeProvider
from ai_agent_platform.providers.factory import create_provider
from ai_agent_platform.providers.openai_compatible import OpenAICompatibleProvider


def test_factory_defaults_to_fake_provider_without_environment():
    provider = create_provider({})

    assert isinstance(provider, FakeProvider)
    assert provider.name == "fake"


def test_factory_selects_fake_provider_explicitly():
    provider = create_provider({"AI_AGENT_PROVIDER": " FAKE "})

    assert isinstance(provider, FakeProvider)


def test_factory_selects_openai_compatible_provider():
    provider = create_provider(
        {
            "AI_AGENT_PROVIDER": "openai_compatible",
            "AI_AGENT_API_KEY": "test-secret",
            "AI_AGENT_MODEL": "test-model",
            "AI_AGENT_API_BASE_URL": "https://models.example/v1",
            "AI_AGENT_TIMEOUT_SECONDS": "12",
        }
    )

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.name == "openai_compatible"


def test_factory_rejects_unknown_provider_name():
    with pytest.raises(ProviderConfigurationError, match="Unsupported AI_AGENT_PROVIDER"):
        create_provider({"AI_AGENT_PROVIDER": "unknown"})


def test_factory_requires_credentials_for_real_provider():
    with pytest.raises(ProviderConfigurationError, match="AI_AGENT_API_KEY"):
        create_provider({"AI_AGENT_PROVIDER": "openai_compatible"})
