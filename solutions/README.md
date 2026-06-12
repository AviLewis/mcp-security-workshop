# ⛔ Solutions — spoilers ahead

This folder is the **complete, finished, runnable** version of all three tasks. It exists so you
can check your work or recover if you're stuck — **try each task yourself first.** Reading the
hardened server before you've attacked the vulnerable one skips the whole point of the CTF.

Each task folder is self-contained and runnable (with the venv from the repo root activated):

```bash
# from repo root:  source .venv/bin/activate

# Task 1 — register the completed server (with the hand-added list_workspace tool), then in
#          Claude Code:  /mcp  and  "read workspace/notes.txt"  (the file explains the loop).
cd solutions/task1_meet_mcp
claude mcp add --transport stdio my_masterschool_mcp_server -- "$(which python)" "$(pwd)/my_masterschool_mcp_server.py"

# Task 2 — HTTP transport + a "peer" client reading your files (two terminals)
cd solutions/task2_network && python my_masterschool_mcp_server.py    # terminal A (then tunnel it)
cd solutions/task2_network && python client_http_demo.py              # terminal B, then Ctrl-C the server

# Task 3 — attack, harden, prove
cd solutions/task3_security
python attack_demo.py            # vulnerable: flag1 LEAKED, flag2 PWNED, flag3 content returned
python attack_demo.py hardened   # hardened:   flag1 & flag2 DEFENDED
python test_hardening.py         # 8/8 checks pass
```

## What each solution file teaches
- `task1_meet_mcp/my_masterschool_mcp_server.py` — the hand-edit answer (`list_workspace` added via
  one `@mcp.tool()`). The starter at the repo root is the same server *before* that tool is added.
- `task2_network/my_masterschool_mcp_server.py` — the transport swap (`host="0.0.0.0"` +
  `transport="streamable-http"`), plus the comment on why `0.0.0.0` disables DNS-rebinding
  protection (and why `127.0.0.1` would break a tunnel with `421`).
- `task2_network/client_http_demo.py` — a stand-in "peer" client to test the network read solo.
- `task3_security/ctf_server_hardened.py` — the three defenses: path canonicalization +
  `is_relative_to`, no-shell argument arrays (`wc -l -- <path>`), and a human-in-the-loop gate on
  side-effectful actions. Prompt injection (flag 3) is intentionally **not** fully fixable here.
- `task3_security/attack_demo.py` / `test_hardening.py` — the attack harness and the proof tests.
