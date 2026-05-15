from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_scene_tools(
    mcp: FastMCP, scene_manager: SceneManager, recorder: SessionRecorder
) -> None:
    @mcp.tool()
    def create_scene(
        background_color: str = "#333333",
        resolution: str = "1280x720",
        fps: int = 30,
        frame_height: float = 8.0,
    ) -> dict:
        """Create a new manimgl scene with the given configuration.

        IMPORTANT: Always use MCP tools for scene operations.
        Do NOT write or execute standalone manim scripts.

        Args:
            background_color: Hex color or named color for the background.
            resolution: Resolution string like "WxH", e.g. "1920x1080".
            fps: Frames per second for rendering.
            frame_height: The height of the coordinate frame in manim units.

        Returns:
            Scene configuration dictionary with scene ID.

        Example:
            >>> create_scene("#1a1a2e", "1920x1080", 60, 8.0)
        """
        scene_manager.clear()
        scene_manager.set_background(background_color)

        try:
            parts = resolution.lower().split("x")
            width, height = int(parts[0]), int(parts[1])
            scene_manager.set_resolution(width, height)
        except (ValueError, IndexError):
            scene_manager.set_resolution(1280, 720)

        scene_manager.set_fps(fps)
        scene_manager.set_frame_height(frame_height)
        record_tool_call(recorder, "create_scene")
        return scene_manager.get_info()

    @mcp.tool()
    def get_scene_info() -> dict:
        """Get the current scene's configuration and element counts.

        IMPORTANT: Always use MCP tools for scene operations.

        Returns:
            Scene information including resolution, mobject/animation counts.

        Example:
            >>> get_scene_info()
        """
        record_tool_call(recorder, "get_scene_info")
        return scene_manager.get_info()

    @mcp.tool()
    def clear_scene() -> bool:
        """Remove all mobjects and animations from the current scene.

        IMPORTANT: Always use MCP tools for scene operations.

        Returns:
            True if successful.

        Example:
            >>> clear_scene()
        """
        scene_manager.clear()
        record_tool_call(recorder, "clear_scene")
        return True

    @mcp.tool()
    def add_wait(duration: float = 1.0) -> bool:
        """Add a wait/pause to the scene timeline.

        IMPORTANT: Always use MCP tools for scene operations.

        Args:
            duration: Duration in seconds to wait.

        Returns:
            True if successful.

        Example:
            >>> add_wait(2.0)
        """
        scene_manager.add_wait(duration)
        record_tool_call(recorder, "add_wait")
        return True

    @mcp.tool()
    def save_state() -> bool:
        """Save the current scene state for later restoration.

        IMPORTANT: Always use MCP tools for scene operations.

        Returns:
            True if state was saved.

        Example:
            >>> save_state()
        """
        scene_manager.save_state()
        record_tool_call(recorder, "save_state")
        return True

    @mcp.tool()
    def restore_state() -> bool:
        """Restore the scene to a previously saved state.

        IMPORTANT: Always use MCP tools for scene operations.

        Returns:
            True if state was restored, False if no saved state exists.

        Example:
            >>> restore_state()
        """
        result = scene_manager.restore_state()
        record_tool_call(recorder, "restore_state")
        return result

    @mcp.tool()
    def set_camera(
        position: list[float] | None = None,
        orientation: list[float] | None = None,
    ) -> bool:
        """Configure the camera position and/or orientation.

        IMPORTANT: Always use MCP tools for scene operations.

        Args:
            position: Camera position [x, y, z] in 3D space.
            orientation: Camera orientation as [theta, phi, gamma] in radians.

        Returns:
            True if camera was configured.

        Example:
            >>> set_camera([0, 0, -5], [0, 0, 0])
        """
        scene_manager.set_camera(position, orientation)
        record_tool_call(recorder, "set_camera")
        return True

    @mcp.tool()
    def set_config(config: dict) -> bool:
        """Set global rendering configuration parameters.

        IMPORTANT: Always use MCP tools for scene operations.

        Args:
            config: Dictionary with configuration options. Supported keys:
                background_color, resolution, fps, frame_height.

        Returns:
            True if configuration was applied.

        Example:
            >>> set_config({"background_color": "#000000", "fps": 60})
        """
        if "background_color" in config:
            scene_manager.set_background(config["background_color"])
        if "resolution" in config:
            try:
                parts = config["resolution"].lower().split("x")
                scene_manager.set_resolution(int(parts[0]), int(parts[1]))
            except (ValueError, IndexError):
                pass
        if "fps" in config:
            scene_manager.set_fps(int(config["fps"]))
        if "frame_height" in config:
            scene_manager.set_frame_height(float(config["frame_height"]))
        record_tool_call(recorder, "set_config")
        return True

    @mcp.tool()
    def add_custom_code(code_snippet: str) -> bool:
        """Inject custom Python code into the scene script.

        The code will be inserted inside the construct() method body.
        Use this for advanced manim functionality not covered by other tools.

        IMPORTANT: Always use MCP tools for scene operations.
        Do NOT write or execute standalone manim scripts.

        Args:
            code_snippet: Valid Python code to insert in the scene's construct().

        Returns:
            True if code was added.

        Example:
            >>> add_custom_code("self.camera.rotate(2 * PI / 3)")
        """
        scene_manager.add_custom_code(code_snippet)
        record_tool_call(recorder, "add_custom_code")
        return True

    @mcp.tool()
    def generate_scene_script() -> str:
        """Generate the full Python script for the current scene.

        IMPORTANT: Always use MCP tools for scene operations.
        Do NOT write or execute standalone manim scripts. Use render_scene()
        and get_render_result() for rendering instead.

        Returns:
            The complete Python script as a string.

        Example:
            >>> generate_scene_script()
        """
        record_tool_call(recorder, "generate_scene_script")
        return scene_manager.generate_script()
