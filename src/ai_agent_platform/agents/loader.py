"""Load and validate declarative JSON agent manifests."""

import json
import re
from pathlib import Path
from typing import Any

from ai_agent_platform.core.errors import AgentDefinitionError
from ai_agent_platform.core.models import AgentDefinition

_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,62}$")


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AgentDefinitionError(f"'{key}' must be a non-empty string")
    return value.strip()


def parse_agent_definition(data: dict[str, Any]) -> AgentDefinition:
    if not isinstance(data, dict):
        raise AgentDefinitionError("Agent manifest must be a JSON object")
    agent_id = _required_string(data, "agent_id")
    if not _ID_PATTERN.fullmatch(agent_id):
        raise AgentDefinitionError("agent_id must be 2-63 chars: lowercase letters, digits, '_' or '-'")
    version = data.get("version", "1.0.0")
    if not isinstance(version, str) or not version.strip():
        raise AgentDefinitionError("'version' must be a non-empty string")
    return AgentDefinition(
        agent_id=agent_id,
        name=_required_string(data, "name"),
        description=_required_string(data, "description"),
        instructions=_required_string(data, "instructions"),
        version=version.strip(),
    )


def load_agent(path: str | Path) -> AgentDefinition:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentDefinitionError(f"Cannot load agent manifest: {exc}") from exc
    return parse_agent_definition(data)
