# my_masterschool_mcp_server.py — read every line; understand it before you run it.
#
# This is the Task 1 starter. You will NOT generate it with an agent — you read it,
# run it, and change it by hand. It exposes ONE tool over the stdio transport.
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import os
import sys

# A stdio server inherits the cwd of whatever LAUNCHES it (your shell, Claude Code, ...).
# Anchor to this file's own folder so "workspace/notes.txt" resolves the same way no matter
# who starts the server — without this, /mcp would resolve relative paths against your shell's cwd.
os.chdir(Path(__file__).resolve().parent)

mcp = FastMCP(
    "my_masterschool_mcp_server"
)  # the SERVER object the host will connect to


@mcp.tool()  # this decorator is what makes the function DISCOVERABLE
def read_workspace_file(path: str) -> str:
    """Read and return the contents of a file in the workspace."""
    sys.stderr.write(
        f"[tool call] read_workspace_file(path={path!r})\n"
    )  # so you SEE invocation
    sys.stderr.flush()
    with open(path) as f:  # deliberately naive — we exploit and fix this in Task 3
        return f.read()


if __name__ == "__main__":
    mcp.run()  # stdio transport by default (local subprocess)
