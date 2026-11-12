"""Composition root for creating and running a configured agent."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.agents.runtime import AgentRuntime
from ai_agent_platform.core.models import AgentDefinition, AgentRequest, AgentResponse
from ai_agent_platform.providers.factory import create_provider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore
from ai_agent_platform.tools import ToolGateway, ToolRegistry, WorkspaceTools, register_workspace_tools


@dataclass(slots=True)
class AgentApplication:
    """A loaded agent connected to its provider, tools, and execution store."""
    agent: AgentDefinition
    runtime: AgentRuntime

    def run(self, task: str, context: dict[str, Any] | None = None) -> AgentResponse:
        return self.runtime.run(self.agent, AgentRequest(task=task, context=context))


def build_application(*, agent_path: str | Path = "examples/agents/researcher.json",
                      database_path: str | Path = "data/agent_platform.sqlite3",
                      workspace_path: str | Path | None = None,
                      environ: Mapping[str, str] | None = None) -> AgentApplication:
    """Compose provider, SQLite, registered workspace tools, gateway, and runtime."""
    agent = load_agent(agent_path)
    provider = create_provider(environ)
    store = SQLiteExecutionStore(database_path)
    workspace_root = workspace_path or Path("data/workspaces") / agent.agent_id
    workspace = WorkspaceTools(workspace_root)
    registry = ToolRegistry()
    register_workspace_tools(registry, workspace)
    gateway = ToolGateway(registry, store=store)
    runtime = AgentRuntime(
        provider=provider, store=store, tool_gateway=gateway, tool_registry=registry
    )
    return AgentApplication(agent=agent, runtime=runtime)
