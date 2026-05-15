from __future__ import annotations

import os
import shutil
import subprocess


NON_PYTHON_DEPS = [
    {
        "name": "ffmpeg",
        "binary": "ffmpeg",
        "purpose": "Audio mixing and video transcoding",
        "install_hint": "apt install ffmpeg",
    },
    {
        "name": "ffprobe",
        "binary": "ffprobe",
        "purpose": "Audio file metadata inspection (duration, channels)",
        "install_hint": "apt install ffmpeg",
    },
    {
        "name": "libfluidsynth",
        "check": "ldconfig",
        "soname": "libfluidsynth",
        "purpose": "System library for MIDI-to-audio rendering",
        "install_hint": "apt install libfluidsynth3",
    },
    {
        "name": "SoundFont",
        "check": "soundfont",
        "purpose": "SoundFont file required for MIDI synthesis",
        "install_hint": "apt install fluidr3mono-gm-soundfont",
    },
]

SOUNDFONT_DIRS = [
    "/usr/share/sounds/sf3",
    "/usr/share/sounds/sf2",
    "/usr/share/fluidr3mono-gm-soundfont",
    "/usr/share/soundfonts",
]


def _check_binary(name: str) -> bool:
    return shutil.which(name) is not None


def _check_libfluidsynth() -> bool:
    try:
        result = subprocess.run(
            ["ldconfig", "-p"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return "libfluidsynth" in result.stdout
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def _check_soundfont() -> bool:
    for d in SOUNDFONT_DIRS:
        if not os.path.isdir(d):
            continue
        try:
            for fname in os.listdir(d):
                if fname.endswith((".sf2", ".sf3")):
                    return True
        except PermissionError:
            continue
    return False


def check_non_python_deps() -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for dep in NON_PYTHON_DEPS:
        available = False
        check_type = dep.get("check", "binary")
        if check_type == "soundfont":
            available = _check_soundfont()
        elif check_type == "ldconfig":
            available = _check_libfluidsynth()
        else:
            available = _check_binary(dep["binary"])

        if not available:
            missing.append(
                {
                    "name": dep["name"],
                    "purpose": dep["purpose"],
                    "install_hint": dep["install_hint"],
                }
            )
    return missing


def format_missing_deps(missing: list[dict[str, str]]) -> str:
    if not missing:
        return ""
    lines: list[str] = [
        "WARNING: Missing system dependencies. Some features will not work:"
    ]
    for dep in missing:
        lines.append(f"  - {dep['name']}: {dep['purpose']}")
        lines.append(f"    Install: {dep['install_hint']}")
    return "\n".join(lines)


def check_dep_status() -> dict[str, bool]:
    return {
        "ffmpeg": _check_binary("ffmpeg"),
        "ffprobe": _check_binary("ffprobe"),
        "libfluidsynth": _check_libfluidsynth(),
        "soundfont": _check_soundfont(),
    }
