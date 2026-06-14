# my_masterschool_mcp_server.py (SOLUTION) — your ONE reusable server.
#
# You don't copy this between tasks — you REUSE it. It's the same file throughout:
#   Task 1 (stdio):  FastMCP("my_masterschool_mcp_server")       + mcp.run()
#   Task 2 (http):   FastMCP(..., host="0.0.0.0", port=8000)     + mcp.run(transport="streamable-http")
# Everything else — read_workspace_file, name, list_workspace — is identical. To keep ONE runnable
# file for both tasks, this answer key picks the transport at launch: stdio by default (Task 1), or
# streamable-HTTP when you pass `--http` (Task 2). Your own server just hardcodes one at a time.
#
# SECURITY NOTE (this matters in Task 3): binding 0.0.0.0 ALSO turns OFF the MCP SDK's
# DNS-rebinding protection, so the server accepts requests with ANY Host header — which is exactly
# why a tunnel domain (e.g. https://xxxx.trycloudflare.com) can reach it. Switch to
# host="127.0.0.1" and the SDK only allows localhost Host headers, so a tunnel dies with
# `421 Misdirected Request`. Convenience vs. safety, in one line.
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import os
import socket
import sys

# Anchor to this file's folder so "the workspace" is well-defined however the server is launched.
# (In Task 1, Claude Code's stdio launch inherits YOUR shell's cwd — not this folder — so chdir here.)
os.chdir(Path(__file__).resolve().parent)

# Task 2: host/port live on the FastMCP object; the path defaults to /mcp.
# (Task 1 was just FastMCP("my_masterschool_mcp_server") — no host/port.)
mcp = FastMCP("my_masterschool_mcp_server", host="0.0.0.0", port=8000)


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read and return the contents of a file in the workspace."""
    sys.stderr.write(f"[tool call] read_workspace_file(path={path!r})\n")
    sys.stderr.flush()
    with open(
        path
    ) as f:  # still naive — the network just made naivety far more dangerous
        return f.read()


@mcp.tool()  # the simplest tool there is: a function + @mcp.tool() + a docstring
def name() -> str:
    """Return the name of the student who owns this server."""
    sys.stderr.write("[tool call] name()\n")
    sys.stderr.flush()
    return "Guy Cohen"  # <- put YOUR name here


@mcp.tool()
def list_workspace() -> list[str]:
    """List the files in the workspace/ folder."""
    sys.stderr.write("[tool call] list_workspace()\n")
    sys.stderr.flush()
    # Scope to the workspace/ sandbox so the planted fake.env stays HIDDEN from this listing —
    # yet read_workspace_file("fake.env") still reads it. That gap IS the Task 2 boundary.
    return sorted(f"workspace/{n}" for n in os.listdir("workspace"))


def lan_ip() -> str:
    """Best-effort LAN IP (opens a UDP socket but sends nothing)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def print_ready_banner(transport: str) -> None:
    """Print a 'server is up' banner tailored to the transport. Always prints.

    Always write to stderr, never stdout: in stdio mode stdout carries the JSON-RPC
    protocol, so a stray print() there would corrupt it. stderr is safe.
    """
    sys.stderr.write("\n" + "=" * 70 + "\n")
    if transport == "stdio":
        sys.stderr.write("✅ MCP server READY — stdio transport (local)\n")
        sys.stderr.write(
            "   Claude Code talks to this over stdin/stdout — there is no URL, and if\n"
        )
        sys.stderr.write(
            "   you ran it by hand it just waits silently. That's correct for stdio.\n"
        )
    else:
        sys.stderr.write(
            "✅ MCP server READY — streamable-http on 0.0.0.0:8000  (served at /mcp)\n"
        )
        sys.stderr.write("   local:       http://127.0.0.1:8000/mcp\n")
        sys.stderr.write(f"   same Wi-Fi:  http://{lan_ip()}:8000/mcp\n")
        sys.stderr.write(
            "   public:      run a tunnel, e.g.  cloudflared tunnel --url http://localhost:8000\n"
        )
        sys.stderr.write("   leave this terminal running · Ctrl-C to stop\n")
    sys.stderr.write("=" * 70 + "\n\n")
    sys.stderr.flush()


if __name__ == "__main__":
    # Task 1 = stdio (default). Task 2 = streamable-HTTP: run with `--http`.
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    print_ready_banner(transport)
    mcp.run(transport=transport)
