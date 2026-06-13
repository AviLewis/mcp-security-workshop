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
task1_meet_mcp/     ← Task 1 starter: my_masterschool_mcp_server.py (one tool) + a
                       workspace/notes.txt that explains the MCP loop when you read it
task2_network/      ← Task 2 fixtures: you add the HTTP transport + tunnel yourself
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

**Why each step is here:**
- **`git clone` + `cd`** — download the files and move into the project folder so the relative paths in later commands resolve.
- **`python3 -m venv .venv`** — create an isolated Python environment. Modern systems (macOS/Homebrew, Debian/Ubuntu, Python 3.11+) **block installing packages into the system Python** (the `externally-managed-environment` error), so a virtual environment is the reliable way to install dependencies without a sudo/permission fight or breaking your system Python.
- **`source .venv/bin/activate`** — switch into that environment so `python`, `pip`, and `which python` all point inside it. (Task 1 registers the server with `"$(which python)"`, so this guarantees Claude Code launches it with the interpreter that has `mcp` installed.)
- **`pip install -r requirements.txt`** — installs the one dependency that matters: the **`mcp` SDK** that every server imports (`from mcp...`). Nothing runs without it.
- **`python -c "import mcp; ..."`** — a quick sanity check that the install worked before you wire up Claude Code.

> The bare minimum is really just *"have the files"* + *"have a Python with `mcp` installed."* The venv steps exist because a plain `pip install mcp` fails on most modern machines.

---

## Task 1 — Meet MCP by hand (stdio, local)

**Goal (🔍 master this):** be able to narrate the request loop unaided —
*your prompt → client lists tools → agent picks one → client invokes it with arguments →
the server runs it → the result returns to the agent's context.*

1. **Read** `task1_meet_mcp/my_masterschool_mcp_server.py` line by line. Find the `@mcp.tool()`
   decorator — that one line is what makes a plain function *discoverable* by an agent.
2. **Register it with your own Claude Code agent.** Run this **from the repo root** (where setup
   left you) — note the `task1_meet_mcp/` in the path, and keep the venv activated:
   ```bash
   claude mcp add --transport stdio my_masterschool_mcp_server -- \
     "$(which python)" "$(pwd)/task1_meet_mcp/my_masterschool_mcp_server.py"
   claude mcp list

   # (optional) remove it again — for troubleshooting or a clean restart:
   claude mcp remove my_masterschool_mcp_server
   ```
   What each part means:
   - `claude mcp add` — register a new MCP server in your Claude Code config.
   - `--transport stdio` — run it as a local subprocess, talking over stdin/stdout.
   - `my_masterschool_mcp_server` — the name it shows up as in `/mcp`.
   - `--` — everything after this is the command Claude Code runs to launch the server:
     `$(which python)` = the venv Python that has `mcp`; `$(pwd)/…/…py` = the absolute path to
     the server file. Both are absolute so Claude Code can launch it from anywhere.

   > Registered from the wrong folder and `claude mcp list` shows a path without `task1_meet_mcp/`?
   > Run `claude mcp remove my_masterschool_mcp_server` and re-run the command above from the repo root.

   > **`/mcp` says `Command: python not found` / `✘ Failed to connect`?** You ran `claude mcp add`
   > with **no venv active**, so `$(which python)` had nothing to find and baked the literal text
   > *"python not found"* in as the launch command. Fix it:
   > `claude mcp remove my_masterschool_mcp_server`, then `source .venv/bin/activate`, confirm
   > `which python` prints a path ending in `.venv/bin/python` (not "python not found"), and re-run
   > the `claude mcp add` above. (The registration is frozen at add-time — it stores whatever
   > `$(which python)` was *then*, so the venv must be active *when you register*.)

   > **Managing the registration (troubleshooting toolkit):**
   > - `claude mcp list` — show every server, its scope, and ✓/✘ status. (Inside Claude Code: `/mcp`.)
   > - `claude mcp remove my_masterschool_mcp_server` — delete it so you can re-add cleanly.
   > - **Scope:** a server lives in a scope — `local` (just you, this project — the default),
   >   `user` (global, all your projects), or `project` (a shared `.mcp.json` in the repo). `remove`
   >   looks in `local` first; if the same name lives elsewhere, force it with `-s user` /
   >   `-s project` / `-s local`.
   > - **By hand (last resort):** delete the entry from `~/.claude.json` under that project's
   >   `"mcpServers"` block — but do it with **Claude Code closed**, or it rewrites the file on exit
   >   and undoes your edit.
3. **Test it entirely from inside the agent** — you never run the Python file yourself; Claude
   Code launches it for you. In Claude Code:
   ```
   /mcp                                         # confirm the tool was discovered
   "Use read_workspace_file to read workspace/notes.txt"
   ```
   `notes.txt` doesn't contain notes — it contains a **step-by-step explanation of the very loop
   that just delivered it to you**. The text coming back *is* your proof the loop ran end-to-end
   (Claude Code also shows the tool call in its interface).
4. **Add a second tool.** In the server, add `list_workspace()` that returns the files in the
   `workspace/` folder (the whole recipe: a function + `@mcp.tool()` + a docstring). You don't
   re-register — the path didn't change; just reconnect the server (`/mcp` → Reconnect, or restart
   Claude Code) so it re-discovers the tools, then ask your agent to call `list_workspace`.

