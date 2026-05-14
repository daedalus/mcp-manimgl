from mcp_manimgl.core import SceneManager


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

        removed_nonexistent = scene_manager.remove_mobject("nonexistent")
        assert removed_nonexistent is False

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

        scene_manager.add_wait(2.0)
        scene_manager.clear()

        restored = scene_manager.restore_state()
        assert restored is True
        assert scene_manager.get_info()["mobject_count"] == 1

    def test_restore_without_save(self, scene_manager: SceneManager) -> None:
        restored = scene_manager.restore_state()
        assert restored is False

    def test_add_wait(self, scene_manager: SceneManager) -> None:
        scene_manager.add_wait(1.5)
        assert len(scene_manager.state.wait_times) == 1
        assert scene_manager.state.wait_times[0] == 1.5

    def test_custom_code(self, scene_manager: SceneManager) -> None:
        code = "self.camera.frame.set_height(10)"
        scene_manager.add_custom_code(code)
        assert len(scene_manager.state.custom_code) == 1

    def test_set_camera(self, scene_manager: SceneManager) -> None:
        scene_manager.set_camera(position=[0, 0, -5])
        assert scene_manager.state.camera_position == [0, 0, -5]

        scene_manager.set_camera(orientation=[0.5, 0.0, 0.0])
        assert scene_manager.state.camera_orientation == [0.5, 0.0, 0.0]

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
