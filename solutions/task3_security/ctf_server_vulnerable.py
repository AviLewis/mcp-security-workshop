# ctf_server_vulnerable.py — DELIBERATELY INSECURE. Runs ONLY in the CTF sandbox.
#
# ⚠️  Safety box: fake secrets only. The path-traversal target (FLAG.txt) is a planted
#     file just OUTSIDE the workspace — not a real system file. Command-injection proof
#     is harmless (whoami). Stop this server when the CTF ends.
#
# This server has the two server-fixable holes from the lecture, plus it can serve a
# file whose CONTENTS carry a prompt-injection payload (the not-fully-fixable one):
#   VULN 1  read_workspace_file  -> path traversal   (hostile INPUT)
#   VULN 2  count_lines          -> command injection (hostile INPUT)
#   VULN 3  meeting_notes.txt    -> indirect prompt injection (hostile OUTPUT)
from mcp.server.fastmcp import FastMCP
import os
import subprocess
import sys

mcp = FastMCP("ctf-vulnerable", host="0.0.0.0", port=8001)


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read a file from the workspace."""
    sys.stderr.write(f"[tool call] read_workspace_file(path={path!r})\n")
    sys.stderr.flush()
    with open(
        path
    ) as f:  # VULN 1: no validation -> '../FLAG.txt' escapes the workspace
        return f.read()


@mcp.tool()
def count_lines(filename: str) -> str:
    """Count the lines in a workspace file."""
    sys.stderr.write(f"[tool call] count_lines(filename={filename!r})\n")
    sys.stderr.flush()
    # VULN 2: shell=True with interpolated input -> 'notes.txt; whoami' runs whoami too.
    out = subprocess.run(
        f"wc -l {filename}", shell=True, capture_output=True, text=True
    )
    return (out.stdout or "") + (out.stderr or "")


if __name__ == "__main__":
    # Anchor to ctf-workspace so "the workspace" is well-defined and FLAG.txt sits one level up.
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctf-workspace"))
    transport = (
        "streamable-http" if (len(sys.argv) > 1 and sys.argv[1] == "http") else "stdio"
    )
    if transport == "streamable-http":
        sys.stderr.write("[server] CTF VULNERABLE server on http://0.0.0.0:8001/mcp\n")
        sys.stderr.flush()
    mcp.run(transport=transport)
