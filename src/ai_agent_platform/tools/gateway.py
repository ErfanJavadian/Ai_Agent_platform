"""Permission-aware, bounded tool execution with an audit trail."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Iterable

from ai_agent_platform.core.errors import ToolExecutionError, ToolPermissionError
from ai_agent_platform.tools.registry import ToolRegistry


class ToolGateway:
    """Validates permissions and arguments before invoking registered tools."""

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        store: Any | None = None,
        max_calls_per_execution: int = 8,
        max_argument_bytes: int = 16_384,
    ) -> None:
        if max_calls_per_execution < 1:
            raise ValueError("max_calls_per_execution must be at least 1")
        if max_argument_bytes < 1:
            raise ValueError("max_argument_bytes must be at least 1")
        self.registry = registry
        self.store = store
        self.max_calls_per_execution = max_calls_per_execution
        self.max_argument_bytes = max_argument_bytes
        self._call_counts: dict[str, int] = {}

    def execute(
        self,
        *,
        agent_id: str,
        tool_name: str,
        arguments: dict[str, Any],
        allowed_tools: Iterable[str],
        execution_id: str = "manual",
    ) -> dict[str, Any]:
        """Execute one approved tool call and persist its outcome when configured."""
        call_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        status = "failed"
        result: dict[str, Any] | None = None
        error: str | None = None
        arguments_json = "{}"

        try:
            if not isinstance(agent_id, str) or not agent_id.strip():
                raise ToolExecutionError("agent_id must be a non-empty string")
            if not isinstance(arguments, dict):
                raise ToolExecutionError("Tool arguments must be a JSON object")

            try:
                arguments_json = json.dumps(
                    arguments, ensure_ascii=False, separators=(",", ":")
                )
            except (TypeError, ValueError) as exc:
                raise ToolExecutionError("Tool arguments must contain JSON values only") from exc
            if len(arguments_json.encode("utf-8")) > self.max_argument_bytes:
                raise ToolExecutionError("Tool arguments exceed the configured size limit")

            if tool_name not in set(allowed_tools):
                raise ToolPermissionError(f"Agent is not permitted to use tool: {tool_name}")

            count = self._call_counts.get(execution_id, 0)
            if count >= self.max_calls_per_execution:
                raise ToolExecutionError("Tool call limit reached for this execution")
            self._call_counts[execution_id] = count + 1

            spec = self.registry.get(tool_name)
            supplied = set(arguments)
            missing = spec.required_arguments - supplied
            unexpected = supplied - spec.allowed_arguments
            if missing:
                raise ToolExecutionError(
                    f"Missing required arguments for {tool_name}: {', '.join(sorted(missing))}"
                )
            if unexpected:
                raise ToolExecutionError(
                    f"Unexpected arguments for {tool_name}: {', '.join(sorted(unexpected))}"
                )

            result = spec.handler(dict(arguments))
            if not isinstance(result, dict):
                raise ToolExecutionError("Tool handler returned an invalid result")
            status = "succeeded"
            return result
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            if self.store is not None:
                self.store.save_tool_call(
                    call_id=call_id,
                    execution_id=execution_id,
                    agent_id=agent_id if isinstance(agent_id, str) else "unknown",
                    tool_name=tool_name if isinstance(tool_name, str) else "unknown",
                    status=status,
                    arguments_json=arguments_json,
                    result_json=(
                        json.dumps(result, ensure_ascii=False, separators=(",", ":"))
                        if result is not None else None
                    ),
                    error=error,
                    created_at=created_at,
                )
