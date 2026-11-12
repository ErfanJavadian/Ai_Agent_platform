"""Single-agent execution lifecycle for Phase 1."""

from datetime import datetime, timezone
from uuid import uuid4

from ai_agent_platform.core.errors import AgentExecutionError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest, AgentResponse
from ai_agent_platform.providers.base import ModelProvider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore


class AgentRuntime:
    def __init__(self, provider: ModelProvider, store: SQLiteExecutionStore,
                 *, max_task_chars: int = 12_000):
        self.provider = provider
        self.store = store
        self.max_task_chars = max_task_chars

    def run(self, agent: AgentDefinition, request: AgentRequest) -> AgentResponse:
        if not isinstance(request.task, str) or not request.task.strip():
            raise AgentExecutionError("Task must be a non-empty string")
        if len(request.task) > self.max_task_chars:
            raise AgentExecutionError(f"Task exceeds the {self.max_task_chars}-character limit")

        execution_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            output = self.provider.generate(agent, request)
            if not isinstance(output, str) or not output.strip():
                raise AgentExecutionError("Provider returned an empty or invalid output")
            self.store.save(
                execution_id=execution_id, agent_id=agent.agent_id,
                status="completed", provider=self.provider.name,
                task=request.task, output=output, created_at=created_at,
            )
        except AgentExecutionError:
            raise
        except Exception as exc:
            raise AgentExecutionError(f"Provider execution failed: {exc}") from exc

        return AgentResponse(
            execution_id=execution_id, agent_id=agent.agent_id,
            status="completed", output=output,
            provider=self.provider.name, created_at=created_at,
        )
