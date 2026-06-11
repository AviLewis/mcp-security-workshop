# ⛔ Solutions — spoilers ahead

This folder is the **complete, finished, runnable** version of all three tasks. It exists so you
can check your work or recover if you're stuck — **try each task yourself first.** Reading the
hardened server before you've attacked the vulnerable one skips the whole point of the CTF.

Each task folder is self-contained and runnable (with the venv from the repo root activated):

```bash
# from repo root:  source .venv/bin/activate

# Task 1 — see the discovery→invoke loop, incl. the hand-added list_workspace tool
cd solutions/task1_meet_mcp && python client_demo.py mcp_server_extended.py

# Task 2 — HTTP transport + a "peer" client reading your files (run in two terminals)
cd solutions/task2_network && python mcp_server_http.py          # terminal A
cd solutions/task2_network && python client_http_demo.py         # terminal B, then Ctrl-C the server

# Task 3 — attack, harden, prove
cd solutions/task3_security
python attack_demo.py            # vulnerable: flag1 LEAKED, flag2 PWNED, flag3 content returned
python attack_demo.py hardened   # hardened:   flag1 & flag2 DEFENDED
python test_hardening.py         # 8/8 checks pass
```

## What each solution file teaches
- `task1_meet_mcp/mcp_server_extended.py` — the hand-edit answer (`list_workspace` via one `@mcp.tool()`).
- `task2_network/mcp_server_http.py` — the transport swap: `host="0.0.0.0"` + `transport="streamable-http"`.
- `task3_security/ctf_server_hardened.py` — the three defenses: path canonicalization +
  `is_relative_to`, no-shell argument arrays (`wc -l -- <path>`), and a human-in-the-loop gate on
  side-effectful actions. Prompt injection (flag 3) is intentionally **not** fully fixable here.
- `task3_security/attack_demo.py` / `test_hardening.py` — the attack harness and the proof tests.
