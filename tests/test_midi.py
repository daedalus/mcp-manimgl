from __future__ import annotations

import os
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pytest

from mcp_manimgl.utils.midi import (
    _find_soundfont,
    _midi_duration,
    render_midi_to_wav,
)


class TestFindSoundfont:
    def test_no_soundfont_dirs_exist(self) -> None:
        with patch("mcp_manimgl.utils.midi.os.path.isdir", return_value=False):
            assert _find_soundfont() is None

    def test_dir_exists_but_no_sf_files(self) -> None:
        with (
            patch("mcp_manimgl.utils.midi.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.midi.os.listdir", return_value=["readme.txt", "some.cache"]),
        ):
            assert _find_soundfont() is None

    def test_first_sf2_found(self) -> None:
        sorted_files = sorted(["zzz.sf3", "aaa.sf2", "other.txt"])
        with (
            patch("mcp_manimgl.utils.midi.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.midi.os.listdir", return_value=sorted_files),
            patch("mcp_manimgl.utils.midi.SOUNDFONT_DIRS", ["/sf"]),
        ):
            result = _find_soundfont()
            assert result == "/sf/aaa.sf2"

    def test_sf3_found_when_no_sf2(self) -> None:
        with (
            patch("mcp_manimgl.utils.midi.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.midi.os.listdir", return_value=["font.sf3"]),
            patch("mcp_manimgl.utils.midi.SOUNDFONT_DIRS", ["/sf"]),
        ):
            result = _find_soundfont()
            assert result == "/sf/font.sf3"

    def test_first_dir_wins(self) -> None:
        with (
            patch("mcp_manimgl.utils.midi.os.path.isdir", side_effect=[True, True]),
            patch(
                "mcp_manimgl.utils.midi.os.listdir",
                side_effect=[["a.sf2"], ["b.sf2"]],
            ),
            patch("mcp_manimgl.utils.midi.SOUNDFONT_DIRS", ["/dir1", "/dir2"]),
        ):
            result = _find_soundfont()
            assert result == "/dir1/a.sf2"

    def test_second_dir_used_when_first_empty(self) -> None:
        with (
            patch("mcp_manimgl.utils.midi.os.path.isdir", side_effect=[True, True]),
            patch(
                "mcp_manimgl.utils.midi.os.listdir",
                side_effect=[["nope.txt"], ["b.sf2"]],
            ),
            patch("mcp_manimgl.utils.midi.SOUNDFONT_DIRS", ["/dir1", "/dir2"]),
        ):
            result = _find_soundfont()
            assert result == "/dir2/b.sf2"


class TestMidiDuration:
    def test_music21_success(self) -> None:
        mock_score = MagicMock()
        mock_score.duration.quarterLength = 20.0
        mock_converter = MagicMock()
        mock_converter.parse.return_value = mock_score
        with patch.dict("sys.modules", {"music21": MagicMock(converter=mock_converter)}):
            dur = _midi_duration("/tmp/test.mid")
            assert dur == pytest.approx(10.0)  # 20 * 0.5

    def test_music21_minimum_duration(self) -> None:
        mock_score = MagicMock()
        mock_score.duration.quarterLength = 0.5
        mock_converter = MagicMock()
        mock_converter.parse.return_value = mock_score
        with patch.dict("sys.modules", {"music21": MagicMock(converter=mock_converter)}):
            dur = _midi_duration("/tmp/test.mid")
            assert dur == pytest.approx(1.0)  # max(0.25, 1.0)

    def test_music21_fallsback_to_pretty_midi(self) -> None:
        mock_pm = MagicMock()
        mock_pm.get_end_time.return_value = 15.0
        with (
            patch.dict("sys.modules", {"music21": None}),
            patch.dict("sys.modules", {"pretty_midi": MagicMock(PrettyMIDI=lambda p: mock_pm)}),
        ):
            dur = _midi_duration("/tmp/test.mid")
            assert dur == pytest.approx(15.0)

    def test_pretty_midi_fallsback_to_file_size(self) -> None:
        fake_data = b"\x00" * 12000
        with (
            patch.dict("sys.modules", {"music21": None, "pretty_midi": None}),
            patch("builtins.open", mock_open(read_data=fake_data)),
        ):
            dur = _midi_duration("/tmp/test.mid")
            # 12000 / 1000 = 12.0
            assert dur == pytest.approx(12.0)

    def test_fallback_minimum_duration(self) -> None:
        fake_data = b"\x00" * 500
        with (
            patch.dict("sys.modules", {"music21": None, "pretty_midi": None}),
            patch("builtins.open", mock_open(read_data=fake_data)),
        ):
            dur = _midi_duration("/tmp/test.mid")
            assert dur == pytest.approx(5.0)

    def test_music21_exception_fallsback(self) -> None:
        mock_converter = MagicMock()
        mock_converter.parse.side_effect = ValueError("bad midi")
        with (
            patch.dict("sys.modules", {"music21": MagicMock(converter=mock_converter)}),
            patch.dict("sys.modules", {"pretty_midi": None}),
            patch("builtins.open", mock_open(read_data=b"\x00" * 10000)),
        ):
            dur = _midi_duration("/tmp/test.mid")
            assert dur == pytest.approx(10.0)


