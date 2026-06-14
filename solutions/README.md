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
#
# End-of-Task-2 reveal — once you've added a partner's box (claude mcp add --transport http partner-box <URL>/mcp),
# traverse THEIR server with read_workspace_file. In Claude Code, prompt your agent:
#   "On partner-box, use read_workspace_file to read example.env"
#       → leaks their planted secret (NOT_REAL_*) — a file list_workspace never advertised
#   "On partner-box, use read_workspace_file to read ../FLAG.txt"
#       → path traversal: ../ escapes server/ entirely (this is Task 3, Flag 1)

# Task 3 — attack YOUR server, harden it, prove it. These are reference copies of your own
#          server (read_workspace_file + count_lines), vulnerable vs hardened — you don't register
#          them; they're the answer key + a runnable proof.
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
- `server/client_http_demo.py` — a raw "peer" client to test the network read solo; with `--attack`
  it fires the path-traversal + command-injection proofs straight at any `--http` server (no agent, so
  no guardrail in the way) — e.g. `python solutions/server/client_http_demo.py --attack http://127.0.0.1:8000/mcp`.
- `server/example.env` + `server/workspace/` — the planted "secret" and the "normal" file: a partner's
  agent reads `workspace/README.md`, then `example.env` (which `list_workspace` never showed) — the boundary.
- `task3_security/server_vulnerable.py` — your server (read_workspace_file + the count_lines tool you
  add in Task 3), still naive — the Task 3 starting point.
- `task3_security/server_hardened.py` — the same server, holes closed: path canonicalization +
  `is_relative_to`, no-shell argument arrays (`wc -l -- <path>`), and a human-in-the-loop gate on
  side-effectful actions. Prompt injection (flag 3) is intentionally **not** fully fixable here.
- `task3_security/attack_demo.py` / `test_hardening.py` — the attack harness and the proof tests.
- `task3_security/workspace/` + `task3_security/FLAG.txt` — the sandbox and the planted traversal
  target (one level *outside* the workspace).
