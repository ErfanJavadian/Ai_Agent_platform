# Phase 1 — Minimal Agent Runtime

## Implemented
- JSON agent manifest loading and validation.
- Typed domain models for definitions, requests, and responses.
- Provider protocol and deterministic FakeProvider.
- Single-agent execution lifecycle with input/output validation.
- SQLite persistence for successful execution records.
- Automated tests for manifest validation, execution, persistence, and input limits.

## Important boundary
FakeProvider is a deterministic test double, not an LLM. Agent instructions are loaded as data but are not yet sent to a real model. Tools, memory retrieval, multi-agent messaging, orchestration, and terminal execution are not enabled.

## Local setup
Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

On Windows, activate with `.venv\\Scripts\\activate`.

## Minimal usage
```python
from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.agents.runtime import AgentRuntime
from ai_agent_platform.core.models import AgentRequest
from ai_agent_platform.providers.fake import FakeProvider
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore

agent = load_agent("examples/agents/researcher.json")
runtime = AgentRuntime(FakeProvider(), SQLiteExecutionStore(":memory:"))
result = runtime.run(agent, AgentRequest(task="Research a topic"))
print(result.output)
```

The example uses an in-memory database and performs no network calls.
