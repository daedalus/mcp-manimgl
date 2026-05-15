from __future__ import annotations

import json
from typing import Any

from mcp_manimgl.core.animation_builder import AnimationBuilder
from mcp_manimgl.core.mobject_builder import MobjectBuilder
from mcp_manimgl.core.scene_manager import SceneManager


def load_session(scene_manager: SceneManager, path: str) -> None:
    """Replay a session JSON file to rebuild scene state."""
    with open(path) as f:
        commands: list[dict[str, Any]] = json.load(f)

    scene_manager.clear()

    for cmd in commands:
        tool = cmd.get("tool", "")
        args = cmd.get("arguments", {})
        handler = _DISPATCH.get(tool)
        if handler is not None:
            handler(scene_manager, **args)


def _set_resolution(sm: SceneManager, resolution: str) -> None:
    parts = resolution.lower().split("x")
    sm.set_resolution(int(parts[0]), int(parts[1]))


def _set_config(sm: SceneManager, config: dict) -> None:
    if "background_color" in config:
        sm.set_background(config["background_color"])
    if "resolution" in config:
        _set_resolution(sm, config["resolution"])
    if "fps" in config:
        sm.set_fps(int(config["fps"]))
    if "frame_height" in config:
        sm.set_frame_height(float(config["frame_height"]))


_DISPATCH: dict[str, Any] = {}

# --- scene tools ---------------------------------------------------------


def _replay_create_scene(sm: SceneManager, **kw: Any) -> None:
    sm.clear()
    sm.set_background(kw.get("background_color", "#333333"))
    _set_resolution(sm, kw.get("resolution", "1280x720"))
    sm.set_fps(kw.get("fps", 30))
    sm.set_frame_height(kw.get("frame_height", 8.0))


def _replay_clear_scene(sm: SceneManager, **kw: Any) -> None:
    sm.clear()


def _replay_add_wait(sm: SceneManager, **kw: Any) -> None:
    sm.add_wait(kw.get("duration", 1.0))


def _replay_save_state(sm: SceneManager, **kw: Any) -> None:
    sm.save_state()


def _replay_restore_state(sm: SceneManager, **kw: Any) -> None:
    sm.restore_state()


def _replay_set_camera(sm: SceneManager, **kw: Any) -> None:
    sm.set_camera(kw.get("position"), kw.get("orientation"))


def _replay_set_config(sm: SceneManager, **kw: Any) -> None:
    _set_config(sm, kw.get("config", {}))


def _replay_add_custom_code(sm: SceneManager, **kw: Any) -> None:
    sm.add_custom_code(kw.get("code_snippet", ""))


_DISPATCH["create_scene"] = _replay_create_scene
_DISPATCH["clear_scene"] = _replay_clear_scene
_DISPATCH["add_wait"] = _replay_add_wait
_DISPATCH["save_state"] = _replay_save_state
_DISPATCH["restore_state"] = _replay_restore_state
_DISPATCH["set_camera"] = _replay_set_camera
_DISPATCH["set_config"] = _replay_set_config
_DISPATCH["add_custom_code"] = _replay_add_custom_code
_DISPATCH["generate_scene_script"] = lambda sm, **kw: None
_DISPATCH["get_scene_info"] = lambda sm, **kw: None

# --- mobject tools -------------------------------------------------------


def _replay_add_mobject(sm: SceneManager, builder_fn: Any, **kw: Any) -> None:
    record = builder_fn(**kw)
    sm.add_mobject(record)


_DISPATCH["add_circle"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_circle, **kw
)
_DISPATCH["add_square"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_square, **kw
)
_DISPATCH["add_rectangle"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_rectangle, **kw
)
_DISPATCH["add_polygon"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_polygon, **kw
)
_DISPATCH["add_line"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_line, **kw
)
_DISPATCH["add_arrow"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_arrow, **kw
)
_DISPATCH["add_dot"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_dot, **kw
)
_DISPATCH["add_text"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_text, **kw
)
_DISPATCH["add_tex"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_tex, **kw
)
_DISPATCH["add_function_graph"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_function_graph, **kw
)
_DISPATCH["add_parametric_curve"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_parametric_curve, **kw
)
_DISPATCH["add_coordinate_system"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_coordinate_system, **kw
)
_DISPATCH["add_vector"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_vector, **kw
)
_DISPATCH["add_labeled_point"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_labeled_point, **kw
)
_DISPATCH["add_3d_object"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_3d_object, **kw
)
_DISPATCH["add_brace"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_brace, **kw
)
_DISPATCH["add_number_line"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_number_line, **kw
)
_DISPATCH["add_decimal_number"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_decimal_number, **kw
)
_DISPATCH["add_matrix"] = lambda sm, **kw: _replay_add_mobject(
    sm, MobjectBuilder.add_matrix, **kw
)

