import tempfile
from unittest.mock import MagicMock, patch

import pytest

from mcp_manimgl.core import SceneManager
from mcp_manimgl.core.scene_manager import MobjectRecord
from mcp_manimgl.core.session_recorder import SessionRecorder


class MockMCP:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}
        self.resources: dict[str, object] = {}

    def tool(self, **kwargs: object) -> object:
        def decorator(f: object) -> object:
            self.tools[f.__name__] = f
            return f
        return decorator

    def resource(self, uri: str) -> object:
        def decorator(f: object) -> object:
            self.resources[uri] = f
            return f
        return decorator


@pytest.fixture
def sm() -> SceneManager:
    return SceneManager()


@pytest.fixture
def recorder() -> SessionRecorder:
    return SessionRecorder(output_dir=tempfile.mkdtemp())


@pytest.fixture
def mock_mcp() -> MockMCP:
    return MockMCP()


# ── Scene Tools ──────────────────────────────────────────────────────────


class TestSceneTools:
    def test_create_scene(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        fn = mock_mcp.tools["create_scene"]
        result = fn("#000000", "800x600", 15, 10.0)
        info = sm.get_info()
        assert info["background_color"] == "#000000"
        assert info["resolution"] == [800, 600]
        assert info["fps"] == 15
        assert info["frame_height"] == 10.0
        assert result["scene_id"] == sm.get_info()["scene_id"]

    def test_create_scene_bad_resolution_falls_back(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        fn = mock_mcp.tools["create_scene"]
        fn(resolution="not_valid")
        assert sm.get_info()["resolution"] == [1280, 720]

    def test_create_scene_defaults(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        fn = mock_mcp.tools["create_scene"]
        fn()
        info = sm.get_info()
        assert info["background_color"] == "#333333"
        assert info["resolution"] == [1280, 720]
        assert info["fps"] == 30

    def test_get_scene_info(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        fn = mock_mcp.tools["get_scene_info"]
        result = fn()
        assert result["mobject_count"] == 0

    def test_clear_scene(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        sm.add_wait(1.0)
        fn = mock_mcp.tools["clear_scene"]
        fn()
        assert sm.get_info()["mobject_count"] == 0

    def test_add_wait(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        fn = mock_mcp.tools["add_wait"]
        fn(2.5)
        assert sm.state.wait_times == [2.5]

    def test_add_wait_default(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_wait"]()
        assert sm.state.wait_times == [1.0]

    def test_save_restore_state(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        m = MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, "")
        sm.add_mobject(m)
        mock_mcp.tools["save_state"]()
        sm.clear()
        mock_mcp.tools["restore_state"]()
        assert sm.get_info()["mobject_count"] == 1

    def test_restore_without_save(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["restore_state"]()
        assert result is False

    def test_set_camera(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["set_camera"](position=[0, 0, -5], orientation=[0.5, 0.0, 0.0])
        assert sm.state.camera_position == [0, 0, -5]

    def test_set_camera_none(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["set_camera"]()
        assert result is True

    @pytest.mark.parametrize("resolution", ["1920x1080", "invalid_bad", None])
    def test_set_config_resolution(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder, resolution: str | None
    ) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        config: dict[str, object] = {"background_color": "#000"}
        if resolution is not None:
            config["resolution"] = resolution
        mock_mcp.tools["set_config"](config=config)
        assert sm.get_info()["background_color"] == "#000"

    def test_set_config_full(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["set_config"](config={
            "background_color": "#FFF",
            "resolution": "800x600",
            "fps": 24,
            "frame_height": 6.0,
        })
        info = sm.get_info()
        assert info["background_color"] == "#FFF"
        assert info["resolution"] == [800, 600]
        assert info["fps"] == 24
        assert info["frame_height"] == 6.0

    def test_add_custom_code(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_custom_code"](code_snippet="x = 1")
        assert sm.state.custom_code == ["x = 1"]

    def test_verify_scene_overlaps(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("a", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        sm.add_mobject(MobjectRecord("b", "circle", "#FFF", [0.5, 0, 0], {"radius": 1}, ""))
        result = mock_mcp.tools["verify_scene_overlaps"]()
        assert len(result) > 0

    def test_generate_scene_script(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.scene_tools import register_scene_tools

        register_scene_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["generate_scene_script"]()
        assert "from manimlib import *" in result


# ── Animation Tools ──────────────────────────────────────────────────────


class TestAnimationTools:
    def test_animate_fade_in(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_fade_in"](mobject_id="m1")
        assert sm.get_info()["animation_count"] == 1

    def test_animate_fade_out(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_fade_out"](mobject_id="m1", run_time=2.0)
        anims = sm.state.animations
        assert len(anims) == 1
        assert anims[0].animation_type == "fade_out"
        assert anims[0].run_time == 2.0

    def test_animate_grow(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_grow"](mobject_id="m1", grow_type="center")
        assert sm.get_info()["animation_count"] == 1

    def test_animate_rotate(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_rotate"](mobject_id="m1", angle=3.14, axis=[0, 0, 1])
        assert sm.state.animations[0].animation_type == "rotate"

    def test_animate_scale(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_scale"](mobject_id="m1", scale_factor=2.0)
        assert sm.state.animations[0].properties["scale_factor"] == 2.0

    def test_animate_shift(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_shift"](mobject_id="m1", vector=[1, 0, 0])
        assert sm.state.animations[0].properties["vector"] == [1, 0, 0]

    def test_animate_indicate(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_indicate"](mobject_id="m1")
        assert sm.state.animations[0].animation_type == "indicate"

    def test_animate_write(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_write"](mobject_id="m1")
        assert sm.state.animations[0].animation_type == "write"

    def test_animate_set_color(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_set_color"](mobject_id="m1", color="#FF0000")
        assert sm.state.animations[0].properties["color"] == "#FF0000"

    def test_animate_move_along_path(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_move_along_path"](mobject_id="m1", path_type="circle")
        assert sm.state.animations[0].animation_type == "move_along_path"

    def test_animate_transform(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_transform"](mobject_id="m1")
        assert sm.state.animations[0].animation_type == "transform"

    def test_animate_group(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        result = mock_mcp.tools["animate_group"](
            animation_data=[{"animation_type": "fade_in", "mobject_id": "m1"}],
        )
        assert result["animation_type"] == "group"
        assert result["animation_count"] == 1

    def test_animate_transform_with_target(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        from mcp_manimgl.tools.animation_tools import register_animation_tools

        register_animation_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        mock_mcp.tools["animate_transform"](
            mobject_id="m1", target_mobject_type="square", target_config={"side_length": 2.0}
        )
        anim = sm.state.animations[0]
        assert anim.properties["target_type"] == "square"


# ── Rendering Tools ──────────────────────────────────────────────────────


class TestRenderingTools:
    def test_render_scene(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.render_scene.return_value = {"render_id": "abc123"}

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["render_scene"]()
        assert result["render_id"] == "abc123"

    def test_get_render_result(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.get_render_result.return_value = {"status": "completed"}

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["get_render_result"](render_id="abc123")
        assert result["status"] == "completed"

    def test_get_render_result_unknown(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        adapter = MagicMock()
        adapter.get_render_result.return_value = None

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["get_render_result"](render_id="unknown")
        assert result["status"] == "unknown"

    def test_save_frame(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.save_frame.return_value = "/tmp/frame.png"

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["save_frame"]()
        assert result == "/tmp/frame.png"

    def test_save_frame_with_path(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.save_frame.return_value = "/custom/path.png"

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["save_frame"](output_path="/custom/path.png")
        assert result == "/custom/path.png"

    def test_get_render_status(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.get_status.return_value = {"manim_available": True, "opengl_available": True}

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["get_render_status"]()
        assert result["manim_available"] is True

    def test_verify_video(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        adapter = MagicMock()
        adapter.verify_video.return_value = {"success": True, "duration_sec": 30.0}

        from mcp_manimgl.tools.rendering_tools import register_rendering_tools

        register_rendering_tools(mock_mcp, adapter, recorder)
        result = mock_mcp.tools["verify_video"](video_path="/tmp/video.mp4")
        assert result["success"] is True
        assert result["duration_sec"] == 30.0


# ── Mobject Tools ────────────────────────────────────────────────────────


class TestMobjectTools:
    def test_add_circle(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_circle"](radius=2.0, color="#FF0000")
        assert sm.get_info()["mobject_count"] == 1
        assert result["mobject_type"] == "circle"
        assert result["color"] == "#FF0000"
        assert result["position"] == [0.0, 0.0, 0.0]
        assert "overlaps" in result

    def test_add_circle_with_position(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_circle"](position=[3.0, 4.0, 0.0])
        assert result["position"] == [3.0, 4.0, 0.0]

    def test_add_square(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_square"]()
        assert sm.get_info()["mobject_count"] == 1
        assert result["mobject_type"] == "square"

    def test_add_rectangle(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_rectangle"](width=6.0, height=3.0)
        assert result["mobject_type"] == "rectangle"

    def test_add_polygon(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_polygon"](vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        assert result["mobject_type"] == "polygon"

    def test_add_line(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_line"](start=[0, 0, 0], end=[1, 1, 0])
        assert result["mobject_type"] == "line"

    def test_add_arrow(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_arrow"](start=[0, 0, 0], end=[1, 1, 0])
        assert result["mobject_type"] == "arrow"

    def test_add_dot(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_dot"]()
        assert result["mobject_type"] == "dot"
        assert "position" in result

    def test_add_text(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_text"](text="Hello World")
        assert result["mobject_type"] == "text"

    def test_add_tex(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_tex"](tex_string="E=mc^2")
        assert result["mobject_type"] == "tex"

    def test_add_function_graph(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_function_graph"](function="np.sin(x)")
        assert result["mobject_type"] == "function_graph"

    def test_add_parametric_curve(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_parametric_curve"](function="np.cos(t)")
        assert result["mobject_type"] == "parametric_curve"

    def test_add_coordinate_system(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_coordinate_system"]()
        assert result["mobject_type"] == "coordinate_system"

    def test_add_vector(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_vector"](vector=[1, 2, 0])
        assert result["mobject_type"] == "vector"

    def test_add_labeled_point(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_labeled_point"](label="A", point=[1, 1, 0])
        assert result["mobject_type"] == "labeled_point"

    def test_add_3d_object(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_3d_object"](object_type="sphere")
        assert result["mobject_type"] == "sphere"

    def test_add_brace(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        result = mock_mcp.tools["add_brace"](mobject_id="m1")
        assert result["mobject_type"] == "brace"

    def test_add_number_line(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_number_line"]()
        assert result["mobject_type"] == "number_line"

    def test_add_decimal_number(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_decimal_number"](value=3.14)
        assert result["mobject_type"] == "decimal_number"

    def test_add_matrix(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_matrix"](rows=[[1, 2], [3, 4]])
        assert result["mobject_type"] == "matrix"

    def test_add_brace_overlap_warning(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        """Add two circles at same position to trigger overlap detection."""
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"](radius=1.0, position=[0, 0, 0])
        result = mock_mcp.tools["add_circle"](radius=1.0, position=[0, 0, 0])
        assert len(result["overlaps"]) > 0

    def test_add_circle_no_overlap(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["add_circle"](radius=1.0, position=[0, 0, 0])
        assert result["overlaps"] is None

    # ── Mobject manipulation tools ─────────────────────────────────────

    def test_move_to_with_overlap(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"](radius=1.0, position=[0, 0, 0])
        mock_mcp.tools["add_circle"](radius=1.0, position=[10, 10, 0])
        mid2 = sm.state.mobjects[1].mobject_id
        result = mock_mcp.tools["move_to"](mobject_id=mid2, position=[0, 0, 0])
        assert result["success"] is True
        assert result["overlaps"] is not None
        assert len(result["overlaps"]) == 1
        assert result["overlaps"][0]["with_id"] == sm.state.mobjects[0].mobject_id

    def test_move_to(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"](radius=1.0)
        result = mock_mcp.tools["move_to"](mobject_id=sm.state.mobjects[0].mobject_id, position=[5, 5, 0])
        assert result["success"] is True
        assert result["position"] == [5, 5, 0]
        assert result["overlaps"] is None
        assert sm.state.mobjects[0].position == [5, 5, 0]

    def test_move_to_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["move_to"](mobject_id="nonexistent", position=[0, 0, 0])
        assert result["success"] is False

    def test_shift(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        result = mock_mcp.tools["shift"](mobject_id=sm.state.mobjects[0].mobject_id, vector=[1, 0, 0])
        assert result is True

    def test_shift_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["shift"](mobject_id="x", vector=[1, 0, 0]) is False

    def test_scale(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        result = mock_mcp.tools["scale"](mobject_id=sm.state.mobjects[0].mobject_id, scale_factor=2.0)
        assert result is True

    def test_rotate(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        result = mock_mcp.tools["rotate"](mobject_id=sm.state.mobjects[0].mobject_id, angle=1.57)
        assert result is True

    def test_set_color(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mid = sm.state.mobjects[0].mobject_id
        result = mock_mcp.tools["set_color"](mobject_id=mid, color="#00FF00")
        assert result is True
        assert sm.get_mobject(mid).color == "#00FF00"

    def test_set_opacity(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        result = mock_mcp.tools["set_opacity"](mobject_id=sm.state.mobjects[0].mobject_id, opacity=0.5)
        assert result is True

    def test_next_to(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mock_mcp.tools["add_square"]()
        mobjs = sm.state.mobjects
        result = mock_mcp.tools["next_to"](mobject_id=mobjs[0].mobject_id, reference_id=mobjs[1].mobject_id)
        assert result is True

    def test_align_to(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mock_mcp.tools["add_square"]()
        mobjs = sm.state.mobjects
        result = mock_mcp.tools["align_to"](
            mobject_id=mobjs[0].mobject_id, reference_id=mobjs[1].mobject_id
        )
        assert result is True

    def test_move_to_with_aligned_edge(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mid = sm.state.mobjects[0].mobject_id
        result = mock_mcp.tools["move_to"](mobject_id=mid, position=[1, 1, 0], aligned_edge="LEFT")
        assert result["success"] is True
        assert sm.get_mobject(mid).position == [1, 1, 0]

    def test_scale_with_about_point(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mid = sm.state.mobjects[0].mobject_id
        result = mock_mcp.tools["scale"](mobject_id=mid, scale_factor=0.5, about_point=[0, 0, 0])
        assert result is True

    def test_rotate_with_axis_and_about(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        mock_mcp.tools["add_circle"]()
        mid = sm.state.mobjects[0].mobject_id
        result = mock_mcp.tools["rotate"](mobject_id=mid, angle=0.5, axis=[0, 1, 0], about_point=[0, 0, 0])
        assert result is True

    def test_scale_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["scale"](mobject_id="x", scale_factor=2.0) is False

    def test_rotate_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["rotate"](mobject_id="x", angle=0.5) is False

    def test_set_color_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["set_color"](mobject_id="x", color="#000") is False

    def test_set_opacity_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["set_opacity"](mobject_id="x", opacity=0.5) is False

    def test_next_to_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["next_to"](mobject_id="x", reference_id="y") is False

    def test_align_to_missing(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        from mcp_manimgl.tools.mobject_tools import register_mobject_tools

        register_mobject_tools(mock_mcp, sm, recorder)
        assert mock_mcp.tools["align_to"](mobject_id="x", reference_id="y") is False


# ── Audio Tools ──────────────────────────────────────────────────────────


class TestAudioTools:
    def test_audio_duration_get_duration_fails(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.tools.audio_tools.get_audio_duration", side_effect=RuntimeError("ffprobe error")),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["audio_duration"](file_path="/tmp/test.wav")
            assert result["success"] is False
            assert "ffprobe error" in result["error"]

    def test_audio_duration(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.tools.audio_tools.get_audio_duration", return_value=3.5),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["audio_duration"](file_path="/tmp/test.wav")
            assert result["success"] is True
            assert result["duration"] == 3.5

    def test_audio_duration_file_not_found(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        from mcp_manimgl.tools.audio_tools import register_audio_tools

        register_audio_tools(mock_mcp, sm, recorder)
        result = mock_mcp.tools["audio_duration"](file_path="/tmp/nonexistent.wav")
        assert result["success"] is False
        assert "error" in result

    def test_add_narration_gtts_not_installed(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        from mcp_manimgl.tools.audio_tools import register_audio_tools

        register_audio_tools(mock_mcp, sm, recorder)
        with patch.dict("sys.modules", {"gtts": None}):
            result = mock_mcp.tools["add_narration"](text="Hello")
            assert result["success"] is False
            assert "gTTS is not installed" in result["error"]

    def test_add_narration_tts_fails(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        from mcp_manimgl.tools.audio_tools import register_audio_tools

        register_audio_tools(mock_mcp, sm, recorder)
        with patch("gtts.gTTS", side_effect=RuntimeError("TTS error")):
            result = mock_mcp.tools["add_narration"](text="Hello")
            assert result["success"] is False
            assert "TTS generation failed" in result["error"]

    def test_add_narration(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        with (
            patch("gtts.gTTS") as mock_gtts,
            patch("mcp_manimgl.tools.audio_tools.get_audio_duration", return_value=3.0),
        ):
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts

            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["add_narration"](text="Hello world")
            assert result["success"] is True
            assert len(sm.state.audio_entries) == 1
            assert sm.state.audio_entries[0].kind == "narration"

    def test_add_narration_with_lang(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        with (
            patch("gtts.gTTS") as mock_gtts,
            patch("mcp_manimgl.tools.audio_tools.get_audio_duration", return_value=3.0),
        ):
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts

            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            mock_mcp.tools["add_narration"](text="Bonjour", lang="fr")
            mock_gtts.assert_called_with(text="Bonjour", lang="fr", slow=False)

    def test_add_background_music(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.tools.audio_tools.uuid.uuid4", return_value=MagicMock(hex="abcd1234")),
            patch("shutil.copy2"),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["add_background_music"](file_path="/path/to/bgm.mp3")
            assert result["success"] is True
            assert len(sm.state.audio_entries) == 1
            assert sm.state.audio_entries[0].kind == "music"

    def test_add_background_music_midi(self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.tools.audio_tools.uuid.uuid4", return_value=MagicMock(hex="abcd1234")),
            patch("shutil.copy2"),
            patch("mcp_manimgl.utils.midi.render_midi_to_wav", return_value="/tmp/rendered_midi.wav") as mock_midi,
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            mock_mcp.tools["add_background_music"](file_path="/path/to/song.mid")
            mock_midi.assert_called_once()

    def test_add_background_music_with_duck_params(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.tools.audio_tools.uuid.uuid4", return_value=MagicMock(hex="abcd1234")),
            patch("shutil.copy2"),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            mock_mcp.tools["add_background_music"](
                file_path="/path/to/bgm.mp3",
                volume=0.5,
                duck_threshold="-30dB",
                duck_ratio=6,
            )
            params = sm.get_music_duck_params()
            assert params is not None
            assert params["threshold"] == "-30dB"
            assert params["ratio"] == 6

    def test_add_background_music_file_not_found(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        with patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=False):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["add_background_music"](file_path="/nonexistent/file.mp3")
            assert result["success"] is False
            assert "error" in result

    def test_add_background_music_midi_import_error(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch.dict("sys.modules", {"mcp_manimgl.utils.midi": None}),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["add_background_music"](file_path="/path/to/song.mid")
            assert result["success"] is False
            assert "MIDI rendering requires pyfluidsynth" in result["error"]

    def test_add_background_music_midi_render_error(
        self, mock_mcp: MockMCP, sm: SceneManager, recorder: SessionRecorder
    ) -> None:
        with (
            patch("mcp_manimgl.tools.audio_tools.os.path.exists", return_value=True),
            patch("mcp_manimgl.utils.midi.render_midi_to_wav", side_effect=RuntimeError("sf error")),
        ):
            from mcp_manimgl.tools.audio_tools import register_audio_tools

            register_audio_tools(mock_mcp, sm, recorder)
            result = mock_mcp.tools["add_background_music"](file_path="/path/to/song.mid")
            assert result["success"] is False
            assert "MIDI rendering failed" in result["error"]
