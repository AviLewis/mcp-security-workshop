# ⛔ Solutions — spoilers ahead

This folder is the **complete, finished, runnable** version of all three tasks. It exists so you
can check your work or recover if you're stuck — **try each task yourself first.** Reading the
hardened server before you've attacked the vulnerable one skips the whole point of the CTF.

Each piece is runnable (with the venv from the repo root activated):

```bash
# from repo root:  source .venv/bin/activate

# Task 1 — register the completed server (with the hand-added name + list_workspace tools), then in
#          Claude Code:  /mcp  and  "read workspace/notes.txt"  (the file explains the loop).
#          Runs stdio by default. Run from the repo root; note the path including solutions/server/.
claude mcp add --transport stdio my_masterschool_mcp_server -- "$(which python)" "$(pwd)/solutions/server/my_masterschool_mcp_server.py"

# Task 2 — the SAME server, now over HTTP (pass --http), + a "peer" client reading your files (two terminals)
cd solutions/server && python my_masterschool_mcp_server.py --http    # terminal A (then tunnel it, or use your LAN IP)
cd solutions/server && python client_http_demo.py                     # terminal B, then Ctrl-C the server

# Task 3 — attack, harden, prove
cd solutions/task3_security
python attack_demo.py            # vulnerable: flag1 LEAKED, flag2 PWNED, flag3 content returned
python attack_demo.py hardened   # hardened:   flag1 & flag2 DEFENDED
python test_hardening.py         # 8/8 checks pass
```

## What each solution file teaches
- `server/my_masterschool_mcp_server.py` — the ONE reusable server (Task 1 **and** Task 2). It has
  the hand-edit answers (`name` + `list_workspace` added via `@mcp.tool()`; the starter at the repo
  root is this same server *before* those tools) and the Task 2 transport swap (`host="0.0.0.0"` +
  `transport="streamable-http"`, run with `--http`), plus the comment on why `0.0.0.0` disables
  DNS-rebinding protection (and why `127.0.0.1` would break a tunnel/LAN client with `421`).
- `server/client_http_demo.py` — a stand-in "peer" client to test the network read solo.
- `server/fake.env` + `server/workspace/` — the planted "secret" and the "normal" file: a partner's
  agent reads `workspace/README.md`, then `fake.env` (which `list_workspace` never showed) — the boundary.
- `task3_security/ctf_server_hardened.py` — the three defenses: path canonicalization +
  `is_relative_to`, no-shell argument arrays (`wc -l -- <path>`), and a human-in-the-loop gate on
  side-effectful actions. Prompt injection (flag 3) is intentionally **not** fully fixable here.
- `task3_security/attack_demo.py` / `test_hardening.py` — the attack harness and the proof tests.
