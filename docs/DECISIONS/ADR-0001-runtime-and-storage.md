# ADR-0001: Initial runtime and storage direction

- Status: Accepted for MVP baseline
- Date: 2026-11-12

## Context
The project needs real agent execution, task orchestration, skill extensibility, and controlled code execution. Development must remain in one repository and be practical to build incrementally with limited infrastructure and cost. Distributed services and paid hosted queues would add operational burden before core behavior is proven.

## Decision
1. Language: Python 3.11 or newer for the initial backend and agent runtime.
2. Application shape: modular monolith with explicit interfaces between runtime, orchestration, messaging, persistence, tools, and execution.
3. Persistence: SQLite for the first local MVP; define repository interfaces so PostgreSQL can replace it when concurrency and deployment justify migration.
4. API: add FastAPI when an HTTP interface is needed; do not make the first runtime depend on a deployed server.
5. Model access: provider-neutral adapter, with a deterministic fake adapter for tests and offline development. Real provider credentials come from environment variables and are never committed.
6. Agent and skill definitions: versioned declarative manifests plus Markdown instructions. Validate schemas and treat package content as untrusted.
7. Messaging: durable database-backed message bus initially, with a transport interface for a future broker if justified.
8. Terminal execution: never run model-generated commands directly on the host. Use a genuine isolated sandbox; if unavailable, arbitrary shell execution remains disabled.
9. Testing: deterministic unit and integration tests. External model/API tests are opt-in and not required for the baseline suite.

## Consequences
Benefits: low-cost local development, simpler debugging, clear contracts, and tests independent of paid APIs.

Trade-offs: SQLite is not the final answer for high-concurrency production; modular monolith boundaries need discipline; secure sandboxing may require Linux containers or an external execution provider; real agent quality depends on model choice, evaluation, prompts, and tools.

## Revisit when
Measured concurrency, multiple runtime workers, production deployment, or a verified sandbox provider justifies a change.
