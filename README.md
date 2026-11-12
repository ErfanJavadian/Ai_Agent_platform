# AI Agent Platform

An extensible, execution-oriented multi-agent organization and AI Company Builder.

> Status: Phase 1 initial implementation. A deterministic single-agent runtime and SQLite execution history are implemented. The default provider is a test double, not a real LLM.

## Product direction
The platform will let users create specialized agents, attach reusable skills and approved tools, organize agents into teams, and delegate real projects. Agents will collaborate through governed messaging, use scoped memory, and execute code in isolated project workspaces.

## Architecture documents
- [Product vision](docs/PRODUCT_VISION.md)
- [Organization charter](docs/ORGANIZATION_CHARTER.md)
- [Architecture overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Agent communication protocol](docs/AGENT_COMMUNICATION_PROTOCOL.md)
- [Orchestration core](docs/ORCHESTRATION_CORE_SPEC.md)
- [Agent and Skill Studio](docs/AGENT_AND_SKILL_STUDIO.md)
- [Terminal execution security](docs/TERMINAL_EXECUTION_SECURITY.md)
- [Roadmap](docs/ROADMAP.md)
- [Project state](docs/PROJECT_STATE.md)
- [ADR-0001: Runtime and storage](docs/DECISIONS/ADR-0001-runtime-and-storage.md)
- [Phase 1 runtime guide](docs/PHASE_1_RUNTIME.md)

## Implemented foundation
- Validated JSON agent definitions.
- Typed request and response models.
- Provider interface with deterministic offline FakeProvider.
- Single-agent execution lifecycle.
- SQLite execution history.
- Automated tests added; execution status is recorded in project state.

## Local setup
Requires Python 3.11 or newer. See [Phase 1 runtime guide](docs/PHASE_1_RUNTIME.md).

## Engineering principles
1. Build real, testable capabilities, not role-play demonstrations.
2. This repository is the sole canonical project workspace.
3. Enforce permissions in runtime code, not only in prompts.
4. Treat model output, skills, retrieved content, and tool output as untrusted.
5. Require approval for consequential external actions.
6. Keep model providers and infrastructure behind replaceable interfaces.
7. Prefer low-cost, local-first development until scale requires otherwise.

No software license has been selected. Do not assume this repository is open-source licensed.
