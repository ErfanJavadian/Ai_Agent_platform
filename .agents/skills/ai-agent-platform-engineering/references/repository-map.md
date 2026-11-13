# Repository map and verified baseline

> This is a navigation aid, not an immutable status file. Re-read the live source, README, project state, roadmap, tests, and ADR before making decisions. The repository may have advanced since this reference was written.

## Product and engineering direction

AI Agent Platform is an extensible, execution-oriented multi-agent organization / AI Company Builder. Users should be able to define an outcome, review a plan and permissions, compose specialist agents with reusable skills and approved tools, observe execution, approve consequential actions, and receive tangible artifacts.

The engineering decision is to begin with a local-first Python modular monolith. Avoid premature microservices. Keep provider, storage, messaging, orchestration, and execution behind clear replaceable interfaces. SQLite is the MVP store; PostgreSQL or a separate queue should be introduced only when measured concurrency or deployment requirements justify them.

## Repository landmarks

| Path | Responsibility |
|---|---|
| AGENTS.md | Repository-wide engineering and safety agreement |
| README.md | Current setup, examples, implementation summary, limitations |
| pyproject.toml | Python package metadata, dependencies, CLI entry point, pytest config |
| src/ai_agent_platform/cli.py | CLI interface |
| src/ai_agent_platform/application.py | Composition root and dependency wiring |
| src/ai_agent_platform/core/ | Shared domain models and errors |
| src/ai_agent_platform/agents/loader.py | Agent manifest parsing and validation |
| src/ai_agent_platform/agents/runtime.py | Agent execution and bounded model/tool loop |
| src/ai_agent_platform/providers/ | Provider protocol, fake provider, provider factory, OpenAI-compatible adapter |
| src/ai_agent_platform/storage/sqlite.py | SQLite execution and tool-call persistence |
| src/ai_agent_platform/tools/registry.py | Tool declarations and provider schemas |
| src/ai_agent_platform/tools/gateway.py | Allowlist, argument checks, bounded execution, audit |
| src/ai_agent_platform/tools/workspace.py | Project/agent workspace file operations |
| examples/agents/ | JSON agent manifests, including builder and researcher |
| tests/ | Deterministic unit and integration tests |
| docs/PRODUCT_VISION.md | Product outcomes and boundaries |
| docs/ARCHITECTURE_OVERVIEW.md | Logical components, flow, and trust boundaries |
| docs/ORCHESTRATION_CORE_SPEC.md | Future task orchestration contract |
| docs/AGENT_COMMUNICATION_PROTOCOL.md | Future authorized agent messaging contract |
| docs/AGENT_AND_SKILL_STUDIO.md | Future agent/skill package and lifecycle contract |
| docs/TERMINAL_EXECUTION_SECURITY.md | Execution sandbox requirements |
| docs/ROADMAP.md | Phases and exit criteria |
| docs/PROJECT_STATE.md | Implemented milestones and explicit limitations |
| docs/DECISIONS/ | Accepted architecture decision records |

## Runtime behavior visible in the current codebase

The repository includes:
- JSON agent definitions with explicit allowed_tools.
- Typed domain records including agent definitions, requests/responses, provider turns, and tool calls.
- A provider protocol, deterministic fake provider, environment-driven provider factory, and OpenAI-compatible Chat Completions adapter.
- A single-agent runtime with a bounded model/tool/result loop.
- A strict in-memory tool registry and permission-aware gateway.
- Workspace file creation, reading, exact-match editing, and listing.
- SQLite execution history and tool-call audit records.
- CLI entry point and a pytest suite.

Verify the latest implementation before relying on this list. In particular, inspect actual code and tests for precise validation behavior and limits.

## Explicitly do not assume these exist

The architecture and roadmap describe intended future capabilities. Do not claim they are implemented unless current source, tests, and documentation prove it. The project-state document has explicitly distinguished these items as not yet implemented or not yet verified:
- Durable multi-agent orchestration, task dependency scheduler, pause/resume/cancel lifecycle.
- Authenticated multi-agent message bus and collaboration.
- In-product Skill Registry/Engine, Agent and Skill Studio, package scanner, skill evaluation, marketplace, and version pinning.
- Scoped long-term memory and knowledge service.
- Hardened OS/container sandbox and arbitrary terminal execution.
- Browser, external network, payment, publishing, and production deployment integrations.
- HTTP API, dashboard, multi-tenant production infrastructure, and distributed services.
- Live model-provider verification.

Do not confuse a repository-local developer Skill under .agents/skills/ with the platform's future user-facing Skill Registry.

## Active product documents to consult

For architecture or product work, read the applicable current versions of:
1. docs/PROJECT_STATE.md and docs/ROADMAP.md
2. docs/ARCHITECTURE_OVERVIEW.md
3. The subsystem specification matching the change
4. The latest relevant ADR in docs/DECISIONS/
5. The implementation and tests themselves

## Phase sequencing discipline

Respect the roadmap's exit criteria. A phase can be marked complete only after implementation, deterministic tests, documentation, and the specific exit criteria all pass. A documented design is not a shipped subsystem. A mocked HTTP test is not a live-provider test. A scoped filesystem path is not a hardened sandbox.

The last recorded state at the time this reference was prepared placed the project at Phase 1.6, with local verification of the model/tool loop still pending. Re-read docs/PROJECT_STATE.md before choosing the next task; prefer completing any outstanding verification before adding unrelated capabilities.
