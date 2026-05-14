from __future__ import annotations

from typing import Any

from mcp_manimgl.core.scene_manager import MobjectRecord


class MobjectBuilder:
    MOBJECT_TYPES = {
        "circle",
        "square",
        "rectangle",
        "polygon",
        "line",
        "arrow",
        "dot",
        "text",
        "tex",
        "function_graph",
        "parametric_curve",
        "coordinate_system",
        "vector",
        "labeled_point",
        "sphere",
        "cube",
        "torus",
        "cone",
        "cylinder",
        "prism",
        "brace",
        "number_line",
        "decimal_number",
        "matrix",
        "vector_field",
        "surrounding_rectangle",
    }

    @staticmethod
    def _next_id() -> str:
        import uuid

        return f"m_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _resolve_color(color: str) -> str:
        return color

    @staticmethod
    def _position_str(pos: list[float] | None) -> str:
        if pos is None:
            return "ORIGIN"
        return f"np.array([{pos[0]}, {pos[1]}, {pos[2] if len(pos) > 2 else 0.0}])"

    @classmethod
    def add_circle(
        cls,
        radius: float = 1.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> MobjectRecord:
        mid = cls._next_id()
        pos = cls._position_str(position)
        code = (
            f"{mid} = Circle(radius={radius}, "
            f"color='{color}', "
            f"fill_opacity={fill_opacity}, "
            f"stroke_width={stroke_width})"
            f"\n{mid}.move_to({pos})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="circle",
            color=color,
            position=position if position else [0, 0, 0],
            properties={
                "radius": radius,
                "fill_opacity": fill_opacity,
                "stroke_width": stroke_width,
            },
            code_snippet=code,
        )

    @classmethod
    def add_square(
        cls,
        side_length: float = 2.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> MobjectRecord:
        mid = cls._next_id()
        pos = cls._position_str(position)
        code = (
            f"{mid} = Square(side_length={side_length}, "
            f"color='{color}', "
            f"fill_opacity={fill_opacity}, "
            f"stroke_width={stroke_width})"
            f"\n{mid}.move_to({pos})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="square",
            color=color,
            position=position if position else [0, 0, 0],
            properties={
                "side_length": side_length,
                "fill_opacity": fill_opacity,
                "stroke_width": stroke_width,
            },
            code_snippet=code,
        )

    @classmethod
    def add_rectangle(
        cls,
        width: float = 4.0,
        height: float = 2.0,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
        position: list[float] | None = None,
    ) -> MobjectRecord:
        mid = cls._next_id()
        pos = cls._position_str(position)
        code = (
            f"{mid} = Rectangle(width={width}, height={height}, "
            f"color='{color}', "
            f"fill_opacity={fill_opacity}, "
            f"stroke_width={stroke_width})"
            f"\n{mid}.move_to({pos})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="rectangle",
            color=color,
            position=position if position else [0, 0, 0],
            properties={
                "width": width,
                "height": height,
                "fill_opacity": fill_opacity,
                "stroke_width": stroke_width,
            },
            code_snippet=code,
        )

    @classmethod
    def add_polygon(
        cls,
        vertices: list[list[float]],
        color: str = "#FFFFFF",
        fill_opacity: float = 0.0,
        stroke_width: float = 4.0,
    ) -> MobjectRecord:
        mid = cls._next_id()
        verts_str = ", ".join(
            f"np.array([{v[0]}, {v[1]}, {v[2] if len(v) > 2 else 0.0}])"
            for v in vertices
        )
        code = (
            f"{mid} = Polygon({verts_str}, "
            f"color='{color}', "
            f"fill_opacity={fill_opacity}, "
            f"stroke_width={stroke_width})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="polygon",
            color=color,
            position=[0, 0, 0],
            properties={
                "num_vertices": len(vertices),
                "fill_opacity": fill_opacity,
                "stroke_width": stroke_width,
            },
            code_snippet=code,
        )

    @classmethod
    def add_line(
        cls,
        start: list[float],
        end: list[float],
        color: str = "#FFFFFF",
        stroke_width: float = 4.0,
    ) -> MobjectRecord:
        mid = cls._next_id()
        s = f"np.array([{start[0]}, {start[1]}, {start[2] if len(start) > 2 else 0.0}])"
        e = f"np.array([{end[0]}, {end[1]}, {end[2] if len(end) > 2 else 0.0}])"
        code = f"{mid} = Line({s}, {e}, color='{color}', stroke_width={stroke_width})"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="line",
            color=color,
            position=[0, 0, 0],
            properties={"start": start, "end": end, "stroke_width": stroke_width},
            code_snippet=code,
        )

    @classmethod
    def add_arrow(
        cls,
        start: list[float],
        end: list[float],
        color: str = "#FFFFFF",
        stroke_width: float = 4.0,
    ) -> MobjectRecord:
        mid = cls._next_id()
        s = f"np.array([{start[0]}, {start[1]}, {start[2] if len(start) > 2 else 0.0}])"
        e = f"np.array([{end[0]}, {end[1]}, {end[2] if len(end) > 2 else 0.0}])"
        code = f"{mid} = Arrow({s}, {e}, color='{color}', stroke_width={stroke_width})"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="arrow",
            color=color,
            position=[0, 0, 0],
            properties={"start": start, "end": end, "stroke_width": stroke_width},
            code_snippet=code,
        )

    @classmethod
    def add_dot(
        cls,
        point: list[float] | None = None,
        color: str = "#FFFFFF",
        radius: float = 0.1,
    ) -> MobjectRecord:
        mid = cls._next_id()
        pt = cls._position_str(point)
        code = f"{mid} = Dot({pt}, color='{color}', radius={radius})"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="dot",
            color=color,
            position=point if point else [0, 0, 0],
            properties={"radius": radius},
            code_snippet=code,
        )

    @classmethod
    def add_text(
        cls,
        text: str,
        font_size: float = 48,
        color: str = "#FFFFFF",
        font: str = "Consolas",
    ) -> MobjectRecord:
        mid = cls._next_id()
        escaped = text.replace("'", "\\'")
        code = (
            f"{mid} = Text('{escaped}', "
            f"font_size={font_size}, "
            f"color='{color}', "
            f"font='{font}')"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="text",
            color=color,
            position=[0, 0, 0],
            properties={"text": text, "font_size": font_size, "font": font},
            code_snippet=code,
        )

    @classmethod
    def add_tex(
        cls, tex_string: str, font_size: float = 48, color: str = "#FFFFFF"
    ) -> MobjectRecord:
        mid = cls._next_id()
        escaped = tex_string.replace("'", "\\'")
        code = f"{mid} = Tex('{escaped}', font_size={font_size}, color='{color}')"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="tex",
            color=color,
            position=[0, 0, 0],
            properties={"tex_string": tex_string, "font_size": font_size},
            code_snippet=code,
        )

    @classmethod
    def add_function_graph(
        cls, function: str, x_range: list[float] | None = None, color: str = "#FFFF00"
    ) -> MobjectRecord:
        mid = cls._next_id()
        xr = x_range if x_range else [-5, 5, 0.1]
        code = (
            f"import numpy as np\n"
            f"{mid} = FunctionGraph("
            f"lambda x: {function}, "
            f"x_range=np.array([{xr[0]}, {xr[1]}, {xr[2] if len(xr) > 2 else 0.1}]), "
            f"color='{color}')"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="function_graph",
            color=color,
            position=[0, 0, 0],
            properties={"function": function, "x_range": x_range},
            code_snippet=code,
        )

    @classmethod
    def add_parametric_curve(
        cls, function: str, t_range: list[float] | None = None, color: str = "#FFFFFF"
    ) -> MobjectRecord:
        mid = cls._next_id()
        tr = t_range if t_range else [0, 2 * 3.14159]
        code = (
            f"import numpy as np\n"
            f"{mid} = ParametricCurve("
            f"lambda t: {function}, "
            f"t_range=np.array([{tr[0]}, {tr[1]}]), "
            f"color='{color}')"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="parametric_curve",
            color=color,
            position=[0, 0, 0],
            properties={"function": function, "t_range": t_range},
            code_snippet=code,
        )

    @classmethod
    def add_coordinate_system(
        cls,
        x_range: list[float] | None = None,
        y_range: list[float] | None = None,
        axis_config: dict[str, Any] | None = None,
    ) -> MobjectRecord:
        _ = axis_config
        mid = cls._next_id()
        xr = x_range if x_range else [-5, 5, 1]
        yr = y_range if y_range else [-4, 4, 1]
        x_start, x_end, x_step = xr[0], xr[1], xr[2] if len(xr) > 2 else 1
        y_start, y_end, y_step = yr[0], yr[1], yr[2] if len(yr) > 2 else 1
        code = (
            f"{mid} = Axes("
            f"x_range=np.array([{x_start}, {x_end}, {x_step}]), "
            f"y_range=np.array([{y_start}, {y_end}, {y_step}]))"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="coordinate_system",
            color="#FFFFFF",
            position=[0, 0, 0],
            properties={"x_range": x_range, "y_range": y_range},
            code_snippet=code,
        )

    @classmethod
    def add_vector(cls, vector: list[float], color: str = "#FFFFFF") -> MobjectRecord:
        mid = cls._next_id()
        v = f"np.array([{vector[0]}, {vector[1]}, {vector[2] if len(vector) > 2 else 0.0}])"
        code = f"{mid} = Vector({v}, color='{color}')"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="vector",
            color=color,
            position=[0, 0, 0],
            properties={"vector": vector},
            code_snippet=code,
        )

    @classmethod
    def add_labeled_point(
        cls,
        label: str,
        point: list[float],
        color: str = "#FFFFFF",
        dot_radius: float = 0.1,
    ) -> MobjectRecord:
        mid = cls._next_id()
        dot_id = f"{mid}_dot"
        label_id = f"{mid}_label"
        pt = cls._position_str(point)
        escaped = label.replace("'", "\\'")
        code = (
            f"{dot_id} = Dot({pt}, color='{color}', radius={dot_radius})\n"
            f"{label_id} = Tex('{escaped}', font_size=24, color='{color}')\n"
            f"{label_id}.next_to({dot_id}, UP)\n"
            f"{mid} = VGroup({dot_id}, {label_id})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="labeled_point",
            color=color,
            position=point,
            properties={"label": label, "dot_radius": dot_radius},
            code_snippet=code,
        )

    @classmethod
    def add_3d_object(
        cls,
        object_type: str,
        color: str = "#FFFFFF",
        fill_opacity: float = 0.5,
        properties: dict | None = None,
    ) -> MobjectRecord:
        mid = cls._next_id()
        props = properties or {}
        type_map = {
            "sphere": "Sphere",
            "cube": "Cube",
            "torus": "Torus",
            "cone": "Cone",
            "cylinder": "Cylinder",
            "prism": "Prism",
        }
        manim_class = type_map.get(object_type, object_type.capitalize())
        extra = ", ".join(f"{k}={v}" for k, v in props.items())
        extra_str = f", {extra}" if extra else ""
        code = (
            f"{mid} = {manim_class}("
            f"color='{color}', "
            f"fill_opacity={fill_opacity}"
            f"{extra_str})"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type=object_type,
            color=color,
            position=[0, 0, 0],
            properties={"3d_type": object_type, "fill_opacity": fill_opacity, **props},
            code_snippet=code,
        )

    @classmethod
    def add_brace(
        cls,
        mobject_id: str,
        direction: str = "DOWN",
        color: str = "#FFFFFF",
        label: str | None = None,
    ) -> MobjectRecord:
        mid = cls._next_id()
        if label is not None:
            escaped = label.replace("'", "\\'")
            brace_id = f"{mid}_brace"
            code = (
                f"{brace_id} = Brace({mobject_id}, direction={direction}, color='{color}')\n"
                f"{mid} = BraceText({mobject_id}, '{escaped}', direction={direction}, color='{color}')"
            )
        else:
            code = (
                f"{mid} = Brace({mobject_id}, direction={direction}, color='{color}')"
            )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="brace",
            color=color,
            position=[0, 0, 0],
            properties={"target": mobject_id, "direction": direction, "label": label},
            code_snippet=code,
        )

    @classmethod
    def add_number_line(
        cls, x_range: list[float] | None = None, color: str = "#FFFFFF"
    ) -> MobjectRecord:
        mid = cls._next_id()
        xr = x_range if x_range else [-5, 5, 1]
        code = (
            f"{mid} = NumberLine("
            f"x_range=np.array([{xr[0]}, {xr[1]}, {xr[2] if len(xr) > 2 else 1}]), "
            f"color='{color}')"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="number_line",
            color=color,
            position=[0, 0, 0],
            properties={"x_range": x_range},
            code_snippet=code,
        )

    @classmethod
    def add_decimal_number(
        cls, value: float = 0.0, color: str = "#FFFFFF", font_size: float = 48
    ) -> MobjectRecord:
        mid = cls._next_id()
        code = f"{mid} = DecimalNumber({value}, color='{color}', font_size={font_size})"
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="decimal_number",
            color=color,
            position=[0, 0, 0],
            properties={"value": value, "font_size": font_size},
            code_snippet=code,
        )

    @classmethod
    def add_matrix(
        cls, rows: list[list[float]], color: str = "#FFFFFF", font_size: float = 24
    ) -> MobjectRecord:
        mid = cls._next_id()
        import json

        rows_str = json.dumps(rows)
        code = (
            f"import numpy as np\n{mid} = Matrix(np.array({rows_str}), color='{color}')"
        )
        return MobjectRecord(
            mobject_id=mid,
            mobject_type="matrix",
            color=color,
            position=[0, 0, 0],
            properties={"rows": rows, "font_size": font_size},
            code_snippet=code,
        )
