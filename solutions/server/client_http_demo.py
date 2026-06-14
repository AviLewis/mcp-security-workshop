#!/usr/bin/env python
"""client_http_demo.py — Task 2: play the role of a PEER's agent over the network.

This connects to a streamable-HTTP MCP server (yours, or a partner's) and:
  1. discovers the tools,
  2. reads a normal file,
  3. reads the planted example.env — the REVEAL: the server has no idea what
     "your workspace" means; it reads whatever the server PROCESS can read.

Start the server first (in another terminal):
    python my_masterschool_mcp_server.py

Then run this:
    python client_http_demo.py                              # talks to localhost
    python client_http_demo.py https://<rand>.trycloudflare.com/mcp   # talks to a tunneled box
    python client_http_demo.py http://<PARTNER-LAN-IP>:8000/mcp       # LAN fallback
"""
import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _text(result) -> str:
    return "\n".join(
        c.text for c in result.content if getattr(c, "type", None) == "text"
    )


async def main(url: str) -> None:
    print(f"\n[peer-client] connecting to {url}")
    print("[peer-client] (this is what a teammate's agent does to YOUR machine)\n")
    async with streamablehttp_client(url) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("[peer-client] discovered tools:", [t.name for t in tools.tools])

            print("\n[peer-client] reading a normal file: workspace/README.md")
            r = await session.call_tool(
                "read_workspace_file", {"path": "workspace/README.md"}
            )
            print("   " + _text(r).replace("\n", "\n   "))

            print(
                "\n[peer-client] THE REVEAL — asking for the planted secret: example.env"
            )
            r2 = await session.call_tool("read_workspace_file", {"path": "example.env"})
            print("   " + _text(r2).replace("\n", "\n   "))

    print(
        "\n[boundary] You just read a file on another machine. The boundary you crossed:"
    )
    print(
        "           the tool reads with the SERVER PROCESS's permissions — not 'the workspace'."
    )
    print(
        "           Anything that process can open is reachable by a stranger's agent.\n"
    )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/mcp"
    asyncio.run(main(target))
