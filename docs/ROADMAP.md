# Engineering roadmap

A phase is complete only when implemented, tested, and documented.

## Phase 0 — Foundation
- [x] Product vision and operating principles.
- [x] High-level architecture and trust boundaries.
- [x] Agent communication and orchestration contracts.
- [x] Custom agent and skill extensibility.
- [x] Terminal execution security requirements.
- [x] Initial technology decisions.
- [ ] Runnable project skeleton and CI checks.

## Phase 1 — Minimal Agent Runtime
Build Python package structure, typed domain models, agent definition loader, provider-neutral model adapter, deterministic fake provider, structured output validation, and configuration/secret handling.

Exit: a local test loads an agent, runs a deterministic task through the runtime interface, validates its result, and persists a trace without a paid model API.

## Phase 2 — Task Orchestration and Messaging
Build durable task/run storage, task state machine, dependency graph, permission-aware message bus, multi-agent collaboration, retry, pause, resume, cancellation, and audit records.

Exit: two agents complete a dependent workflow and exchange authorized messages; unauthorized communication is rejected.

## Phase 3 — Agent and Skill Studio
Build schemas, skill registry, version pinning, compatibility checks, custom agent lifecycle, and skill evaluations.

Exit: create a custom agent and attach a custom skill without editing runtime source.

## Phase 4 — Tools, Workspaces, and Terminal
Build tool registry, policy gateway, project artifacts, isolated execution adapter, quotas, file operations, command execution, tests, and approval gates.

Exit: an authorized coding agent creates and tests a small project in an isolated workspace without accessing host files or other projects.

## Phase 5 — Engineering Organization
Add product, research, architecture, development, QA, security, and reviewer agents with end-to-end workflows and reproducible exports.

Exit: a user request produces a tested, reviewable software artifact with traceable contributions.

## Phase 6 — Business Agents
Implement YouTube production workflow, content planning, asset pipeline, metadata, analytics, and permission-gated publishing integrations.

Exit: the workflow creates a complete reviewable content package; publishing occurs only through authorized integrations and policy approval.

## Phase 7 — AI Company Builder
Add organization templates, custom team builder, concurrent projects, scoped budgets, governance dashboard, approvals, analytics, and evaluation.

Exit: users can define, operate, inspect, and improve custom multi-agent organizations.

## Delivery discipline
Prefer a small working vertical slice over broad scaffolding. Each phase includes tests, setup instructions, security review, and an accurate project-state update.
