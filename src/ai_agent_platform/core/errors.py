"""Domain-specific exceptions."""


class AgentPlatformError(Exception):
    """Base exception for expected platform errors."""


class AgentDefinitionError(AgentPlatformError):
    """An agent manifest is missing fields or contains invalid values."""


class AgentExecutionError(AgentPlatformError):
    """An agent execution could not be completed."""


class ProviderConfigurationError(AgentPlatformError):
    """A model provider is missing or has invalid configuration."""


class ProviderRequestError(AgentPlatformError):
    """A model provider request or response failed."""
