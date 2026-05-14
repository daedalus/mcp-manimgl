from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.animation_builder import AnimationBuilder

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_animation_tools(mcp: FastMCP, scene_manager: SceneManager) -> None:
    @mcp.tool()
    def animate_transform(
        mobject_id: str,
        target_mobject_type: str | None = None,
        target_config: dict | None = None,
        run_time: float = 1.0,
        rate_func: str = "smooth",
    ) -> dict:
        """Animate a mobject transforming into a new shape.

        Args:
            mobject_id: ID of the mobject to transform.
            target_mobject_type: Target shape type (e.g. "square", "circle").
                If None, no shape change occurs.
            target_config: Configuration for the target shape (color, etc.).
            run_time: Duration of the animation in seconds.
            rate_func: Rate function for easing.

        Returns:
            Animation information.

        Example:
            >>> animate_transform("m_abc12345", "square",
            ...     {"color": "#FF0000"}, 2.0, "ease_out_sine")
        """
        record = AnimationBuilder.animate_transform(
            mobject_id,
            target_mobject_type,
            target_config,
            run_time,
            rate_func,
        )
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_fade_in(
        mobject_id: str,
        run_time: float = 1.0,
        shift_direction: list[float] | None = None,
    ) -> dict:
        """Animate a mobject fading into the scene.

        Args:
            mobject_id: ID of the mobject to fade in.
            run_time: Duration of the animation in seconds.
            shift_direction: Optional direction vector to shift while fading.

        Returns:
            Animation information.

        Example:
            >>> animate_fade_in("m_abc12345", 2.0, [0, 1, 0])
        """
        record = AnimationBuilder.animate_fade_in(mobject_id, run_time, shift_direction)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_fade_out(mobject_id: str, run_time: float = 1.0) -> dict:
        """Animate a mobject fading out of the scene.

        Args:
            mobject_id: ID of the mobject to fade out.
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_fade_out("m_abc12345", 1.5)
        """
        record = AnimationBuilder.animate_fade_out(mobject_id, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_grow(
        mobject_id: str,
        grow_type: str = "center",
        run_time: float = 1.0,
    ) -> dict:
        """Animate a mobject growing into view.

        Args:
            mobject_id: ID of the mobject to animate.
            grow_type: Growth style:
                "center" - grow from center outwards
                "point" - grow from a specific point
                "edge" - grow from an edge
                "arrow" - special grow for arrows
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_grow("m_abc12345", "center", 2.0)
        """
        record = AnimationBuilder.animate_grow(mobject_id, grow_type, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_rotate(
        mobject_id: str,
        angle: float | None = None,
        axis: list[float] | None = None,
        run_time: float = 1.0,
    ) -> dict:
        """Animate a mobject rotating.

        Args:
            mobject_id: ID of the mobject to rotate.
            angle: Rotation angle in radians (default: full rotation).
            axis: Rotation axis [x, y, z] (default: [0, 0, 1]).
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_rotate("m_abc12345", 3.14159, [0, 0, 1], 2.0)
        """
        record = AnimationBuilder.animate_rotate(mobject_id, angle, axis, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_scale(
        mobject_id: str, scale_factor: float, run_time: float = 1.0
    ) -> dict:
        """Animate a mobject scaling in size.

        Args:
            mobject_id: ID of the mobject to scale.
            scale_factor: Target scale factor.
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_scale("m_abc12345", 2.0, 1.5)
        """
        record = AnimationBuilder.animate_scale(mobject_id, scale_factor, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_shift(
        mobject_id: str, vector: list[float], run_time: float = 1.0
    ) -> dict:
        """Animate a mobject shifting by a displacement vector.

        Args:
            mobject_id: ID of the mobject to shift.
            vector: Displacement [dx, dy, dz].
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_shift("m_abc12345", [2, 0, 0], 1.5)
        """
        record = AnimationBuilder.animate_shift(mobject_id, vector, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_indicate(mobject_id: str, run_time: float = 0.5) -> dict:
        """Animate a mobject being highlighted/indicated.

        Args:
            mobject_id: ID of the mobject to indicate.
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_indicate("m_abc12345", 0.8)
        """
        record = AnimationBuilder.animate_indicate(mobject_id, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_write(mobject_id: str, run_time: float = 3.0) -> dict:
        """Animate text being written onto the scene (stroke-by-stroke).

        Args:
            mobject_id: ID of the mobject to write (typically text or drawn shape).
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_write("m_abc12345", 4.0)
        """
        record = AnimationBuilder.animate_write(mobject_id, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_set_color(mobject_id: str, color: str, run_time: float = 1.0) -> dict:
        """Animate a mobject changing color.

        Args:
            mobject_id: ID of the mobject.
            color: Target color as hex string or named color.
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_set_color("m_abc12345", "#FF0000", 1.0)
        """
        record = AnimationBuilder.animate_set_color(mobject_id, color, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_move_along_path(
        mobject_id: str,
        path_type: str = "circle",
        path_config: dict | None = None,
        run_time: float = 3.0,
    ) -> dict:
        """Animate a mobject moving along a defined path.

        Args:
            mobject_id: ID of the mobject to move.
            path_type: Type of path ("circle" or "line").
            path_config: Path configuration:
                For "circle": {"radius": 2.0}
                For "line": {"end": [x, y, z]}
            run_time: Duration of the animation in seconds.

        Returns:
            Animation information.

        Example:
            >>> animate_move_along_path("m_abc12345", "circle",
            ...     {"radius": 3.0}, 5.0)
        """
        record = AnimationBuilder.animate_move_along_path(
            mobject_id,
            path_type,
            path_config,
            run_time,
        )
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_group(
        animation_data: list[dict],
        group_type: str = "animation_group",
        run_time: float = 1.0,
    ) -> dict:
        """Run multiple animations together in a group.

        Args:
            animation_data: List of animation descriptors, each with:
                - "type": Animation class name (e.g. "FadeIn", "Transform")
                - "mobject_id": ID of the target mobject
                - "config": Optional dict of additional parameters
            group_type: How to group:
                "animation_group" - all at once (default)
                "succession" - one after another
                "lagged_start" - staggered starts
            run_time: Duration applied to the group.

        Returns:
            Animation information.

        Example:
            >>> animate_group([
            ...     {"type": "FadeIn", "mobject_id": "m_abc12345"},
            ...     {"type": "Transform", "mobject_id": "m_def67890",
            ...      "config": {"color": "#FF0000"}},
            ... ], "lagged_start", 2.0)
        """
        record = AnimationBuilder.animate_group(animation_data, group_type, run_time)
        scene_manager.add_animation(record)
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "animation_count": len(animation_data),
            "run_time": record.run_time,
        }
