import sys

from mcp_manimgl.server import mcp


def main() -> int:
    mcp.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
