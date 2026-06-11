#!/usr/bin/env python
"""client_demo.py — a tiny MCP client that makes the discovery->invoke loop VISIBLE.

This stands in for Claude Code's built-in client so you can SEE, in your own terminal,
the exact steps the Master objective asks you to narrate WITHOUT NOTES:

    your prompt
      -> client asks the server "what tools do you have?"   (DISCOVERY)
      -> the agent picks one
      -> client invokes it with arguments                   (INVOKE)
      -> the server's function runs                          (you'll see its [tool call] line)
      -> the result returns to the agent's context          (RESULT)

Run it:
    python client_demo.py                     # uses mcp_server.py (1 tool)
    python client_demo.py mcp_server_extended.py   # uses your hand-edited server (2 tools)
"""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


def _params(tool) -> str:
    props = (tool.inputSchema or {}).get("properties", {})
    return "(" + ", ".join(props.keys()) + ")"


def _text(result) -> str:
    return "\n".join(
        c.text for c in result.content if getattr(c, "type", None) == "text"
    )


async def main(server_file: str) -> None:
    print(f"\n[client] STEP 1 — start the server as a local subprocess: {server_file}")
    # sys.executable == this venv's python, so the child also has `mcp` installed.
    params = StdioServerParameters(command=sys.executable, args=[server_file], cwd=HERE)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            print("[client] STEP 2 — handshake with the server (initialize)")
            await session.initialize()

            print("[client] STEP 3 — DISCOVERY: client asks 'what tools do you have?'")
            tools = await session.list_tools()
            for t in tools.tools:
                desc = (t.description or "").strip().splitlines()[0]
                print(f"           • {t.name}{_params(t)}  ::  {desc}")
            names = {t.name for t in tools.tools}

            print(
                "\n[client] STEP 4 — the agent PICKS read_workspace_file; client INVOKES it"
            )
            print("           args = {'path': 'workspace/README.md'}")
            result = await session.call_tool(
                "read_workspace_file", {"path": "workspace/README.md"}
            )
            print("\n[client] STEP 5 — RESULT returns to context:")
            print("           " + _text(result).replace("\n", "\n           "))

            if "list_workspace" in names:
                print(
                    "\n[client] BONUS — calling your HAND-ADDED tool: list_workspace()"
                )
                r2 = await session.call_tool("list_workspace", {})
                print("           files: " + ", ".join(_text(r2).split("\n")))

    print(
        "\n[client] done. The [tool call] lines above came from the SERVER process — that is"
    )
    print("         the live proof of invocation.\n")


if __name__ == "__main__":
    server = sys.argv[1] if len(sys.argv) > 1 else "mcp_server.py"
    asyncio.run(main(server))
