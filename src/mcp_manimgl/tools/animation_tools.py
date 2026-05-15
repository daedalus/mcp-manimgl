from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.animation_builder import AnimationBuilder
from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_animation_tools(
    mcp: FastMCP, scene_manager: SceneManager, recorder: SessionRecorder
) -> None:
    @mcp.tool()
    def animate_transform(
        mobject_id: str,
        target_mobject_type: str | None = None,
        target_config: dict | None = None,
        run_time: float = 1.0,
        rate_func: str = "smooth",
    ) -> dict:
        record = AnimationBuilder.animate_transform(
            mobject_id,
            target_mobject_type,
            target_config,
            run_time,
            rate_func,
        )
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_transform")
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
        record = AnimationBuilder.animate_fade_in(mobject_id, run_time, shift_direction)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_fade_in")
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_fade_out(mobject_id: str, run_time: float = 1.0) -> dict:
        record = AnimationBuilder.animate_fade_out(mobject_id, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_fade_out")
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
        record = AnimationBuilder.animate_grow(mobject_id, grow_type, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_grow")
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
        record = AnimationBuilder.animate_rotate(mobject_id, angle, axis, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_rotate")
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
        record = AnimationBuilder.animate_scale(mobject_id, scale_factor, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_scale")
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
        record = AnimationBuilder.animate_shift(mobject_id, vector, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_shift")
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_indicate(mobject_id: str, run_time: float = 0.5) -> dict:
        record = AnimationBuilder.animate_indicate(mobject_id, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_indicate")
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_write(mobject_id: str, run_time: float = 3.0) -> dict:
        record = AnimationBuilder.animate_write(mobject_id, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_write")
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "mobject_id": record.mobject_id,
            "run_time": record.run_time,
        }

    @mcp.tool()
    def animate_set_color(mobject_id: str, color: str, run_time: float = 1.0) -> dict:
        record = AnimationBuilder.animate_set_color(mobject_id, color, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_set_color")
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
        record = AnimationBuilder.animate_move_along_path(
            mobject_id,
            path_type,
            path_config,
            run_time,
        )
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_move_along_path")
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
        record = AnimationBuilder.animate_group(animation_data, group_type, run_time)
        scene_manager.add_animation(record)
        record_tool_call(recorder, "animate_group")
        return {
            "animation_id": record.animation_id,
            "animation_type": record.animation_type,
            "animation_count": len(animation_data),
            "run_time": record.run_time,
        }
