# Phase 1.3 — Provider Factory and Local Configuration

## Scope

The runtime can now obtain a provider through create_provider() instead of requiring callers to instantiate a concrete provider themselves.

Supported environment configuration:

| Variable | Purpose | Default |
|---|---|---|
| AI_AGENT_PROVIDER | Provider implementation: fake or openai_compatible | fake |
| AI_AGENT_API_KEY | Secret for the compatible endpoint | none |
| AI_AGENT_MODEL | Model identifier | none |
| AI_AGENT_API_BASE_URL | API base URL | https://api.openai.com/v1 |
| AI_AGENT_TIMEOUT_SECONDS | HTTP timeout | 30 |

## Safe local configuration

For offline development, leave the provider unset or use:

```bash
export AI_AGENT_PROVIDER=fake
```

To use a compatible live endpoint, set secrets locally in the shell session. Do not paste a real key into chat, source files, .env.example, commits, screenshots, or issue reports:

```bash
export AI_AGENT_PROVIDER=openai_compatible
export AI_AGENT_API_KEY='YOUR_KEY'
export AI_AGENT_MODEL='YOUR_MODEL'
export AI_AGENT_API_BASE_URL='https://api.openai.com/v1'
export AI_AGENT_TIMEOUT_SECONDS=30
```

Replace the example values locally. The factory reads the current process environment; it does not automatically parse .env files and introduces no dotenv dependency.

## Behavior and safety boundaries

- The default is the deterministic fake provider; no network request or API credential is needed.
- Unknown provider names fail with a configuration error rather than silently falling back.
- Selecting openai_compatible requires its normal configuration; missing values fail before a request is made.
- The factory does not make a live API call. It only constructs the selected provider.
- No key is written to disk by this feature.
- The existing OpenAI-compatible adapter still supports Chat Completions only; tool calling and multi-agent execution are out of scope.

## Verification

Run:

```bash
pytest -v
```

Factory tests use an injected environment mapping and do not need network access or real credentials.
