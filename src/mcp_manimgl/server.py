from __future__ import annotations

from fastmcp import FastMCP

from mcp_manimgl.adapters.manim_adapter import ManimAdapter
from mcp_manimgl.core import SceneManager
from mcp_manimgl.tools.animation_tools import register_animation_tools
from mcp_manimgl.tools.audio_tools import register_audio_tools
from mcp_manimgl.tools.mobject_tools import register_mobject_tools
from mcp_manimgl.tools.rendering_tools import register_rendering_tools
from mcp_manimgl.tools.scene_tools import register_scene_tools

_scene_manager = SceneManager()
_adapter = ManimAdapter(_scene_manager)

mcp = FastMCP("mcp-manimgl")

register_scene_tools(mcp, _scene_manager)
register_mobject_tools(mcp, _scene_manager)
register_animation_tools(mcp, _scene_manager)
register_rendering_tools(mcp, _adapter)
register_audio_tools(mcp, _scene_manager)


@mcp.resource("mcp-manimgl://info")
def get_info() -> dict:
    """Get server and environment information."""
    return {
        "server": "mcp-manimgl",
        "version": "0.1.0",
        "render_status": _adapter.get_status(),
        "scene": _scene_manager.get_info(),
    }
