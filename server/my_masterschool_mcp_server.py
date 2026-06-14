import os
import socket
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

os.chdir(Path(__file__).resolve().parent)

mcp = FastMCP("my_masterschool_mcp_server")


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read and return the contents of a file in the workspace."""
    sys.stderr.write(f"[tool call] read_workspace_file(path={path!r})\n")
    sys.stderr.flush()
    with open(path) as f:
        return f.read()


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def print_ready_banner(transport: str) -> None:
    sys.stderr.write("\n" + "=" * 70 + "\n")
    if transport == "stdio":
        sys.stderr.write("✅ MCP server READY — stdio transport (local)\n")
        sys.stderr.write(
            "   Claude Code talks to this over stdin/stdout; there is no URL.\n"
        )
    else:
        ip = lan_ip()
        sys.stderr.write(
            "✅ MCP server READY — streamable-http on 0.0.0.0:8000  (served at /mcp)\n"
        )
        sys.stderr.write("   local URL:   http://127.0.0.1:8000/mcp\n")
        sys.stderr.write(f"   Wi-Fi URL:   http://{ip}:8000/mcp\n")
        sys.stderr.write("   ── connect a client (run in ANOTHER terminal) ──\n")
        sys.stderr.write(
            "   on THIS machine:   claude mcp add --transport http partner-box http://127.0.0.1:8000/mcp\n"
        )
        sys.stderr.write(
            f"   from same Wi-Fi:   claude mcp add --transport http partner-box http://{ip}:8000/mcp\n"
        )
        sys.stderr.write("   leave this terminal running · Ctrl-C to stop\n")
    sys.stderr.write("=" * 70 + "\n\n")
    sys.stderr.flush()


if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    print_ready_banner(transport)
    mcp.run(transport=transport)
