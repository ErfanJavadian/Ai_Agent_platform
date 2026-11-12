import json

import pytest

from ai_agent_platform.agents.loader import load_agent, parse_agent_definition
from ai_agent_platform.core.errors import AgentDefinitionError


def test_load_example_agent():
    agent = load_agent("examples/agents/researcher.json")
    assert agent.agent_id == "researcher"
    assert agent.name == "Research Agent"


def test_reject_invalid_agent_id():
    with pytest.raises(AgentDefinitionError):
        parse_agent_definition({
            "agent_id": "Bad ID", "name": "Agent", "description": "Test",
            "instructions": "Do work",
        })


def test_reject_missing_instructions():
    with pytest.raises(AgentDefinitionError):
        parse_agent_definition({
            "agent_id": "agent", "name": "Agent", "description": "Test",
        })


def test_parse_agent_allowed_tools():
    agent = parse_agent_definition({
        "agent_id": "builder", "name": "Builder", "description": "Build",
        "instructions": "Use tools", "allowed_tools": ["workspace_write_file"],
    })
    assert agent.allowed_tools == ("workspace_write_file",)


def test_reject_duplicate_allowed_tools():
    with pytest.raises(AgentDefinitionError, match="unique"):
        parse_agent_definition({
            "agent_id": "builder", "name": "Builder", "description": "Build",
            "instructions": "Use tools",
            "allowed_tools": ["workspace_write_file", "workspace_write_file"],
        })
