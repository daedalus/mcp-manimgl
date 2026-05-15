import os

__version__ = "0.1.1"
__all__: list[str] = []

MCP_MANIMGL_WORKDIR = os.environ.get(
    "MCP_MANIMGL_WORKDIR",
    "/tmp/mcp_manimgl",
)
