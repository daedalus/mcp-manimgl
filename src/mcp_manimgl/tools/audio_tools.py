from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING

from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call
from mcp_manimgl.utils.audio_mixer import get_audio_duration

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from mcp_manimgl.core import SceneManager


def register_audio_tools(
    mcp: FastMCP, scene_manager: SceneManager, recorder: SessionRecorder
) -> None:
    @mcp.tool()
    def audio_duration(file_path: str) -> dict:
        """Get the duration of any audio file in seconds.

        Accepts audio files (.mp3, .wav, .ogg, .mid) created by the server.
        Uses ffprobe internally.

        Args:
            file_path: Path to the audio file.

        Returns:
            Dictionary with the duration in seconds.

        Example:
            >>> audio_duration("/tmp/mcp_manimgl/audio/audio_abc123.mp3")
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        try:
            duration = get_audio_duration(file_path)
            return {"success": True, "file_path": file_path, "duration": duration}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @mcp.tool()
    def add_narration(
        text: str,
        lang: str = "en",
    ) -> dict:
        """Generate and add a text-to-speech narration audio track to the scene.

        The audio plays at the point in the timeline where this tool is called.
        Uses Google TTS (gTTS) for voice synthesis.

        IMPORTANT: Always use MCP tools for scene operations.

        Args:
            text: The text to be spoken in the narration.
            lang: Language code (default: "en"). See gTTS docs for supported codes.

        Returns:
            Dictionary with audio_id, file_path, and status.

        Example:
            >>> add_narration("Hello, this is a test narration.")
            >>> add_narration("Bonjour le monde", "fr")
        """
        try:
            from gtts import gTTS
        except ImportError:
            return {
                "success": False,
                "error": "gTTS is not installed. Install it with: pip install gtts",
            }

        audio_id = f"audio_{uuid.uuid4().hex[:8]}"
        from mcp_manimgl import MCP_MANIMGL_WORKDIR

        audio_dir = os.path.join(MCP_MANIMGL_WORKDIR, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        file_path = os.path.join(audio_dir, f"{audio_id}.mp3")

        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(file_path)
        except Exception as exc:
            return {
                "success": False,
                "error": f"TTS generation failed: {exc}",
            }

        from mcp_manimgl.core.scene_manager import AudioRecord

        duration = get_audio_duration(file_path)

        record = AudioRecord(
            audio_id=audio_id,
            file_path=os.path.abspath(file_path),
            text=text,
            duration=duration,
        )
        scene_manager.add_audio(record)
        record_tool_call(recorder, "add_narration")
        return {
            "success": True,
            "audio_id": audio_id,
            "file_path": os.path.abspath(file_path),
            "text": text,
        }

    @mcp.tool()
    def add_background_music(
        file_path: str,
        volume: float = 0.2,
        loop: bool = False,
        duck_threshold: str = "-24dB",
        duck_ratio: float = 4.0,
        duck_attack: float = 0.1,
        duck_release: float = 0.5,
    ) -> dict:
        """Add background music to the scene.

        The music plays from the beginning of the rendered video.
        Accepts audio files (.mp3, .wav, .ogg) or MIDI files (.mid, .midi).
        MIDI files are rendered to audio using FluidSynth and a system SoundFont.

        When narration tracks are also present, the music volume auto-ducks
        during narration via sidechain compression in post-processing.

        IMPORTANT: Always use MCP tools for scene operations.

        Args:
            file_path: Path to an audio file or MIDI file.
            volume: Playback volume 0.0-1.0 (default: 0.3).
            loop: Loop the music to fill the video duration if shorter (default: False).
            duck_threshold: Sidechain compression threshold for ducking (default: "-24dB").
            duck_ratio: Compression ratio for ducking (default: 4.0).
            duck_attack: Duck attack time in seconds (default: 0.1).
            duck_release: Duck release time in seconds (default: 0.5).

        Returns:
            Dictionary with audio_id, file_path, and status.

        Example:
            >>> add_background_music("/path/to/music.mp3", volume=0.3, loop=True)
            >>> add_background_music("/path/to/song.mid", volume=0.2)
        """
        file_path = str(file_path)

        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        audio_id = f"bgm_{uuid.uuid4().hex[:8]}"
        from mcp_manimgl import MCP_MANIMGL_WORKDIR

        audio_dir = os.path.join(MCP_MANIMGL_WORKDIR, "audio")
        os.makedirs(audio_dir, exist_ok=True)

        is_midi = file_path.lower().endswith((".mid", ".midi"))
        final_path = file_path

        if is_midi:
            try:
                from mcp_manimgl.utils.midi import render_midi_to_wav

                wav_path = render_midi_to_wav(file_path)
                final_path = wav_path
            except ImportError:
                return {
                    "success": False,
                    "error": (
                        "MIDI rendering requires pyfluidsynth. "
                        "Install it with: pip install pyfluidsynth"
                    ),
                }
            except Exception as exc:
                return {
                    "success": False,
                    "error": f"MIDI rendering failed: {exc}",
                }

        import shutil

        ext = os.path.splitext(final_path)[1] or ".wav"
        dest_path = os.path.join(audio_dir, f"{audio_id}{ext}")
        if os.path.abspath(final_path) != os.path.abspath(dest_path):
            shutil.copy2(final_path, dest_path)

        from mcp_manimgl.core.scene_manager import AudioRecord

        record = AudioRecord(
            audio_id=audio_id,
            file_path=os.path.abspath(dest_path),
            text="",
            kind="music",
            volume=volume,
            loop=loop,
        )
        scene_manager.add_audio(record)

        duck_params = {
            "threshold": duck_threshold,
            "ratio": duck_ratio,
            "attack": duck_attack,
            "release": duck_release,
        }
        scene_manager.set_music_duck_params(duck_params)
        record_tool_call(recorder, "add_background_music")
        return {
            "success": True,
            "audio_id": audio_id,
            "file_path": os.path.abspath(dest_path),
            "volume": volume,
            "loop": loop,
            "midi_rendered": is_midi,
            "duck_params": duck_params,
        }
