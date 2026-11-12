"""Provider contract. Implementations return plain text."""

from typing import Protocol
from ai_agent_platform.core.models import AgentDefinition, AgentRequest


class ModelProvider(Protocol):
    @property
    def name(self) -> str: ...

    def generate(self, agent: AgentDefinition, request: AgentRequest) -> str: ...
