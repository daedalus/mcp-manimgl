from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class EventKind(Enum):
    MOBJECT = auto()
    ANIMATION = auto()
    WAIT = auto()
    AUDIO = auto()
    CUSTOM_CODE = auto()


@dataclass
class TimelineEvent:
    kind: EventKind
    data: dict[str, Any]


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
class AudioRecord:
    audio_id: str
    file_path: str
    text: str
    kind: str = "narration"
    volume: float = 1.0
    loop: bool = False
    duration: float = 0.0


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
    audio_entries: list[AudioRecord] = field(default_factory=list)
    custom_code: list[str] = field(default_factory=list)
    saved_state: dict[str, Any] | None = None
    has_rendered: bool = False
    music_duck_params: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_id": str(uuid.uuid4())[:8],
            "background_color": self.background_color,
            "resolution": list(self.resolution),
            "fps": self.fps,
            "frame_height": self.frame_height,
            "mobject_count": len(self.mobjects),
            "animation_count": len(self.animations),
            "audio_count": len(self.audio_entries),
            "has_rendered": self.has_rendered,
        }


class SceneManager:
    def __init__(self) -> None:
        self._state = SceneState()
        self._saved_state: SceneState | None = None
        self._timeline: list[TimelineEvent] = []

    def get_info(self) -> dict[str, Any]:
        return self._state.to_dict()

    def clear(self) -> None:
        self._state = SceneState()
        self._timeline = []

    def set_music_duck_params(self, params: dict[str, Any]) -> None:
        self._state.music_duck_params = params

    def get_music_duck_params(self) -> dict[str, Any] | None:
        return self._state.music_duck_params

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
        self._timeline.append(
            TimelineEvent(
                kind=EventKind.MOBJECT,
                data={"record": record},
            )
        )

    def get_mobject(self, mobject_id: str) -> MobjectRecord | None:
        for m in self._state.mobjects:
            if m.mobject_id == mobject_id:
                return m
        return None

    def remove_mobject(self, mobject_id: str) -> bool:
        for i, m in enumerate(self._state.mobjects):
            if m.mobject_id == mobject_id:
                self._state.mobjects.pop(i)
                self._timeline = [
                    e
                    for e in self._timeline
                    if not (
                        e.kind == EventKind.MOBJECT
                        and e.data["record"].mobject_id == mobject_id
                    )
                ]
                return True
        return False

    def add_animation(self, record: AnimationRecord) -> None:
        self._state.animations.append(record)
        self._timeline.append(
            TimelineEvent(
                kind=EventKind.ANIMATION,
                data={"record": record},
            )
        )

    def add_wait(self, duration: float) -> None:
        self._state.wait_times.append(duration)
        self._timeline.append(
            TimelineEvent(
                kind=EventKind.WAIT,
                data={"duration": duration},
            )
        )

    def add_audio(self, record: AudioRecord) -> None:
        self._state.audio_entries.append(record)
        self._timeline.append(
            TimelineEvent(
                kind=EventKind.AUDIO,
                data={"record": record},
            )
        )

    def add_custom_code(self, code: str) -> None:
        self._state.custom_code.append(code)
        self._timeline.append(
            TimelineEvent(
                kind=EventKind.CUSTOM_CODE,
                data={"code": code},
            )
        )

    def save_state(self) -> None:
        import copy

        self._saved_state = copy.deepcopy(self._state)
        self._saved_timeline = copy.deepcopy(self._timeline)

    def restore_state(self) -> bool:
        if self._saved_state is None:
            return False
        import copy

        self._state = copy.deepcopy(self._saved_state)
        self._timeline = copy.deepcopy(getattr(self, "_saved_timeline", []))
        return True

    def mark_rendered(self) -> None:
        self._state.has_rendered = True

    @property
    def state(self) -> SceneState:
        return self._state

    def _parse_add_sound_paths(self, code: str) -> list[str]:
        import re

        return re.findall(r"self\.add_sound\s*\(\s*'([^']+)'\s*\)", code)

    def get_audio_manifest(self) -> dict[str, Any]:
        music: list[dict[str, Any]] = []
        narration: list[dict[str, Any]] = []
        current_time = 0.0
        for event in self._timeline:
            if event.kind == EventKind.WAIT:
                current_time += event.data["duration"]
            elif event.kind == EventKind.ANIMATION:
                current_time += event.data["record"].run_time
            elif event.kind == EventKind.AUDIO:
                record: AudioRecord = event.data["record"]
                entry: dict[str, Any] = {
                    "audio_id": record.audio_id,
                    "file_path": record.file_path,
                    "text": record.text,
                    "kind": record.kind,
                    "volume": record.volume,
                    "loop": record.loop,
                    "start_time": current_time,
                }
                if record.kind == "music":
                    music.append(entry)
                else:
                    narration.append(entry)
            elif event.kind == EventKind.CUSTOM_CODE:
                for path in self._parse_add_sound_paths(event.data["code"]):
                    is_music = any(
                        kw in path.lower() for kw in ("classical", "rendered", "bgm")
                    )
                    kind = "music" if is_music else "narration"
                    entry: dict[str, Any] = {
                        "audio_id": "",
                        "file_path": path,
                        "text": "",
                        "kind": kind,
                        "volume": 0.3 if is_music else 1.0,
                        "loop": is_music,
                        "start_time": current_time,
                    }
                    if kind == "music":
                        music.append(entry)
                    else:
                        narration.append(entry)
        return {
            "music": music,
            "narration": narration,
            "total_duration": current_time,
        }

    def generate_script(self, include_audio: bool = True) -> str:
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

        if include_audio:
            for event in self._timeline:
                if (
                    event.kind == EventKind.AUDIO
                    and event.data["record"].kind == "music"
                ):
                    path = event.data["record"].file_path.replace("\\", "/")
                    lines.append(f"{indent}self.add_sound('{path}')")

        for event in self._timeline:
            if event.kind == EventKind.MOBJECT:
                mob_record: MobjectRecord = event.data["record"]
                for line in mob_record.code_snippet.split("\n"):
                    if line.strip():
                        lines.append(f"{indent}{line.strip()}")

            elif event.kind == EventKind.ANIMATION:
                anim_record: AnimationRecord = event.data["record"]
                for line in anim_record.code_snippet.split("\n"):
                    if line.strip():
                        lines.append(f"{indent}{line.strip()}")

            elif event.kind == EventKind.WAIT:
                lines.append(f"{indent}self.wait({event.data['duration']})")

            elif event.kind == EventKind.AUDIO:
                if not include_audio:
                    continue
                if event.data["record"].kind == "music":
                    continue
                audio_record: AudioRecord = event.data["record"]
                path = audio_record.file_path.replace("\\", "/")
                lines.append(f"{indent}self.add_sound('{path}')")
                if audio_record.duration > 0:
                    lines.append(f"{indent}self.wait({audio_record.duration})")

            elif event.kind == EventKind.CUSTOM_CODE:
                code_block = event.data["code"]
                code_lines = code_block.split("\n")
                non_empty = [ln for ln in code_lines if ln.strip()]
                base_indent = 0
                if non_empty:
                    base_indent = min(len(ln) - len(ln.lstrip()) for ln in non_empty)
                for line in code_lines:
                    if not line.strip():
                        continue
                    processed = (
                        line[base_indent:] if len(line) > base_indent else line.lstrip()
                    )
                    if not include_audio and "self.add_sound(" in processed:
                        continue
                    lines.append(f"{indent}{processed}")

        lines.append("")
        return "\n".join(lines)
