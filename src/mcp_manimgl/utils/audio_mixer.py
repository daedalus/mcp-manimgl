from __future__ import annotations

import json
import subprocess
from typing import Any


def _get_audio_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        dur = stream.get("duration")
        if dur:
            return float(dur)
    return 0.0


def mix_audio(
    video_path: str,
    music_path: str | None,
    music_volume: float,
    music_loop: bool,
    narration_tracks: list[dict[str, Any]],
    duck_params: dict[str, Any] | None = None,
    output_path: str | None = None,
) -> str:
    """Mix background music and narration into a rendered video.

    Args:
        video_path: Path to the rendered video (without audio or with placeholder audio).
        music_path: Path to background music audio file. None if no music.
        music_volume: Volume for music track (0.0-1.0).
        music_loop: Whether to loop the music to fill video duration.
        narration_tracks: List of dicts with 'file_path', 'start_time' keys.
        duck_params: Dict with 'threshold', 'ratio', 'attack', 'release' keys.
        output_path: Final output path. If None, replaces video_path.

    Returns:
        Path to the final mixed video.
    """
    if duck_params is None:
        duck_params = {
            "threshold": "-24dB",
            "ratio": 4,
            "attack": 0.1,
            "release": 0.5,
        }

    if output_path is None:
        output_path = video_path

    need_mixing = music_path is not None or narration_tracks

    if not need_mixing:
        return video_path

    video_duration = _get_audio_duration(video_path)
    if video_duration <= 0:
        video_duration = 60.0

    inputs = [video_path]
    input_labels = []

    if music_path:
        inputs.append(music_path)
        music_idx = 1
        input_labels.append("music")

    for i, nt in enumerate(narration_tracks):
        inputs.append(nt["file_path"])
        input_labels.append(f"narration{i}")

    filter_parts: list[str] = []
    filter_outputs: list[str] = []

    if music_path:
        loop_filter = ""
        if music_loop:
            music_dur = _get_audio_duration(music_path)
            if music_dur > 0:
                loops_needed = int(video_duration / music_dur) + 1
                loop_filter = f",aloop=loop={loops_needed}:size=2000000000"
        label = f"[music_{music_idx}]"
        dur_sec = video_duration + 2.0
        filter_parts.append(
            f"[{music_idx}:a]volume={music_volume}{loop_filter}"
            f",atrim=duration={dur_sec}[music_trim]"
        )
        filter_outputs.append("[music_trim]")

    narration_mix_parts: list[str] = []
    narration_mix_count = 0

    for i, nt in enumerate(narration_tracks):
        idx = i + (1 if music_path else 0) + 1
        start_ms = int(nt.get("start_time", 0) * 1000)
        label = f"[nar_delayed_{i}]"
        dur_ms = int(_get_audio_duration(nt["file_path"]) * 1000)
        filter_parts.append(
            f"[{idx}:a]adelay={start_ms}|{start_ms}"
            f",atrim=duration={dur_ms + start_ms}ms[{label}]"
        )
        narration_mix_parts.append(label)
        narration_mix_count += 1

    if narration_mix_count > 1:
        inputs_str = "".join(narration_mix_parts)
        filter_parts.append(
            f"{inputs_str}amix=inputs={narration_mix_count}"
            f":dropout_transition=2[narration_mix]"
        )
        narration_out = "[narration_mix]"
    elif narration_mix_count == 1:
        narration_out = narration_mix_parts[0]
    else:
        narration_out = None

    if music_path and narration_out:
        duck_threshold = duck_params.get("threshold", "-24dB")
        duck_ratio = duck_params.get("ratio", 4)
        duck_attack = duck_params.get("attack", 0.1)
        duck_release = duck_params.get("release", 0.5)

        filter_parts.append(
            f"[music_trim][{narration_out}]sidechaincompress="
            f"threshold={duck_threshold}:ratio={duck_ratio}"
            f":attack={duck_attack}:release={duck_release}"
            f"[music_ducked]"
        )

        filter_parts.append(
            "[narration_mix][music_ducked]amix=inputs=2"
            ":weights=1 0.7[final_audio]"
        )
        audio_out = "[final_audio]"
    elif music_path:
        audio_out = "[music_trim]"
    elif narration_out:
        audio_out = narration_out
    else:
        audio_out = None

    if audio_out is None:
        return video_path

    filter_complex = "; ".join(filter_parts)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
    ]
    for inp in inputs[1:]:
        cmd.extend(["-i", inp])

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[0:v]",
        "-map", audio_out,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ])

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Audio mixing failed:\n{exc.stderr}"
        ) from exc

    return output_path
