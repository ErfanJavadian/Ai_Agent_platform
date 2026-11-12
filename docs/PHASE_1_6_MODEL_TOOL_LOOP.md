# Phase 1.6 — Model-Controlled Tool Loop

## Goal
Allow a configured model to choose explicitly registered tools, receive their results, and continue for a bounded number of turns.

## Included
- OpenAI-compatible Chat Completions function/tool declarations and tool-call parsing.
- Agent manifests can declare an explicit `allowed_tools` list.
- The runtime sends only that allowlist to the model and re-checks it at the tool gateway.
- Tool results are returned to the model as tool messages.
- A configurable runtime turn ceiling and the gateway's per-execution tool-call ceiling bound the loop.
- Workspace tools are composed into each application instance; workspaces are isolated by agent ID by default.
- Tool calls and outcomes are persisted in SQLite.

## Example agent
Use `examples/agents/builder.json`. Its workspace defaults to `data/workspaces/builder`.

## Run
Configure a compatible model using environment variables (never commit credentials):
- `AI_AGENT_PROVIDER=openai_compatible`
- `AI_AGENT_API_KEY`
- `AI_AGENT_MODEL`
- Optional `AI_AGENT_API_BASE_URL`

Then run:
~~~bash
python -m ai_agent_platform run --agent examples/agents/builder.json --task "Create a simple landing page with index.html and styles.css"
~~~

## Important limitations
- The real provider path has not been live-tested against an API in this project.
- Offline loop tests use a scripted deterministic provider; they verify orchestration and real local file operations, not model intelligence.
- Only workspace file tools are available. No shell, network, browser, payment, publishing, or arbitrary host filesystem access is exposed.
- The workspace is a path-scoped application boundary, not a hardened OS sandbox.
- Tool schemas use the OpenAI-compatible Chat Completions function format. Provider-specific support for strict JSON schema can vary.

## Tests
Run `pytest -v`. Tests cover provider tool-call parsing, model/tool/result sequencing, permission enforcement, and turn limits.
