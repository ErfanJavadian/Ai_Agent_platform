"""Interactive, privacy-conscious personal chat mode."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_agent_platform.core.errors import ProviderConfigurationError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest


def run_chat(
    provider: Any,
    agent: AgentDefinition,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    max_history_messages: int = 20,
) -> None:
    """Run a terminal conversation; history stays in memory and is not persisted."""
    generate_turn = getattr(provider, "generate_turn", None)
    if not callable(generate_turn):
        raise ProviderConfigurationError(
            "Interactive chat requires AI_AGENT_PROVIDER=openai_compatible."
        )
    if max_history_messages < 2:
        raise ValueError("max_history_messages must be at least 2")

    history: list[dict[str, str]] = []
    output_fn(f"{agent.name} is ready. Type /exit to quit, /clear to clear this chat.")
    while True:
        try:
            user_text = input_fn("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\nChat ended.")
            return

        if not user_text:
            continue
        command = user_text.lower()
        if command in {"/exit", "/quit"}:
            output_fn("Chat ended.")
            return
        if command == "/clear":
            history.clear()
            output_fn("Conversation history cleared.")
            continue

        history.append({"role": "user", "content": user_text})
        # Keep complete user/assistant pairs near the context window.
        if len(history) > max_history_messages:
            history = history[-max_history_messages:]
            while history and history[0]["role"] != "user":
                history.pop(0)

        try:
            turn = generate_turn(
                agent,
                AgentRequest(task=user_text),
                list(history),
                [],
            )
        except Exception as exc:
            # Remove the unanswered user message so a retry does not duplicate it.
            if history and history[-1]["role"] == "user":
                history.pop()
            output_fn(f"Assistant error: {exc}")
            continue

        answer = getattr(turn, "content", None)
        if not isinstance(answer, str) or not answer.strip():
            output_fn("Assistant error: the model returned an empty response.")
            continue
        history.append({"role": "assistant", "content": answer.strip()})
        output_fn(f"Assistant: {answer.strip()}")
