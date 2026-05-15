import subprocess
from unittest.mock import patch, MagicMock

import pytest

from mcp_manimgl.utils.audio_mixer import (
    _serialize_narration_tracks,
    get_audio_duration,
    get_audio_channels,
    _preloop_audio,
    mix_audio,
)


class TestSerializeNarrationTracks:
    def test_empty(self) -> None:
        assert _serialize_narration_tracks([]) == []

    def test_single_track(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=5.0,
        ):
            tracks = [{"file_path": "/tmp/a.wav", "start_time": 0.0}]
            result = _serialize_narration_tracks(tracks)
            assert len(result) == 1
            assert result[0]["start_time"] == 0.0

    def test_no_overlap_needed(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=2.0,
        ):
            tracks = [
                {"file_path": "/tmp/a.wav", "start_time": 0.0},
                {"file_path": "/tmp/b.wav", "start_time": 5.0},
            ]
            result = _serialize_narration_tracks(tracks)
            assert len(result) == 2
            assert result[0]["start_time"] == 0.0
            assert result[1]["start_time"] == 5.0

    def test_overlap_shifted(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=3.0,
        ):
            tracks = [
                {"file_path": "/tmp/a.wav", "start_time": 0.0},
                {"file_path": "/tmp/b.wav", "start_time": 1.0},
            ]
            result = _serialize_narration_tracks(tracks)
            assert len(result) == 2
            assert result[0]["start_time"] == 0.0
            assert result[1]["start_time"] == 3.0

    def test_overlap_shifted_deep(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=2.0,
        ):
            tracks = [
                {"file_path": "/tmp/a.wav", "start_time": 0.0},
                {"file_path": "/tmp/b.wav", "start_time": 1.0},
                {"file_path": "/tmp/c.wav", "start_time": 2.0},
            ]
            result = _serialize_narration_tracks(tracks)
            assert len(result) == 3
            assert result[0]["start_time"] == 0.0
            assert result[1]["start_time"] == 2.0
            assert result[2]["start_time"] == 4.0

    def test_unsorted_input(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=2.0,
        ):
            tracks = [
                {"file_path": "/tmp/b.wav", "start_time": 5.0},
                {"file_path": "/tmp/a.wav", "start_time": 0.0},
            ]
            result = _serialize_narration_tracks(tracks)
            assert len(result) == 2
            assert result[0]["start_time"] == 0.0
            assert result[1]["start_time"] == 5.0

    def test_preserves_extra_keys(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.get_audio_duration",
            return_value=2.0,
        ):
            tracks = [
                {"file_path": "/tmp/a.wav", "start_time": 0.0, "volume": 0.8},
            ]
            result = _serialize_narration_tracks(tracks)
            assert result[0]["volume"] == 0.8


class TestGetAudioDuration:
    def test_normal(self) -> None:
        mock_stdout = (
            '{"streams": [{"codec_type": "audio", "duration": "3.5"}]}'
        )
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_duration("/tmp/test.wav") == 3.5

    def test_no_streams(self) -> None:
        mock_stdout = '{"streams": []}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_duration("/tmp/test.wav") == 0.0

    def test_no_duration_field(self) -> None:
        mock_stdout = '{"streams": [{"codec_type": "audio"}]}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_duration("/tmp/test.wav") == 0.0

    def test_multiple_streams_first_with_duration_wins(self) -> None:
        mock_stdout = (
            '{"streams": ['
            '{"codec_type": "video", "duration": "10.0"},'
            '{"codec_type": "audio", "duration": "5.0"}'
            "]}"
        )
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_duration("/tmp/test.wav") == 10.0

    def test_ffprobe_fails(self) -> None:
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            side_effect=FileNotFoundError("ffprobe not found"),
        ):
            with pytest.raises(FileNotFoundError):
                get_audio_duration("/tmp/test.wav")


class TestGetAudioChannels:
    def test_stereo(self) -> None:
        mock_stdout = '{"streams": [{"codec_type": "audio", "channels": 2}]}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_channels("/tmp/test.wav") == 2

    def test_mono(self) -> None:
        mock_stdout = '{"streams": [{"codec_type": "audio", "channels": 1}]}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_channels("/tmp/test.wav") == 1

    def test_no_channels_field(self) -> None:
        mock_stdout = '{"streams": [{"codec_type": "audio"}]}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_channels("/tmp/test.wav") == 2

    def test_no_streams_returns_default(self) -> None:
        mock_stdout = '{"streams": []}'
        with patch(
            "mcp_manimgl.utils.audio_mixer.subprocess.run",
            return_value=MagicMock(stdout=mock_stdout, returncode=0),
        ):
            assert get_audio_channels("/tmp/test.wav") == 2


class TestPreloopAudio:
    def test_ffmpeg_called_with_correct_args(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ) as mock_run,
            patch(
                "mcp_manimgl.utils.audio_mixer.tempfile.NamedTemporaryFile"
            ) as mock_tmp,
        ):
            mock_tmp.return_value.name = "/tmp/looped_000.wav"
            result = _preloop_audio("/src/bgm.wav", 60.0)
            assert result == "/tmp/looped_000.wav"
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "-stream_loop" in args
            assert "-1" in args
            assert args[args.index("-i") + 1] == "/src/bgm.wav"
            assert args[args.index("-t") + 1] == "60.0"
            assert "pcm_s16le" in args

    def test_ffmpeg_failure(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                side_effect=FileNotFoundError("ffmpeg not found"),
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.tempfile.NamedTemporaryFile"
            ) as mock_tmp,
        ):
            mock_tmp.return_value.name = "/tmp/looped_000.wav"
            with pytest.raises(FileNotFoundError):
                _preloop_audio("/src/bgm.wav", 60.0)


