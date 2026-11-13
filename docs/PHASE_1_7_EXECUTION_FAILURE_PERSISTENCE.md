# Phase 1.7 — Execution Failure Persistence

## Goal
Make accepted Agent executions diagnosable when the provider or runtime fails, without losing existing SQLite history.

## Behavior
- A runtime failure after execution begins creates an execution row with `status="failed"`.
- Failed executions store an empty output string and a bounded error summary (up to 2,000 characters).
- Invalid requests rejected before execution starts are not recorded as runs.
- If writing the failure record itself fails, the raised error reports that persistence also failed without dumping database details.
- Existing databases are migrated by adding a nullable `error` column when absent; existing execution rows are preserved.

## Verification
Run:

~~~bash
pytest -v
~~~

Tests cover provider failure persistence, tool-loop exhaustion persistence, and migration of a legacy executions table.

## Limitations
- This is execution-history persistence, not retry, resume, or a durable task state machine.
- A process kill or device crash before the failure handler runs can still leave no terminal failure record.
- Live provider behavior remains unverified unless a separate opt-in API smoke test is performed.
