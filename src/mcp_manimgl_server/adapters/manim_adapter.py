from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_manimgl_server.core.scene_manager import SceneManager


class ManimAdapter:
    def __init__(self, scene_manager: SceneManager) -> None:
        self._scene_manager = scene_manager
        self._manim_available: bool | None = None

    def check_manim_available(self) -> bool:
        if self._manim_available is not None:
            return self._manim_available
        try:
            import manimlib  # noqa: F401

            self._manim_available = True
        except ImportError:
            self._manim_available = False
        return self._manim_available

    def check_opengl_available(self) -> bool:
        try:
            import moderngl

            moderngl.create_standalone_context()
            return True
        except Exception:
            return False

    def render_scene(
        self, output_path: str | None = None, fmt: str = "mp4"
    ) -> dict[str, Any]:
        script = self._scene_manager.generate_script()

        if output_path is None:
            output_dir = tempfile.mkdtemp(prefix="manimgl_")
            output_path = os.path.join(output_dir, f"output.{fmt}")
        else:
            output_dir = os.path.dirname(os.path.abspath(output_path))
            os.makedirs(output_dir, exist_ok=True)

        script_file = os.path.join(output_dir, "scene.py")
        with open(script_file, "w", encoding="utf-8") as fp:
            fp.write(script)

        env = os.environ.copy()
        env["MANIMGL_HEADLESS"] = "1"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "manimlib",
                    script_file,
                    "GeneratedScene",
                    "-w",
                    "-o",
                    output_path,
                    "-q",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                env=env,
            )

            if result.returncode == 0:
                self._scene_manager.mark_rendered()
                actual_output = output_path
                if not os.path.exists(actual_output):
                    for dirpath, _, filenames in os.walk(output_dir):
                        for fname in filenames:
                            if fname.endswith(f".{fmt}") or fname.endswith(".mp4"):
                                actual_output = os.path.join(dirpath, fname)
                                break

                return {
                    "success": True,
                    "output_path": actual_output
                    if os.path.exists(actual_output)
                    else None,
                    "script_path": script_file,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

            return {
                "success": False,
                "output_path": None,
                "script_path": script_file,
                "error": result.stderr,
                "stdout": result.stdout,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output_path": None,
                "script_path": script_file,
                "error": "Rendering timed out after 300 seconds",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "output_path": None,
                "script_path": script_file,
                "error": "manimgl binary not found. Is manimgl installed?",
            }

    def save_frame(self, output_path: str | None = None) -> dict[str, Any]:
        script = self._scene_manager.generate_script()

        if output_path is None:
            output_dir = tempfile.mkdtemp(prefix="manimgl_")
            output_path = os.path.join(output_dir, "frame.png")
        else:
            output_dir = os.path.dirname(os.path.abspath(output_path))
            os.makedirs(output_dir, exist_ok=True)

        script_file = os.path.join(output_dir, "scene.py")
        with open(script_file, "w", encoding="utf-8") as fp:
            fp.write(script)

        env = os.environ.copy()
        env["MANIMGL_HEADLESS"] = "1"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "manimlib",
                    script_file,
                    "GeneratedScene",
                    "-s",
                    "-o",
                    output_path,
                ],
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )

            if result.returncode == 0:
                self._scene_manager.mark_rendered()
                return {
                    "success": True,
                    "output_path": output_path if os.path.exists(output_path) else None,
                    "stdout": result.stdout,
                }

            return {
                "success": False,
                "output_path": None,
                "error": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output_path": None,
                "error": "Frame rendering timed out after 120 seconds",
            }

    def get_status(self) -> dict[str, bool]:
        return {
            "manim_available": self.check_manim_available(),
            "opengl_available": self.check_opengl_available(),
            "can_render": self.check_manim_available()
            and self.check_opengl_available(),
        }
