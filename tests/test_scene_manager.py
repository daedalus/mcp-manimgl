from mcp_manimgl.core import SceneManager
from mcp_manimgl.core.scene_manager import AnimationRecord, AudioRecord, MobjectRecord


class TestSceneManager:
    def test_initial_state(self) -> None:
        sm = SceneManager()
        info = sm.get_info()
        assert info["background_color"] == "#333333"
        assert info["resolution"] == [1280, 720]
        assert info["fps"] == 30
        assert info["frame_height"] == 8.0
        assert info["mobject_count"] == 0
        assert info["animation_count"] == 0
        assert info["has_rendered"] is False

    def test_create_scene_overrides_defaults(self, scene_manager: SceneManager) -> None:
        scene_manager.set_background("#000000")
        scene_manager.set_resolution(1920, 1080)
        scene_manager.set_fps(60)
        scene_manager.set_frame_height(10.0)
        info = scene_manager.get_info()
        assert info["background_color"] == "#000000"
        assert info["resolution"] == [1920, 1080]
        assert info["fps"] == 60
        assert info["frame_height"] == 10.0

    def test_clear_scene(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(1.0)
        scene_manager.clear()
        info = scene_manager.get_info()
        assert info["mobject_count"] == 0
        assert info["animation_count"] == 0

    def test_mobject_lifecycle(
        self, scene_manager: SceneManager, sample_mobject_record
    ) -> None:
        scene_manager.add_mobject(sample_mobject_record)
        assert scene_manager.get_info()["mobject_count"] == 1

        found = scene_manager.get_mobject("m_test")
        assert found is not None
        assert found.mobject_type == "circle"

        not_found = scene_manager.get_mobject("nonexistent")
        assert not_found is None

        removed = scene_manager.remove_mobject("m_test")
        assert removed is True
        assert scene_manager.get_info()["mobject_count"] == 0

        not_removed = scene_manager.remove_mobject("nonexistent")
        assert not_removed is False

    def test_animation_lifecycle(
        self,
        scene_manager: SceneManager,
        sample_mobject_record,
        sample_animation_record,
    ) -> None:
        scene_manager.add_mobject(sample_mobject_record)
        scene_manager.add_animation(sample_animation_record)
        assert scene_manager.get_info()["animation_count"] == 1

    def test_save_and_restore_state(
        self, scene_manager: SceneManager, sample_mobject_record
    ) -> None:
        scene_manager.add_mobject(sample_mobject_record)
        scene_manager.save_state()
        scene_manager.clear()
        assert scene_manager.get_info()["mobject_count"] == 0
        restored = scene_manager.restore_state()
        assert restored is True
        assert scene_manager.get_info()["mobject_count"] == 1

    def test_restore_without_save(self, scene_manager: SceneManager) -> None:
        restored = scene_manager.restore_state()
        assert restored is False

    def test_add_wait(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(1.0)
        assert scene_manager.get_info()["mobject_count"] == 0

    def test_custom_code(self, scene_manager: SceneManager) -> None:
        scene_manager.add_custom_code("x = 1")
        assert scene_manager.get_info()["mobject_count"] == 0

    def test_set_camera(self, scene_manager: SceneManager) -> None:
        scene_manager.set_camera(position=[1, 2, 3], orientation=[0.5, 0.5, 0.0])
        scene_manager.set_camera(position=[4, 5, 6])
        scene_manager.set_camera()

    def test_mark_rendered(self, scene_manager: SceneManager) -> None:
        assert scene_manager.get_info()["has_rendered"] is False
        scene_manager.mark_rendered()
        assert scene_manager.get_info()["has_rendered"] is True

    def test_generate_script_empty_scene(self, scene_manager: SceneManager) -> None:
        script = scene_manager.generate_script()
        assert "from manimlib import *" in script
        assert "class GeneratedScene(Scene):" in script
        assert "def construct(self):" in script

    def test_generate_script_with_mobjects(
        self, scene_manager: SceneManager, sample_mobject_record
    ) -> None:
        scene_manager.add_mobject(sample_mobject_record)
        script = scene_manager.generate_script()
        assert "m_test = Circle" in script

    def test_generate_script_with_animations(
        self,
        scene_manager: SceneManager,
        sample_mobject_record,
        sample_animation_record,
    ) -> None:
        scene_manager.add_mobject(sample_mobject_record)
        scene_manager.add_animation(sample_animation_record)
        script = scene_manager.generate_script()
        assert "FadeIn(m_test" in script

    def test_generate_script_with_wait(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(2.5)
        script = scene_manager.generate_script()
        assert "self.wait(2.5)" in script

    def test_generate_script_with_custom_code(self, scene_manager: SceneManager) -> None:
        scene_manager.add_custom_code("x = 42\nprint(x)")
        script = scene_manager.generate_script()
        assert "x = 42" in script
        assert "print(x)" in script

    def test_generate_script_custom_code_with_blank_lines(
        self, scene_manager: SceneManager
    ) -> None:
        scene_manager.add_custom_code("x = 42\n\n\ny = 7")
        script = scene_manager.generate_script()
        assert "x = 42" in script
        assert "y = 7" in script

    def test_generate_script_with_custom_code_indentation(
        self, scene_manager: SceneManager
    ) -> None:
        scene_manager.add_custom_code("    x = 42\n    y = x + 1")
        script = scene_manager.generate_script()
        assert "x = 42" in script
        assert "y = x + 1" in script

    def test_generate_script_with_music(self, scene_manager: SceneManager) -> None:
        from mcp_manimgl.core.scene_manager import AudioRecord

        scene_manager.add_audio(
            AudioRecord(
                audio_id="bgm1",
                file_path="/tmp/music.mp3",
                text="",
                kind="music",
            )
        )
        script = scene_manager.generate_script(include_audio=True)
        assert "self.add_sound('/tmp/music.mp3')" in script

    def test_generate_script_include_audio_false_skips_narration(
        self, scene_manager: SceneManager
    ) -> None:
        from mcp_manimgl.core.scene_manager import AudioRecord

        scene_manager.add_audio(
            AudioRecord(
                audio_id="n1",
                file_path="/tmp/nar.mp3",
                text="hello",
                kind="narration",
                duration=2.0,
            )
        )
        script = scene_manager.generate_script(include_audio=False)
        assert "self.add_sound('/tmp/nar.mp3')" not in script

    def test_generate_script_custom_code_with_add_sound(
        self, scene_manager: SceneManager
    ) -> None:
        scene_manager.add_custom_code(
            "self.add_sound('/tmp/classical.mp3')"
        )
        script = scene_manager.generate_script(include_audio=True)
        assert "self.add_sound('/tmp/classical.mp3')" in script
        script_no_audio = scene_manager.generate_script(include_audio=False)
        assert "self.add_sound('/tmp/classical.mp3')" not in script_no_audio


class TestOverlapDetection:
    def _make(self, mobject_type: str, position: list[float],
              properties: dict | None = None, mid: str = "") -> MobjectRecord:
        import uuid
        return MobjectRecord(
            mobject_id=mid or str(uuid.uuid4()),
            mobject_type=mobject_type,
            color="#FFFFFF",
            position=position,
            properties=properties or {},
            code_snippet="",
        )

    def test_add_mobject_no_overlap(self, scene_manager: SceneManager) -> None:
        r = self._make("circle", [-5.0, 0.0, 0.0], {"radius": 1.0})
        assert scene_manager.add_mobject(r) == []

    def test_add_mobject_circle_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("circle", [0.5, 0.0, 0.0], {"radius": 1.0})
        )
        assert len(overlaps) == 1
        assert overlaps[0]["new_type"] == "circle"
        assert overlaps[0]["with_type"] == "circle"
        assert overlaps[0]["overlap_x"] > 0

    def test_add_mobject_square_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("square", [0.0, 0.0, 0.0], {"side_length": 2.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("square", [0.0, 0.0, 0.0], {"side_length": 2.0})
        )
        assert len(overlaps) == 1

    def test_add_mobject_rectangle_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("rectangle", [0.0, 0.0, 0.0], {"width": 4.0, "height": 2.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("rectangle", [1.0, 0.0, 0.0], {"width": 4.0, "height": 2.0})
        )
        assert len(overlaps) == 1

    def test_add_mobject_dot_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("dot", [0.0, 0.0, 0.0], {"radius": 0.1})
        )
        overlaps = scene_manager.add_mobject(
            self._make("dot", [0.05, 0.0, 0.0], {"radius": 0.1})
        )
        assert len(overlaps) == 1

    def test_add_mobject_text_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("text", [0.0, 0.0, 0.0],
                       {"text": "HELLO", "font_size": 48})
        )
        assert len(overlaps) >= 1

    def test_add_mobject_tex_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("tex", [0.0, 0.0, 0.0],
                       {"tex_string": "E=mc^2", "font_size": 48})
        )
        assert len(overlaps) >= 1

    def test_add_mobject_non_overlapping(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [-10.0, 0.0, 0.0], {"radius": 1.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("circle", [10.0, 0.0, 0.0], {"radius": 1.0})
        )
        assert overlaps == []

    def test_unknown_type_skipped(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("unknown", [0.0, 0.0, 0.0])
        )
        overlaps = scene_manager.add_mobject(
            self._make("unknown", [0.0, 0.0, 0.0])
        )
        assert overlaps == []

    def test_check_overlaps_empty(self) -> None:
        sm = SceneManager()
        assert sm.check_overlaps() == []

    def test_check_overlaps_single(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        )
        assert scene_manager.check_overlaps() == []

    def test_check_overlaps_non_overlapping(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [-5.0, 0.0, 0.0], {"radius": 1.0})
        )
        scene_manager.add_mobject(
            self._make("circle", [5.0, 0.0, 0.0], {"radius": 1.0})
        )
        assert scene_manager.check_overlaps() == []

    def test_check_overlaps_detects_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        )
        scene_manager.add_mobject(
            self._make("circle", [0.5, 0.0, 0.0], {"radius": 1.0})
        )
        assert len(scene_manager.check_overlaps()) > 0

    def test_three_way_overlap(self, scene_manager: SceneManager) -> None:
        scene_manager.add_mobject(
            self._make("circle", [-0.5, 0.0, 0.0], {"radius": 1.0})
        )
        scene_manager.add_mobject(
            self._make("circle", [0.5, 0.0, 0.0], {"radius": 1.0})
        )
        overlaps = scene_manager.add_mobject(
            self._make("circle", [0.0, 1.0, 0.0], {"radius": 1.0})
        )
        assert len(overlaps) == 2

    def test_all_pairs_vs_placement_consistent(self, scene_manager: SceneManager) -> None:
        a = self._make("square", [0.0, 0.0, 0.0], {"side_length": 2.0})
        b = self._make("square", [0.0, 0.0, 0.0], {"side_length": 2.0})
        scene_manager.add_mobject(a)
        scene_manager.add_mobject(b)
        all_o = scene_manager.check_overlaps()
        assert len(all_o) > 0
        assert all_o[0]["new_type"] == "square"
        assert all_o[0]["with_type"] == "square"

    def test_check_mobject_overlaps_missing(self, scene_manager: SceneManager) -> None:
        assert scene_manager.check_mobject_overlaps("nonexistent") == []

    def test_check_mobject_overlaps_finds_overlap(self, scene_manager: SceneManager) -> None:
        a = self._make("circle", [0.0, 0.0, 0.0], {"radius": 1.0})
        b = self._make("circle", [0.5, 0.0, 0.0], {"radius": 1.0})
        scene_manager.add_mobject(a)
        scene_manager.add_mobject(b)
        result = scene_manager.check_mobject_overlaps(a.mobject_id)
        assert len(result) == 1
        assert result[0]["with_id"] == b.mobject_id

    def test_check_mobject_overlaps_no_overlap(self, scene_manager: SceneManager) -> None:
        a = self._make("circle", [-5.0, 0.0, 0.0], {"radius": 1.0})
        b = self._make("circle", [5.0, 0.0, 0.0], {"radius": 1.0})
        scene_manager.add_mobject(a)
        scene_manager.add_mobject(b)
        result = scene_manager.check_mobject_overlaps(a.mobject_id)
        assert result == []


