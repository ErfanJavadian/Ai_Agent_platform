# Architecture overview

## Goal
Start with a reliable single-machine runtime while preserving boundaries for later scaling. Avoid premature microservices. Every major subsystem needs a stable interface and independent tests.

## Logical components
1. API / Command Interface — accepts goals and exposes project and run status.
2. Agent Registry — definitions, versions, capabilities, lifecycle.
3. Agent Runtime — context assembly, model invocation, response validation, approved tool calls.
4. Model Gateway — provider-neutral model interface and usage reporting.
5. Orchestrator — planning, task creation, dependencies, dispatch, retries, escalation.
6. Message Bus — structured agent messaging with identity, authorization, correlation, and audit.
7. Task Store — durable task/run state, ownership, dependencies, attempts, outcomes.
8. Memory and Knowledge — scoped memory with provenance and retention.
9. Skill Registry / Engine — validates, versions, resolves, and supplies skill packages.
10. Tool Registry / Gateway — tool schemas, permissions, budgets, approvals.
11. Workspace and Artifact Service — project-scoped files and immutable artifact references.
12. Execution Service — isolated terminal/code execution with resource limits.
13. Evaluation and Observability — traces, logs, metrics, evaluations, reviewer reports.
14. Human Approval Service — approval requests for sensitive or external actions.

## Main flow
A user submits a goal; the API creates a run; the orchestrator prepares a reviewable plan; policy validates agents, skills, tools, and budgets; tasks are persisted; ready tasks are dispatched; agents collaborate through the message bus; tools and terminal calls pass through gateways; outputs become artifacts; QA and review evaluate them; approvals are requested where required; the run closes with a report and deliverables.

## Trust boundaries
Model providers are external and may return untrusted output. Skills and instructions are not security boundaries. Tools and APIs have independent permissions and failure modes. Workspaces must be isolated by project. The execution service must be isolated from the platform host. Publishing, payments, account mutations, and destructive actions are gated.

## Initial implementation shape
Use a modular Python application. SQLite is suitable for a local MVP; production concurrency may require PostgreSQL and a dedicated queue. The initial message bus can be durable and database-backed. Provider, persistence, messaging, and execution implementations must sit behind replaceable interfaces.

## Quality attributes
Correctness through typed contracts and tests; safety through least privilege and sandboxing; reliability through durable state and bounded retries; observability through correlation and traces; extensibility through versioned definitions; cost control through budgets and local-first development.
