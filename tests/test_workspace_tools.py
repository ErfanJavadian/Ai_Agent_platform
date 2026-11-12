import pytest

from ai_agent_platform.core.errors import ToolExecutionError, ToolPermissionError
from ai_agent_platform.storage.sqlite import SQLiteExecutionStore
from ai_agent_platform.tools import (
    ToolGateway,
    ToolRegistry,
    WorkspaceTools,
    register_workspace_tools,
)


def make_gateway(tmp_path, **gateway_options):
    workspace = WorkspaceTools(tmp_path / "workspace")
    registry = ToolRegistry()
    register_workspace_tools(registry, workspace)
    store = SQLiteExecutionStore(tmp_path / "history.sqlite3")
    gateway = ToolGateway(registry, store=store, **gateway_options)
    return gateway, workspace, store


def call(gateway, name, arguments, *, allowed=None, execution_id="run-1"):
    return gateway.execute(
        agent_id="builder",
        tool_name=name,
        arguments=arguments,
        allowed_tools=allowed or {
            "workspace_read_file",
            "workspace_write_file",
            "workspace_edit_file",
            "workspace_list_files",
        },
        execution_id=execution_id,
    )


def test_workspace_tools_create_read_edit_and_list_files(tmp_path):
    gateway, _, store = make_gateway(tmp_path)
    created = call(gateway, "workspace_write_file", {
        "relative_path": "site/index.html",
        "content": "<h1>Hello</h1>",
    })
    assert created["bytes_written"] > 0

    read = call(gateway, "workspace_read_file", {"relative_path": "site/index.html"})
    assert read["content"] == "<h1>Hello</h1>"

    edited = call(gateway, "workspace_edit_file", {
        "relative_path": "site/index.html",
        "old_text": "Hello",
        "new_text": "Agent",
    })
    assert edited["bytes_written"] > 0

    listed = call(gateway, "workspace_list_files", {"relative_path": "."})
    assert listed["files"] == ["site/index.html"]
    assert listed["truncated"] is False

    traces = store.list_tool_calls("run-1")
    assert len(traces) == 4
    assert all(item["status"] == "succeeded" for item in traces)


def test_workspace_rejects_parent_traversal(tmp_path):
    gateway, _, _ = make_gateway(tmp_path)
    with pytest.raises(ToolExecutionError, match="inside the workspace"):
        call(gateway, "workspace_write_file", {
            "relative_path": "../outside.txt",
            "content": "blocked",
        })


def test_workspace_rejects_absolute_paths(tmp_path):
    gateway, workspace, _ = make_gateway(tmp_path)
    with pytest.raises(ToolExecutionError, match="inside the workspace"):
        call(gateway, "workspace_read_file", {
            "relative_path": str(tmp_path / "outside.txt"),
        })


def test_workspace_rejects_symlink_escape(tmp_path):
    gateway, workspace, _ = make_gateway(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace.root / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ToolExecutionError, match="Symbolic links"):
        call(gateway, "workspace_write_file", {
            "relative_path": "linked/escape.txt",
            "content": "blocked",
        })


def test_gateway_rejects_tools_not_in_agent_allowlist(tmp_path):
    gateway, _, store = make_gateway(tmp_path)
    with pytest.raises(ToolPermissionError):
        call(
            gateway,
            "workspace_list_files",
            {},
            allowed={"workspace_read_file"},
        )
    trace = store.list_tool_calls("run-1")
    assert trace[0]["status"] == "failed"
    assert "not permitted" in trace[0]["error"]


def test_gateway_rejects_unexpected_arguments(tmp_path):
    gateway, _, _ = make_gateway(tmp_path)
    with pytest.raises(ToolExecutionError, match="Unexpected arguments"):
        call(gateway, "workspace_read_file", {
            "relative_path": "missing.txt",
            "delete_everything": True,
        })


def test_gateway_rejects_missing_arguments(tmp_path):
    gateway, _, _ = make_gateway(tmp_path)
    with pytest.raises(ToolExecutionError, match="Missing required arguments"):
        call(gateway, "workspace_write_file", {"relative_path": "a.txt"})


def test_gateway_enforces_per_execution_call_limit(tmp_path):
    gateway, _, _ = make_gateway(tmp_path, max_calls_per_execution=1)
    call(gateway, "workspace_list_files", {})
    with pytest.raises(ToolExecutionError, match="call limit"):
        call(gateway, "workspace_list_files", {})


def test_workspace_enforces_file_size_limit(tmp_path):
    workspace = WorkspaceTools(tmp_path / "workspace", max_file_bytes=4)
    with pytest.raises(ToolExecutionError, match="size limit"):
        workspace.write_file({"relative_path": "large.txt", "content": "12345"})


def test_edit_requires_one_exact_match(tmp_path):
    gateway, _, _ = make_gateway(tmp_path)
    call(gateway, "workspace_write_file", {
        "relative_path": "same.txt",
        "content": "repeat repeat",
    })
    with pytest.raises(ToolExecutionError, match="exactly one match"):
        call(gateway, "workspace_edit_file", {
            "relative_path": "same.txt",
            "old_text": "repeat",
            "new_text": "changed",
        })


def test_registry_rejects_duplicate_tool_names(tmp_path):
    workspace = WorkspaceTools(tmp_path / "workspace")
    registry = ToolRegistry()
    register_workspace_tools(registry, workspace)
    with pytest.raises(ToolExecutionError, match="already registered"):
        register_workspace_tools(registry, workspace)
