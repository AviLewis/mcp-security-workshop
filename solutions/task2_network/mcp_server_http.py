# mcp_server_http.py — Task 2: the SAME server, now on the network.
#
# 〰️ Gist this code (in the real workshop the agent writes it for you). 🔍 Master the boundary.
#
# The ONLY meaningful change vs. Task 1 is the transport:
#   Task 1:  FastMCP("my-server")            + mcp.run()
#   Task 2:  FastMCP(..., host="0.0.0.0")    + mcp.run(transport="streamable-http")
#
# host="0.0.0.0" means "bind on every network interface" — i.e. anyone who can reach
# this machine on port 8000 can now speak to this server. That single line moves you
# from "local subprocess only my agent can spawn" to "a web service on the WiFi."
from mcp.server.fastmcp import FastMCP
import os
import socket
import sys

# host/port are configured on the FastMCP object; the path defaults to /mcp.
mcp = FastMCP("my-server", host="0.0.0.0", port=8000)


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
    ip = lan_ip()
    sys.stderr.write("=" * 64 + "\n")
    sys.stderr.write(f"[server] streamable-http bound on 0.0.0.0:8000\n")
    sys.stderr.write(f"[server] a teammate on the same WiFi connects with:\n")
    sys.stderr.write(
        f"[server]   claude mcp add --transport http my-box http://{ip}:8000/mcp\n"
    )
    sys.stderr.write(f"[server] local URL for testing: http://127.0.0.1:8000/mcp\n")
    sys.stderr.write("=" * 64 + "\n")
    sys.stderr.flush()
    mcp.run(transport="streamable-http")  # served at http://<host>:8000/mcp