class TestOverlapDetectionAdversarial:
    def _make(self, mobject_type: str, position: list[float],
              properties: dict | None = None) -> MobjectRecord:
        import uuid
        return MobjectRecord(
            mobject_id=str(uuid.uuid4()),
            mobject_type=mobject_type,
            color="#FFFFFF",
            position=position,
            properties=properties or {},
            code_snippet="",
        )

    def _sm(self) -> SceneManager:
        return SceneManager()

    def test_zero_radius_circle(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 0}))
        o = sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 0}))
        assert o == []

    def test_zero_side_length_square(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("square", [0, 0, 0], {"side_length": 0}))
        o = sm.add_mobject(self._make("square", [0, 0, 0], {"side_length": 0}))
        assert o == []

    def test_zero_width_height_rectangle(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("rectangle", [0, 0, 0], {"width": 0, "height": 0}))
        o = sm.add_mobject(self._make("rectangle", [0, 0, 0], {"width": 0, "height": 0}))
        assert o == []

    def test_zero_radius_dot(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("dot", [0, 0, 0], {"radius": 0}))
        o = sm.add_mobject(self._make("dot", [0, 0, 0], {"radius": 0}))
        assert o == []

    def test_zero_font_size_text(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("text", [0, 0, 0], {"text": "X", "font_size": 0}))
        assert len(o) == 1

    def test_negative_radius_no_overlap(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": -5}))
        assert o == []

    def test_negative_side_length_no_overlap(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("square", [0, 0, 0], {"side_length": 2}))
        o = sm.add_mobject(self._make("square", [0, 0, 0], {"side_length": -10}))
        assert o == []

    def test_huge_coordinates_no_overlap(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [1e8, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("circle", [-1e8, 0, 0], {"radius": 1}))
        assert o == []

    def test_huge_coordinates_overlap(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [1e8, 0, 0], {"radius": 1e6}))
        o = sm.add_mobject(self._make("circle", [1e8 + 1, 0, 0], {"radius": 1e6}))
        assert len(o) == 1

    def test_missing_properties_all_defaults(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("circle", [0, 0, 0], {}))
        assert len(o) == 1

    def test_missing_tex_string(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("tex", [0, 0, 0], {}))
        assert len(o) == 1

    def test_very_long_text(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        long_text = "A" * 10000
        o = sm.add_mobject(self._make("text", [0, 0, 0],
                                       {"text": long_text, "font_size": 48}))
        assert len(o) >= 1

    def test_unicode_text(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("text", [0, 0, 0],
                                       {"text": "αβγδ εζηθ\nकखगघ", "font_size": 48}))
        assert len(o) == 1

    def test_contained_inside(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 10}))
        o = sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        assert len(o) == 1

    def test_barely_touching_inside(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("circle", [1.999, 0, 0], {"radius": 1}))
        assert len(o) == 1

    def test_barely_not_touching(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("circle", [2.001, 0, 0], {"radius": 1}))
        assert o == []

    def test_line_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("line", [0, 0, 0], {"radius": 1}))
        o = sm.add_mobject(self._make("line", [0, 0, 0], {"radius": 1}))
        assert o == []

    def test_polygon_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("polygon", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("polygon", [0, 0, 0], {}))
        assert o == []

    def test_arrow_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("arrow", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("arrow", [0, 0, 0], {}))
        assert o == []

    def test_function_graph_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("function_graph", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("function_graph", [0, 0, 0], {}))
        assert o == []

    def test_parametric_curve_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("parametric_curve", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("parametric_curve", [0, 0, 0], {}))
        assert o == []

    def test_coordinate_system_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("coordinate_system", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("coordinate_system", [0, 0, 0], {}))
        assert o == []

    def test_vector_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("vector", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("vector", [0, 0, 0], {}))
        assert o == []

    def test_brace_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("brace", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("brace", [0, 0, 0], {}))
        assert o == []

    def test_number_line_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("number_line", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("number_line", [0, 0, 0], {}))
        assert o == []

    def test_decimal_number_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("decimal_number", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("decimal_number", [0, 0, 0], {}))
        assert o == []

    def test_matrix_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("matrix", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("matrix", [0, 0, 0], {}))
        assert o == []

    def test_labeled_point_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("labeled_point", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("labeled_point", [0, 0, 0], {}))
        assert o == []

    def test_3d_object_type_skipped(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("3d_object", [0, 0, 0], {}))
        o = sm.add_mobject(self._make("3d_object", [0, 0, 0], {}))
        assert o == []

    def test_many_mobjects_stress(self) -> None:
        sm = self._sm()
        for i in range(100):
            sm.add_mobject(self._make("circle", [i * 2, 0, 0], {"radius": 0.5}))
        o = sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 0.5}))
        assert len(o) >= 1

    def test_many_mobjects_no_overlap_stress(self) -> None:
        sm = self._sm()
        for i in range(100):
            sm.add_mobject(self._make("circle", [i * 10, 0, 0], {"radius": 0.5}))
        o = sm.add_mobject(self._make("circle", [-100, 0, 0], {"radius": 0.5}))
        assert o == []

    def test_all_at_origin_many(self) -> None:
        sm = self._sm()
        for _ in range(50):
            sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        o = sm.check_overlaps()
        assert len(o) > 0

    def test_mixed_known_and_unknown_types(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        sm.add_mobject(self._make("line", [0, 0, 0], {}))
        sm.add_mobject(self._make("square", [0.5, 0, 0], {"side_length": 1}))
        sm.add_mobject(self._make("arrow", [1, 0, 0], {}))
        o = sm.check_overlaps()
        assert len(o) > 0
        for entry in o:
            assert entry["new_type"] in ("circle", "square")

    def test_check_overlaps_with_unknown_types(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("line", [0, 0, 0], {}))
        sm.add_mobject(self._make("line", [0, 0, 0], {}))
        assert sm.check_overlaps() == []

    def test_circle_without_radius_key(self) -> None:
        sm = self._sm()
        r = MobjectRecord("c1", "circle", "#FFF", [0, 0, 0], {}, "")
        r2 = MobjectRecord("c2", "circle", "#FFF", [0, 0, 0], {}, "")
        sm.add_mobject(r)
        o = sm.add_mobject(r2)
        assert len(o) == 1

    def test_square_without_side_length_key(self) -> None:
        sm = self._sm()
        sm.add_mobject(MobjectRecord("s1", "square", "#FFF", [0, 0, 0], {}, ""))
        o = sm.add_mobject(MobjectRecord("s2", "square", "#FFF", [0, 0, 0], {}, ""))
        assert len(o) == 1

    def test_rectangle_without_dimension_keys(self) -> None:
        sm = self._sm()
        sm.add_mobject(MobjectRecord("r1", "rectangle", "#FFF", [0, 0, 0], {}, ""))
        o = sm.add_mobject(MobjectRecord("r2", "rectangle", "#FFF", [0, 0, 0], {}, ""))
        assert len(o) == 1

    def test_dot_without_radius_key(self) -> None:
        sm = self._sm()
        sm.add_mobject(MobjectRecord("d1", "dot", "#FFF", [0, 0, 0], {}, ""))
        o = sm.add_mobject(MobjectRecord("d2", "dot", "#FFF", [0, 0, 0], {}, ""))
        assert len(o) == 1

    def test_text_without_text_key(self) -> None:
        sm = self._sm()
        sm.add_mobject(MobjectRecord("t1", "circle", "#FFF", [0, 0, 0],
                                      {"radius": 1}, ""))
        o = sm.add_mobject(MobjectRecord("t2", "text", "#FFF", [0, 0, 0],
                                          {}, ""))
        assert len(o) == 1

    def test_tex_without_tex_string_key(self) -> None:
        sm = self._sm()
        sm.add_mobject(MobjectRecord("tx1", "circle", "#FFF", [0, 0, 0],
                                      {"radius": 1}, ""))
        o = sm.add_mobject(MobjectRecord("tx2", "tex", "#FFF", [0, 0, 0],
                                          {}, ""))
        assert len(o) == 1

    def test_negative_font_size(self) -> None:
        sm = self._sm()
        sm.add_mobject(self._make("circle", [0, 0, 0], {"radius": 1}))
        sm.add_mobject(self._make("text", [0, 0, 0],
                                   {"text": "X", "font_size": -48}))
        assert sm.get_info()["mobject_count"] == 2


class TestSceneManagerAudio:
    def test_set_get_music_duck_params(self) -> None:
        sm = SceneManager()
        assert sm.get_music_duck_params() is None
        params = {"threshold": "-30dB", "ratio": 6, "attack": 0.05, "release": 0.3}
        sm.set_music_duck_params(params)
        assert sm.get_music_duck_params() == params

    def test_set_music_duck_params_partial(self) -> None:
        sm = SceneManager()
        sm.set_music_duck_params({"threshold": "-20dB"})
        assert sm.get_music_duck_params() == {"threshold": "-20dB"}

    def test_add_audio_narration(self, scene_manager: SceneManager) -> None:
        record = AudioRecord(
            audio_id="a1", file_path="/tmp/test_narration.wav",
            text="Hello", kind="narration", volume=0.8,
        )
        scene_manager.add_audio(record)
        assert len(scene_manager.state.audio_entries) == 1
        assert scene_manager.state.audio_entries[0].audio_id == "a1"
        assert scene_manager.state.audio_entries[0].kind == "narration"

    def test_add_audio_music(self, scene_manager: SceneManager) -> None:
        record = AudioRecord(
            audio_id="a2", file_path="/tmp/test_music.wav",
            text="", kind="music", volume=0.3, loop=True,
        )
        scene_manager.add_audio(record)
        assert len(scene_manager.state.audio_entries) == 1
        assert scene_manager.state.audio_entries[0].kind == "music"
        assert scene_manager.state.audio_entries[0].loop is True

    def test_add_audio_idempotent(self, scene_manager: SceneManager) -> None:
        r = AudioRecord(audio_id="dup", file_path="/tmp/a.wav", text="x", kind="narration")
        scene_manager.add_audio(r)
        scene_manager.add_audio(r)
        assert len(scene_manager.state.audio_entries) == 2

    def test_parse_add_sound_paths(self) -> None:
        sm = SceneManager()
        code = "self.add_sound('/music/bgm.wav')\nself.add_sound('/voice/narration.wav')"
        paths = sm._parse_add_sound_paths(code)
        assert paths == ["/music/bgm.wav", "/voice/narration.wav"]

    def test_parse_add_sound_paths_no_match(self) -> None:
        sm = SceneManager()
        assert sm._parse_add_sound_paths("x = 1") == []

    def test_parse_add_sound_paths_varied_quotes(self) -> None:
        sm = SceneManager()
        code = "self.add_sound('path with spaces.wav')"
        assert sm._parse_add_sound_paths(code) == ["path with spaces.wav"]

    def test_get_audio_manifest_empty(self, scene_manager: SceneManager) -> None:
        m = scene_manager.get_audio_manifest()
        assert m == {"music": [], "narration": [], "total_duration": 0.0}

    def test_get_audio_manifest_with_wait(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(3.5)
        m = scene_manager.get_audio_manifest()
        assert m["total_duration"] == 3.5
        assert m["music"] == []
        assert m["narration"] == []

    def test_get_audio_manifest_with_narration(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(2.0)
        scene_manager.add_audio(AudioRecord(
            audio_id="n1", file_path="/tmp/nar.wav",
            text="Hello", kind="narration",
        ))
        m = scene_manager.get_audio_manifest()
        assert len(m["narration"]) == 1
        assert m["narration"][0]["start_time"] == 2.0
        assert m["narration"][0]["kind"] == "narration"
        assert m["narration"][0]["audio_id"] == "n1"
        assert m["total_duration"] == 2.0

    def test_get_audio_manifest_with_music(self, scene_manager: SceneManager) -> None:
        scene_manager.add_audio(AudioRecord(
            audio_id="m1", file_path="/tmp/mus.wav",
            text="", kind="music", volume=0.5, loop=True,
        ))
        m = scene_manager.get_audio_manifest()
        assert len(m["music"]) == 1
        assert m["music"][0]["kind"] == "music"
        assert m["music"][0]["loop"] is True
        assert m["music"][0]["volume"] == 0.5

    def test_get_audio_manifest_timing(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(1.0)
        scene_manager.add_audio(AudioRecord(
            audio_id="n1", file_path="/tmp/a.wav", text="A", kind="narration",
        ))
        scene_manager.add_wait(2.0)
        scene_manager.add_audio(AudioRecord(
            audio_id="n2", file_path="/tmp/b.wav", text="B", kind="narration",
        ))
        m = scene_manager.get_audio_manifest()
        assert len(m["narration"]) == 2
        assert m["narration"][0]["start_time"] == 1.0
        assert m["narration"][1]["start_time"] == 3.0
        assert m["total_duration"] == 3.0

    def test_get_audio_manifest_custom_code_bgm(self, scene_manager: SceneManager) -> None:
        scene_manager.add_custom_code(
            "self.add_sound('/music/classical.wav')"
        )
        m = scene_manager.get_audio_manifest()
        assert len(m["music"]) == 1
        assert m["music"][0]["file_path"] == "/music/classical.wav"
        assert m["music"][0]["kind"] == "music"
        assert m["music"][0]["loop"] is True
        assert m["music"][0]["volume"] == 0.3

    def test_get_audio_manifest_custom_code_narration(self, scene_manager: SceneManager) -> None:
        scene_manager.add_custom_code(
            "self.add_sound('/voice/explain.wav')"
        )
        m = scene_manager.get_audio_manifest()
        assert len(m["narration"]) == 1
        assert m["narration"][0]["file_path"] == "/voice/explain.wav"
        assert m["narration"][0]["kind"] == "narration"
        assert m["narration"][0]["loop"] is False
        assert m["narration"][0]["volume"] == 1.0

    def test_get_audio_manifest_rendered_keyword(self, scene_manager: SceneManager) -> None:
        scene_manager.add_custom_code(
            "self.add_sound('/tmp/rendered_output.wav')"
        )
        m = scene_manager.get_audio_manifest()
        assert len(m["music"]) == 1
        assert m["music"][0]["kind"] == "music"

    def test_get_audio_manifest_timing_with_custom_code(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(1.5)
        scene_manager.add_custom_code("self.add_sound('/music/bgm.wav')")
        scene_manager.add_wait(2.5)
        m = scene_manager.get_audio_manifest()
        assert m["total_duration"] == 4.0
        assert len(m["music"]) == 1
        assert m["music"][0]["start_time"] == 1.5

    def test_get_audio_manifest_with_animation(
        self, scene_manager: SceneManager, sample_animation_record: AnimationRecord
    ) -> None:
        scene_manager.add_audio(AudioRecord(
            audio_id="n1", file_path="/tmp/a.wav", text="A", kind="narration",
        ))
        scene_manager.add_animation(sample_animation_record)
        m = scene_manager.get_audio_manifest()
        assert m["total_duration"] == 1.0
        assert len(m["narration"]) == 1
        assert m["narration"][0]["start_time"] == 0.0
