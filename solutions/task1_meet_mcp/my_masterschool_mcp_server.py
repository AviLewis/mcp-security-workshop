# my_masterschool_mcp_server.py (SOLUTION) — the result of the Task 1 "hand-edit" beat.
#
# Same as the Task 1 starter, but with ONE tool added BY HAND: list_workspace().
# This is the "you just extended an MCP server yourself" moment. Notice the pattern:
# a plain Python function + the @mcp.tool() decorator + a docstring == a new tool the
# agent can discover and call. Nothing else changes.
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import sys
import os

# Anchor to this file's folder so relative paths work no matter who launches the server
# (your shell, Claude Code's /mcp, ...). A stdio server otherwise inherits the launcher's cwd.
os.chdir(Path(__file__).resolve().parent)

mcp = FastMCP("my_masterschool_mcp_server")


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read and return the contents of a file in the workspace."""
    sys.stderr.write(f"[tool call] read_workspace_file(path={path!r})\n")
    sys.stderr.flush()
    with open(path) as f:
        return f.read()


@mcp.tool()  # <-- the ONLY thing that makes list_workspace discoverable
def list_workspace() -> list[str]:
    """List the filenames in the server's current working directory."""
    sys.stderr.write("[tool call] list_workspace()\n")
    sys.stderr.flush()
    return sorted(os.listdir("."))


if __name__ == "__main__":
    mcp.run()
