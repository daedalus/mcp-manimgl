from mcp_manimgl.core.animation_builder import AnimationBuilder


class TestAnimationBuilder:
    def test_transform(self) -> None:
        record = AnimationBuilder.animate_transform(
            "m_circle", "square", {"color": "#FF0000"}, 2.0
        )
        assert record.animation_type == "transform"
        assert record.mobject_id == "m_circle"
        assert record.run_time == 2.0
        assert "Transform(m_circle" in record.code_snippet

    def test_transform_without_target(self) -> None:
        record = AnimationBuilder.animate_transform("m_circle", run_time=1.0)
        assert record.mobject_id == "m_circle"

    def test_fade_in(self) -> None:
        record = AnimationBuilder.animate_fade_in("m_circle", 1.5)
        assert record.animation_type == "fade_in"
        assert "FadeIn(m_circle" in record.code_snippet

    def test_fade_in_with_shift(self) -> None:
        record = AnimationBuilder.animate_fade_in("m_circle", 1.0, [0, 1, 0])
        assert "FadeIn(m_circle" in record.code_snippet

    def test_fade_out(self) -> None:
        record = AnimationBuilder.animate_fade_out("m_circle", 2.0)
        assert record.animation_type == "fade_out"
        assert "FadeOut(m_circle" in record.code_snippet

    def test_grow_center(self) -> None:
        record = AnimationBuilder.animate_grow("m_circle", "center", 2.0)
        assert "GrowFromCenter" in record.code_snippet

    def test_grow_edge(self) -> None:
        record = AnimationBuilder.animate_grow("m_circle", "edge", 1.0)
        assert "GrowFromEdge" in record.code_snippet

    def test_grow_arrow(self) -> None:
        record = AnimationBuilder.animate_grow("m_arrow", "arrow", 1.0)
        assert "GrowArrow" in record.code_snippet

    def test_rotate(self) -> None:
        record = AnimationBuilder.animate_rotate("m_circle", 3.14159, None, 2.0)
        assert "Rotate(m_circle" in record.code_snippet

    def test_rotate_with_axis(self) -> None:
        record = AnimationBuilder.animate_rotate("m_circle", 1.57, [0, 0, 1], 1.0)
        assert "axis" in record.code_snippet

    def test_scale(self) -> None:
        record = AnimationBuilder.animate_scale("m_circle", 2.0, 1.5)
        assert "ScaleInPlace(m_circle" in record.code_snippet
        assert "2.0" in record.code_snippet

    def test_shift(self) -> None:
        record = AnimationBuilder.animate_shift("m_circle", [2, 0, 0], 1.0)
        assert "ApplyMethod" in record.code_snippet
        assert ".shift" in record.code_snippet

    def test_indicate(self) -> None:
        record = AnimationBuilder.animate_indicate("m_circle", 0.8)
        assert "Indicate(m_circle" in record.code_snippet

    def test_write(self) -> None:
        record = AnimationBuilder.animate_write("m_text", 4.0)
        assert "Write(m_text" in record.code_snippet

    def test_set_color(self) -> None:
        record = AnimationBuilder.animate_set_color("m_circle", "#FF0000", 1.0)
        assert "set_color('#FF0000')" in record.code_snippet

    def test_move_along_path_circle(self) -> None:
        record = AnimationBuilder.animate_move_along_path(
            "m_circle",
            "circle",
            {"radius": 3.0},
            5.0,
        )
        assert "MoveAlongPath" in record.code_snippet
        assert "Circle(radius=3.0)" in record.code_snippet

    def test_move_along_path_line(self) -> None:
        record = AnimationBuilder.animate_move_along_path(
            "m_circle",
            "line",
            {"end": [3, 0, 0]},
            3.0,
        )
        assert "MoveAlongPath" in record.code_snippet
        assert "Line(ORIGIN" in record.code_snippet

    def test_move_along_path_unknown_type(self) -> None:
        record = AnimationBuilder.animate_move_along_path(
            "m1",
            "unknown_path",
            {},
            2.0,
        )
        assert "MoveAlongPath" in record.code_snippet
        assert "unknown_path" in record.code_snippet

    def test_rate_func_str(self) -> None:
        assert AnimationBuilder._rate_func_str("smooth") == "smooth"

    def test_group(self) -> None:
        record = AnimationBuilder.animate_group(
            [
                {"type": "FadeIn", "mobject_id": "m_circle"},
                {
                    "type": "Transform",
                    "mobject_id": "m_square",
                    "config": {"color": "#FF0000"},
                },
            ],
            "animation_group",
            2.0,
        )
        assert record.animation_type == "group"
        assert record.properties["animation_count"] == 2

    def test_group_succession(self) -> None:
        record = AnimationBuilder.animate_group(
            [
                {"type": "FadeIn", "mobject_id": "m_a"},
                {"type": "FadeOut", "mobject_id": "m_b"},
            ],
            "succession",
            1.0,
        )
        assert "Succession" in record.code_snippet

    def test_group_lagged_start(self) -> None:
        record = AnimationBuilder.animate_group(
            [
                {"type": "FadeIn", "mobject_id": "m_a"},
            ],
            "lagged_start",
            1.0,
        )
        assert "LaggedStart" in record.code_snippet

    def test_rate_functions_set(self) -> None:
        assert "smooth" in AnimationBuilder.RATE_FUNCTIONS
        assert "linear" in AnimationBuilder.RATE_FUNCTIONS
        assert "ease_out_back" in AnimationBuilder.RATE_FUNCTIONS
        assert "wiggle" in AnimationBuilder.RATE_FUNCTIONS
        assert "there_and_back" in AnimationBuilder.RATE_FUNCTIONS

    def test_animation_id_uniqueness(self) -> None:
        ids = [
            AnimationBuilder.animate_fade_in("m_circle").animation_id for _ in range(10)
        ]
        assert len(set(ids)) == 10

    def test_zero_run_time(self) -> None:
        record = AnimationBuilder.animate_fade_in("m_circle", 0.0)
        assert record.run_time == 0.0

    def test_negative_scale(self) -> None:
        record = AnimationBuilder.animate_scale("m_circle", -1.0, 1.0)
        assert "ScaleInPlace(m_circle, -1.0" in record.code_snippet
