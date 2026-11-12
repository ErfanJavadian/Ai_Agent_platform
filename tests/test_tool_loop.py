import json

import pytest

from ai_agent_platform.agents.loader import parse_agent_definition
from ai_agent_platform.agents.runtime import AgentRuntime
from ai_agent_platform.core.errors import AgentExecutionError
from ai_agent_platform.core.models import AgentRequest, ProviderTurn, ToolCall
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore
from ai_agent_platform.tools import ToolGateway, ToolRegistry, WorkspaceTools, register_workspace_tools


class ScriptedProvider:
    name = "scripted"

    def __init__(self, turns):
        self.turns = list(turns)
        self.received_messages = []

    def generate(self, agent, request):
        return "plain response"

    def generate_turn(self, agent, request, messages, tools):
        self.received_messages.append((list(messages), list(tools)))
        return self.turns.pop(0)


def make_runtime(tmp_path, provider, *, max_model_turns=4):
    agent = parse_agent_definition({
        "agent_id": "builder", "name": "Builder", "description": "Test builder",
        "instructions": "Build files safely.",
        "allowed_tools": ["workspace_write_file", "workspace_read_file"],
    })
    store = SQLiteExecutionStore(tmp_path / "history.sqlite3")
    workspace = WorkspaceTools(tmp_path / "workspace")
    registry = ToolRegistry()
    register_workspace_tools(registry, workspace)
    gateway = ToolGateway(registry, store=store)
    runtime = AgentRuntime(
        provider, store, tool_gateway=gateway, tool_registry=registry,
        max_model_turns=max_model_turns,
    )
    return agent, runtime, workspace, store


def test_model_selects_tool_then_receives_result_and_finishes(tmp_path):
    provider = ScriptedProvider([
        ProviderTurn(content=None, tool_calls=(
            ToolCall("call-1", "workspace_write_file", {
                "relative_path": "hello.txt", "content": "Hello from agent",
            }),
        )),
        ProviderTurn(content="Created hello.txt successfully."),
    ])
    agent, runtime, workspace, store = make_runtime(tmp_path, provider)
    response = runtime.run(agent, AgentRequest("Create hello.txt"))

    assert response.status == "completed"
    assert (workspace.root / "hello.txt").read_text() == "Hello from agent"
    assert len(provider.received_messages) == 2
    assert provider.received_messages[0][1][0]["function"]["name"] == "workspace_write_file"
    second_messages = provider.received_messages[1][0]
    assert second_messages[-1]["role"] == "tool"
    assert json.loads(second_messages[-1]["content"])["ok"] is True
    assert len(store.list_tool_calls(response.execution_id)) == 1


def test_model_cannot_call_tool_outside_agent_allowlist(tmp_path):
    provider = ScriptedProvider([
        ProviderTurn(content=None, tool_calls=(
            ToolCall("call-1", "workspace_write_file", {
                "relative_path": "blocked.txt", "content": "no",
            }),
        )),
        ProviderTurn(content="The operation was denied."),
    ])
    agent, runtime, workspace, store = make_runtime(tmp_path, provider)
    response = runtime.run(agent, AgentRequest("Do something"))
    assert not (workspace.root / "blocked.txt").exists()
    trace = store.list_tool_calls(response.execution_id)
    assert trace[0]["status"] == "failed"
    denied = json.loads(provider.received_messages[1][0][-1]["content"])
    assert denied["ok"] is False


def test_tool_loop_stops_at_model_turn_limit(tmp_path):
    provider = ScriptedProvider([
        ProviderTurn(content=None, tool_calls=(
            ToolCall(f"call-{i}", "workspace_write_file", {
                "relative_path": f"{i}.txt", "content": "x",
            }),
        ))
        for i in range(3)
    ])
    agent, runtime, _, _ = make_runtime(tmp_path, provider, max_model_turns=2)
    with pytest.raises(AgentExecutionError, match="tool-loop limit"):
        runtime.run(agent, AgentRequest("Keep creating files"))
