from __future__ import annotations

from fastmcp import FastMCP

from mcp_manimgl_server.adapters.manim_adapter import ManimAdapter
from mcp_manimgl_server.core import SceneManager
from mcp_manimgl_server.tools.animation_tools import register_animation_tools
from mcp_manimgl_server.tools.mobject_tools import register_mobject_tools
from mcp_manimgl_server.tools.rendering_tools import register_rendering_tools
from mcp_manimgl_server.tools.scene_tools import register_scene_tools

_scene_manager = SceneManager()
_adapter = ManimAdapter(_scene_manager)

mcp = FastMCP("mcp-manimgl-server")

register_scene_tools(mcp, _scene_manager)
register_mobject_tools(mcp, _scene_manager)
register_animation_tools(mcp, _scene_manager)
register_rendering_tools(mcp, _adapter)


@mcp.resource("mcp-manimgl://info")
def get_info() -> dict:
    """Get server and environment information."""
    return {
        "server": "mcp-manimgl-server",
        "version": "0.1.0",
        "render_status": _adapter.get_status(),
        "scene": _scene_manager.get_info(),
    }
