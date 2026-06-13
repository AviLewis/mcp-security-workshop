# my_masterschool_mcp_server.py (SOLUTION) — the result of the Task 1 "hand-edit" beat.
#
# Same as the Task 1 starter, but with TWO tools added BY HAND: name() and list_workspace().
# This is the "you just extended an MCP server yourself" moment. Notice the pattern:
# a plain Python function + the @mcp.tool() decorator + a docstring == a new tool the
# agent can discover and call. Nothing else changes.
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import sys
import os

# Set the current working directory to this file's folder so relative paths resolve.
os.chdir(Path(__file__).resolve().parent)

mcp = FastMCP("my_masterschool_mcp_server")


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read and return the contents of a file in the workspace."""
    sys.stderr.write(f"[tool call] read_workspace_file(path={path!r})\n")
    sys.stderr.flush()
    with open(path) as f:
        return f.read()


@mcp.tool()  # the simplest tool there is: a function + @mcp.tool() + a docstring
def name() -> str:
    """Return the name of the student who owns this server."""
    sys.stderr.write("[tool call] name()\n")
    sys.stderr.flush()
    return "Ada Lovelace"  # <- put YOUR name here


@mcp.tool()  # <-- the ONLY thing that makes list_workspace discoverable
def list_workspace() -> list[str]:
    """List the files in the workspace/ folder."""
    sys.stderr.write("[tool call] list_workspace()\n")
    sys.stderr.flush()
    # Scope to the workspace/ sandbox (not the server's own folder), and return
    # workspace/<name> so each result can be passed straight to read_workspace_file.
    return sorted(f"workspace/{n}" for n in os.listdir("workspace"))


if __name__ == "__main__":
    mcp.run()
