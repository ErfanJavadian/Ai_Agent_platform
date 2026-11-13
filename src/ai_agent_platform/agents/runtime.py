"""Single-agent execution with a bounded, permission-aware tool loop."""

import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from ai_agent_platform.core.errors import AgentExecutionError, ToolExecutionError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest, AgentResponse
from ai_agent_platform.providers.base import ModelProvider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore


class AgentRuntime:
    def __init__(self, provider: ModelProvider, store: SQLiteExecutionStore,
                 *, tool_gateway: Any | None = None, tool_registry: Any | None = None,
                 max_task_chars: int = 12_000, max_model_turns: int = 6):
        if max_model_turns < 1:
            raise ValueError("max_model_turns must be at least 1")
        self.provider, self.store = provider, store
        self.tool_gateway, self.tool_registry = tool_gateway, tool_registry
        self.max_task_chars, self.max_model_turns = max_task_chars, max_model_turns

    def _run_with_tools(self, agent: AgentDefinition, request: AgentRequest,
                        execution_id: str) -> str:
        generate_turn = getattr(self.provider, "generate_turn", None)
        if not callable(generate_turn) or self.tool_gateway is None or self.tool_registry is None:
            return self.provider.generate(agent, request)

        allowed = agent.allowed_tools
        tool_schemas = self.tool_registry.provider_tools(allowed)
        messages: list[dict[str, Any]] = [{"role": "user", "content": request.task}]
        for _ in range(self.max_model_turns):
            turn = generate_turn(agent, request, messages, tool_schemas)
            if not turn.tool_calls:
                if not turn.content:
                    raise AgentExecutionError("Model completed without a final response")
                return turn.content
            messages.append({
                "role": "assistant",
                "content": turn.content,
                "tool_calls": [
                    {"id": call.call_id, "type": "function",
                     "function": {"name": call.name,
                                  "arguments": json.dumps(call.arguments, ensure_ascii=False)}}
                    for call in turn.tool_calls
                ],
            })
            for call in turn.tool_calls:
                try:
                    result = self.tool_gateway.execute(
                        agent_id=agent.agent_id, tool_name=call.name,
                        arguments=call.arguments, allowed_tools=allowed,
                        execution_id=execution_id,
                    )
                    tool_result = {"ok": True, "result": result}
                except ToolExecutionError as exc:
                    tool_result = {"ok": False, "error": str(exc)}
                messages.append({
                    "role": "tool", "tool_call_id": call.call_id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                })
        raise AgentExecutionError(
            f"Model reached the {self.max_model_turns}-turn tool-loop limit without a final answer"
        )

    def _persist_failure(
        self, *, execution_id: str, agent: AgentDefinition, request: AgentRequest,
        created_at: str, error: Exception,
    ) -> None:
        error_text = f"{type(error).__name__}: {error}"[:2_000]
        try:
            self.store.save(
                execution_id=execution_id, agent_id=agent.agent_id,
                status="failed", provider=self.provider.name,
                task=request.task, output="", error=error_text, created_at=created_at,
            )
        except Exception as persistence_error:
            raise AgentExecutionError(
                "Agent execution failed and its failure record could not be persisted "
                f"({type(persistence_error).__name__})"
            ) from error

    def run(self, agent: AgentDefinition, request: AgentRequest) -> AgentResponse:
        if not isinstance(request.task, str) or not request.task.strip():
            raise AgentExecutionError("Task must be a non-empty string")
        if len(request.task) > self.max_task_chars:
            raise AgentExecutionError(f"Task exceeds the {self.max_task_chars}-character limit")

        execution_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            output = self._run_with_tools(agent, request, execution_id)
            if not isinstance(output, str) or not output.strip():
                raise AgentExecutionError("Provider returned an empty or invalid output")
            self.store.save(
                execution_id=execution_id, agent_id=agent.agent_id,
                status="completed", provider=self.provider.name,
                task=request.task, output=output, created_at=created_at,
            )
        except AgentExecutionError as exc:
            self._persist_failure(
                execution_id=execution_id, agent=agent, request=request,
                created_at=created_at, error=exc,
            )
            raise
        except Exception as exc:
            failure = AgentExecutionError(f"Agent execution failed: {exc}")
            self._persist_failure(
                execution_id=execution_id, agent=agent, request=request,
                created_at=created_at, error=failure,
            )
            raise failure from exc
        return AgentResponse(
            execution_id=execution_id, agent_id=agent.agent_id,
            status="completed", output=output, provider=self.provider.name,
            created_at=created_at,
        )