> **Current working directory (cwd) note:** a stdio server inherits the *current working
> directory* — the folder a process resolves relative paths against — of whatever launches it.
> This server calls `os.chdir(Path(__file__).resolve().parent)` so `workspace/notes.txt` resolves
> no matter who starts it. (Same truth as Task 2's boundary: a tool reads with the *process's*
> view of the filesystem, not your idea of "the workspace.")

✅ **Checkpoint:** your agent reads `notes.txt`, your hand-added `list_workspace` tool works, and
you can narrate the discovery→invoke loop without notes.

---

## Task 2 — Expose it on the public internet (streamable HTTP + tunnel)

**Goal (🔍 master this):** the moment your server is reachable off your machine, its tools are
callable by *someone else's* agent — and the server has no idea what "your workspace" means. It
reads whatever the **process** can read. We use a **tunnel** (not the LAN) so this works through
any firewall/NAT — and so the boundary is honest: your file-reader is now on the *public internet*.

1. **Swap the transport** (agent-assisted is fine — "gist" level). Ask your agent:
   > "Change my MCP server to **streamable HTTP** on host `0.0.0.0`, port `8000`, served at `/mcp`."

   The change is `FastMCP(..., host="0.0.0.0", port=8000)` + `mcp.run(transport="streamable-http")`.
   Start it: `python my_masterschool_mcp_server.py` (leave it running).

   > **What you're actually doing:** same server, same tools — you're only swapping the *transport*
   > (the channel the MCP messages ride on). Task 1 used **stdio**: Claude Code spawned your script as
   > a local subprocess and spoke over its private stdin/stdout pipe, so only this machine could reach
   > it. **Streamable HTTP** instead runs your server as a long-lived web server listening on a network
   > port, so any HTTP client can connect to it by URL. `host="0.0.0.0"` = accept connections on every
   > network interface (not just localhost); `port=8000` = the TCP port it listens on; `/mcp` = the URL
   > path the protocol is served at. That's also why *you* start it now and leave it running — with
   > stdio, Claude Code launched it on demand.

2. **Expose it with a tunnel** (default path — pick one; all give you a public HTTPS URL):
   ```bash
   cloudflared tunnel --url http://localhost:8000      # no signup → https://<rand>.trycloudflare.com
   # or:  ngrok http 8000                              # free authtoken → https://<rand>.ngrok-free.app
   # or:  npx localtunnel --port 8000                  # no signup → https://<rand>.loca.lt
   ```

   > **`zsh: command not found`?** None of these ship with your OS — install one (you only need
   > one). Easiest on macOS: `brew install cloudflared` (no signup, no click-through — recommended),
   > or `brew install ngrok` (then add a free authtoken). If you have Node, `npx localtunnel --port
   > 8000` needs no install — npx fetches it on the fly — but localtunnel shows a one-time reminder
   > page, so cloudflared is the smoothest for this demo.

   > **On the same Wi-Fi? You may not need a tunnel at all.** If you and your partner are on the
   > same network and it doesn't block device-to-device traffic (no client/AP "isolation"), your
   > server is already reachable directly: it binds `0.0.0.0:8000`, so a partner connects over the
   > LAN with the **same HTTP transport** — no tunnel tool required. The server prints your LAN URL
   > on startup (or run `ipconfig getifaddr en0` on macOS Wi-Fi); the partner uses
   > `http://<YOUR-LAN-IP>:8000/mcp` in the next step. A tunnel is only needed to cross networks —
   > NAT, firewalls, or to hand out a truly public URL.

3. **A partner connects to your URL** — the tunnel URL **or** your `http://<LAN-IP>:8000` on the
   same Wi-Fi — **note the `/mcp` path:**
   ```bash
   claude mcp add --transport http partner-box https://<rand>.trycloudflare.com/mcp
   # same network instead?  claude mcp add --transport http partner-box http://<YOUR-LAN-IP>:8000/mcp
   # inside Claude Code:  "Use read_workspace_file on partner-box to read workspace/notes.txt"
   ```

4. **The reveal:** a planted `task2_network/fake.env` (fake secret) is readable too. Predict
   whether your partner's agent can read it, then have them try. It can.

> 🔍 **Why the tunnel "just works" — and the trap.** Binding `host="0.0.0.0"` *also turns off*
> the MCP SDK's **DNS-rebinding protection**, so the server accepts requests with *any* `Host`
> header — including your tunnel's domain. If you "harden" by switching to `host="127.0.0.1"`,
> the SDK only allows a `localhost` Host and your tunnel dies with **`421 Misdirected Request`** —
> a *security control* that looks exactly like a network bug. Convenience vs. safety, in one line.

> 🛑 **Stop the server and the tunnel** when you're done — don't leave a file-reader exposed to
> the internet.

**Rehearse solo (no partner)?** Be the "peer" client against your own server:
`python solutions/task2_network/client_http_demo.py http://127.0.0.1:8000/mcp`.

✅ **Checkpoint:** a partner's agent read a file on your machine **and** you can state in one
sentence the boundary you crossed.

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
