# Phase 1.2 — OpenAI-Compatible Model Provider

## Implemented

- A real HTTP provider for endpoints implementing the OpenAI Chat Completions request/response format.
- Standard-library HTTP transport; no additional runtime dependency is required.
- API key, model, API base URL, and timeout are read from environment variables.
- Agent instructions, description, task, and optional request context are sent to the model.
- Explicit configuration and provider-request errors.
- Deterministic tests use a mocked HTTP response and do not require internet access, an API key, or paid model usage.

## Configuration

Set these environment variables in the runtime environment:

- `AI_AGENT_PROVIDER=openai_compatible`
- `AI_AGENT_API_KEY` — secret API key; never commit it.
- `AI_AGENT_MODEL` — model identifier supported by the selected endpoint.
- `AI_AGENT_API_BASE_URL` — optional API base URL; defaults to `https://api.openai.com/v1`.
- `AI_AGENT_TIMEOUT_SECONDS` — optional request timeout; defaults to `30`.

The provider appends `/chat/completions` to the base URL unless that path is already present.

## Usage

```python
from ai_agent_platform.providers.openai_compatible import OpenAICompatibleProvider

provider = OpenAICompatibleProvider.from_env()
```

Pass the provider to the existing `AgentRuntime` in place of `FakeProvider`. The runtime contract remains unchanged.

## Compatibility and boundaries

- The endpoint must implement the OpenAI Chat Completions JSON format.
- This adapter performs one request and returns the assistant message text.
- Tool calling, streaming, retries, token accounting, provider selection/factory wiring, and multi-agent orchestration are not implemented in this milestone.
- The provider does not load `.env` files itself; the process environment must be configured by the deployment or shell.
- Never store real API keys in source files, test fixtures, commits, or public issue reports.
