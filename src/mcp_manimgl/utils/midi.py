from __future__ import annotations

import os
import wave

import numpy as np


SOUNDFONT_DIRS = [
    "/usr/share/sounds/sf3",
    "/usr/share/sounds/sf2",
    "/usr/share/fluidr3mono-gm-soundfont",
    "/usr/share/soundfonts",
]

DEFAULT_SAMPLE_RATE = 44100


def _find_soundfont() -> str | None:
    for d in SOUNDFONT_DIRS:
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if fname.endswith((".sf2", ".sf3")):
                return os.path.join(d, fname)
    return None


def _midi_duration(path: str) -> float:
    """Estimate total duration of a MIDI file in seconds."""
    try:
        from music21 import converter  # type: ignore[import-untyped]

        score = converter.parse(str(path))
        dur: float = score.duration.quarterLength
        return max(dur * 0.5, 1.0)
    except Exception:
        pass
    try:
        from pretty_midi import PrettyMIDI  # type: ignore[import-untyped]

        pm = PrettyMIDI(str(path))
        return float(pm.get_end_time())
    except Exception:
        pass
    with open(path, "rb") as f:  # noqa: SIM115
        data = f.read()
    approx_len_sec = len(data) / 1000.0
    return max(approx_len_sec, 5.0)


def render_midi_to_wav(
    midi_path: str,
    sf_path: str | None = None,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> str:
    """Render a MIDI file to WAV audio using FluidSynth.

    Args:
        midi_path: Path to the .mid/.midi file.
        sf_path: Path to a SoundFont (.sf2/.sf3). Auto-discovered if None.
        sample_rate: Output sample rate.

    Returns:
        Path to the rendered WAV file.
    """
    midi_path = str(midi_path)
    if sf_path is None:
        found = _find_soundfont()
        if found is None:
            raise FileNotFoundError(
                "No SoundFont found. Install fluidr3mono-gm-soundfont or "
                "provide an sf_path."
            )
        sf_path = found
    sf_path = str(sf_path)

    import fluidsynth

    fs = fluidsynth.Synth(samplerate=sample_rate)

    sfid = fs.sfload(sf_path)
    if sfid == fluidsynth.FLUID_FAILED:
        fs.delete()
        raise RuntimeError(f"Failed to load SoundFont: {sf_path}")

    for ch in range(16):
        fs.program_select(ch, sfid, 0, 0)

    fs.play_midi_file(midi_path)

    duration = _midi_duration(midi_path)
    total_frames = int(sample_rate * max(duration + 1.0, 5.0))
    buf_size = 4096
    all_bufs: list[np.ndarray] = []
    written = 0
    while written < total_frames:
        samples = fs.get_samples(buf_size)
        if len(samples) == 0:
            import time

            time.sleep(0.05)
            continue
        all_bufs.append(samples.copy())
        written += len(samples) // 2

    fs.delete()

    audio = np.concatenate(all_bufs)[: total_frames * 2]
    peak: float = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio / peak * 0.9

    audio_int16 = (audio * 32767).astype(np.int16)

    wav_path = midi_path
    if wav_path.lower().endswith((".mid", ".midi")):
        wav_path = wav_path[:-4]
    wav_path += "_rendered.wav"

    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    return os.path.abspath(wav_path)