class TestRenderMidiToWav:
    def test_no_soundfont_found_raises(self) -> None:
        with patch("mcp_manimgl.utils.midi._find_soundfont", return_value=None):
            with pytest.raises(FileNotFoundError, match="No SoundFont found"):
                render_midi_to_wav("/tmp/test.mid", sf_path=None)

    def test_fluidsynth_failed_to_load_soundfont(self) -> None:
        mock_fs = MagicMock()
        mock_fs.sfload.return_value = -1
        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1
        with (
            patch("mcp_manimgl.utils.midi._find_soundfont", return_value="/sf/font.sf2"),
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
        ):
            with pytest.raises(RuntimeError, match="Failed to load SoundFont"):
                render_midi_to_wav("/tmp/test.mid")

    def _make_samples_generator(self) -> MagicMock:
        """Return a MagicMock whose get_samples first returns empty once,
        then returns 4096-element arrays repeatedly until written >= total_frames."""
        empty_returned = False

        def get_samples_side(_buf_size: int) -> np.ndarray:
            nonlocal empty_returned
            if not empty_returned:
                empty_returned = True
                return np.array([], dtype=np.float32)
            return np.array([0.5, -0.3] * 2048, dtype=np.float32)

        return get_samples_side

    def test_empty_buffer_loops_with_sleep(self) -> None:
        mock_fs = MagicMock()
        mock_fs.sfload.return_value = 0
        mock_fs.get_samples.side_effect = self._make_samples_generator()

        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1

        with (
            patch("mcp_manimgl.utils.midi._find_soundfont", return_value="/sf/font.sf2"),
            patch("mcp_manimgl.utils.midi._midi_duration", return_value=0.5),
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
        ):
            result = render_midi_to_wav("/tmp/test.mid")
            assert result.endswith("_rendered.wav")
            mock_fs.get_samples.assert_called()
            # Should have been called at least twice (empty then non-empty)
            assert mock_fs.get_samples.call_count >= 2
            os.remove(result)

    def test_render_success_with_auto_soundfont(self, tmp_path: pytest.TempPathFactory) -> None:
        midi_file = os.path.join(tmp_path, "test.mid")
        with open(midi_file, "w") as f:
            f.write("fake midi")

        mock_fs = MagicMock()
        mock_fs.sfload.return_value = 0
        mock_fs.get_samples.side_effect = self._make_samples_generator()

        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1

        with (
            patch("mcp_manimgl.utils.midi._find_soundfont", return_value="/sf/font.sf2"),
            patch("mcp_manimgl.utils.midi._midi_duration", return_value=0.5),
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
        ):
            result = render_midi_to_wav(midi_file)
            assert result.endswith("_rendered.wav")

            # Verify WAV file has correct format
            import wave

            with wave.open(result, "r") as wf:
                assert wf.getnchannels() == 2
                assert wf.getsampwidth() == 2
                assert wf.getframerate() == 44100

            os.remove(result)

    def test_render_with_explicit_sf_path(self, tmp_path: pytest.TempPathFactory) -> None:
        midi_file = os.path.join(tmp_path, "song.mid")
        with open(midi_file, "w") as f:
            f.write("data")

        mock_fs = MagicMock()
        mock_fs.sfload.return_value = 0
        mock_fs.get_samples.side_effect = self._make_samples_generator()

        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1

        with (
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
            patch("mcp_manimgl.utils.midi._midi_duration", return_value=0.5),
        ):
            result = render_midi_to_wav(midi_file, sf_path="/custom/font.sf2")
            assert result.endswith("_rendered.wav")
            os.remove(result)

    def test_normalize_silent_audio(self, tmp_path: pytest.TempPathFactory) -> None:
        midi_file = os.path.join(tmp_path, "silent.mid")
        with open(midi_file, "w") as f:
            f.write("")

        def silent_samples(_buf_size: int) -> np.ndarray:
            return np.zeros(4096, dtype=np.float32)

        mock_fs = MagicMock()
        mock_fs.sfload.return_value = 0
        mock_fs.get_samples.side_effect = silent_samples

        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1

        with (
            patch("mcp_manimgl.utils.midi._find_soundfont", return_value="/sf/font.sf2"),
            patch("mcp_manimgl.utils.midi._midi_duration", return_value=0.5),
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
        ):
            result = render_midi_to_wav(midi_file)
            assert result.endswith("_rendered.wav")
            os.remove(result)

    def test_non_midi_extension_output_path(self, tmp_path: pytest.TempPathFactory) -> None:
        input_path = os.path.join(tmp_path, "song.midi")
        with open(input_path, "w") as f:
            f.write("data")

        mock_fs = MagicMock()
        mock_fs.sfload.return_value = 0
        mock_fs.get_samples.side_effect = self._make_samples_generator()

        mock_fluidsynth = MagicMock()
        mock_fluidsynth.Synth.return_value = mock_fs
        mock_fluidsynth.FLUID_FAILED = -1

        with (
            patch("mcp_manimgl.utils.midi._find_soundfont", return_value="/sf/font.sf2"),
            patch("mcp_manimgl.utils.midi._midi_duration", return_value=0.5),
            patch.dict("sys.modules", {"fluidsynth": mock_fluidsynth}),
        ):
            result = render_midi_to_wav(input_path)
            assert result.endswith("_rendered.wav")
            os.remove(result)
