# Workshop 3 — MCP Servers & Security

Hands-on starter kit for the **MCP & Security** workshop. You'll build a real MCP server
**by hand**, expose it on the network, then attack and harden it.

> The arc: **build by hand until you know the shape, then delegate.** Task 1 is hand-built
> (no agent writes your server). From Task 2 you may use your agent — but you must be able to
> *explain* every line that runs.

> ⚠️ **Educational use only.** This repo contains a **deliberately vulnerable** server and a
> capture-the-flag exercise. It uses **fake secrets only** (`NOT_REAL_*`). Run the CTF only in
> the provided `ctf-workspace/` sandbox. Never point these tools at real files or credentials,
> and stop any network server when you're done.

---

## What's here

```
task1_meet_mcp/     ← Task 1 starter: a ~20-line MCP server with one tool
task2_network/      ← Task 2 fixtures: you add the HTTP transport yourself
task3_security/     ← Task 3 CTF: a vulnerable server to attack, then harden
solutions/          ← ⛔ SPOILERS — the finished, runnable version of all three tasks
```

Work from the root task folders. **Only open `solutions/` if you're stuck** or want to check
your answer — it gives away the CTF.

---

## Setup (5 min)

Requires **Python 3.10+** and **[Claude Code](https://docs.claude.com/en/docs/claude-code)** installed and authenticated.

```bash
git clone https://github.com/AviLewis/mcp-security-workshop.git
cd mcp-security-workshop

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -c "import mcp; print('mcp ready')"
```

Keep this venv activated for the rest of the workshop (so `python` and `claude mcp` use it).

---

## Task 1 — Meet MCP by hand (stdio, local)

**Goal (🔍 master this):** be able to narrate the request loop unaided —
*your prompt → client lists tools → agent picks one → client invokes it with arguments →
the server runs it → the result returns to the agent's context.*

1. **Read** `task1_meet_mcp/mcp_server.py` line by line. Find the `@mcp.tool()` decorator —
   that one line is what makes a plain function *discoverable* by an agent.
2. **See the loop** without Claude Code — a tiny client prints every step:
   ```bash
   cd task1_meet_mcp
   python client_demo.py
   ```
   Watch the `[tool call]` line: that's your server being invoked, live.
3. **Connect your own agent.** Register the server with Claude Code:
   ```bash
   # from inside task1_meet_mcp, with the venv activated:
   claude mcp add --transport stdio my-server -- "$(which python)" "$(pwd)/mcp_server.py"
   claude mcp list
   # then inside Claude Code:  /mcp   and:  "Use read_workspace_file to read workspace/README.md"
   ```
4. **Hand-edit (no agent):** add a second tool `list_workspace()` that returns the filenames in
   the folder. Pattern: a function + `@mcp.tool()` + a docstring. Re-run `python client_demo.py`
   — it will discover and call your new tool automatically.

> **cwd note:** a stdio server inherits the working directory of whatever launches it. This
> starter calls `os.chdir(Path(__file__).resolve().parent)` so relative paths like
> `workspace/README.md` resolve no matter who starts it. (Same truth as Task 2's boundary: a
> tool reads with the *process's* view of the filesystem.)

✅ **Checkpoint:** your agent calls your tool, your hand-added tool works, and you can narrate the
discovery→invoke loop without notes.

---

## Task 2 — Expose it on the network (streamable HTTP)

**Goal (🔍 master this):** the moment your server is on the network, its tools are reachable by
*someone else's* agent — and the server has no idea what "your workspace" means. It reads
whatever the **process** can read.

1. **Swap the transport** (agent-assisted is fine here — this is "gist" level). Ask your agent:
   > "Change my MCP server to **streamable HTTP** on host `0.0.0.0`, port `8000`, served at
   > `/mcp`. Tell me my LAN IP and the exact URL a teammate on the same WiFi would use."

   The key change is `FastMCP(..., host="0.0.0.0", port=8000)` + `mcp.run(transport="streamable-http")`,
   served at `http://<LAN-IP>:8000/mcp`.
2. **Read the one line that changed** and explain *why* it moves you from "local subprocess" to
   "anyone on the WiFi." If you can't, you don't understand the transport yet — ask.
3. **Cross-connect a partner** (or simulate with localhost):
   ```bash
   claude mcp add --transport http partner-box http://<PARTNER-LAN-IP>:8000/mcp
   # inside Claude Code:  "Use read_workspace_file on partner-box to read workspace/README.md"
   ```
4. **The reveal:** a planted `task2_network/fake.env` (fake secret) is readable too. Predict
   whether your partner's agent can read it, then try. It can.

> 🛑 **Stop the server** when you're done — don't leave a file-reader bound to `0.0.0.0`.

✅ **Checkpoint:** you read a file on another machine **and** can state in one sentence the
boundary you crossed.

---

## Task 3 — Break it, then close the door (CTF + harden)

> ⚠️ **Safety box.** Attack **only** the provided `task3_security/` sandbox. Fake secrets only.
> The path-traversal target `FLAG.txt` is a planted file just *outside* `ctf-workspace/`.
> Command-injection proof is harmless (`whoami`). Stop the server when you're done.

### Round A — attack
Start the vulnerable server and point your agent at it (over stdio locally, or HTTP to a partner).
For **each flag, write one line: "worked / didn't, because ___"** — that sentence is the point.

| 🚩 | Vector | Try | Proof |
|---|---|---|---|
| 1 | **Path traversal** | `read_workspace_file("../FLAG.txt")` | you read a file outside the workspace |
| 2 | **Command injection** | `count_lines("notes.txt; whoami")` | the injected `whoami` runs |
| 3 | **Indirect prompt injection** | have the agent read `ctf-workspace/meeting_notes.txt` and "summarize" it | the agent obeys instructions hidden in the file's *contents* |

*Flag 3 note:* modern Claude often **resists** naive injections — that's a feature and a teaching
moment. If it doesn't fire, ask: *why did the defense hold, and what would a determined attacker change?*

### Round B — harden your own server (agent-assisted, but read the diff)
Ask your agent to:
> "Harden this server: (1) confine `read_workspace_file` to one allowed root by canonicalizing the
> path and rejecting anything outside it; (2) remove any `shell=True`, use argument arrays;
> (3) document that tool output is untrusted and require confirmation before side-effectful actions.
> Write tests proving the Round-A attacks fail."

The single most important diff — the path-traversal patch. Read it and be able to explain why
`is_relative_to` kills `../` (and why a naive `str.startswith` check would **not**):
```python
from pathlib import Path
ALLOWED_ROOT = Path("./ctf-workspace").resolve()

target = (ALLOWED_ROOT / path).resolve()      # collapses ../ AND follows symlinks
if not target.is_relative_to(ALLOWED_ROOT):   # blocks traversal — component-wise, not string-prefix
    raise ValueError("Access denied: path escapes the workspace.")
```

Re-run Round A: flags 1 & 2 should fail cleanly; flag 3 is the discussion.

✅ **Checkpoint:** your hardened server blocks traversal + injection **and** you can explain why
prompt injection can't be fully patched server-side — the danger lives in how the *consuming agent*
treats tool output. That's an orchestration / human-in-the-loop problem (the next workshop).

---

## Stuck? Check the answers

The `solutions/` folder is the complete, finished, **runnable** version of all three tasks:

```bash
# e.g. prove the hardening works:
cd solutions/task3_security
python attack_demo.py           # attacks the vulnerable server — flags land
python attack_demo.py hardened  # attacks the hardened server — flags 1 & 2 fail
python test_hardening.py        # 8/8 checks pass
```

## Debrief questions
1. Which flag was easiest to land, and which was hardest to patch?
2. Where did the agent have an easier time — building the server, or attacking one?
3. What's one tool *your* product's server exposes that you now realize is a door you'd lock?
