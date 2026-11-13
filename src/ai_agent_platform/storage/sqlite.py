"""Small SQLite execution-history and tool-audit repository."""

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteExecutionStore:
    def __init__(self, database_path: str | Path = "data/agent_platform.sqlite3"):
        self.database_path = str(database_path)
        self._memory_connection: sqlite3.Connection | None = None
        if self.database_path == ":memory:":
            self._memory_connection = sqlite3.connect(":memory:")
            self._memory_connection.row_factory = sqlite3.Row
        else:
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        if self._memory_connection is not None:
            return self._memory_connection
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    task TEXT NOT NULL,
                    output TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    error TEXT
                )
            """)
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(executions)").fetchall()
            }
            if "error" not in columns:
                connection.execute("ALTER TABLE executions ADD COLUMN error TEXT")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    call_id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    arguments_json TEXT NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tool_calls_execution "
                "ON tool_calls(execution_id, created_at)"
            )

    def save(self, *, execution_id: str, agent_id: str, status: str,
             provider: str, task: str, output: str, created_at: str,
             error: str | None = None) -> None:
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO executions
                (execution_id, agent_id, status, provider, task, output, created_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id, agent_id, status, provider, task, output, created_at, error,
            ))

    def get(self, execution_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM executions WHERE execution_id = ?", (execution_id,)
            ).fetchone()
        return dict(row) if row else None

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 100))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM executions ORDER BY created_at DESC LIMIT ?", (safe_limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def save_tool_call(
        self, *, call_id: str, execution_id: str, agent_id: str, tool_name: str,
        status: str, arguments_json: str, result_json: str | None,
        error: str | None, created_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO tool_calls
                (call_id, execution_id, agent_id, tool_name, status,
                 arguments_json, result_json, error, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id, execution_id, agent_id, tool_name, status,
                arguments_json, result_json, error, created_at,
            ))

    def list_tool_calls(self, execution_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tool_calls WHERE execution_id = ? "
                "ORDER BY created_at, rowid",
                (execution_id,),
            ).fetchall()
        return [dict(row) for row in rows]
