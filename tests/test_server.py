from unittest.mock import patch, MagicMock

from mcp_manimgl.core import SceneManager
from mcp_manimgl.core.session_recorder import SessionRecorder


class TestBuildServer:
    def test_build_server_returns_fastmcp(self) -> None:
        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=[]),
            patch("mcp_manimgl.server.check_dep_status", return_value="ok"),
            patch("mcp_manimgl.server.format_missing_deps"),
            patch("mcp_manimgl.server.register_scene_tools"),
            patch("mcp_manimgl.server.register_mobject_tools"),
            patch("mcp_manimgl.server.register_animation_tools"),
            patch("mcp_manimgl.server.register_rendering_tools"),
            patch("mcp_manimgl.server.register_audio_tools"),
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            sm = SceneManager()
            result = build_server(scene_manager=sm)

            assert result is mock_fastmcp
            mock_fastmcp_cls.assert_called_once_with("mcp-manimgl")

    def test_build_server_default_args(self) -> None:
        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=[]),
            patch("mcp_manimgl.server.check_dep_status", return_value="ok"),
            patch("mcp_manimgl.server.format_missing_deps"),
            patch("mcp_manimgl.server.register_scene_tools"),
            patch("mcp_manimgl.server.register_mobject_tools"),
            patch("mcp_manimgl.server.register_animation_tools"),
            patch("mcp_manimgl.server.register_rendering_tools"),
            patch("mcp_manimgl.server.register_audio_tools"),
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            result = build_server()
            assert result is mock_fastmcp

    def test_build_server_registers_all_tools(self) -> None:
        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=[]),
            patch("mcp_manimgl.server.check_dep_status", return_value="ok"),
            patch("mcp_manimgl.server.format_missing_deps"),
            patch("mcp_manimgl.server.register_scene_tools") as mock_scene,
            patch("mcp_manimgl.server.register_mobject_tools") as mock_mobj,
            patch("mcp_manimgl.server.register_animation_tools") as mock_anim,
            patch("mcp_manimgl.server.register_rendering_tools") as mock_render,
            patch("mcp_manimgl.server.register_audio_tools") as mock_audio,
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            sm = SceneManager()
            result = build_server(scene_manager=sm)

            mock_scene.assert_called_once()
            mock_mobj.assert_called_once()
            mock_anim.assert_called_once()
            mock_render.assert_called_once()
            mock_audio.assert_called_once()

    def test_build_server_resource_registered(self) -> None:
        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=["ffmpeg"]),
            patch("mcp_manimgl.server.check_dep_status", return_value="partial"),
            patch("mcp_manimgl.server.format_missing_deps"),
            patch("mcp_manimgl.server.register_scene_tools"),
            patch("mcp_manimgl.server.register_mobject_tools"),
            patch("mcp_manimgl.server.register_animation_tools"),
            patch("mcp_manimgl.server.register_rendering_tools"),
            patch("mcp_manimgl.server.register_audio_tools"),
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            result = build_server()
            mock_fastmcp.resource.assert_called_once_with("mcp-manimgl://info")

    def test_build_server_reports_missing_deps(self) -> None:
        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=["ffmpeg"]),
            patch("mcp_manimgl.server.check_dep_status"),
            patch("mcp_manimgl.server.format_missing_deps", return_value="Missing: ffmpeg") as mock_fmt,
            patch("mcp_manimgl.server.register_scene_tools"),
            patch("mcp_manimgl.server.register_mobject_tools"),
            patch("mcp_manimgl.server.register_animation_tools"),
            patch("mcp_manimgl.server.register_rendering_tools"),
            patch("mcp_manimgl.server.register_audio_tools"),
            patch("mcp_manimgl.server.print") as mock_print,
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            build_server()
            mock_fmt.assert_called_once_with(["ffmpeg"])
            mock_print.assert_called_once()

    def test_info_resource_handler(self) -> None:
        captured_handler: dict[str, object] = {}

        def fake_resource(uri: str) -> object:
            def decorator(f: object) -> object:
                captured_handler["handler"] = f
                captured_handler["uri"] = uri
                return f
            return decorator

        with (
            patch("mcp_manimgl.server.FastMCP") as mock_fastmcp_cls,
            patch("mcp_manimgl.server.ManimAdapter"),
            patch("mcp_manimgl.server.check_non_python_deps", return_value=[]),
            patch("mcp_manimgl.server.check_dep_status", return_value="ok"),
            patch("mcp_manimgl.server.format_missing_deps"),
            patch("mcp_manimgl.server.register_scene_tools"),
            patch("mcp_manimgl.server.register_mobject_tools"),
            patch("mcp_manimgl.server.register_animation_tools"),
            patch("mcp_manimgl.server.register_rendering_tools"),
            patch("mcp_manimgl.server.register_audio_tools"),
        ):
            mock_fastmcp = MagicMock()
            mock_fastmcp.resource.side_effect = fake_resource
            mock_fastmcp_cls.return_value = mock_fastmcp

            from mcp_manimgl.server import build_server

            build_server()
            handler = captured_handler.get("handler")
            assert handler is not None
            result = handler()
            assert result["server"] == "mcp-manimgl"
            assert "version" in result
