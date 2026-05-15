from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from mcp_manimgl.__main__ import _run, _run_with_reload, main


class TestRun:
    def test_run_defaults(self) -> None:
        args = MagicMock()
        args.session_dir = None
        args.resume_from_json = None

        with (
            patch("mcp_manimgl.server.build_server") as mock_build,
            patch("mcp_manimgl.core.scene_manager.SceneManager"),
            patch("mcp_manimgl.core.session_recorder.SessionRecorder"),
        ):
            _run(args)
            mock_build.assert_called_once()

    def test_run_with_session_dir(self) -> None:
        args = MagicMock()
        args.session_dir = "/custom/sessions"
        args.resume_from_json = None

        with (
            patch("mcp_manimgl.server.build_server") as mock_build,
            patch("mcp_manimgl.core.scene_manager.SceneManager"),
            patch("mcp_manimgl.core.session_recorder.SessionRecorder"),
        ):
            _run(args)
            mock_build.assert_called_once()

    def test_run_with_resume(self) -> None:
        args = MagicMock()
        args.session_dir = None
        args.resume_from_json = "/path/to/session.json"

        with (
            patch("mcp_manimgl.server.build_server") as mock_build,
            patch("mcp_manimgl.core.scene_manager.SceneManager"),
            patch("mcp_manimgl.core.session_recorder.SessionRecorder"),
            patch("mcp_manimgl.core.session_loader.load_session") as mock_load,
        ):
            _run(args)
            mock_load.assert_called_once()
            mock_build.assert_called_once()

    def test_run_server_called(self) -> None:
        args = MagicMock()
        args.session_dir = None
        args.resume_from_json = None

        mock_server = MagicMock()
        with (
            patch("mcp_manimgl.server.build_server", return_value=mock_server) as mock_build,
            patch("mcp_manimgl.core.scene_manager.SceneManager"),
            patch("mcp_manimgl.core.session_recorder.SessionRecorder"),
        ):
            _run(args)
            mock_server.run.assert_called_once()


class TestRunWithReload:
    def test_watchfiles_not_installed(self) -> None:
        args = MagicMock()
        with (
            patch.dict("sys.modules", {"watchfiles": None}),
            pytest.raises(SystemExit) as exc,
        ):
            _run_with_reload(args)
            assert exc.value.code == 1

    def test_watchfiles_not_installed_stderr_message(self) -> None:
        args = MagicMock()
        with (
            patch.dict("sys.modules", {"watchfiles": None}),
            pytest.raises(SystemExit),
            patch("mcp_manimgl.__main__.sys.stderr") as mock_stderr,
        ):
            _run_with_reload(args)
            mock_stderr.write.assert_called()

    def test_reload_loop_and_keyboard_interrupt(self) -> None:
        args = MagicMock()
        args.resume_from_json = None
        args.session_dir = None

        class KiIterator:
            def __iter__(self) -> KiIterator:
                return self

            def __next__(self) -> list:
                raise KeyboardInterrupt

        mock_watch_module = MagicMock()
        mock_watch_module.watch.return_value = KiIterator()

        with (
            patch.dict("sys.modules", {"watchfiles": mock_watch_module}),
            patch("mcp_manimgl.__main__._run"),
            patch("mcp_manimgl.__main__.multiprocessing.Process") as mock_proc,
        ):
            mock_process = MagicMock()
            mock_proc.return_value = mock_process

            _run_with_reload(args)
            mock_proc.assert_called()
            mock_process.start.assert_called()
            mock_process.terminate.assert_called_once()
            mock_process.join.assert_called()

    def test_reload_watches_py_files(self) -> None:
        args = MagicMock()
        args.resume_from_json = None
        args.session_dir = None

        class ChangeOnce:
            def __init__(self) -> None:
                self._done = False

            def __iter__(self) -> ChangeOnce:
                return self

            def __next__(self) -> list:
                if not self._done:
                    self._done = True
                    return [("modified", "/path/to/file.py")]
                raise StopIteration

        mock_watch_module = MagicMock()
        mock_watch_module.watch.return_value = ChangeOnce()

        mock_process = MagicMock()
        with (
            patch.dict("sys.modules", {"watchfiles": mock_watch_module}),
            patch("mcp_manimgl.__main__._run"),
            patch("mcp_manimgl.__main__.multiprocessing.Process", return_value=mock_process),
        ):
            _run_with_reload(args)
            assert mock_process.terminate.call_count == 2


class TestMainFunction:
    def test_main_no_args(self) -> None:
        with (
            patch("mcp_manimgl.__main__._run") as mock_run,
            patch("sys.argv", ["mcp-manimgl"]),
        ):
            result = main()
            assert result == 0
            mock_run.assert_called_once()

    def test_main_with_resume(self) -> None:
        with (
            patch("mcp_manimgl.__main__._run") as mock_run,
            patch("sys.argv", ["mcp-manimgl", "--resume-from-json", "/tmp/session.json"]),
        ):
            result = main()
            assert result == 0
            args = mock_run.call_args[0][0]
            assert args.resume_from_json == "/tmp/session.json"

    def test_main_with_session_dir(self) -> None:
        with (
            patch("mcp_manimgl.__main__._run") as mock_run,
            patch("sys.argv", ["mcp-manimgl", "--session-dir", "/tmp/mysessions"]),
        ):
            result = main()
            assert result == 0
            args = mock_run.call_args[0][0]
            assert args.session_dir == "/tmp/mysessions"

    def test_main_with_reload(self) -> None:
        with (
            patch("mcp_manimgl.__main__._run_with_reload") as mock_reload,
            patch("sys.argv", ["mcp-manimgl", "--reload"]),
        ):
            result = main()
            assert result == 0
            mock_reload.assert_called_once()

    def test_main_reload_flag_not_passed_to_run(self) -> None:
        with (
            patch("mcp_manimgl.__main__._run") as mock_run,
            patch("sys.argv", ["mcp-manimgl"]),
        ):
            main()
            args = mock_run.call_args[0][0]
            assert args.reload is False