class TestMixAudio:
    def test_no_mixing_needed(self) -> None:
        result = mix_audio(
            video_path="/tmp/video.mp4",
            music_path=None,
            music_volume=0.3,
            music_loop=False,
            narration_tracks=[],
        )
        assert result == "/tmp/video.mp4"

    def test_returns_output_path(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=30.0,
            ) as mock_dur,
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path="/tmp/music.wav",
                music_volume=0.5,
                music_loop=False,
                narration_tracks=[
                    {"file_path": "/tmp/nar.wav", "start_time": 2.0, "volume": 1.0},
                ],
                output_path="/tmp/output.mp4",
            )
            assert result == "/tmp/output.mp4"
            assert mock_dur.call_count >= 2

    def test_mix_audio_no_output_path_overwrites(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path=None,
                music_volume=0.3,
                music_loop=False,
                narration_tracks=[
                    {"file_path": "/tmp/nar.wav", "start_time": 0.0, "volume": 0.9},
                ],
            )
            assert result == "/tmp/video.mp4"

    def test_mix_audio_multiple_narrations(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=5.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=1,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path="/tmp/music.wav",
                music_volume=0.3,
                music_loop=False,
                narration_tracks=[
                    {"file_path": "/tmp/nar1.wav", "start_time": 0.0, "volume": 1.0},
                    {"file_path": "/tmp/nar2.wav", "start_time": 2.0, "volume": 1.0},
                ],
            )
            assert result is not None

    def test_mix_audio_narration_only(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=10.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=1,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path=None,
                music_volume=0.3,
                music_loop=False,
                narration_tracks=[
                    {"file_path": "/tmp/nar1.wav", "start_time": 0.0, "volume": 1.0},
                ],
            )
            assert result is not None

    def test_mix_audio_music_loop_no_loop_needed(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path="/tmp/music.wav",
                music_volume=0.3,
                music_loop=True,
                narration_tracks=[],
            )
            assert result is not None

    def test_mix_audio_music_loop(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                side_effect=lambda p: 5.0 if "music" in p else 10.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer._preloop_audio",
                return_value="/tmp/looped.wav",
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path="/tmp/music.wav",
                music_volume=0.3,
                music_loop=True,
                narration_tracks=[],
            )
            assert result is not None

    def test_mix_audio_zero_video_duration(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=0.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                return_value=MagicMock(returncode=0),
            ),
        ):
            result = mix_audio(
                video_path="/tmp/video.mp4",
                music_path="/tmp/music.wav",
                music_volume=0.3,
                music_loop=False,
                narration_tracks=[
                    {"file_path": "/tmp/nar.wav", "start_time": 0.0, "volume": 1.0},
                ],
            )
            assert result is not None

    def test_mix_audio_ffmpeg_failure(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                side_effect=FileNotFoundError("ffmpeg not found"),
            ),
        ):
            with pytest.raises(FileNotFoundError):
                mix_audio(
                    video_path="/tmp/video.mp4",
                    music_path="/tmp/music.wav",
                    music_volume=0.5,
                    music_loop=False,
                    narration_tracks=[
                        {"file_path": "/tmp/nar.wav", "start_time": 0.0, "volume": 1.0},
                    ],
                )

    def test_mix_audio_called_process_error(self) -> None:
        mock_failed = MagicMock()
        mock_failed.returncode = 1
        mock_failed.stderr = "ffmpeg error"
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                return_value=30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, "ffmpeg", stderr="mocked error"
                ),
            ),
        ):
            with pytest.raises(RuntimeError, match="Audio mixing failed"):
                mix_audio(
                    video_path="/tmp/video.mp4",
                    music_path="/tmp/music.wav",
                    music_volume=0.5,
                    music_loop=False,
                    narration_tracks=[
                        {"file_path": "/tmp/nar.wav", "start_time": 0.0, "volume": 1.0},
                    ],
                )

    def test_mix_audio_ffmpeg_failure_with_cleanup(self) -> None:
        mock_failed = MagicMock()
        mock_failed.returncode = 1
        mock_failed.stderr = "ffmpeg error"
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                side_effect=lambda p: 3.0 if "music" in p else 30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer._preloop_audio",
                return_value="/tmp/looped.wav",
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.os.unlink",
            ) as mock_unlink,
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, "ffmpeg", stderr="mocked error"
                ),
            ),
        ):
            with pytest.raises(RuntimeError, match="Audio mixing failed"):
                mix_audio(
                    video_path="/tmp/video.mp4",
                    music_path="/tmp/music.wav",
                    music_volume=0.5,
                    music_loop=True,
                    narration_tracks=[],
                )
            mock_unlink.assert_called_once_with("/tmp/looped.wav")

    def test_mix_audio_ffmpeg_failure_cleanup_oserror(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_duration",
                side_effect=lambda p: 3.0 if "music" in p else 30.0,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.get_audio_channels",
                return_value=2,
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer._preloop_audio",
                return_value="/tmp/looped.wav",
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.os.unlink",
                side_effect=OSError("permission denied"),
            ),
            patch(
                "mcp_manimgl.utils.audio_mixer.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, "ffmpeg", stderr="mocked error"
                ),
            ),
        ):
            with pytest.raises(RuntimeError, match="Audio mixing failed"):
                mix_audio(
                    video_path="/tmp/video.mp4",
                    music_path="/tmp/music.wav",
                    music_volume=0.5,
                    music_loop=True,
                    narration_tracks=[],
                )
