import argparse
import multiprocessing
import os
import sys

from mcp_manimgl import MCP_MANIMGL_WORKDIR


def _run(args: argparse.Namespace) -> None:
    """Start the MCP server (runs in subprocess when --reload is active)."""
    from mcp_manimgl.core import SceneManager
    from mcp_manimgl.core.session_recorder import SessionRecorder
    from mcp_manimgl.server import build_server

    if args.session_dir is None:
        args.session_dir = os.path.join(MCP_MANIMGL_WORKDIR, "sessions")
    scene_manager = SceneManager()
    recorder = SessionRecorder(output_dir=args.session_dir)
    server = build_server(scene_manager=scene_manager, recorder=recorder)

    if args.resume_from_json:
        from mcp_manimgl.core.session_loader import load_session

        load_session(scene_manager, args.resume_from_json)

    server.run()


def main() -> int:
    parser = argparse.ArgumentParser(description="mcp-manimgl MCP server")
    parser.add_argument(
        "--resume-from-json",
        type=str,
        default=None,
        help="Path to a session JSON file to resume from",
    )
    parser.add_argument(
        "--session-dir",
        type=str,
        default=None,
        help="Directory to store session recordings (default: $MCP_MANIMGL_WORKDIR/sessions, which is /tmp/mcp_manimgl/sessions)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="Auto-reload server when source files change (requires watchfiles)",
    )
    args = parser.parse_args()

    if args.reload:
        _run_with_reload(args)
    else:
        _run(args)
    return 0


def _run_with_reload(args: argparse.Namespace) -> None:
    """Run the server with auto-reload using watchfiles."""
    try:
        from watchfiles import watch
    except ImportError:
        print(
            "error: --reload requires watchfiles. Install with: pip install watchfiles",
            file=sys.stderr,
        )
        sys.exit(1)

    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if not os.path.isdir(src_dir):
        src_dir = os.path.abspath(os.path.dirname(__file__))

    proc = multiprocessing.Process(target=_run, args=(args,), daemon=True)
    proc.start()
    print(f"server started (pid={proc.pid}), watching {src_dir}", file=sys.stderr)

    try:
        for changes in watch(src_dir):
            for change, path in changes:
                if path.endswith(".py"):
                    print(
                        f"change detected: {os.path.relpath(path, src_dir)}, restarting...",
                        file=sys.stderr,
                    )
                    break
            proc.terminate()
            proc.join()
            proc = multiprocessing.Process(target=_run, args=(args,), daemon=True)
            proc.start()
            print(f"server restarted (pid={proc.pid})", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        if proc.is_alive():
            proc.terminate()
            proc.join()


if __name__ == "__main__":
    sys.exit(main())
