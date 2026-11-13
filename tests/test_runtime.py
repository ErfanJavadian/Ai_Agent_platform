import sqlite3

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



class FailingProvider:
    name = "failing"

    def generate(self, agent, request):
        raise RuntimeError("provider unavailable")


def test_runtime_persists_failed_execution(tmp_path):
    store = SQLiteExecutionStore(tmp_path / "failed.sqlite3")
    runtime = AgentRuntime(FailingProvider(), store)
    agent = load_agent("examples/agents/researcher.json")

    with pytest.raises(AgentExecutionError, match="provider unavailable"):
        runtime.run(agent, AgentRequest(task="Run a task"))

    rows = store.list_recent()
    assert len(rows) == 1
    assert rows[0]["status"] == "failed"
    assert rows[0]["task"] == "Run a task"
    assert rows[0]["output"] == ""
    assert "AgentExecutionError" in rows[0]["error"]
    assert "provider unavailable" in rows[0]["error"]


def test_store_migrates_existing_execution_table_without_data_loss(tmp_path):
    database = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("""
            CREATE TABLE executions (
                execution_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                status TEXT NOT NULL,
                provider TEXT NOT NULL,
                task TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            INSERT INTO executions
            (execution_id, agent_id, status, provider, task, output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("legacy-1", "researcher", "completed", "fake",
              "old task", "old result", "2026-01-01"))

    store = SQLiteExecutionStore(database)
    old_record = store.get("legacy-1")
    assert old_record is not None
    assert old_record["output"] == "old result"
    assert old_record["error"] is None

    store.save(
        execution_id="failed-2", agent_id="researcher", status="failed",
        provider="fake", task="new task", output="", error="expected failure",
        created_at="2026-01-02",
    )
    assert store.get("failed-2")["error"] == "expected failure"
