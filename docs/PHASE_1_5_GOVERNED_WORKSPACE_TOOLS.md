# Phase 1.5 — Governed Workspace Tools

## Goal

Introduce the first executable platform tools without granting agents arbitrary host access.

## Included

- A tool registry with explicit argument contracts.
- A gateway that checks an agent's tool allowlist before execution.
- A per-execution tool-call limit and argument-size limit.
- Four workspace tools:
  - `workspace_write_file`
  - `workspace_read_file`
  - `workspace_edit_file`
  - `workspace_list_files`
- UTF-8 text-only file operations below one configured workspace root.
- Rejection of absolute paths, parent traversal, and symbolic links.
- SQLite audit records for successful and failed tool calls.

## Security boundaries

- Tools are registered by platform code; a model cannot install a new handler.
- The caller supplies an explicit allowlist for each agent execution.
- Tool arguments must be JSON objects matching the registered argument contract.
- Tool calls are bounded per execution.
- File content and arguments have size limits.
- No shell, subprocess, network, or arbitrary host filesystem tool is exposed.

The workspace layer is a path-scoped application boundary, not an operating-system sandbox against hostile local processes or concurrent filesystem races. A hardened execution sandbox remains a separate milestone.

## Example (direct gateway use)

~~~python
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore
from ai_agent_platform.tools import (
    ToolGateway, ToolRegistry, WorkspaceTools, register_workspace_tools,
)

workspace = WorkspaceTools("data/workspaces/demo")
registry = ToolRegistry()
register_workspace_tools(registry, workspace)
store = SQLiteExecutionStore("data/agent_platform.sqlite3")
gateway = ToolGateway(registry, store=store)

result = gateway.execute(
    agent_id="builder",
    tool_name="workspace_write_file",
    arguments={"relative_path": "index.html", "content": "<h1>Hello</h1>"},
    allowed_tools={"workspace_write_file"},
    execution_id="demo-001",
)
print(result)
~~~

## Tests

Run `pytest -v`. Tests cover real file creation, reading, exact-match editing, listing, path traversal, absolute paths, symlink escapes, permission denial, strict arguments, call limits, file-size limits, and persisted audit records.

## Not yet included

The model does not yet select or call tools. The next milestone adds tool-call support to the model-provider contract and a bounded model/tool/result loop. Fake-provider tests remain deterministic and are not evidence of live LLM tool use.