# Manipulation tools — these mutate existing mobject records in place


def _replay_move_to(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    from mcp_manimgl.core.mobject_builder import MobjectBuilder

    record.position = kw["position"]
    pos = MobjectBuilder._position_str(kw["position"])
    edge = f", aligned_edge={kw.get('aligned_edge')}" if kw.get("aligned_edge") else ""
    record.code_snippet += f"\n{record.mobject_id}.move_to({pos}{edge})"


def _replay_shift(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    v = f"np.array([{kw['vector'][0]}, {kw['vector'][1]}, {kw['vector'][2] if len(kw['vector']) > 2 else 0.0}])"
    record.code_snippet += f"\n{record.mobject_id}.shift({v})"


def _replay_scale(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    about = kw.get("about_point")
    pt = (
        f", about_point=np.array([{about[0]}, {about[1]}, {about[2] if len(about) > 2 else 0.0}])"
        if about
        else ""
    )
    record.code_snippet += f"\n{record.mobject_id}.scale({kw['scale_factor']}{pt})"


def _replay_rotate(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    axis = kw.get("axis")
    about = kw.get("about_point")
    ax = (
        f", axis=np.array([{axis[0]}, {axis[1]}, {axis[2] if len(axis) > 2 else 0.0}])"
        if axis
        else ""
    )
    pt = (
        f", about_point=np.array([{about[0]}, {about[1]}, {about[2] if len(about) > 2 else 0.0}])"
        if about
        else ""
    )
    record.code_snippet += f"\n{record.mobject_id}.rotate({kw['angle']}{ax}{pt})"


def _replay_set_color(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    record.color = kw["color"]
    record.code_snippet += f"\n{record.mobject_id}.set_color('{kw['color']}')"


def _replay_set_opacity(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    record.code_snippet += f"\n{record.mobject_id}.set_opacity({kw['opacity']})"


def _replay_next_to(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    record.code_snippet += (
        f"\n{record.mobject_id}.next_to({kw['reference_id']}, "
        f"direction={kw.get('direction', 'RIGHT')}, "
        f"buff={kw.get('buff', 0.25)})"
    )


def _replay_align_to(sm: SceneManager, **kw: Any) -> None:
    record = sm.get_mobject(kw["mobject_id"])
    if record is None:
        return
    record.code_snippet += f"\n{record.mobject_id}.align_to({kw['reference_id']}, {kw.get('direction', 'UP')})"


_DISPATCH["move_to"] = _replay_move_to
_DISPATCH["shift"] = _replay_shift
_DISPATCH["scale"] = _replay_scale
_DISPATCH["rotate"] = _replay_rotate
_DISPATCH["set_color"] = _replay_set_color
_DISPATCH["set_opacity"] = _replay_set_opacity
_DISPATCH["next_to"] = _replay_next_to
_DISPATCH["align_to"] = _replay_align_to

# --- animation tools -----------------------------------------------------


def _replay_add_animation(sm: SceneManager, builder_fn: Any, **kw: Any) -> None:
    record = builder_fn(**kw)
    sm.add_animation(record)


_DISPATCH["animate_transform"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_transform, **kw
)
_DISPATCH["animate_fade_in"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_fade_in, **kw
)
_DISPATCH["animate_fade_out"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_fade_out, **kw
)
_DISPATCH["animate_grow"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_grow, **kw
)
_DISPATCH["animate_rotate"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_rotate, **kw
)
_DISPATCH["animate_scale"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_scale, **kw
)
_DISPATCH["animate_shift"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_shift, **kw
)
_DISPATCH["animate_indicate"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_indicate, **kw
)
_DISPATCH["animate_write"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_write, **kw
)
_DISPATCH["animate_set_color"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_set_color, **kw
)
_DISPATCH["animate_move_along_path"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_move_along_path, **kw
)
_DISPATCH["animate_group"] = lambda sm, **kw: _replay_add_animation(
    sm, AnimationBuilder.animate_group, **kw
)

# --- audio tools ---------------------------------------------------------

_DISPATCH["add_narration"] = lambda sm, **kw: None  # audio files must exist
_DISPATCH["add_background_music"] = lambda sm, **kw: None

# --- rendering tools -----------------------------------------------------

_DISPATCH["render_scene"] = lambda sm, **kw: None
_DISPATCH["save_frame"] = lambda sm, **kw: None
_DISPATCH["get_render_status"] = lambda sm, **kw: None
