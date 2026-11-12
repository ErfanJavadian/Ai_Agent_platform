# AI Agent Platform

An extensible, execution-oriented multi-agent organization and AI Company Builder.

> Status: Phase 1.4. A local application entry point now connects an agent manifest, provider factory, single-agent runtime, and SQLite execution history. The default provider remains a deterministic test double, not a real LLM.

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
- [Phase 1.2 real provider](docs/PHASE_1_2_REAL_PROVIDER.md)
- [Phase 1.3 provider factory](docs/PHASE_1_3_PROVIDER_FACTORY.md)
- [Phase 1.4 application entry point](docs/PHASE_1_4_APPLICATION_ENTRY_POINT.md)

## Implemented foundation
- Validated JSON agent definitions.
- Typed request and response models.
- Provider protocol with deterministic offline FakeProvider.
- OpenAI-compatible Chat Completions adapter.
- Environment-driven provider factory.
- Single-agent execution lifecycle.
- SQLite execution history.
- Python application composition root and CLI (python -m ai_agent_platform run ...).
- Automated integration tests for application wiring and CLI execution.

## Local setup
Requires Python 3.11 or newer. Install the project in editable mode with development dependencies:

~~~bash
pip install -e ".[dev]"
~~~

Run the default example agent:

~~~bash
python -m ai_agent_platform run --task "Create a short project plan"
~~~

## Engineering principles
1. Build real, testable capabilities, not role-play demonstrations.
2. This repository is the sole canonical project workspace.
3. Enforce permissions in runtime code, not only in prompts.
4. Treat model output, skills, retrieved content, and tool output as untrusted.
5. Require approval for consequential external actions.
6. Keep model providers and infrastructure behind replaceable interfaces.
7. Prefer low-cost, local-first development until scale requires otherwise.

No software license has been selected. Do not assume this repository is open-source licensed.
