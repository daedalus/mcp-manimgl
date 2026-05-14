from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MobjectRecord:
    mobject_id: str
    mobject_type: str
    color: str
    position: list[float]
    properties: dict[str, Any]
    code_snippet: str


@dataclass
class AnimationRecord:
    animation_id: str
    animation_type: str
    mobject_id: str
    run_time: float
    rate_func: str
    properties: dict[str, Any]
    code_snippet: str


@dataclass
class SceneState:
    background_color: str = "#333333"
    resolution: tuple[int, int] = (1280, 720)
    fps: int = 30
    frame_height: float = 8.0
    camera_position: list[float] | None = None
    camera_orientation: list[float] | None = None
    mobjects: list[MobjectRecord] = field(default_factory=list)
    animations: list[AnimationRecord] = field(default_factory=list)
    wait_times: list[float] = field(default_factory=list)
    custom_code: list[str] = field(default_factory=list)
    saved_state: dict[str, Any] | None = None
    has_rendered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_id": str(uuid.uuid4())[:8],
            "background_color": self.background_color,
            "resolution": list(self.resolution),
            "fps": self.fps,
            "frame_height": self.frame_height,
            "mobject_count": len(self.mobjects),
            "animation_count": len(self.animations),
            "has_rendered": self.has_rendered,
        }


class SceneManager:
    def __init__(self) -> None:
        self._state = SceneState()
        self._saved_state: SceneState | None = None

    def get_info(self) -> dict[str, Any]:
        return self._state.to_dict()

    def clear(self) -> None:
        self._state = SceneState()

    def set_background(self, color: str) -> None:
        self._state.background_color = color

    def set_resolution(self, width: int, height: int) -> None:
        self._state.resolution = (width, height)

    def set_fps(self, fps: int) -> None:
        self._state.fps = fps

    def set_frame_height(self, height: float) -> None:
        self._state.frame_height = height

    def set_camera(
        self,
        position: list[float] | None = None,
        orientation: list[float] | None = None,
    ) -> None:
        if position is not None:
            self._state.camera_position = position
        if orientation is not None:
            self._state.camera_orientation = orientation

    def add_mobject(self, record: MobjectRecord) -> None:
        self._state.mobjects.append(record)

    def get_mobject(self, mobject_id: str) -> MobjectRecord | None:
        for m in self._state.mobjects:
            if m.mobject_id == mobject_id:
                return m
        return None

    def remove_mobject(self, mobject_id: str) -> bool:
        for i, m in enumerate(self._state.mobjects):
            if m.mobject_id == mobject_id:
                self._state.mobjects.pop(i)
                return True
        return False

    def add_animation(self, record: AnimationRecord) -> None:
        self._state.animations.append(record)

    def add_wait(self, duration: float) -> None:
        self._state.wait_times.append(duration)

    def add_custom_code(self, code: str) -> None:
        self._state.custom_code.append(code)

    def save_state(self) -> None:
        import copy

        self._saved_state = copy.deepcopy(self._state)

    def restore_state(self) -> bool:
        if self._saved_state is None:
            return False
        import copy

        self._state = copy.deepcopy(self._saved_state)
        return True

    def mark_rendered(self) -> None:
        self._state.has_rendered = True

    @property
    def state(self) -> SceneState:
        return self._state

    def generate_script(self) -> str:
        lines: list[str] = []
        lines.append("from manimlib import *")
        lines.append("import numpy as np")
        lines.append("")
        lines.append("")
        lines.append("class GeneratedScene(Scene):")
        lines.append("    def construct(self):")

        indent = "        "

        if self._state.background_color != "#333333":
            lines.append(
                f"{indent}self.camera.frame.set_color('{self._state.background_color}')"
            )

        for mob in self._state.mobjects:
            for line in mob.code_snippet.split("\n"):
                if line.strip():
                    lines.append(f"{indent}{line.strip()}")

        for anim in self._state.animations:
            for line in anim.code_snippet.split("\n"):
                if line.strip():
                    lines.append(f"{indent}{line.strip()}")

        for dur in self._state.wait_times:
            lines.append(f"{indent}self.wait({dur})")

        for code in self._state.custom_code:
            for line in code.split("\n"):
                if line.strip():
                    lines.append(f"{indent}{line}")

        lines.append("")
        return "\n".join(lines)
