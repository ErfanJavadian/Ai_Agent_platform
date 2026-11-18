# Personal Chatbot

The repository includes **Erfan Personal AI**, a Persian-first interactive assistant configured for practical help with product strategy, AI-agent engineering, business research, and learning.

## Requirements

- Python 3.11+
- An API key for an OpenAI-compatible Chat Completions endpoint
- Network access to that endpoint

## Setup

Install the project:

```bash
pip install -e ".[dev]"
```

Set configuration in your shell (do not commit credentials):

```bash
export AI_AGENT_PROVIDER=openai_compatible
export AI_AGENT_API_KEY="YOUR_API_KEY"
export AI_AGENT_MODEL="YOUR_MODEL_NAME"
# Optional for a compatible provider:
export AI_AGENT_API_BASE_URL="https://api.openai.com/v1"
export AI_AGENT_TIMEOUT_SECONDS="30"
```

On Windows PowerShell, use `$env:VARIABLE_NAME="value"` instead of `export`.

Start chatting:

```bash
ai-agent chat
```

Or run from the repository without installing the console script:

```bash
python -m ai_agent_platform chat
```

Use `/clear` to clear the in-memory conversation and `/exit` to quit. Conversation history is held only in process memory and is not written to SQLite or files. The configured model provider receives the conversation messages needed to answer. API usage may incur provider charges.

## Customization

Edit `examples/agents/erfan_personal_assistant.json` and change the `instructions` field to adjust the assistant's behavior. Keep secrets out of this file.

## Scope and limitations

This is a terminal chatbot, not a hosted website or mobile app. It does not authenticate users, provide a public endpoint, or sync conversations across devices. The model and API availability depend on the provider configured by the operator. No API key is included in the repository.
