from __future__ import annotations

import inspect
import json
import os
import uuid
from typing import Any


def record_tool_call(recorder: SessionRecorder, tool_name: str) -> None:
    """Capture the calling function's parameters and record them.

    Call this as the last line inside any MCP tool function.
    Uses inspect to extract only the function's formal parameters,
    excluding closure variables and local temporaries.
    """
    frame = inspect.currentframe()
    if frame is None:
        return
    caller = frame.f_back
    if caller is None:
        return
    arg_info = inspect.getargvalues(caller)
    params: dict[str, Any] = {}
    for arg in arg_info.args:
        if arg in arg_info.locals:
            params[arg] = arg_info.locals[arg]
    if arg_info.keywords is not None and arg_info.keywords in arg_info.locals:
        kw = arg_info.locals[arg_info.keywords]
        if isinstance(kw, dict):
            params.update(kw)
    recorder.record(tool_name, params)


class SessionRecorder:
    def __init__(self, output_dir: str | None = None) -> None:
        if output_dir is None:
            from mcp_manimgl import MCP_MANIMGL_WORKDIR
            output_dir = os.path.join(MCP_MANIMGL_WORKDIR, "sessions")
        self._session_id = uuid.uuid4().hex[:12]
        self._output_dir = output_dir
        self._path = os.path.join(output_dir, f"session_{self._session_id}.json")
        self._commands: list[dict[str, Any]] = []
        os.makedirs(output_dir, exist_ok=True)

    @property
    def path(self) -> str:
        return self._path

    def record(self, tool: str, arguments: dict[str, Any]) -> None:
        self._commands.append({"tool": tool, "arguments": dict(arguments)})
        try:
            with open(self._path, "w") as f:
                json.dump(self._commands, f, indent=2)
        except OSError:
            pass
