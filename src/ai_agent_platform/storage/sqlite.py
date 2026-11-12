"""Small SQLite execution-history repository."""

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteExecutionStore:
    def __init__(self, database_path: str | Path = "data/agent_platform.sqlite3"):
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
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
                    created_at TEXT NOT NULL
                )
            """)

    def save(self, *, execution_id: str, agent_id: str, status: str,
             provider: str, task: str, output: str, created_at: str) -> None:
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO executions
                (execution_id, agent_id, status, provider, task, output, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (execution_id, agent_id, status, provider, task, output, created_at))

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
