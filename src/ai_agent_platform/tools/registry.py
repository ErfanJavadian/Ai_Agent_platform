"""Strict tool registration and provider-compatible argument schemas."""

from dataclasses import dataclass
from typing import Any, Callable

from ai_agent_platform.core.errors import ToolExecutionError


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    required_arguments: frozenset[str]
    allowed_arguments: frozenset[str]
    handler: ToolHandler
    parameters: dict[str, Any]


class ToolRegistry:
    """In-memory registry of explicitly installed platform tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if not spec.name or not spec.name.replace("_", "").isalnum():
            raise ToolExecutionError("Tool name must contain only letters, numbers, and underscores")
        if spec.name in self._tools:
            raise ToolExecutionError(f"Tool is already registered: {spec.name}")
        if not spec.required_arguments.issubset(spec.allowed_arguments):
            raise ToolExecutionError("Required tool arguments must be included in allowed arguments")
        if set(spec.parameters.get("properties", {})) != set(spec.allowed_arguments):
            raise ToolExecutionError("Tool parameter schema must match allowed arguments")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolExecutionError(f"Unknown tool: {name}") from exc

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "required_arguments": sorted(spec.required_arguments),
                "allowed_arguments": sorted(spec.allowed_arguments),
            }
            for spec in sorted(self._tools.values(), key=lambda item: item.name)
        ]

    def provider_tools(self, allowed_names: tuple[str, ...] | list[str]) -> list[dict[str, Any]]:
        """Return OpenAI-compatible function declarations for an explicit allowlist."""
        declarations = []
        for name in allowed_names:
            spec = self.get(name)
            declarations.append({
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                    "strict": True,
                },
            })
        return declarations
