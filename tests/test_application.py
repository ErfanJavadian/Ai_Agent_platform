"""End-to-end tests for the application composition root and CLI."""

import json

from ai_agent_platform.application import build_application
from ai_agent_platform.cli import main
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore


def write_agent_manifest(path):
    path.write_text(
        json.dumps(
            {
                "agent_id": "test_agent",
                "name": "Test Agent",
                "description": "Agent used by application integration tests.",
                "version": "1.0.0",
                "instructions": "Complete the supplied task clearly.",
            }
        ),
        encoding="utf-8",
    )
    return path


def test_application_runs_agent_and_persists_result(tmp_path):
    manifest = write_agent_manifest(tmp_path / "agent.json")
    database = tmp_path / "executions.sqlite3"

    application = build_application(
        agent_path=manifest,
        database_path=database,
        environ={},
    )
    response = application.run("Create a short project plan")

    assert response.agent_id == "test_agent"
    assert response.provider == "fake"
    assert response.status == "completed"
    assert "Create a short project plan" in response.output

    saved = application.runtime.store.get(response.execution_id)
    assert saved is not None
    assert saved["task"] == "Create a short project plan"
    assert saved["output"] == response.output

    # Reopening the database proves the execution survived the application object.
    reopened_store = SQLiteExecutionStore(database)
    assert reopened_store.get(response.execution_id)["status"] == "completed"


def test_cli_runs_agent_and_prints_result(tmp_path, monkeypatch, capsys):
    manifest = write_agent_manifest(tmp_path / "cli_agent.json")
    database = tmp_path / "cli.sqlite3"
    monkeypatch.setenv("AI_AGENT_PROVIDER", "fake")

    exit_code = main(
        [
            "run",
            "--agent",
            str(manifest),
            "--task",
            "Summarize this test",
            "--database",
            str(database),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Agent: test_agent" in captured.out
    assert "Provider: fake" in captured.out
    assert "Status: completed" in captured.out
    assert "Summarize this test" in captured.out
    assert captured.err == ""

    rows = SQLiteExecutionStore(database).list_recent()
    assert len(rows) == 1
    assert rows[0]["task"] == "Summarize this test"
