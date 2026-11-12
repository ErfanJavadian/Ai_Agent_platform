import json
from urllib.request import Request

import pytest

from ai_agent_platform.core.errors import ProviderConfigurationError, ProviderRequestError
from ai_agent_platform.core.models import AgentDefinition, AgentRequest
from ai_agent_platform.providers.openai_compatible import OpenAICompatibleProvider


def make_agent():
    return AgentDefinition(
        agent_id="researcher", name="Researcher",
        description="Research assistant", instructions="Be accurate and cite uncertainty.",
    )


def test_provider_loads_configuration_from_environment():
    provider = OpenAICompatibleProvider.from_env({
        "AI_AGENT_API_KEY": "test-secret", "AI_AGENT_MODEL": "test-model",
        "AI_AGENT_API_BASE_URL": "https://example.test/v1",
        "AI_AGENT_TIMEOUT_SECONDS": "12",
    })
    assert provider.name == "openai_compatible"
    assert provider._endpoint == "https://example.test/v1/chat/completions"
    assert provider._timeout == 12


@pytest.mark.parametrize("environment", [
    {}, {"AI_AGENT_API_KEY": "test-secret"}, {"AI_AGENT_MODEL": "test-model"},
])
def test_provider_rejects_missing_required_environment(environment):
    with pytest.raises(ProviderConfigurationError):
        OpenAICompatibleProvider.from_env(environment)


def test_provider_rejects_invalid_timeout():
    with pytest.raises(ProviderConfigurationError, match="must be a number"):
        OpenAICompatibleProvider.from_env({
            "AI_AGENT_API_KEY": "test-secret", "AI_AGENT_MODEL": "test-model",
            "AI_AGENT_TIMEOUT_SECONDS": "not-a-number",
        })


def test_provider_sends_agent_instructions_and_returns_model_content(monkeypatch):
    captured = {}

    class FakeHTTPResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({"choices":[{"message":{"content":"  Real model answer  "}}]}).encode()

    def fake_urlopen(request, timeout):
        assert isinstance(request, Request)
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode())
        return FakeHTTPResponse()

    monkeypatch.setattr("ai_agent_platform.providers.openai_compatible.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider(
        api_key="test-secret", model="test-model",
        api_base_url="https://example.test/v1", timeout=9,
    )
    output = provider.generate(make_agent(), AgentRequest(
        task="Compare two approaches", context={"region":"EU"}
    ))
    assert output == "Real model answer"
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["authorization"] == "Bearer test-secret"
    assert captured["timeout"] == 9
    assert captured["payload"]["model"] == "test-model"
    assert "Be accurate and cite uncertainty." in captured["payload"]["messages"][0]["content"]
    assert captured["payload"]["messages"][1]["content"] == "Compare two approaches"
    assert '"region": "EU"' in captured["payload"]["messages"][0]["content"]


def test_provider_rejects_invalid_response(monkeypatch):
    class FakeHTTPResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"unexpected": true}'
    monkeypatch.setattr("ai_agent_platform.providers.openai_compatible.urlopen",
                        lambda *args, **kwargs: FakeHTTPResponse())
    provider = OpenAICompatibleProvider(api_key="secret", model="model")
    with pytest.raises(ProviderRequestError, match="invalid Chat Completions response"):
        provider.generate(make_agent(), AgentRequest(task="Hello"))


def test_provider_rejects_empty_model_content(monkeypatch):
    class FakeHTTPResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"choices":[{"message":{"content":"  "}}]}'
    monkeypatch.setattr("ai_agent_platform.providers.openai_compatible.urlopen",
                        lambda *args, **kwargs: FakeHTTPResponse())
    provider = OpenAICompatibleProvider(api_key="secret", model="model")
    with pytest.raises(ProviderRequestError, match="empty message content"):
        provider.generate(make_agent(), AgentRequest(task="Hello"))


def test_provider_parses_tool_calls_and_sends_tool_schemas(monkeypatch):
    captured = {}
    response = {"choices":[{"message":{
        "content":None,
        "tool_calls":[{"id":"call-1","type":"function","function":{
            "name":"workspace_write_file",
            "arguments":'{"relative_path":"index.html","content":"Hello"}'
        }}]
    }}]}
    class FakeHTTPResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(response).encode()
    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode())
        return FakeHTTPResponse()
    monkeypatch.setattr("ai_agent_platform.providers.openai_compatible.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider(api_key="secret", model="tool-model")
    from ai_agent_platform.core.models import AgentRequest
    from ai_agent_platform.providers.openai_compatible import OpenAICompatibleProvider
    tools = [{"type":"function","function":{"name":"workspace_write_file","description":"write","parameters":{
        "type":"object","properties":{"relative_path":{"type":"string"},"content":{"type":"string"}},
        "required":["relative_path","content"],"additionalProperties":False
    },"strict":True}}]
    turn = provider.generate_turn(make_agent(), AgentRequest("Build a page"), [
        {"role":"user","content":"Build a page"}
    ], tools)
    assert turn.tool_calls[0].name == "workspace_write_file"
    assert turn.tool_calls[0].arguments["content"] == "Hello"
    assert captured["payload"]["tools"] == tools
    assert captured["payload"]["tool_choice"] == "auto"
