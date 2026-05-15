import json
import tempfile

import pytest

from mcp_manimgl.core import SceneManager
from mcp_manimgl.core.animation_builder import AnimationBuilder
from mcp_manimgl.core.mobject_builder import MobjectBuilder
from mcp_manimgl.core.scene_manager import MobjectRecord
from mcp_manimgl.core.session_loader import (
    load_session,
    _DISPATCH,
    _replay_add_animation,
    _replay_add_custom_code,
    _replay_add_mobject,
    _replay_add_wait,
    _replay_align_to,
    _replay_clear_scene,
    _replay_create_scene,
    _replay_move_to,
    _replay_next_to,
    _replay_restore_state,
    _replay_rotate,
    _replay_save_state,
    _replay_scale,
    _replay_set_camera,
    _replay_set_color,
    _replay_set_config,
    _replay_set_opacity,
    _replay_shift,
)


class TestSessionLoaderReplayFunctions:
    def test_replay_create_scene(self) -> None:
        sm = SceneManager()
        sm.set_background("#000")
        sm.set_resolution(640, 480)
        _replay_create_scene(sm, background_color="#FFF", resolution="1920x1080",
                             fps=60, frame_height=10.0)
        info = sm.get_info()
        assert info["background_color"] == "#FFF"
        assert info["resolution"] == [1920, 1080]
        assert info["fps"] == 60
        assert info["frame_height"] == 10.0

    def test_replay_create_scene_defaults(self) -> None:
        sm = SceneManager()
        sm.set_background("#000")
        _replay_create_scene(sm)
        info = sm.get_info()
        assert info["background_color"] == "#333333"
        assert info["resolution"] == [1280, 720]

    def test_replay_clear_scene(self) -> None:
        sm = SceneManager()
        sm.add_wait(1.0)
        _replay_clear_scene(sm)
        assert sm.get_info()["mobject_count"] == 0

    def test_replay_add_wait(self) -> None:
        sm = SceneManager()
        _replay_add_wait(sm, duration=2.5)
        assert len(sm.state.wait_times) == 1
        assert sm.state.wait_times[0] == 2.5

    def test_replay_add_wait_default(self) -> None:
        sm = SceneManager()
        _replay_add_wait(sm)
        assert sm.state.wait_times[0] == 1.0

    def test_replay_save_restore_state(self) -> None:
        sm = SceneManager()
        m = MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, "")
        sm.add_mobject(m)
        _replay_save_state(sm)
        sm.clear()
        assert sm.get_info()["mobject_count"] == 0
        _replay_restore_state(sm)
        assert sm.get_info()["mobject_count"] == 1

    def test_replay_set_camera(self) -> None:
        sm = SceneManager()
        _replay_set_camera(sm, position=[0, 0, -5], orientation=[0.5, 0, 0])
        assert sm.state.camera_position == [0, 0, -5]
        assert sm.state.camera_orientation == [0.5, 0, 0]

    def test_replay_set_camera_partial(self) -> None:
        sm = SceneManager()
        _replay_set_camera(sm, position=[1, 2, 3])
        assert sm.state.camera_position == [1, 2, 3]

    def test_replay_set_config(self) -> None:
        sm = SceneManager()
        _replay_set_config(sm, config={
            "background_color": "#000",
            "resolution": "800x600",
            "fps": 15,
            "frame_height": 6.0,
        })
        info = sm.get_info()
        assert info["background_color"] == "#000"
        assert info["resolution"] == [800, 600]
        assert info["fps"] == 15
        assert info["frame_height"] == 6.0

    def test_replay_set_config_partial(self) -> None:
        sm = SceneManager()
        sm.set_background("#123456")
        _replay_set_config(sm, config={"fps": 24})
        assert sm.get_info()["fps"] == 24
        assert sm.get_info()["background_color"] == "#123456"

    def test_replay_set_config_empty(self) -> None:
        sm = SceneManager()
        _replay_set_config(sm, config={})
        info = sm.get_info()
        assert info["background_color"] == "#333333"

    def test_replay_add_custom_code(self) -> None:
        sm = SceneManager()
        _replay_add_custom_code(sm, code_snippet="x = 1")
        assert len(sm.state.custom_code) == 1
        assert sm.state.custom_code[0] == "x = 1"

    def test_replay_add_custom_code_default(self) -> None:
        sm = SceneManager()
        _replay_add_custom_code(sm)
        assert sm.state.custom_code[0] == ""

    def test_replay_move_to(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_move_to(sm, mobject_id="m1", position=[3, 4, 0])
        assert sm.get_mobject("m1").position == [3, 4, 0]

    def test_replay_move_to_with_aligned_edge(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_move_to(sm, mobject_id="m1", position=[1, 1, 0], aligned_edge="LEFT")
        record = sm.get_mobject("m1")
        assert record.position == [1, 1, 0]
        assert "aligned_edge=LEFT" in record.code_snippet

    def test_replay_move_to_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_move_to(sm, mobject_id="nonexistent", position=[0, 0, 0])
        assert sm.get_info()["mobject_count"] == 0

    def test_replay_shift(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_shift(sm, mobject_id="m1", vector=[1.0, 2.0, 3.0])
        assert "shift(np.array([1.0, 2.0, 3.0]))" in sm.get_mobject("m1").code_snippet

    def test_replay_shift_2d_vector(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_shift(sm, mobject_id="m1", vector=[1, 2])
        assert "shift(np.array([1, 2, 0.0]))" in sm.get_mobject("m1").code_snippet

    def test_replay_shift_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_shift(sm, mobject_id="x", vector=[1, 0, 0])
        assert len(sm.state.mobjects) == 0

    def test_replay_scale(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_scale(sm, mobject_id="m1", scale_factor=2.0)
        assert "scale(2.0)" in sm.get_mobject("m1").code_snippet

    def test_replay_scale_with_about_point(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_scale(sm, mobject_id="m1", scale_factor=0.5, about_point=[1.0, 1.0, 1.0])
        assert "about_point=np.array([1.0, 1.0, 1.0])" in sm.get_mobject("m1").code_snippet

    def test_replay_scale_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_scale(sm, mobject_id="x", scale_factor=2.0)
        assert len(sm.state.mobjects) == 0

    def test_replay_rotate(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_rotate(sm, mobject_id="m1", angle=3.14)
        assert "rotate(3.14)" in sm.get_mobject("m1").code_snippet

    def test_replay_rotate_with_axis(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_rotate(sm, mobject_id="m1", angle=1.57, axis=[0.0, 1.0, 0.0])
        assert "axis=np.array([0.0, 1.0, 0.0])" in sm.get_mobject("m1").code_snippet

    def test_replay_rotate_with_about_point(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_rotate(sm, mobject_id="m1", angle=0.5, about_point=[0.0, 0.0, 1.0])
        assert "about_point=np.array([0.0, 0.0, 1.0])" in sm.get_mobject("m1").code_snippet

    def test_replay_rotate_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_rotate(sm, mobject_id="x", angle=1.0)
        assert len(sm.state.mobjects) == 0

    def test_replay_set_color(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_set_color(sm, mobject_id="m1", color="#FF0000")
        assert sm.get_mobject("m1").color == "#FF0000"
        assert "set_color('#FF0000')" in sm.get_mobject("m1").code_snippet

    def test_replay_set_color_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_set_color(sm, mobject_id="x", color="#000")
        assert len(sm.state.mobjects) == 0

    def test_replay_set_opacity(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_set_opacity(sm, mobject_id="m1", opacity=0.5)
        assert "set_opacity(0.5)" in sm.get_mobject("m1").code_snippet

    def test_replay_set_opacity_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_set_opacity(sm, mobject_id="x", opacity=0.5)
        assert len(sm.state.mobjects) == 0

    def test_replay_next_to(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_next_to(sm, mobject_id="m1", reference_id="m2")
        snippet = sm.get_mobject("m1").code_snippet
        assert "next_to(m2, direction=RIGHT, buff=0.25)" in snippet

    def test_replay_next_to_with_options(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_next_to(sm, mobject_id="m1", reference_id="m2", direction="DOWN", buff=1.0)
        snippet = sm.get_mobject("m1").code_snippet
        assert "direction=DOWN" in snippet
        assert "buff=1.0" in snippet

    def test_replay_next_to_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_next_to(sm, mobject_id="x", reference_id="y")
        assert len(sm.state.mobjects) == 0

    def test_replay_align_to(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_align_to(sm, mobject_id="m1", reference_id="m2")
        snippet = sm.get_mobject("m1").code_snippet
        assert "align_to(m2, UP)" in snippet

    def test_replay_align_to_with_direction(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_align_to(sm, mobject_id="m1", reference_id="m2", direction="LEFT")
        snippet = sm.get_mobject("m1").code_snippet
        assert "align_to(m2, LEFT)" in snippet

    def test_replay_align_to_missing_mobject(self) -> None:
        sm = SceneManager()
        _replay_align_to(sm, mobject_id="x", reference_id="y")
        assert len(sm.state.mobjects) == 0

    def test_replay_add_mobject(self) -> None:
        sm = SceneManager()
        _replay_add_mobject(sm, MobjectBuilder.add_circle, radius=1.0, color="#FFF")
        assert sm.get_info()["mobject_count"] == 1
        assert sm.state.mobjects[0].mobject_type == "circle"

    def test_replay_add_animation(self) -> None:
        sm = SceneManager()
        sm.add_mobject(MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, ""))
        _replay_add_animation(
            sm, AnimationBuilder.animate_fade_in, mobject_id="m1", run_time=1.0
        )
        assert sm.get_info()["animation_count"] == 1
        assert sm.state.animations[0].animation_type == "fade_in"


class TestSessionLoader:
    def test_load_session_unknown_tool_skipped(self) -> None:
        sm = SceneManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"tool": "nonexistent_tool", "arguments": {}}], f)
            path = f.name
        try:
            load_session(sm, path)
            assert sm.get_info()["mobject_count"] == 0
        finally:
            import os
            os.unlink(path)

    def test_load_session_empty_commands(self) -> None:
        sm = SceneManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            path = f.name
        try:
            load_session(sm, path)
            assert sm.get_info()["mobject_count"] == 0
        finally:
            import os
            os.unlink(path)

    def test_load_session_clears_first(self) -> None:
        sm = SceneManager()
        sm.add_wait(5.0)
        assert sm.get_info()["mobject_count"] == 0
        assert len(sm.state.wait_times) == 1
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"tool": "add_wait", "arguments": {"duration": 1.0}}], f)
            path = f.name
        try:
            load_session(sm, path)
            assert len(sm.state.wait_times) == 1
            assert sm.state.wait_times[0] == 1.0
        finally:
            import os
            os.unlink(path)

    def test_load_session_multiple_commands(self) -> None:
        sm = SceneManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([
                {"tool": "add_wait", "arguments": {"duration": 2.0}},
                {"tool": "add_wait", "arguments": {"duration": 3.0}},
            ], f)
            path = f.name
        try:
            load_session(sm, path)
            assert sm.state.wait_times == [2.0, 3.0]
        finally:
            import os
            os.unlink(path)

    def test_load_session_full_flow(self) -> None:
        sm = SceneManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([
                {"tool": "create_scene",
                 "arguments": {"background_color": "#000",
                               "resolution": "800x600", "fps": 15}},
                {"tool": "add_wait", "arguments": {"duration": 0.5}},
                {"tool": "save_state", "arguments": {}},
                {"tool": "clear_scene", "arguments": {}},
                {"tool": "restore_state", "arguments": {}},
            ], f)
            path = f.name
        try:
            load_session(sm, path)
            info = sm.get_info()
            assert info["background_color"] == "#000"
            assert info["resolution"] == [800, 600]
            assert info["fps"] == 15
            assert sm.state.wait_times == [0.5]
        finally:
            import os
            os.unlink(path)
