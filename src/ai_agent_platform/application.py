"""Composition root for creating and running a configured agent."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.agents.runtime import AgentRuntime
from ai_agent_platform.core.models import AgentDefinition, AgentRequest, AgentResponse
from ai_agent_platform.providers.factory import create_provider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore


@dataclass(slots=True)
class AgentApplication:
    """A loaded agent connected to its provider and execution store."""

    agent: AgentDefinition
    runtime: AgentRuntime

    def run(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> AgentResponse:
        """Run one task through the configured runtime."""
        return self.runtime.run(
            self.agent,
            AgentRequest(task=task, context=context),
        )


def build_application(
    *,
    agent_path: str | Path = "examples/agents/researcher.json",
    database_path: str | Path = "data/agent_platform.sqlite3",
    environ: Mapping[str, str] | None = None,
) -> AgentApplication:
    """Load the agent and compose provider, storage, and runtime.

    Paths are resolved relative to the current working directory unless
    absolute paths are supplied. The default provider is the offline fake.
    """
    agent = load_agent(agent_path)
    provider = create_provider(environ)
    store = SQLiteExecutionStore(database_path)
    runtime = AgentRuntime(provider=provider, store=store)
    return AgentApplication(agent=agent, runtime=runtime)
