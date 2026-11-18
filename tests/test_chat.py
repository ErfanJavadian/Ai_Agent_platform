from collections import deque

from ai_agent_platform.chat import run_chat
from ai_agent_platform.core.models import AgentDefinition, ProviderTurn


class StubProvider:
    def __init__(self):
        self.calls = []

    def generate_turn(self, agent, request, messages, tools):
        self.calls.append((request.task, list(messages), list(tools)))
        return ProviderTurn(content=f"پاسخ: {request.task}")


def make_agent():
    return AgentDefinition(
        agent_id="test",
        name="Test Assistant",
        description="",
        instructions="Be helpful.",
    )


def test_chat_sends_conversation_history_and_exits():
    provider = StubProvider()
    inputs = iter(["سلام", "حالت چطوره؟", "/exit"])
    outputs = []

    run_chat(provider, make_agent(), input_fn=lambda _: next(inputs), output_fn=outputs.append)

    assert len(provider.calls) == 2
    assert provider.calls[0][1] == [{"role": "user", "content": "سلام"}]
    assert provider.calls[1][1][-2:] == [
        {"role": "user", "content": "حالت چطوره؟"},
        {"role": "assistant", "content": "پاسخ: سلام"},
    ]
    assert provider.calls[0][2] == []


def test_clear_resets_history():
    provider = StubProvider()
    inputs = iter(["first", "/clear", "second", "/exit"])
    run_chat(provider, make_agent(), input_fn=lambda _: next(inputs), output_fn=lambda _: None)

    assert provider.calls[1][1] == [{"role": "user", "content": "second"}]
