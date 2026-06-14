# my_masterschool_mcp_server.py — read every line; understand it before you run it.
#
# This is the Task 1 starter. You will NOT generate it with an agent — you read it,
# run it, and change it. It exposes ONE tool over the stdio transport.
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import os
import socket
import sys

# Set the current working directory to this file's folder so relative paths resolve.
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

    Always write to stderr, never stdout — in stdio mode stdout carries the JSON-RPC protocol,
    so a stray print() there would corrupt it. stderr is safe (Claude Code shows it in MCP logs).
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
        sys.stderr.write("   leave this terminal running · Ctrl-C to stop\n")
    sys.stderr.write("=" * 70 + "\n\n")
    sys.stderr.flush()


if __name__ == "__main__":
    # Task 1: stdio. Task 2: change transport to "streamable-http" AND add
    #         host="0.0.0.0", port=8000 to the FastMCP(...) call above.
    # The banner adapts to whichever transport you pick, and always prints.
    transport = "stdio"
    print_ready_banner(transport)
    mcp.run(transport=transport)
