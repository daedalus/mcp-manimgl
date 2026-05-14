from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.adapters.manim_adapter import ManimAdapter


def register_rendering_tools(mcp: FastMCP, adapter: ManimAdapter) -> None:
    @mcp.tool()
    def render_scene(output_path: str | None = None, fmt: str = "mp4") -> dict:
        """Render the current scene to a video file.

        Args:
            output_path: Path for the output video file. If None, uses a temp file.
            fmt: Output format ("mp4", "gif", "mov").

        Returns:
            Dictionary with rendering result including output_path and status.

        Example:
            >>> render_scene("/tmp/my_animation.mp4", "mp4")
        """
        return adapter.render_scene(output_path, fmt)

    @mcp.tool()
    def save_frame(output_path: str | None = None) -> dict:
        """Save a single frame (image) of the current scene.

        Args:
            output_path: Path for the output PNG image. If None, uses a temp file.

        Returns:
            Dictionary with frame save result including output_path.

        Example:
            >>> save_frame("/tmp/frame.png")
        """
        return adapter.save_frame(output_path)

    @mcp.tool()
    def get_render_status() -> dict:
        """Check if manimgl and OpenGL are available for rendering.

        Returns:
            Dictionary with availability status of manimgl and OpenGL.

        Example:
            >>> get_render_status()
        """
        return adapter.get_status()
