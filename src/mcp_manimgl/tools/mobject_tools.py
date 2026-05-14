from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_manimgl.core.mobject_builder import MobjectBuilder

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_mobject_tools(mcp: FastMCP, scene_manager: SceneManager) -> None:
    @mcp.tool()
    def add_circle(
        radius: float = 1.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> dict:
        """Add a circle mobject to the scene.

        Args:
            radius: Radius of the circle.
            color: Color as hex string or named color.
            fill_opacity: Opacity of the fill (0.0 = transparent, 1.0 = solid).
            stroke_width: Width of the outline stroke.
            position: Position [x, y, z] to place the circle.

        Returns:
            Mobject information including the mobject ID.

        Example:
            >>> add_circle(2.0, "#FF0000", 0.5, 2.0, [0, 0, 0])
        """
        record = MobjectBuilder.add_circle(
            radius, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
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
        """Add a square mobject to the scene.

        Args:
            side_length: Length of each side.
            color: Color as hex string or named color.
            fill_opacity: Opacity of the fill.
            stroke_width: Width of the outline stroke.
            position: Position [x, y, z].

        Returns:
            Mobject information.

        Example:
            >>> add_square(3.0, "#00FF00", 0.3)
        """
        record = MobjectBuilder.add_square(
            side_length, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
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
        """Add a rectangle mobject to the scene.

        Args:
            width: Width of the rectangle.
            height: Height of the rectangle.
            color: Color as hex string or named color.
            fill_opacity: Opacity of the fill.
            stroke_width: Width of the outline stroke.
            position: Position [x, y, z].

        Returns:
            Mobject information.

        Example:
            >>> add_rectangle(5.0, 3.0, "#0000FF", 0.2)
        """
        record = MobjectBuilder.add_rectangle(
            width, height, color, fill_opacity, stroke_width, position
        )
        scene_manager.add_mobject(record)
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
        """Add a polygon mobject defined by its vertices.

        Args:
            vertices: List of vertex positions as [x, y] or [x, y, z] arrays.
            color: Color as hex string or named color.
            fill_opacity: Opacity of the fill.
            stroke_width: Width of the outline stroke.

        Returns:
            Mobject information.

        Example:
            >>> add_polygon([[-1, -1], [1, -1], [0, 1]], "#FF00FF", 0.5)
        """
        record = MobjectBuilder.add_polygon(vertices, color, fill_opacity, stroke_width)
        scene_manager.add_mobject(record)
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
        """Add a line from start to end.

        Args:
            start: Starting position [x, y, z].
            end: Ending position [x, y, z].
            color: Color as hex string or named color.
            stroke_width: Width of the line stroke.

        Returns:
            Mobject information.

        Example:
            >>> add_line([-2, 0, 0], [2, 0, 0], "#FFFFFF", 2.0)
        """
        record = MobjectBuilder.add_line(start, end, color, stroke_width)
        scene_manager.add_mobject(record)
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
        """Add an arrow from start to end.

        Args:
            start: Starting position [x, y, z].
            end: Ending (tip) position [x, y, z].
            color: Color as hex string or named color.
            stroke_width: Width of the arrow stroke.

        Returns:
            Mobject information.

        Example:
            >>> add_arrow([0, 0, 0], [3, 0, 0], "#FFFF00", 2.0)
        """
        record = MobjectBuilder.add_arrow(start, end, color, stroke_width)
        scene_manager.add_mobject(record)
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
        """Add a dot at a specified position.

        Args:
            point: Position [x, y, z]. Defaults to origin.
            color: Color as hex string or named color.
            radius: Radius of the dot.

        Returns:
            Mobject information.

        Example:
            >>> add_dot([1, 2, 0], "#FF0000", 0.15)
        """
        record = MobjectBuilder.add_dot(point, color, radius)
        scene_manager.add_mobject(record)
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
        """Add a text mobject to the scene.

        Args:
            text: The text string to display.
            font_size: Font size in points.
            color: Color as hex string or named color.
            font: Font name to use.

        Returns:
            Mobject information.

        Example:
            >>> add_text("Hello, World!", 64, "#00FF00")
        """
        record = MobjectBuilder.add_text(text, font_size, color, font)
        scene_manager.add_mobject(record)
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
        """Add a LaTeX math expression to the scene.

        Args:
            tex_string: LaTeX math expression (e.g. "x^2 + y^2 = z^2").
            font_size: Font size in points.
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_tex("E = mc^2", 64, "#FFFF00")
        """
        record = MobjectBuilder.add_tex(tex_string, font_size, color)
        scene_manager.add_mobject(record)
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
        """Graph a mathematical function.

        Args:
            function: Python expression using 'x', e.g. "x**2" or "sin(x)".
            x_range: Range [start, end, step] for x values.
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_function_graph("x**2", [-3, 3, 0.05], "#FF0000")
        """
        record = MobjectBuilder.add_function_graph(function, x_range, color)
        scene_manager.add_mobject(record)
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
        """Add a parametric curve defined by a vector function of t.

        Args:
            function: Lambda body returning [x, y, z], e.g.
                "[cos(t), sin(t), 0]" for a circle.
            t_range: Range [start, end] for parameter t.
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_parametric_curve("[cos(2*t), sin(3*t), 0]", [0, 6.28], "#00FFFF")
        """
        record = MobjectBuilder.add_parametric_curve(function, t_range, color)
        scene_manager.add_mobject(record)
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
        """Add coordinate axes (NumberPlane/Axes) to the scene.

        Args:
            x_range: Range [min, max, step] for x-axis.
            y_range: Range [min, max, step] for y-axis.
            axis_config: Additional axis configuration options.

        Returns:
            Mobject information.

        Example:
            >>> add_coordinate_system([-5, 5, 1], [-3, 3, 1])
        """
        record = MobjectBuilder.add_coordinate_system(x_range, y_range, axis_config)
        scene_manager.add_mobject(record)
        return {
            "mobject_id": record.mobject_id,
            "mobject_type": record.mobject_type,
        }

    @mcp.tool()
    def add_vector(
        vector: list[float],
        color: str = "#FFFFFF",
    ) -> dict:
        """Add a vector as an arrow from the origin.

        Args:
            vector: The vector components [x, y, z].
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_vector([3, 1, 0], "#FF8800")
        """
        record = MobjectBuilder.add_vector(vector, color)
        scene_manager.add_mobject(record)
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
        """Add a labeled point (dot with text label) to the scene.

        Args:
            label: Text label for the point (rendered as LaTeX).
            point: Position [x, y, z] of the point.
            color: Color as hex string or named color.
            dot_radius: Radius of the dot.

        Returns:
            Mobject information.

        Example:
            >>> add_labeled_point("P", [1, 2, 0], "#FF0000", 0.12)
        """
        record = MobjectBuilder.add_labeled_point(label, point, color, dot_radius)
        scene_manager.add_mobject(record)
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
        """Add a 3D object to the scene.

        Args:
            object_type: Type of 3D object. One of:
                "sphere", "cube", "torus", "cone", "cylinder", "prism".
            color: Color as hex string or named color.
            fill_opacity: Opacity of the fill.
            properties: Additional parameters for the 3D object
                (e.g. {"radius": 2.0} for sphere,
                 {"major_radius": 2.0, "minor_radius": 1.0} for torus).

        Returns:
            Mobject information.

        Example:
            >>> add_3d_object("sphere", "#4488FF", 0.6)
            >>> add_3d_object("torus", "#FF4488", 0.7, {"major_radius": 2, "minor_radius": 1})
        """
        record = MobjectBuilder.add_3d_object(
            object_type, color, fill_opacity, properties
        )
        scene_manager.add_mobject(record)
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
        """Add a brace underneath or next to an existing mobject.

        Args:
            mobject_id: ID of the mobject to brace.
            direction: Direction for the brace ("UP", "DOWN", "LEFT", "RIGHT").
            color: Color as hex string or named color.
            label: Optional LaTeX label text.

        Returns:
            Mobject information.

        Example:
            >>> add_brace("m_abc12345", "DOWN", "#FFFFFF", "length")
        """
        record = MobjectBuilder.add_brace(mobject_id, direction, color, label)
        scene_manager.add_mobject(record)
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
        """Add a number line to the scene.

        Args:
            x_range: Range [min, max, step] for the number line.
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_number_line([-5, 5, 1], "#FFFFFF")
        """
        record = MobjectBuilder.add_number_line(x_range, color)
        scene_manager.add_mobject(record)
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
        """Add a decimal number that can be animated to change.

        Args:
            value: Initial numeric value.
            color: Color as hex string or named color.
            font_size: Font size in points.

        Returns:
            Mobject information.

        Example:
            >>> add_decimal_number(3.14159, "#00FF00", 36)
        """
        record = MobjectBuilder.add_decimal_number(value, color, font_size)
        scene_manager.add_mobject(record)
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
        """Add a matrix to the scene.

        Args:
            rows: List of rows, each row is a list of numbers.
            color: Color as hex string or named color.

        Returns:
            Mobject information.

        Example:
            >>> add_matrix([[1, 0], [0, 1]], "#FFFFFF")
        """
        record = MobjectBuilder.add_matrix(rows, color)
        scene_manager.add_mobject(record)
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
        """Move a mobject to a specified position.

        Args:
            mobject_id: ID of the mobject to move.
            position: Target position [x, y, z].
            aligned_edge: Which edge to align (e.g. "LEFT", "RIGHT", "UP", "DOWN").

        Returns:
            True if mobject was moved.

        Example:
            >>> move_to("m_abc12345", [2, 0, 0])
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        record.position = position
        pos = MobjectBuilder._position_str(position)
        edge = f", aligned_edge={aligned_edge}" if aligned_edge else ""
        record.code_snippet += f"\n{record.mobject_id}.move_to({pos}{edge})"
        return True

    @mcp.tool()
    def shift(mobject_id: str, vector: list[float]) -> bool:
        """Shift a mobject by a displacement vector.

        Args:
            mobject_id: ID of the mobject to shift.
            vector: Displacement [dx, dy, dz].

        Returns:
            True if mobject was shifted.

        Example:
            >>> shift("m_abc12345", [1, 0, 0])
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        v = f"np.array([{vector[0]}, {vector[1]}, {vector[2] if len(vector) > 2 else 0.0}])"
        record.code_snippet += f"\n{record.mobject_id}.shift({v})"
        return True

    @mcp.tool()
    def scale(
        mobject_id: str, scale_factor: float, about_point: list[float] | None = None
    ) -> bool:
        """Scale a mobject by a factor.

        Args:
            mobject_id: ID of the mobject to scale.
            scale_factor: Scaling factor (1.0 = no change).
            about_point: Point [x, y, z] to scale about (default: center).

        Returns:
            True if mobject was scaled.

        Example:
            >>> scale("m_abc12345", 2.0)
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        pt = (
            f", about_point=np.array([{about_point[0]}, {about_point[1]}, {about_point[2] if len(about_point) > 2 else 0.0}])"
            if about_point
            else ""
        )
        record.code_snippet += f"\n{record.mobject_id}.scale({scale_factor}{pt})"
        return True

    @mcp.tool()
    def rotate(
        mobject_id: str,
        angle: float,
        axis: list[float] | None = None,
        about_point: list[float] | None = None,
    ) -> bool:
        """Rotate a mobject by an angle.

        Args:
            mobject_id: ID of the mobject to rotate.
            angle: Rotation angle in radians.
            axis: Rotation axis [x, y, z] (default: OUT/[0,0,1]).
            about_point: Point [x, y, z] to rotate about.

        Returns:
            True if mobject was rotated.

        Example:
            >>> rotate("m_abc12345", 3.14159, [0, 0, 1])
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
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
        return True

    @mcp.tool()
    def set_color(mobject_id: str, color: str) -> bool:
        """Set the color of a mobject.

        Args:
            mobject_id: ID of the mobject.
            color: Color as hex string or named color.

        Returns:
            True if color was set.

        Example:
            >>> set_color("m_abc12345", "#FF0000")
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        record.color = color
        record.code_snippet += f"\n{record.mobject_id}.set_color('{color}')"
        return True

    @mcp.tool()
    def set_opacity(mobject_id: str, opacity: float) -> bool:
        """Set the opacity of a mobject.

        Args:
            mobject_id: ID of the mobject.
            opacity: Opacity value (0.0 = transparent, 1.0 = solid).

        Returns:
            True if opacity was set.

        Example:
            >>> set_opacity("m_abc12345", 0.5)
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        record.code_snippet += f"\n{record.mobject_id}.set_opacity({opacity})"
        return True

    @mcp.tool()
    def next_to(
        mobject_id: str, reference_id: str, direction: str = "RIGHT", buff: float = 0.25
    ) -> bool:
        """Position a mobject next to another mobject.

        Args:
            mobject_id: ID of the mobject to position.
            reference_id: ID of the reference mobject.
            direction: Direction relative to reference ("RIGHT", "LEFT", "UP", "DOWN").
            buff: Buffer distance between mobjects.

        Returns:
            True if position was updated.

        Example:
            >>> next_to("m_abc12345", "m_def67890", "RIGHT", 0.5)
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        record.code_snippet += f"\n{record.mobject_id}.next_to({reference_id}, direction={direction}, buff={buff})"
        return True

    @mcp.tool()
    def align_to(mobject_id: str, reference_id: str, direction: str = "UP") -> bool:
        """Align a mobject to another mobject along an edge.

        Args:
            mobject_id: ID of the mobject to align.
            reference_id: ID of the reference mobject.
            direction: Edge to align ("UP", "DOWN", "LEFT", "RIGHT").

        Returns:
            True if alignment was applied.

        Example:
            >>> align_to("m_abc12345", "m_def67890", "UP")
        """
        record = scene_manager.get_mobject(mobject_id)
        if record is None:
            return False
        record.code_snippet += (
            f"\n{record.mobject_id}.align_to({reference_id}, {direction})"
        )
        return True
