import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from mcp_manimgl.core.session_recorder import SessionRecorder, record_tool_call


class TestSessionRecorder:
    def test_init_default_path(self) -> None:
        with patch("mcp_manimgl.core.session_recorder.os.makedirs"):
            sr = SessionRecorder(output_dir="/tmp/mcp_sessions")
            assert "session_" in sr.path
            assert sr.path.endswith(".json")
            assert sr.path.startswith("/tmp/mcp_sessions/")

    def test_init_custom_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sr = SessionRecorder(output_dir=td)
            assert sr.path.startswith(td)
            assert sr.path.endswith(".json")

    def test_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sr = SessionRecorder(output_dir=td)
            sr.record("add_circle", {"radius": 1.0, "color": "#FF0000"})
            assert len(sr._commands) == 1
            assert sr._commands[0]["tool"] == "add_circle"
            assert sr._commands[0]["arguments"]["radius"] == 1.0
            with open(sr.path) as f:
                saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["tool"] == "add_circle"

    def test_record_multiple(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sr = SessionRecorder(output_dir=td)
            sr.record("add_circle", {"radius": 1.0})
            sr.record("add_wait", {"duration": 2.0})
            sr.record("animate_fade_in", {"mobject_id": "m1"})
            assert len(sr._commands) == 3
            with open(sr.path) as f:
                saved = json.load(f)
            assert len(saved) == 3
            assert saved[1]["tool"] == "add_wait"

    def test_record_persists_to_disk_each_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sr = SessionRecorder(output_dir=td)
            for i in range(5):
                sr.record(f"tool_{i}", {"idx": i})
            with open(sr.path) as f:
                saved = json.load(f)
            assert len(saved) == 5

    def test_record_write_failure_does_not_raise(self) -> None:
        sr = SessionRecorder(output_dir="/tmp")
        sr._path = "/nonexistent/dir/sesh.json"
        sr.record("add_circle", {"r": 1})
        assert len(sr._commands) == 1

    def test_path_property(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sr = SessionRecorder(output_dir=td)
            assert sr.path == sr._path


class TestRecordToolCall:
    def test_records_caller_params(self) -> None:
        mock_recorder = MagicMock(spec=SessionRecorder)

        def fake_tool(radius: float = 1.0, color: str = "#FFF") -> None:
            record_tool_call(mock_recorder, "add_circle")

        fake_tool(2.0, "#000")
        mock_recorder.record.assert_called_once_with("add_circle", {"radius": 2.0, "color": "#000"})

    def test_records_default_params(self) -> None:
        mock_recorder = MagicMock(spec=SessionRecorder)

        def fake_tool(radius: float = 1.0, color: str = "#FFF") -> None:
            record_tool_call(mock_recorder, "add_circle")

        fake_tool()
        mock_recorder.record.assert_called_once_with(
            "add_circle", {"radius": 1.0, "color": "#FFF"}
        )

    def test_handles_kwargs(self) -> None:
        mock_recorder = MagicMock(spec=SessionRecorder)

        def fake_tool(**kwargs: float | str) -> None:
            record_tool_call(mock_recorder, "some_tool")

        fake_tool(x=1, y="hello")
        mock_recorder.record.assert_called_once()
        args = mock_recorder.record.call_args[0][1]
        assert args["x"] == 1
        assert args["y"] == "hello"

    def test_no_frame_does_not_crash(self) -> None:
        mock_recorder = MagicMock(spec=SessionRecorder)
        with patch("mcp_manimgl.core.session_recorder.inspect.currentframe", return_value=None):
            record_tool_call(mock_recorder, "tool")
            mock_recorder.record.assert_not_called()

    def test_no_caller_frame_does_not_crash(self) -> None:
        mock_recorder = MagicMock(spec=SessionRecorder)
        frame = MagicMock()
        frame.f_back = None
        with patch("mcp_manimgl.core.session_recorder.inspect.currentframe", return_value=frame):
            record_tool_call(mock_recorder, "tool")
            mock_recorder.record.assert_not_called()
