# Mobile Web Chat

This is a minimal same-origin web interface for the existing Persian personal assistant. It uses the existing agent manifest and OpenAI-compatible provider.

## Deploy without installing anything on your phone

1. Open the repository on GitHub and confirm these files are present.
2. In Render, create a new Blueprint deployment from this repository and review `render.yaml`.
3. Add the required environment variables in the Render service settings:
   - `AI_AGENT_API_KEY`: your provider key (never commit it or send it in chat).
   - `AI_AGENT_MODEL`: a model name supported by your provider.
   - `APP_ACCESS_PASSWORD`: a long, unique password (at least 16 characters).
   - `AI_AGENT_API_BASE_URL`: optional; defaults to `https://api.openai.com/v1`.
4. Deploy, then open the generated HTTPS service URL on your phone.

The Render free plan's availability, sleep behavior, and limits may change. Model API usage may incur provider charges.

## Security and limitations

- The model API key stays in the server environment; it is never sent to browser JavaScript.
- The API requires a separate access password and applies a small in-memory per-IP request limit.
- Conversation history is held in the browser tab only and is not persisted.
- This is a personal prototype, not a multi-user production service. Add durable authentication, persistent rate limiting, monitoring, and abuse protection before public use.
- The server intentionally returns generic provider errors rather than leaking server details.
