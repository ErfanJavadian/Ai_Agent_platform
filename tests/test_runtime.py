import pytest
from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.agents.runtime import AgentRuntime
from ai_agent_platform.core.errors import AgentExecutionError
from ai_agent_platform.core.models import AgentRequest
from ai_agent_platform.providers.fake import FakeProvider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore


def make_runtime(tmp_path):
    store = SQLiteExecutionStore(tmp_path / "test.sqlite3")
    return AgentRuntime(FakeProvider(), store), store


def test_runtime_executes_and_persists_result(tmp_path):
    runtime, store = make_runtime(tmp_path)
    agent = load_agent("examples/agents/researcher.json")
    response = runtime.run(agent, AgentRequest(task="Compare two approaches"))
    assert response.status == "completed"
    assert response.provider == "fake"
    assert "[FAKE:researcher]" in response.output
    saved = store.get(response.execution_id)
    assert saved is not None and saved["task"] == "Compare two approaches"
    assert saved["status"] == "completed"


def test_in_memory_store_keeps_schema_and_records_between_operations():
    store = SQLiteExecutionStore(":memory:")
    store.save(execution_id="exec-1", agent_id="researcher", status="completed",
               provider="fake", task="test", output="result", created_at="2026-01-01")
    assert store.get("exec-1")["output"] == "result"


def test_runtime_rejects_empty_task(tmp_path):
    runtime, _ = make_runtime(tmp_path)
    agent = load_agent("examples/agents/researcher.json")
    with pytest.raises(AgentExecutionError):
        runtime.run(agent, AgentRequest(task="  "))


def test_runtime_rejects_oversized_task(tmp_path):
    runtime, _ = make_runtime(tmp_path)
    agent = load_agent("examples/agents/researcher.json")
    with pytest.raises(AgentExecutionError):
        runtime.run(agent, AgentRequest(task="x" * 20_000))
