# my_masterschool_mcp_server.py (SOLUTION) — Task 2: the SAME server, now on the network.
#
# 〰️ Gist this code (in the real workshop the agent writes it for you). 🔍 Master the boundary.
#
# The ONLY meaningful change vs. Task 1 is the transport:
#   Task 1:  FastMCP("my_masterschool_mcp_server")          + mcp.run()
#   Task 2:  FastMCP(..., host="0.0.0.0")                   + mcp.run(transport="streamable-http")
#
# host="0.0.0.0" means "bind on every network interface" — anyone who can reach this machine
# on port 8000 can speak to this server. With a tunnel (Task 2 default) that's the PUBLIC INTERNET.
#
# SECURITY NOTE (this matters in Task 3): binding 0.0.0.0 ALSO turns OFF the MCP SDK's
# DNS-rebinding protection, so the server accepts requests with ANY Host header — which is
# exactly why a tunnel domain (e.g. https://xxxx.trycloudflare.com) can reach it. If you
# "harden" by switching to host="127.0.0.1", the SDK only allows localhost Host headers and
# your tunnel connection dies with `421 Misdirected Request`. Convenience vs. safety, in one line.
from mcp.server.fastmcp import FastMCP
import os
import socket
import sys

# host/port are configured on the FastMCP object; the path defaults to /mcp.
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


@mcp.tool()
def name() -> str:
    """Return the name of the student who owns this server."""
    sys.stderr.write("[tool call] name()\n")
    sys.stderr.flush()
    return "Ada Lovelace"  # <- put YOUR name here


@mcp.tool()
def list_workspace() -> list[str]:
    """List the filenames in the server's current working directory."""
    sys.stderr.write("[tool call] list_workspace()\n")
    sys.stderr.flush()
    return sorted(os.listdir("."))


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


if __name__ == "__main__":
    # Anchor to this folder so "the workspace" is well-defined regardless of where you launch from.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.stderr.write("=" * 70 + "\n")
    sys.stderr.write(
        "[server] streamable-http bound on 0.0.0.0:8000  (served at /mcp)\n"
    )
    sys.stderr.write(
        "[server] DEFAULT path — expose to the internet with a tunnel, e.g.:\n"
    )
    sys.stderr.write("[server]     cloudflared tunnel --url http://localhost:8000\n")
    sys.stderr.write("[server]   then share:  https://<random>.trycloudflare.com/mcp\n")
    sys.stderr.write(
        f"[server] LAN fallback (same WiFi):  http://{lan_ip()}:8000/mcp\n"
    )
    sys.stderr.write("[server] local test URL:            http://127.0.0.1:8000/mcp\n")
    sys.stderr.write("=" * 70 + "\n")
    sys.stderr.flush()
    mcp.run(transport="streamable-http")
