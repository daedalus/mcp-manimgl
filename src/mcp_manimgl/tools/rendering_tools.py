from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.adapters.manim_adapter import ManimAdapter


def register_rendering_tools(
    mcp: FastMCP, adapter: ManimAdapter, recorder: SessionRecorder
) -> None:
    @mcp.tool()
    def render_scene(output_path: str | None = None, fmt: str = "mp4") -> dict:
        """Render the current scene to a video file.

        Renders in the background to avoid MCP timeouts.
        Returns a render_id immediately. Poll get_render_result() with
        that render_id to check completion and get the output path.

        IMPORTANT: Always use this MCP tool for rendering. Do NOT write
        or execute standalone manim scripts for scene operations.

        Args:
            output_path: Path for the output video file. If None, uses a temp file.
            fmt: Output format ("mp4", "gif", "mov").

        Returns:
            Dictionary with render_id and status.

        Example:
            >>> render_scene("/tmp/my_animation.mp4", "mp4")
        """
        result = adapter.render_scene(output_path, fmt)
        record_tool_call(recorder, "render_scene")
        return result

    @mcp.tool()
    def get_render_result(render_id: str) -> dict:
        """Poll for the result of an async render started by render_scene().

        Returns the render result dict when done, or a "still running" status.
        Keep polling every 5-10 seconds until status is "completed" or "failed".

        IMPORTANT: Always use this MCP tool for scene operations. Do NOT write
        or execute standalone manim scripts.

        Args:
            render_id: The render_id returned by render_scene().

        Returns:
            Dictionary with render status and result.

        Example:
            >>> get_render_result("abc123def456")
        """
        result = adapter.get_render_result(render_id)
        record_tool_call(recorder, "get_render_result")
        if result is None:
            return {"status": "unknown", "error": "No render found with this ID"}
        return result

    @mcp.tool()
    def save_frame(output_path: str | None = None) -> dict:
        """Save a single frame (image) of the current scene.

        IMPORTANT: Always use this MCP tool for scene operations. Do NOT write
        or execute standalone manim scripts.

        Args:
            output_path: Path for the output PNG image. If None, uses a temp file.

        Returns:
            Dictionary with frame save result including output_path.

        Example:
            >>> save_frame("/tmp/frame.png")
        """
        result = adapter.save_frame(output_path)
        record_tool_call(recorder, "save_frame")
        return result

    @mcp.tool()
    def get_render_status() -> dict:
        """Check if manimgl and OpenGL are available for rendering.

        IMPORTANT: Always use this MCP tool for scene operations. Do NOT write
        or execute standalone manim scripts.

        Returns:
            Dictionary with availability status of manimgl and OpenGL.

        Example:
            >>> get_render_status()
        """
        record_tool_call(recorder, "get_render_status")
        return adapter.get_status()
