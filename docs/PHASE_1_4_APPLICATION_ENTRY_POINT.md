# Phase 1.4 — Application Entry Point

## What was added

The application composition root connects the existing building blocks:

1. Load and validate one JSON agent manifest.
2. Select a model provider through the environment-driven provider factory.
3. Create the SQLite execution-history store.
4. Construct the single-agent runtime.
5. Execute a task and return the persisted response.

The command-line interface makes this flow available without writing Python code.

## Run locally

From the repository root:

~~~bash
python -m ai_agent_platform run --task "Create a short project plan"
~~~

Optional paths:

~~~bash
python -m ai_agent_platform run \
  --agent examples/agents/researcher.json \
  --task "Analyze the pros and cons of two approaches" \
  --database data/agent_platform.sqlite3
~~~

An installed console command is also registered:

~~~bash
ai-agent run --task "Create a short project plan"
~~~

If the package was already installed in editable mode before this change, refresh its project metadata with:

~~~bash
pip install -e .
~~~

## Provider behavior

- With AI_AGENT_PROVIDER unset or set to fake, the platform uses the deterministic FakeProvider. This is useful for checking the complete application flow, but it is not a language model and does not perform semantic work.
- With AI_AGENT_PROVIDER=openai_compatible and valid local environment variables, the existing OpenAI-compatible Chat Completions adapter is selected.
- The provider factory validates configuration before execution.
- A real provider request is not part of the automated tests. A successful CLI run with the fake provider does not prove live model connectivity.

See docs/PHASE_1_2_REAL_PROVIDER.md and docs/PHASE_1_3_PROVIDER_FACTORY.md for the local provider configuration.

## Tests

~~~bash
pytest -v
~~~

The integration tests use the fake provider and temporary SQLite files. They verify composition, CLI output, and persisted execution history without network access.

## Not yet implemented

This entry point does not add tool calling, an agent decision/action loop, external tools, shared memory, multiple agents, or terminal execution. The model can generate a response, but it cannot yet take actions through platform tools. Those capabilities belong to the next execution milestone.
