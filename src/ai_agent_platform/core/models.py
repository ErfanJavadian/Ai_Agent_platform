"""Typed domain models used by the agent runtime."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    agent_id: str
    name: str
    description: str
    instructions: str
    version: str = "1.0.0"
    allowed_tools: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AgentRequest:
    task: str
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class AgentResponse:
    execution_id: str
    agent_id: str
    status: str
    output: str
    provider: str
    created_at: str


@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ProviderTurn:
    content: str | None
    tool_calls: tuple[ToolCall, ...] = ()
