# AI Agent Platform

An extensible, execution-oriented multi-agent organization and AI Company Builder.

> Status: Phase 1.7 implementation. In addition to the bounded model/tool loop, failed executions are persisted in SQLite with a bounded error summary. Local verification of Phase 1.7 is pending.

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
- [Phase 1.2 real provider](docs/PHASE_1_2_REAL_PROVIDER.md)
- [Phase 1.3 provider factory](docs/PHASE_1_3_PROVIDER_FACTORY.md)
- [Phase 1.4 application entry point](docs/PHASE_1_4_APPLICATION_ENTRY_POINT.md)
- [Phase 1.5 governed workspace tools](docs/PHASE_1_5_GOVERNED_WORKSPACE_TOOLS.md)
- [Phase 1.6 model/tool loop](docs/PHASE_1_6_MODEL_TOOL_LOOP.md)

## Implemented
- Validated JSON agent manifests with explicit per-agent tool allowlists.
- Deterministic offline FakeProvider and OpenAI-compatible Chat Completions adapter.
- Model-controlled function/tool call parsing and bounded tool/result loop.
- Permission-aware tool registry and gateway.
- Workspace file creation, reading, exact-match editing, and listing.
- SQLite execution history, failed-run records, and tool-call audit records (including a non-destructive schema migration).
- CLI application entry point and automated tests.

## Local setup
Requires Python 3.11 or newer:
~~~bash
pip install -e ".[dev]"
pytest -v
~~~

Default deterministic example:
~~~bash
python -m ai_agent_platform run --task "Create a short project plan"
~~~

Real-model builder example:
~~~bash
python -m ai_agent_platform run --agent examples/agents/builder.json --task "Create a simple landing page with index.html and styles.css"
~~~

Configure `AI_AGENT_PROVIDER=openai_compatible`, `AI_AGENT_API_KEY`, and `AI_AGENT_MODEL` in the local shell before the real-model example. Do not commit API keys.

No arbitrary shell execution or external side effects are enabled. The workspace path boundary is not a hardened OS sandbox. No software license has been selected.
