from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from mcp_manimgl.utils.dependency_checker import (
    _check_binary,
    _check_libfluidsynth,
    _check_soundfont,
    check_dep_status,
    check_non_python_deps,
    format_missing_deps,
)


class TestCheckBinary:
    def test_found(self) -> None:
        with patch("mcp_manimgl.utils.dependency_checker.shutil.which", return_value="/usr/bin/ffmpeg"):
            assert _check_binary("ffmpeg") is True

    def test_not_found(self) -> None:
        with patch("mcp_manimgl.utils.dependency_checker.shutil.which", return_value=None):
            assert _check_binary("ffmpeg") is False


class TestCheckLibFluidsynth:
    def test_found_in_ldconfig(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = "libfluidsynth.so.3 => /lib/x86_64-linux-gnu/libfluidsynth.so.3"
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run", return_value=mock_result
        ):
            assert _check_libfluidsynth() is True

    def test_not_found(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = "libfoo.so => /lib/libfoo.so"
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run", return_value=mock_result
        ):
            assert _check_libfluidsynth() is False

    def test_ldconfig_not_found(self) -> None:
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            assert _check_libfluidsynth() is False

    def test_subprocess_error(self) -> None:
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "cmd"),
        ):
            assert _check_libfluidsynth() is False

    def test_timeout_error(self) -> None:
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run",
            side_effect=subprocess.TimeoutExpired("cmd", 10),
        ):
            assert _check_libfluidsynth() is False

    def test_ldconfig_called_correctly(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch(
            "mcp_manimgl.utils.dependency_checker.subprocess.run", return_value=mock_result
        ) as mock_run:
            _check_libfluidsynth()
            mock_run.assert_called_with(
                ["ldconfig", "-p"], capture_output=True, text=True, timeout=10, check=False
            )


class TestCheckSoundfont:
    def test_no_dirs_exist(self) -> None:
        with patch("mcp_manimgl.utils.dependency_checker.os.path.isdir", return_value=False):
            assert _check_soundfont() is False

    def test_dir_exists_no_sf_files(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker.os.listdir", return_value=["readme.txt"]),
        ):
            assert _check_soundfont() is False

    def test_sf2_found(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker.os.listdir", return_value=["font.sf2"]),
        ):
            assert _check_soundfont() is True

    def test_sf3_found(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker.os.path.isdir", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker.os.listdir", return_value=["font.sf3"]),
        ):
            assert _check_soundfont() is True

    def test_second_dir_checked(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.dependency_checker.os.path.isdir",
                side_effect=[True, True],
            ),
            patch(
                "mcp_manimgl.utils.dependency_checker.os.listdir",
                side_effect=[["readme.txt"], ["font.sf2"]],
            ),
        ):
            assert _check_soundfont() is True

    def test_permission_error_continues(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.dependency_checker.os.path.isdir",
                side_effect=[True, True],
            ),
            patch(
                "mcp_manimgl.utils.dependency_checker.os.listdir",
                side_effect=[PermissionError, ["font.sf2"]],
            ),
        ):
            assert _check_soundfont() is True

    def test_all_dirs_permission_error(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker.os.path.isdir", return_value=True),
            patch(
                "mcp_manimgl.utils.dependency_checker.os.listdir",
                side_effect=PermissionError,
            ),
        ):
            assert _check_soundfont() is False


class TestCheckNonPythonDeps:
    def test_all_present(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker._check_binary", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=True),
        ):
            result = check_non_python_deps()
            assert result == []

    def test_all_missing(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker._check_binary", return_value=False),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=False),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=False),
        ):
            result = check_non_python_deps()
            assert len(result) == 4
            assert all("name" in d for d in result)
            assert all("purpose" in d for d in result)
            assert all("install_hint" in d for d in result)

    def test_missing_subset(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.dependency_checker._check_binary",
                side_effect=[True, False],
            ),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=False),
        ):
            result = check_non_python_deps()
            names = [d["name"] for d in result]
            assert "ffprobe" in names
            assert "SoundFont" in names
            assert "ffmpeg" not in names
            assert "libfluidsynth" not in names


class TestFormatMissingDeps:
    def test_empty_list(self) -> None:
        assert format_missing_deps([]) == ""

    def test_single_missing(self) -> None:
        result = format_missing_deps(
            [{"name": "ffmpeg", "purpose": "Audio mixing", "install_hint": "apt install ffmpeg"}]
        )
        assert "WARNING: Missing system dependencies" in result
        assert "ffmpeg" in result
        assert "Audio mixing" in result
        assert "apt install ffmpeg" in result

    def test_multiple_missing(self) -> None:
        deps = [
            {"name": "ffmpeg", "purpose": "Audio mixing", "install_hint": "apt install ffmpeg"},
            {"name": "SoundFont", "purpose": "MIDI", "install_hint": "apt install soundfont"},
        ]
        result = format_missing_deps(deps)
        assert result.count("Install:") == 2


class TestCheckDepStatus:
    def test_all_false(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker._check_binary", return_value=False),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=False),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=False),
        ):
            status = check_dep_status()
            assert all(v is False for v in status.values())
            assert set(status.keys()) == {"ffmpeg", "ffprobe", "libfluidsynth", "soundfont"}

    def test_all_true(self) -> None:
        with (
            patch("mcp_manimgl.utils.dependency_checker._check_binary", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=True),
        ):
            status = check_dep_status()
            assert all(v is True for v in status.values())

    def test_mixed(self) -> None:
        with (
            patch(
                "mcp_manimgl.utils.dependency_checker._check_binary",
                side_effect=[True, False],
            ),
            patch("mcp_manimgl.utils.dependency_checker._check_libfluidsynth", return_value=True),
            patch("mcp_manimgl.utils.dependency_checker._check_soundfont", return_value=False),
        ):
            status = check_dep_status()
            assert status == {
                "ffmpeg": True,
                "ffprobe": False,
                "libfluidsynth": True,
                "soundfont": False,
            }
