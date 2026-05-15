from __future__ import annotations

import sys

from fastmcp import FastMCP

from mcp_manimgl.adapters.manim_adapter import ManimAdapter
from mcp_manimgl.core import SceneManager
from mcp_manimgl.core.session_recorder import SessionRecorder
from mcp_manimgl.tools.animation_tools import register_animation_tools
from mcp_manimgl.tools.audio_tools import register_audio_tools
from mcp_manimgl.tools.mobject_tools import register_mobject_tools
from mcp_manimgl.tools.rendering_tools import register_rendering_tools
from mcp_manimgl.tools.scene_tools import register_scene_tools
from mcp_manimgl.utils.dependency_checker import (
    check_dep_status,
    check_non_python_deps,
    format_missing_deps,
)


def build_server(
    scene_manager: SceneManager | None = None,
    recorder: SessionRecorder | None = None,
) -> FastMCP:
    if scene_manager is None:
        scene_manager = SceneManager()
    if recorder is None:
        recorder = SessionRecorder()

    adapter = ManimAdapter(scene_manager)

    _report_missing_deps()

    mcp = FastMCP("mcp-manimgl")

    register_scene_tools(mcp, scene_manager, recorder)
    register_mobject_tools(mcp, scene_manager, recorder)
    register_animation_tools(mcp, scene_manager, recorder)
    register_rendering_tools(mcp, adapter, recorder)
    register_audio_tools(mcp, scene_manager, recorder)

    @mcp.resource("mcp-manimgl://info")
    def get_info() -> dict:
        missing = check_non_python_deps()
        return {
            "server": "mcp-manimgl",
            "description": "Manim OpenGL animation server. ALWAYS use the MCP tools for all scene operations. Do NOT write standalone Python scripts or execute subprocess commands for scene building, rendering, or animation tasks.",
            "version": "0.1.1",
            "session_path": recorder.path,
            "dependencies": {
                "missing_non_python_deps": missing,
                "all_available": len(missing) == 0,
                "status": check_dep_status(),
            },
            "render_status": adapter.get_status(),
            "scene": scene_manager.get_info(),
        }

    return mcp


def _report_missing_deps() -> None:
    missing = check_non_python_deps()
    if missing:
        msg = format_missing_deps(missing)
        print(msg, file=sys.stderr)
