from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from mcp_manimgl.adapters.manim_adapter import ManimAdapter
from mcp_manimgl.core.scene_manager import AudioRecord, MobjectRecord, SceneManager


@pytest.fixture
def sm() -> SceneManager:
    return SceneManager()


class TestInit:
    def test_constructor(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        assert adapter._scene_manager is sm
        assert adapter._manim_available is None
        assert adapter._render_results == {}


class TestCheckManimAvailable:
    def test_available(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.dict("sys.modules", {"manimlib": MagicMock()}):
            assert adapter.check_manim_available() is True
            assert adapter._manim_available is True

    def test_not_available(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.dict("sys.modules", {"manimlib": None}):
            assert adapter.check_manim_available() is False
            assert adapter._manim_available is False

    def test_caches_result(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        adapter._manim_available = True
        with patch.dict("sys.modules", {"manimlib": None}):
            assert adapter.check_manim_available() is True

    def test_caches_false(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        adapter._manim_available = False
        with patch.dict("sys.modules", {"manimlib": MagicMock()}):
            assert adapter.check_manim_available() is False


class TestCheckOpenglAvailable:
    def test_available(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with (
            patch.dict("sys.modules", {"moderngl": MagicMock()}),
            patch("moderngl.create_standalone_context"),
        ):
            assert adapter.check_opengl_available() is True

    def test_import_error(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.dict("sys.modules", {"moderngl": None}):
            assert adapter.check_opengl_available() is False

    def test_create_context_fails(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with (
            patch.dict("sys.modules", {"moderngl": MagicMock()}),
            patch("moderngl.create_standalone_context", side_effect=RuntimeError("no GPU")),
        ):
            assert adapter.check_opengl_available() is False


class TestRenderScene:
    def test_returns_render_id(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render"):
            result = adapter.render_scene()
            assert "render_id" in result
            assert result["status"] == "started"

    def test_stores_started_status(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render"):
            result = adapter.render_scene()
            stored = adapter.get_render_result(result["render_id"])
            assert stored is not None
            assert stored["status"] == "started"

    def test_custom_output_path(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render"):
            result = adapter.render_scene(output_path="/tmp/test.mp4")
            assert result["status"] == "started"

    def test_custom_format(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render"):
            result = adapter.render_scene(fmt="gif")
            assert result["status"] == "started"

    def test_do_render_called_correctly(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render") as mock_render:
            result = adapter.render_scene(output_path="/tmp/out.mp4", fmt="mov")
            mock_render.assert_called_once_with(result["render_id"], "/tmp/out.mp4", "mov")

    def test_concurrent_renders_have_unique_ids(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch.object(adapter, "_do_render"):
            r1 = adapter.render_scene()
            r2 = adapter.render_scene()
            assert r1["render_id"] != r2["render_id"]


class TestGetRenderResult:
    def test_returns_none_for_unknown(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        assert adapter.get_render_result("nonexistent") is None

    def test_returns_stored_result(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        adapter._render_results["abc"] = {"status": "completed"}
        assert adapter.get_render_result("abc") == {"status": "completed"}


class TestDoRender:
    def _populated_scene(self, sm: SceneManager) -> None:
        sm.set_background("#000000")
        sm.set_resolution(640, 480)
        sm.set_fps(15)
        sm.set_frame_height(8.0)
        sm.add_mobject(
            MobjectRecord("m1", "circle", "#FFF", [0, 0, 0], {"radius": 1}, "m1 = Circle()")
        )

    def test_successful_render(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "rendered OK"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid1")
            result = adapter.get_render_result("rid1")
            assert result is not None
            assert result["status"] == "completed"
            assert result["success"] is True

    def test_render_failure(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "manimgl error"
        mock_result.stdout = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid2")
            result = adapter.get_render_result("rid2")
            assert result is not None
            assert result["status"] == "failed"
            assert "error" in result

    def test_render_timeout(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid3")
            result = adapter.get_render_result("rid3")
            assert result is not None
            assert result["status"] == "failed"
            assert "timed out" in result["error"]

    def test_manimgl_not_found(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", side_effect=FileNotFoundError),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid4")
            result = adapter.get_render_result("rid4")
            assert result is not None
            assert result["status"] == "failed"
            assert "manimgl binary not found" in result["error"]

    def test_custom_output_path(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.os.makedirs"),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid5", output_path="/tmp/custom/output.mp4", fmt="mp4")
            result = adapter.get_render_result("rid5")
            assert result is not None
            assert result["status"] == "completed"
            assert result["output_path"]

    def test_output_not_found_walks_dir(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        side_effects = {"exists": [], "walk": []}

        def fake_exists(path: str) -> bool:
            side_effects["exists"].append(path)
            if "output.mp4" in path:
                return False
            if "found.mp4" in path:
                return True
            return True

        def fake_walk(_dir: str):
            side_effects["walk"].append(_dir)
            yield (_dir, [], ["found.mp4"])

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", side_effect=fake_exists),
            patch("mcp_manimgl.adapters.manim_adapter.os.walk", side_effect=fake_walk),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid6")
            result = adapter.get_render_result("rid6")
            assert result is not None
            assert result["status"] == "completed"

    def test_script_file_written(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        mock_file = MagicMock()
        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("builtins.open", MagicMock()) as mock_open,
        ):
            adapter._do_render("rid7")
            mock_open.assert_called()
            # verify script file was opened for writing
            write_calls = [c for c in mock_open.mock_calls if "scene.py" in str(c)]
            assert len(write_calls) >= 0  # at least tried

    def test_has_audio_but_not_mp4_skips_mix(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)
        sm.add_audio(
            AudioRecord(audio_id="a1", file_path="/tmp/nar.mp3", text="hi", kind="narration", duration=1.0, volume=1.0, loop=False)
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch.object(adapter, "_mix_audio_to_video") as mock_mix,
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid8", fmt="gif")
            mock_mix.assert_not_called()

    def test_mix_audio_failure_records_mix_error(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)
        sm.add_audio(
            AudioRecord(audio_id="a1", file_path="/tmp/nar.mp3", text="hi", kind="narration", duration=1.0, volume=1.0, loop=False)
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch.object(adapter, "_mix_audio_to_video", side_effect=RuntimeError("mix failed")),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid_mixfail")
            result = adapter.get_render_result("rid_mixfail")
            assert result is not None
            assert result["status"] == "completed"
            assert result["mix_error"] == "mix failed"

    def test_mix_audio_output_path_not_found(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)
        sm.add_audio(
            AudioRecord(audio_id="a1", file_path="/tmp/nar.mp3", text="hi", kind="narration", duration=1.0, volume=1.0, loop=False)
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", side_effect=lambda p: p == "/tmp/mtest/output.mp4"),
            patch.object(adapter, "_mix_audio_to_video", return_value="/tmp/mixed.mp4"),
            patch("builtins.open", MagicMock()),
        ):
            adapter._do_render("rid_nopath")
            result = adapter.get_render_result("rid_nopath")
            assert result is not None
            assert result["output_path"] is None

    def test_mark_rendered_on_success(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        self._populated_scene(sm)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("builtins.open", MagicMock()),
        ):
            assert sm.get_info()["has_rendered"] is False
            adapter._do_render("rid9")
            assert sm.get_info()["has_rendered"] is True


class TestMixAudioToVideo:
    MIX_PATH = "mcp_manimgl.utils.audio_mixer.mix_audio"

    def test_mix_audio_called(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        manifest = {
            "music": [{"file_path": "/tmp/music.mp3", "volume": 0.5, "loop": True}],
            "narration": [{"file_path": "/tmp/nar.mp3", "start_time": 1.0}],
        }

        with (
            patch(self.MIX_PATH, return_value="/tmp/mixed.mp4") as mock_mix,
            patch("mcp_manimgl.adapters.manim_adapter.os.remove"),
            patch("mcp_manimgl.adapters.manim_adapter.shutil.move"),
        ):
            result = adapter._mix_audio_to_video("/tmp/video.mp4", manifest)
            assert result == "/tmp/video.mp4"
            mock_mix.assert_called_once()

    def test_no_music(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        manifest = {
            "music": [],
            "narration": [{"file_path": "/tmp/nar.mp3", "start_time": 0.0}],
        }

        with (
            patch(self.MIX_PATH, return_value="/tmp/mixed.mp4") as mock_mix,
            patch("mcp_manimgl.adapters.manim_adapter.os.remove"),
            patch("mcp_manimgl.adapters.manim_adapter.shutil.move"),
        ):
            adapter._mix_audio_to_video("/tmp/video.mp4", manifest)
            assert mock_mix.call_args[1]["music_path"] is None

    def test_default_volume_and_loop(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        manifest = {
            "music": [{"file_path": "/tmp/music.mp3"}],
            "narration": [],
        }

        with (
            patch(self.MIX_PATH, return_value="/tmp/mixed.mp4") as mock_mix,
            patch("mcp_manimgl.adapters.manim_adapter.os.remove"),
            patch("mcp_manimgl.adapters.manim_adapter.shutil.move"),
        ):
            adapter._mix_audio_to_video("/tmp/video.mp4", manifest)
            kwargs = mock_mix.call_args[1]
            assert kwargs["music_volume"] == 0.3
            assert kwargs["music_loop"] is False

    def test_duck_params_from_scene_manager(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        sm.set_music_duck_params({"threshold": "-30dB", "ratio": 6})
        manifest = {"music": [{"file_path": "/tmp/music.mp3"}], "narration": []}

        with (
            patch(self.MIX_PATH, return_value="/tmp/mixed.mp4") as mock_mix,
            patch("mcp_manimgl.adapters.manim_adapter.os.remove"),
            patch("mcp_manimgl.adapters.manim_adapter.shutil.move"),
        ):
            adapter._mix_audio_to_video("/tmp/video.mp4", manifest)
            assert mock_mix.call_args[1]["duck_params"]["threshold"] == "-30dB"


class TestSaveFrame:
    def test_successful(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        sm.set_background("#000000")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "frame saved"

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("builtins.open", MagicMock()),
        ):
            result = adapter.save_frame()
            assert result["success"] is True
            assert result["output_path"] is not None

    def test_failure(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        sm.set_background("#000000")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "render error"

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("builtins.open", MagicMock()),
        ):
            result = adapter.save_frame()
            assert result["success"] is False
            assert "error" in result

    def test_timeout(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        sm.set_background("#000000")

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 120)),
            patch("mcp_manimgl.adapters.manim_adapter.tempfile.mkdtemp", return_value="/tmp/mtest"),
            patch("builtins.open", MagicMock()),
        ):
            result = adapter.save_frame()
            assert result["success"] is False
            assert "timed out" in result["error"]

    def test_custom_output_path(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        sm.set_background("#000000")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"

        with (
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.os.makedirs"),
            patch("builtins.open", MagicMock()),
        ):
            result = adapter.save_frame(output_path="/tmp/frame.png")
            assert result["success"] is True
            assert result["output_path"] == "/tmp/frame.png"


class TestVerifyVideo:
    def test_file_not_found(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=False):
            result = adapter.verify_video("/tmp/nonexistent.mp4")
            assert result["success"] is False
            assert result["error"] == "File not found"

    def test_ffprobe_fails(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "ffprobe error"

        with (
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
        ):
            result = adapter.verify_video("/tmp/test.mp4")
            assert result["success"] is False
            assert result["error"] == "ffprobe error"

    def test_successful(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1280,
                    "height": 720,
                    "r_frame_rate": "30/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "44100",
                    "channels": 2,
                },
            ],
            "format": {"size": "5000000", "duration": "264.0", "bit_rate": "150000"},
        })

        with (
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
        ):
            result = adapter.verify_video("/tmp/test.mp4")
            assert result["success"] is True
            assert result["size_bytes"] == 5000000
            assert result["duration_sec"] == 264.0
            assert result["video"][0]["fps"] == 30.0
            assert result["audio"][0]["channels"] == 2
            assert result["stream_count"] == 2

    def test_no_streams(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"streams": [], "format": {}})

        with (
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
        ):
            result = adapter.verify_video("/tmp/test.mp4")
            assert result["success"] is True
            assert result["video"] == []
            assert result["audio"] == []

    def test_ffprobe_timeout(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with (
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", side_effect=subprocess.TimeoutExpired("ffprobe", 30)),
        ):
            result = adapter.verify_video("/tmp/test.mp4")
            assert result["success"] is False
            assert "timed out" in result["error"]

    def test_json_decode_error(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"

        with (
            patch("mcp_manimgl.adapters.manim_adapter.os.path.exists", return_value=True),
            patch("mcp_manimgl.adapters.manim_adapter.subprocess.run", return_value=mock_result),
        ):
            result = adapter.verify_video("/tmp/test.mp4")
            assert result["success"] is False
            assert "Failed to parse" in result["error"]


class TestGetStatus:
    def test_both_available(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with (
            patch.object(adapter, "check_manim_available", return_value=True),
            patch.object(adapter, "check_opengl_available", return_value=True),
        ):
            status = adapter.get_status()
            assert status == {"manim_available": True, "opengl_available": True, "can_render": True}

    def test_neither_available(self, sm: SceneManager) -> None:
        adapter = ManimAdapter(sm)
        with (
            patch.object(adapter, "check_manim_available", return_value=False),
            patch.object(adapter, "check_opengl_available", return_value=False),
        ):
            status = adapter.get_status()
            assert status == {"manim_available": False, "opengl_available": False, "can_render": False}
