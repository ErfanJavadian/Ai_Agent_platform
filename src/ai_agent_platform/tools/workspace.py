"""Workspace-scoped file tools; no host shell or arbitrary path access."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
from typing import Any

from ai_agent_platform.core.errors import ToolExecutionError
from ai_agent_platform.tools.registry import ToolRegistry, ToolSpec


class WorkspaceTools:
    """Read and write UTF-8 text files below one configured workspace root."""

    def __init__(
        self,
        root: str | Path,
        *,
        max_file_bytes: int = 1_000_000,
        max_list_entries: int = 200,
    ) -> None:
        if max_file_bytes < 1 or max_list_entries < 1:
            raise ValueError("Workspace limits must be positive")
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)
        self.root = self.root.resolve()
        self.max_file_bytes = max_file_bytes
        self.max_list_entries = max_list_entries

    def _resolve(self, relative_path: str, *, allow_root: bool = False) -> Path:
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ToolExecutionError("relative_path must be a non-empty string")
        if "\x00" in relative_path or "\\" in relative_path:
            raise ToolExecutionError("Invalid path")
        raw = PurePosixPath(relative_path)
        if raw.is_absolute() or ".." in raw.parts:
            raise ToolExecutionError("Path must stay inside the workspace")
        candidate = self.root.joinpath(*raw.parts)
        current = self.root
        for part in raw.parts:
            current = current / part
            if current.is_symlink():
                raise ToolExecutionError("Symbolic links are not allowed in workspace paths")
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.root):
            raise ToolExecutionError("Path escapes the workspace")
        if not allow_root and resolved == self.root:
            raise ToolExecutionError("A file path is required")
        return resolved

    def read_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        path = self._resolve(arguments["relative_path"])
        if not path.is_file():
            raise ToolExecutionError("Requested workspace file does not exist")
        if path.stat().st_size > self.max_file_bytes:
            raise ToolExecutionError("File exceeds the configured size limit")
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ToolExecutionError("Only UTF-8 text files can be read") from exc
        return {"relative_path": path.relative_to(self.root).as_posix(), "content": content}

    def write_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        relative_path = arguments["relative_path"]
        content = arguments["content"]
        if not isinstance(content, str):
            raise ToolExecutionError("content must be a string")
        size = len(content.encode("utf-8"))
        if size > self.max_file_bytes:
            raise ToolExecutionError("Content exceeds the configured file size limit")
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path = self._resolve(relative_path)
        if path.exists() and not path.is_file():
            raise ToolExecutionError("Target path is not a regular file")
        path.write_text(content, encoding="utf-8")
        return {"relative_path": path.relative_to(self.root).as_posix(), "bytes_written": size}

    def list_files(self, arguments: dict[str, Any]) -> dict[str, Any]:
        directory = self._resolve(arguments.get("relative_path", "."), allow_root=True)
        if not directory.is_dir():
            raise ToolExecutionError("Requested workspace directory does not exist")
        found: list[str] = []
        for current, directories, filenames in os.walk(directory, followlinks=False):
            current_path = Path(current)
            directories[:] = sorted(
                name for name in directories if not (current_path / name).is_symlink()
            )
            for filename in sorted(filenames):
                candidate = current_path / filename
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                found.append(candidate.relative_to(self.root).as_posix())
                if len(found) >= self.max_list_entries:
                    return {"files": found, "truncated": True}
        return {"files": found, "truncated": False}


def register_workspace_tools(registry: ToolRegistry, workspace: WorkspaceTools) -> None:
    """Register the four built-in workspace operations."""
    registry.register(ToolSpec(
        name="workspace_read_file",
        description="Read a UTF-8 text file from the agent workspace.",
        required_arguments=frozenset({"relative_path"}),
        allowed_arguments=frozenset({"relative_path"}),
        handler=workspace.read_file,
        parameters={"type":"object","properties":{"relative_path":{"type":"string"}},"required":["relative_path"],"additionalProperties":False},
    ))
    registry.register(ToolSpec(
        name="workspace_write_file",
        description="Create or replace a UTF-8 text file inside the agent workspace.",
        required_arguments=frozenset({"relative_path", "content"}),
        allowed_arguments=frozenset({"relative_path", "content"}),
        handler=workspace.write_file,
        parameters={"type":"object","properties":{"relative_path":{"type":"string"},"content":{"type":"string"}},"required":["relative_path","content"],"additionalProperties":False},
    ))
    registry.register(ToolSpec(
        name="workspace_list_files",
        description="List files in the agent workspace or one subdirectory.",
        required_arguments=frozenset(),
        allowed_arguments=frozenset({"relative_path"}),
        handler=workspace.list_files,
        parameters={"type":"object","properties":{"relative_path":{"type":"string"}},"required":[],"additionalProperties":False},
    ))
    registry.register(ToolSpec(
        name="workspace_edit_file",
        description="Replace the first exact occurrence of text in a UTF-8 workspace file.",
        required_arguments=frozenset({"relative_path", "old_text", "new_text"}),
        allowed_arguments=frozenset({"relative_path", "old_text", "new_text"}),
        handler=lambda args: _edit_file(workspace, args),
        parameters={"type":"object","properties":{"relative_path":{"type":"string"},"old_text":{"type":"string"},"new_text":{"type":"string"}},"required":["relative_path","old_text","new_text"],"additionalProperties":False},
    ))


def _edit_file(workspace: WorkspaceTools, arguments: dict[str, Any]) -> dict[str, Any]:
    old_text, new_text = arguments["old_text"], arguments["new_text"]
    if not isinstance(old_text, str) or not old_text:
        raise ToolExecutionError("old_text must be a non-empty string")
    if not isinstance(new_text, str):
        raise ToolExecutionError("new_text must be a string")
    existing = workspace.read_file({"relative_path": arguments["relative_path"]})
    occurrences = existing["content"].count(old_text)
    if occurrences != 1:
        raise ToolExecutionError(f"Edit requires exactly one match; found {occurrences}")
    return workspace.write_file({
        "relative_path": arguments["relative_path"],
        "content": existing["content"].replace(old_text, new_text, 1),
    })
