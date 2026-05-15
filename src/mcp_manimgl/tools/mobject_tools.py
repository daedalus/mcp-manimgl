from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.mobject_builder import MobjectBuilder
from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_mobject_tools(
    mcp: FastMCP, scene_manager: SceneManager, recorder: SessionRecorder
) -> None:
    @mcp.tool()
    def add_circle(
        radius: float = 1.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> dict:
        record = MobjectBuilder.add_circle(
            radius, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_circle")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
            "position": record.position,
        }

    @mcp.tool()
    def add_square(
        side_length: float = 2.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> dict:
        record = MobjectBuilder.add_square(
            side_length, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_square")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
            "position": record.position,
        }

    @mcp.tool()
    def add_rectangle(
        width: float = 4.0,
        height: float = 2.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> dict:
        record = MobjectBuilder.add_rectangle(
            width, height, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_rectangle")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
            "position": record.position,
        }

    @mcp.tool()
    def add_polygon(
        vertices: list[list[float]],
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
    ) -> dict:
        record = MobjectBuilder.add_polygon(vertices, color, fill_opacity, stroke_width)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_polygon")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_line(
        start: list[float],
        end: list[float],
        color: str = "#FFFFFF",
        stroke_width: float = 4.0,
    ) -> dict:
        record = MobjectBuilder.add_line(start, end, color, stroke_width)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_line")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_arrow(
        start: list[float],
        end: list[float],
        color: str = "#FFFFFF",
        stroke_width: float = 4.0,
    ) -> dict:
        record = MobjectBuilder.add_arrow(start, end, color, stroke_width)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_arrow")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_dot(
        point: list[float] | None = None,
        color: str = "#FFFFFF",
        radius: float = 0.1,
    ) -> dict:
        record = MobjectBuilder.add_dot(point, color, radius)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_dot")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
            "position": record.position,
        }

    @mcp.tool()
    def add_text(
        text: str,
        font_size: float = 48,
        color: str = "#FFFFFF",
        font: str = "Consolas",
    ) -> dict:
        record = MobjectBuilder.add_text(text, font_size, color, font)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_text")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_tex(
        tex_string: str,
        font_size: float = 48,
        color: str = "#FFFFFF",
    ) -> dict:
        record = MobjectBuilder.add_tex(tex_string, font_size, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_tex")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_function_graph(
        function: str,
        x_range: list[float] | None = None,
        color: str = "#FFFF00",
    ) -> dict:
        record = MobjectBuilder.add_function_graph(function, x_range, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_function_graph")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_parametric_curve(
        function: str,
        t_range: list[float] | None = None,
        color: str = "#FFFFFF",
    ) -> dict:
        record = MobjectBuilder.add_parametric_curve(function, t_range, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_parametric_curve")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_coordinate_system(
        x_range: list[float] | None = None,
        y_range: list[float] | None = None,
        axis_config: dict | None = None,
    ) -> dict:
        record = MobjectBuilder.add_coordinate_system(x_range, y_range, axis_config)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_coordinate_system")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
        }

    @mcp.tool()
    def add_vector(
        vector: list[float],
        color: str = "#FFFFFF",
    ) -> dict:
        record = MobjectBuilder.add_vector(vector, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_vector")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_labeled_point(
        label: str,
        point: list[float],
        color: str = "#FFFFFF",
        dot_radius: float = 0.1,
    ) -> dict:
        record = MobjectBuilder.add_labeled_point(label, point, color, dot_radius)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_labeled_point")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
            "position": record.position,
        }

    @mcp.tool()
    def add_3d_object(
        object_type: str,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.5,
        properties: dict = {},
    ) -> dict:
        record = MobjectBuilder.add_3d_object(
            object_type, color, fill_opacity, properties
        )
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_3d_object")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_brace(
        mobject_id: str,
        direction: str = "DOWN",
        color: str = "#FFFFFF",
        label: str | None = None,
    ) -> dict:
        record = MobjectBuilder.add_brace(mobject_id, direction, color, label)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_brace")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_number_line(
        x_range: list[float] | None = None,
        color: str = "#FFFFFF",
    ) -> dict:
        record = MobjectBuilder.add_number_line(x_range, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_number_line")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_decimal_number(
        value: float = 0.0,
        color: str = "#FFFFFF",
        font_size: float = 48,
    ) -> dict:
        record = MobjectBuilder.add_decimal_number(value, color, font_size)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_decimal_number")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def add_matrix(
        rows: list[list[float]],
        color: str = "#FFFFFF",
    ) -> dict:
        record = MobjectBuilder.add_matrix(rows, color)
        scene_manager.add_mobject(record)
        record_tool_call(recorder, "add_matrix")
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
            "color": record.color,
        }

    @mcp.tool()
    def move_to(
        mobject_id: str,
        position: list[float],
        aligned_edge: str | None = None,
    ) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "move_to")
            return False
        record.position = position
        pos = MobjectBuilder._position_str(position)
        edge = f", aligned_edge={aligned_edge}" if aligned_edge else ""
        record.code_snippet += f"\n{record.mobject_id}.move_to({pos}{edge})"
        record_tool_call(recorder, "move_to")
        return True

    @mcp.tool()
    def shift(mobject_id: str, vector: list[float]) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "shift")
            return False
        v = f"np.array([{vector[0]}, {vector[1]}, {vector[2] if len(vector) > 2 else 0.0}])"
        record.code_snippet += f"\n{record.mobject_id}.shift({v})"
        record_tool_call(recorder, "shift")
        return True

    @mcp.tool()
    def scale(
        mobject_id: str, scale_factor: float, about_point: list[float] | None = None
    ) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "scale")
            return False
        pt = (
            f", about_point=np.array([{about_point[0]}, {about_point[1]}, {about_point[2] if len(about_point) > 2 else 0.0}])"
            if about_point
            else ""
        )
        record.code_snippet += f"\n{record.mobject_id}.scale({scale_factor}{pt})"
        record_tool_call(recorder, "scale")
        return True

    @mcp.tool()
    def rotate(
        mobject_id: str,
        angle: float,
        axis: list[float] | None = None,
        about_point: list[float] | None = None,
    ) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "rotate")
            return False
        ax = (
            f", axis=np.array([{axis[0]}, {axis[1]}, {axis[2] if len(axis) > 2 else 0.0}])"
            if axis
            else ""
        )
        pt = (
            f", about_point=np.array([{about_point[0]}, {about_point[1]}, {about_point[2] if len(about_point) > 2 else 0.0}])"
            if about_point
            else ""
        )
        record.code_snippet += f"\n{record.mobject_id}.rotate({angle}{ax}{pt})"
        record_tool_call(recorder, "rotate")
        return True

    @mcp.tool()
    def set_color(mobject_id: str, color: str) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "set_color")
            return False
        record.color = color
        record.code_snippet += f"\n{record.mobject_id}.set_color('{color}')"
        record_tool_call(recorder, "set_color")
        return True

    @mcp.tool()
    def set_opacity(mobject_id: str, opacity: float) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "set_opacity")
            return False
        record.code_snippet += f"\n{record.mobject_id}.set_opacity({opacity})"
        record_tool_call(recorder, "set_opacity")
        return True

    @mcp.tool()
    def next_to(
        mobject_id: str, reference_id: str, direction: str = "RIGHT", buff: float = 0.25
    ) -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "next_to")
            return False
        record.code_snippet += f"\n{record.mobject_id}.next_to({reference_id}, direction={direction}, buff={buff})"
        record_tool_call(recorder, "next_to")
        return True

    @mcp.tool()
    def align_to(mobject_id: str, reference_id: str, direction: str = "UP") -> bool:
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            record_tool_call(recorder, "align_to")
            return False
        record.code_snippet += (
            f"\n{record.mobject_id}.align_to({reference_id}, {direction})"
        )
        record_tool_call(recorder, "align_to")
        return True
