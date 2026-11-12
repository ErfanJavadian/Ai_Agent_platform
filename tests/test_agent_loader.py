import pytest
from ai_agent_platform.agents.loader import load_agent, parse_agent_definition
from ai_agent_platform.core.errors import AgentDefinitionError


def test_load_example_agent():
    agent = load_agent("examples/agents/researcher.json")
    assert agent.agent_id == "researcher"
    assert agent.name == "Research Agent"


def test_reject_invalid_agent_id():
    with pytest.raises(AgentDefinitionError):
        parse_agent_definition({"agent_id": "Bad ID", "name": "Name",
            "description": "Description", "instructions": "Instructions"})


def test_reject_missing_instructions():
    with pytest.raises(AgentDefinitionError):
        parse_agent_definition({"agent_id": "researcher", "name": "Name",
            "description": "Description"})
