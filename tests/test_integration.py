from mcp_manimgl.core import AnimationBuilder, MobjectBuilder


class TestMobjectTemplates:
    def test_circle_to_square_animation_flow(self) -> None:
        circle = MobjectBuilder.add_circle(
            radius=1.0, color="#FFFFFF", position=[0, 0, 0]
        )
        assert circle.mobject_id.startswith("m_")

        anim = AnimationBuilder.animate_transform(
            circle.mobject_id,
            "square",
            {"color": "#FF0000"},
            2.0,
        )
        assert anim.mobject_id == circle.mobject_id
        assert "Transform" in anim.code_snippet
        assert "m_" in circle.code_snippet

    def test_complex_scene_building(self) -> None:
        axes = MobjectBuilder.add_coordinate_system([-5, 5, 1], [-3, 3, 1])
        graph = MobjectBuilder.add_function_graph("x**2", [-3, 3, 0.05], "#FFFF00")
        dot = MobjectBuilder.add_dot([0, 0, 0], "#FF0000", 0.1)
        label = MobjectBuilder.add_labeled_point("origin", [0, 0, 0], "#FFFFFF")

        assert all(m.mobject_id.startswith("m_") for m in [axes, graph, dot, label])
        assert all(
            m.mobject_type in MobjectBuilder.MOBJECT_TYPES
            for m in [axes, graph, dot, label]
        )

    def test_animate_then_fade_out(self) -> None:
        circle = MobjectBuilder.add_circle()
        anim1 = AnimationBuilder.animate_grow(circle.mobject_id, "center", 1.0)
        anim2 = AnimationBuilder.animate_fade_out(circle.mobject_id, 1.0)
        assert anim1.mobject_id == anim2.mobject_id
        assert anim1.animation_type == "grow"
        assert anim2.animation_type == "fade_out"

    def test_empty_scene_no_elements(self) -> None:
        from mcp_manimgl.core import SceneManager

        sm = SceneManager()
        info = sm.get_info()
        assert info["mobject_count"] == 0
        assert info["animation_count"] == 0
