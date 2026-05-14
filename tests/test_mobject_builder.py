
from mcp_manimgl.core.mobject_builder import MobjectBuilder


class TestMobjectBuilder:
    def test_circle_defaults(self) -> None:
        record = MobjectBuilder.add_circle()
        assert record.mobject_type == "circle"
        assert record.color == "#FFFFFF"
        assert record.position == [0, 0, 0]
        assert record.properties["radius"] == 1.0
        assert "Circle(radius=1.0" in record.code_snippet
        assert "move_to(ORIGIN)" in record.code_snippet

    def test_circle_custom(self) -> None:
        record = MobjectBuilder.add_circle(
            radius=2.5,
            color="#FF0000",
            fill_opacity=0.5,
            stroke_width=2.0,
            position=[1, 2, 3],
        )
        assert record.properties["radius"] == 2.5
        assert record.color == "#FF0000"
        assert record.position == [1, 2, 3]
        assert "fill_opacity=0.5" in record.code_snippet
        assert "stroke_width=2.0" in record.code_snippet

    def test_square(self) -> None:
        record = MobjectBuilder.add_square(side_length=3.0, color="#00FF00")
        assert record.mobject_type == "square"
        assert "Square(side_length=3.0" in record.code_snippet

    def test_rectangle(self) -> None:
        record = MobjectBuilder.add_rectangle(width=5.0, height=3.0, color="#0000FF")
        assert record.mobject_type == "rectangle"
        assert "Rectangle(width=5.0, height=3.0" in record.code_snippet

    def test_polygon(self) -> None:
        vertices = [[0, 0], [1, 0], [0.5, 1]]
        record = MobjectBuilder.add_polygon(vertices, color="#FF00FF")
        assert record.mobject_type == "polygon"
        assert "Polygon(" in record.code_snippet

    def test_line(self) -> None:
        record = MobjectBuilder.add_line([-2, 0, 0], [2, 0, 0], color="#FFFF00")
        assert record.mobject_type == "line"
        assert "Line(" in record.code_snippet

    def test_arrow(self) -> None:
        record = MobjectBuilder.add_arrow([0, 0, 0], [3, 0, 0], color="#FF8800")
        assert record.mobject_type == "arrow"
        assert "Arrow(" in record.code_snippet

    def test_dot_defaults(self) -> None:
        record = MobjectBuilder.add_dot()
        assert record.mobject_type == "dot"
        assert record.position == [0, 0, 0]
        assert "Dot(" in record.code_snippet

    def test_dot_custom_position(self) -> None:
        record = MobjectBuilder.add_dot(point=[2, -1, 0])
        assert record.position == [2, -1, 0]

    def test_text(self) -> None:
        record = MobjectBuilder.add_text("Hello, World!", font_size=64, color="#00FF00")
        assert record.mobject_type == "text"
        assert "Text('Hello, World!'" in record.code_snippet
        assert "font_size=64" in record.code_snippet

    def test_text_with_unicode(self) -> None:
        record = MobjectBuilder.add_text("Café ñoño", font_size=48)
        assert record.mobject_type == "text"

    def test_tex(self) -> None:
        record = MobjectBuilder.add_tex("E = mc^2", font_size=64, color="#FFFF00")
        assert record.mobject_type == "tex"
        assert "Tex('E = mc^2'" in record.code_snippet

    def test_function_graph(self) -> None:
        record = MobjectBuilder.add_function_graph("x**2", [-3, 3, 0.05], "#FF0000")
        assert record.mobject_type == "function_graph"
        assert "lambda x: x**2" in record.code_snippet

    def test_function_graph_default_range(self) -> None:
        record = MobjectBuilder.add_function_graph("sin(x)")
        assert record.code_snippet is not None

    def test_parametric_curve(self) -> None:
        record = MobjectBuilder.add_parametric_curve(
            "[cos(t), sin(t), 0]",
            [0, 6.28],
            "#00FFFF",
        )
        assert record.mobject_type == "parametric_curve"

    def test_coordinate_system(self) -> None:
        record = MobjectBuilder.add_coordinate_system([-5, 5, 1], [-3, 3, 1])
        assert record.mobject_type == "coordinate_system"
        assert "Axes(" in record.code_snippet

    def test_vector(self) -> None:
        record = MobjectBuilder.add_vector([3, 1, 0], color="#FF8800")
        assert record.mobject_type == "vector"
        assert "Vector(" in record.code_snippet

    def test_labeled_point(self) -> None:
        record = MobjectBuilder.add_labeled_point(
            "P",
            [1, 2, 0],
            "#FF0000",
            0.12,
        )
        assert record.mobject_type == "labeled_point"
        assert "Dot(" in record.code_snippet
        assert "Tex('P'" in record.code_snippet

    def test_3d_object(self) -> None:
        record = MobjectBuilder.add_3d_object("sphere", "#4488FF", 0.6)
        assert record.mobject_type == "sphere"
        assert "Sphere(" in record.code_snippet

    def test_3d_torus(self) -> None:
        record = MobjectBuilder.add_3d_object("torus", "#FF4488", 0.7)
        assert record.mobject_type == "torus"
        assert "Torus(" in record.code_snippet

    def test_brace_without_label(self) -> None:
        record = MobjectBuilder.add_brace("m_target", "DOWN", "#FFFFFF")
        assert record.mobject_type == "brace"
        assert "Brace(m_target" in record.code_snippet

    def test_brace_with_label(self) -> None:
        record = MobjectBuilder.add_brace("m_target", "DOWN", "#FFFFFF", "label")
        assert "BraceText(" in record.code_snippet or "Brace(" in record.code_snippet

    def test_number_line(self) -> None:
        record = MobjectBuilder.add_number_line([-5, 5, 1])
        assert record.mobject_type == "number_line"

    def test_decimal_number(self) -> None:
        record = MobjectBuilder.add_decimal_number(3.14159, "#00FF00", 36)
        assert record.mobject_type == "decimal_number"
        assert "DecimalNumber(3.14159" in record.code_snippet

    def test_matrix(self) -> None:
        record = MobjectBuilder.add_matrix([[1, 0], [0, 1]], "#FFFFFF")
        assert record.mobject_type == "matrix"

    def test_all_mobject_types(self) -> None:
        assert len(MobjectBuilder.MOBJECT_TYPES) == 26

    def test_mobject_id_uniqueness(self) -> None:
        ids = [MobjectBuilder.add_circle().mobject_id for _ in range(10)]
        assert len(set(ids)) == 10

    def test_position_string_origin(self) -> None:
        result = MobjectBuilder._position_str(None)
        assert result == "ORIGIN"

    def test_position_string_custom(self) -> None:
        result = MobjectBuilder._position_str([1.0, 2.0, 3.0])
        assert "1.0" in result
        assert "2.0" in result
        assert "3.0" in result

    def test_position_string_2d(self) -> None:
        result = MobjectBuilder._position_str([1.0, 2.0])
        assert "0.0" in result  # z should be 0.0
