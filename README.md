# Workshop 3 — MCP Servers & Security

Hands-on starter kit for the **MCP & Security** workshop. You'll build a real MCP server
**by hand**, expose it on the network, then attack and harden it.

> The arc: **build by hand until you know the shape, then delegate.** Task 1 is hand-built
> (no agent writes your server). From Task 2 you may use your agent — but you must be able to
> *explain* every line that runs.

> ⚠️ **Educational use only.** In Task 3 you make your own server **deliberately vulnerable** and
> attack it. It uses **fake secrets only** (`NOT_REAL_*`) and a planted `FLAG.txt`. Keep it to the
> provided `server/` sandbox — never point these tools at real files or credentials — and stop any
> network server when you're done.

---

## What's here

```
CLAUDE.md           ← ground rules that keep your agent a lab instrument you drive (not an auto-solver)
server/             ← YOUR server, reused across all three tasks: my_masterschool_mcp_server.py
                       + workspace/ (notes.txt, README.md, meeting_notes.txt) + a planted example.env
FLAG.txt            ← a planted file just OUTSIDE server/ (you'll meet it in Task 3)
MY_FINDINGS.md      ← Task 3 worksheet — fill one block per flag (your graded deliverable)
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

## Task 1 — Meet MCP by hand (Run Local MCP server)

**Goal (🔍 master this):** be able to narrate the request loop unaided —
*your prompt → client lists tools → agent picks one → client invokes it with arguments →
the server runs it → the result returns to the agent's context.*

1. **Read** `server/my_masterschool_mcp_server.py` line by line. Find the `@mcp.tool()`
   decorator — that one line is what makes a plain function *discoverable* by an agent.
2. **Register it with your own Claude Code agent.** Run this **from the repo root** (where setup
   left you) — note the `server/` in the path, and keep the venv activated:
   ```bash
   claude mcp add --transport stdio my_masterschool_mcp_server -- \
     "$(which python)" "$(pwd)/server/my_masterschool_mcp_server.py"
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

   > Registered from the wrong folder and `claude mcp list` shows a path without `server/`?
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
4. **Add your own tools by hand.** This is the "you can extend the server yourself" beat — write
   two tools, each just a function + `@mcp.tool()` + a docstring:
   - **`name()`** — returns *your* name (e.g. `return "Guy Cohen"`). The simplest possible tool,
     and it makes the server uniquely yours — in Task 2 a partner calls it to confirm they reached
     *your* machine.
   - **`list_workspace()`** — returns the files in the `workspace/` folder (a tool that does real
     work; its results feed straight into `read_workspace_file`).

   You don't re-register — the path didn't change; just reconnect the server (`/mcp` → Reconnect, or
   restart Claude Code) so it re-discovers the tools, then ask your agent to call `name` and
   `list_workspace`.

> **Current working directory (cwd) note:** a stdio server inherits the *current working
> directory* — the folder a process resolves relative paths against — of whatever launches it.
> This server calls `os.chdir(Path(__file__).resolve().parent)` so `workspace/notes.txt` resolves
> no matter who starts it. (Same truth as Task 2's boundary: a tool reads with the *process's*
> view of the filesystem, not your idea of "the workspace.")

✅ **Checkpoint:** your agent reads `notes.txt`, your hand-added `name` and `list_workspace` tools work, and
you can narrate the discovery→invoke loop without notes.

---

## Task 2 — Expose it on the network (streamable HTTP — LAN or public tunnel)

**Goal (🔍 master this):** the moment your server is reachable off your machine, its tools are
callable by *someone else's* agent — and the server has no idea what "your workspace" means. It
reads whatever the **process** can read. You can expose it two ways — on your **local network**
(same Wi-Fi, simplest) or, to cross any firewall/NAT and hand out a *public* URL, through a
**tunnel**. Either way the boundary is the same: your file-reader is now reachable by another
machine's agent.

1. **Put your Task 1 server on the network — launch it with `--http`.** It's the **same file-reading
   server you built in Task 1** (`read_workspace_file`, `list_workspace`, `name`) in the same
   `server/` folder — no new server, no edits. It already supports both transports; the `if "--http"
   in sys.argv` line in `__main__` flips it to **streamable-HTTP on `0.0.0.0:8000`**:
   ```bash
   source .venv/bin/activate                              # new terminal? activate first, or `python` won't be found
   python server/my_masterschool_mcp_server.py --http     # ← the --http flag = HTTP. Leave it running.
   #   WITHOUT --http it runs stdio and opens NO port — the #1 "can't connect to :8000" cause.
   # stale/duplicate server, or port 8000 stuck? kill every copy and start fresh:
   pkill -f my_masterschool_mcp_server
   ```
   You'll see the `✅ … streamable-http … Uvicorn running on http://0.0.0.0:8000` banner and it holds
   the terminal — *this* is the process a partner (or you) connects to in steps 2–3. "The workspace"
   stays `server/`, so a remote agent reaches `workspace/README.md` (a normal file) **and** `example.env`
   (the planted secret that `list_workspace` never shows).

   > **Your server prints a startup banner.** `__main__` already calls `print_ready_banner(transport)`,
   > which **always prints** a clear "✅ server READY" line tailored to the transport — a "stdio, no
   > URL" note in Task 1, your localhost + LAN URLs in Task 2. It writes to **`sys.stderr`**, never
   > `print()` (stdout carries the protocol in stdio mode), so it's safe either way.

   > **What you're actually doing:** same server, same tools — the `--http` flag only switches the
   > *transport* (the channel the MCP messages ride on). Task 1 used **stdio**: Claude Code spawned your script as
   > a local subprocess and spoke over its private stdin/stdout pipe, so only this machine could reach
   > it. **Streamable HTTP** instead runs your server as a long-lived web server listening on a network
   > port, so any HTTP client can connect to it by URL. `host="0.0.0.0"` = accept connections on every
   > network interface (not just localhost); `port=8000` = the TCP port it listens on; `/mcp` = the URL
   > path the protocol is served at. That's also why *you* start it now and leave it running — with
   > stdio, Claude Code launched it on demand.

   > **🩺 A client says "unable to connect" to `:8000`?** You launched the server **without `--http`**,
   > so it's running on **stdio** — which opens **no port** (its banner even says "stdio transport …
   > there is no URL"). Stop it and re-run **with `--http`**; the banner then shows your URLs and it
   > keeps listening on `0.0.0.0:8000`. Confirm with `lsof -nP -iTCP:8000 -sTCP:LISTEN` (should show
   > your `python`). Clear stray servers with `pkill -f my_masterschool_mcp_server`.

2. **Expose it — default to your local Wi-Fi network.** Both paths below serve the same `/mcp` over
   the same HTTP transport, but **(a) the local network is the default for this workshop** — simplest,
   no extra tools. Use **(b) a tunnel** only if you and your partner aren't on the same network.

   **(a) Local network (same Wi-Fi) — the default.** With your server from step 1 **running**, it
   already binds `0.0.0.0:8000` (every interface) — so anyone on your Wi-Fi who can reach your machine
   can talk to it. You just need your LAN IP. Easiest source: **your server's startup banner prints
   it** (the `same Wi-Fi: http://<ip>:8000/mcp` line). Or look it up:
   ```bash
   ipconfig getifaddr en0          # macOS Wi-Fi (most common); if empty, try:  ipconfig getifaddr en1
   # still nothing? list every IPv4 and pick your 192.168.x / 10.x address:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   #   Linux:    hostname -I | awk '{print $1}'
   #   Windows:  ipconfig   → "IPv4 Address"
   ```
   **Share `http://<YOUR-LAN-IP>:8000/mcp` — this is the URL your partner uses in step 3.**

   > **Caveats for the LAN path:** you must both be on the **same network**; it must **not** isolate
   > devices (guest/corporate Wi-Fi often blocks device-to-device — "AP/client isolation"); and your
   > OS firewall must allow inbound TCP **8000** (macOS may prompt "accept incoming connections?" the
   > first time — click **Allow**). Nothing leaves your LAN — no internet round-trip.

   > **On a VPN / corporate network? (no usable LAN IP)** If `ipconfig getifaddr en0`/`en1` print
   > nothing and `ifconfig | grep "inet "` shows only an address like `192.0.0.2` (or `100.x`) with
   > `netmask 0xffffffff` and `broadcast` equal to itself, that's a **VPN/tunnel address — a `/32`
   > point-to-point link, not a LAN IP.** A partner on your Wi-Fi can't reach it. Options:
   > - **Solo / just to see it work:** use `http://127.0.0.1:8000/mcp` — localhost always works, no
   >   LAN IP needed. (Your server's banner may show the tunnel addr on its `same Wi-Fi:` line —
   >   ignore it; use the `local:` line.)
   > - **Real two-machine demo:** drop off the VPN onto plain Wi-Fi (then `ipconfig getifaddr en0`
   >   shows a real `192.168.x.x`), or use a **tunnel** (b) — though tunnels are flaky behind a
   >   corporate proxy.

   **(b) Public internet — a tunnel (only if you're *not* on the same network).** To cross
   NAT/firewalls or hand out a public URL, run one tunnel (you only need one); each prints a public
   HTTPS URL:
   ```bash
   cloudflared tunnel --url http://localhost:8000      # no signup → https://<rand>.trycloudflare.com
   # or:  ngrok http 8000                              # free authtoken → https://<rand>.ngrok-free.app
   # or:  npx localtunnel --port 8000                  # no signup → https://<rand>.loca.lt
   ```
   > **`zsh: command not found`?** None of these ship with your OS — install one. Easiest on macOS:
   > `brew install cloudflared` (no signup, no click-through — recommended), or `brew install ngrok`
   > (then add a free authtoken). `npx localtunnel --port 8000` needs only Node (npx fetches it on
   > the fly), but loca.lt is unreliable — it often just **hangs with no URL** (a blank line),
   > especially behind a corporate proxy/VPN. **cloudflared is the smoothest; or skip the tunnel and
   > use the LAN path (a) above.**

3. **A partner connects to your URL — default to your LAN URL** (`http://<YOUR-LAN-IP>:8000/mcp`);
   use the tunnel URL only if you're not on the same network. **Note the `/mcp` path:**
   ```bash
   claude mcp add --transport http partner-box http://<YOUR-LAN-IP>:8000/mcp
   # Example: claude mcp add --transport http partner-box http://127.0.0.1:8000/mcp
   # not on the same network? use your tunnel's URL (always add the /mcp path):
   #   cloudflared:  claude mcp add --transport http partner-box https://<rand>.trycloudflare.com/mcp
   #   ngrok:        claude mcp add --transport http partner-box https://<rand>.ngrok-free.app/mcp
   #   localtunnel:  claude mcp add --transport http partner-box https://<rand>.loca.lt/mcp
   # remove it (wrong URL / clean restart) — just the NAME, no flags/URL:  claude mcp remove partner-box
   ```
   Confirm Claude Code discovered it: `/mcp` should now list **partner-box** with its tools.

4. **Test the tools on the box you just connected to** — run each as its **own prompt**, one at a
   time, so you see each round-trip on its own. In Claude Code:
   > "On partner-box, call name."

   > "On partner-box, call list_workspace."

   > "On partner-box, use read_workspace_file to read workspace/README.md."

   You should get back the owner's name, the workspace listing, and the file's contents — all fetched
   over the network from another machine's process. That's the Task 1 loop, now crossing a machine boundary.

> 🔍 **Why it "just works" off your machine — and the trap.** Binding `host="0.0.0.0"` *also turns off*
> the MCP SDK's **DNS-rebinding protection**, so the server accepts requests with *any* `Host`
> header — including your tunnel's domain or your LAN IP. If you "harden" by switching to `host="127.0.0.1"`,
> the SDK only allows a `localhost` Host and a tunnel/LAN connection dies with **`421 Misdirected Request`** —
> a *security control* that looks exactly like a network bug. Convenience vs. safety, in one line.

**Rehearse solo (no partner)?** Be the "peer" client against your own server:
`python solutions/server/client_http_demo.py http://127.0.0.1:8000/mcp`.

✅ **Checkpoint:** a partner's agent read a file on your machine **and** you can state in one
sentence the boundary you crossed.

---

## Task 3 — Break it, then close the door (attack a server, then harden your *own*)

> ⚠️ **Safety box.** Attack **only** the workshop servers — your own `server/`, or a **partner's**
> (with their OK), just like Task 2. Everything is **fake secrets only** (`NOT_REAL_*`): the
> path-traversal target `FLAG.txt` is a planted file just *outside* `server/`, and the
> command-injection proof is harmless (`whoami`). Never point these tools at real files or
> credentials, and stop the server when you're done.

This is the **same server you built and exposed in Tasks 1–2** — no new server to register. The
holes were there all along; now you exploit them, then close them.

**Warm-up — the Task 2 reveal:** point your agent at a server and run
`read_workspace_file("example.env")`. It reads the planted secret **even though `list_workspace`
never listed it** (`example.env` sits beside `workspace/`, not inside it). That gap — *listed ≠
reachable* — is the boundary Round A blows wide open.

**Who does what — read this first:**
- **You add the vulnerable `count_lines` tool to YOUR OWN server** (`server/my_masterschool_mcp_server.py`).
  *You* author the hole — that's the point.
- **You run the attacks (via your agent) against a *running* server.** Simplest is **your own** — you
  have the tools and the planted files, so it's fully self-contained. For the realistic cross-machine
  version, pair up and attack each other's `partner-box` from Task 2 — but note: **command injection
  only works if the target server actually exposes `count_lines`, so both partners must add it first.**
  Path traversal and prompt injection work on any of these servers as-is.
- **You harden YOUR OWN server** in Round B.

**How to work it — this *is* the skill:**
- **One attack per step.** Your agent runs exactly one tool call at a time — no sweeps. (The repo's
  `CLAUDE.md` already tells it to.)
- **Predict first, then test.** Before each call write your prediction; run it; reconcile. Your agent
  reports the raw result — **you** write the explanation.
- **Your deliverable is `MY_FINDINGS.md`, not the transcript.** A blank `MY_FINDINGS.md` is already in
  the repo — just open it and fill one block per flag (predict *before* the attack, result + "because"
  *after*). A filled block looks like:
  ```markdown
  ## Flag 1 — path traversal
  Predict: Yes — read_workspace_file is open(path) with no checks, so "../" should escape server/.
  Result:  worked — read FLAG{path_traversal_pwned}
  Because: Path traversal (CWE-22). The sandbox boundary failed: open() honors any path the process
           can reach, so "../" walks out of server/. A scoped list_workspace gave false confidence.
  ```
  Do the same for Flags 2 and 3 (three blocks total). Then swap files with your Task 2 partner and check
  each other's "Because" lines — **that's the grade: can you *explain* it, not just land it.**

### Round A — attack (do all three, in order)
Run against your own server (or a partner's `partner-box`, per "who does what" above). The server's
working directory is `server/`, so attack paths are relative to that.

**🚩 Flag 1 — path traversal.** Predict, then run **one** call: `read_workspace_file("../FLAG.txt")`.
Did you read a file *outside* `server/`? Record it — then ask: `list_workspace` only showed three files,
so how did the reader reach one it never listed? (No setup needed — this hole has been in
`read_workspace_file` since Task 1.)

**🚩 Flag 2 — command injection.** Needs a tool first: **add a deliberately unsafe `count_lines` to your
own server**, the way you hand-added `name`/`list_workspace`:
```python
import subprocess  # at the top of the file

@mcp.tool()
def count_lines(filename: str) -> str:
    """Count the lines in a workspace file."""
    out = subprocess.run(f"wc -l {filename}", shell=True, capture_output=True, text=True)
    return (out.stdout or "") + (out.stderr or "")
```
Reconnect, predict, then run **one** call: `count_lines("workspace/notes.txt; whoami")`. Did the injected
`whoami` run? Record it. (You just authored a remote-code-execution hole in your own server — every tool
you expose is an attack surface.)

**🚩 Flag 3 — indirect prompt injection.** Have your agent read `workspace/meeting_notes.txt` and
summarize it. Predict what it will do, then watch. A modern agent usually **refuses** the hidden
instruction — that's the *start*, not the end:
- **Try to make it fire.** Edit `meeting_notes.txt` and escalate: (a) drop any obvious "instruction"
  framing; (b) phrase it as a plausible business rule; (c) make it conditional/indirect; (d) split the
  ask across a second file read in the same chat. Note where the refusal gets *less* confident. (Fake
  secrets only, inside `server/`.)
- **Write the defense.** In `MY_FINDINGS.md`, draft a 3-line human-in-the-loop policy *in your own
  words* (e.g. tool/file output is data not instructions; any instruction found in content is surfaced,
  never obeyed; sensitive/side-effectful actions need human confirmation). *Then* ask your agent why it
  refused and compare.

> ✅ **Gate:** all three "Because" lines + a draft HITL policy written before you start Round B.

### Round B — close the doors (agent-assisted, but read the diff)
**Predict the fix first:** how would *you* stop `../FLAG.txt`? Write it down. Then ask your agent:
> "Harden this server: (1) confine `read_workspace_file` to one allowed root by canonicalizing the
> path and rejecting anything outside it; (2) rewrite `count_lines` with no `shell=True` — use an
> argument array; (3) document that tool output is untrusted and require confirmation before
> side-effectful actions. Write tests proving the Round-A attacks fail."

Compare the patch to your prediction. The single most important diff — read it and be able to explain
why `is_relative_to` kills `../` (and why a naive `str.startswith` check would **not**):
```python
from pathlib import Path
ALLOWED_ROOT = Path(__file__).resolve().parent       # confine tools to the server's own folder

def _safe_target(path: str) -> Path:
    target = (ALLOWED_ROOT / path).resolve()         # collapses ../ AND follows symlinks
    if not target.is_relative_to(ALLOWED_ROOT):      # blocks traversal — component-wise, not string-prefix
        raise ValueError("Access denied: path escapes the workspace.")
    return target
```
Then read with `_safe_target(path).read_text()`, and make `count_lines` pass an **argument array** —
`subprocess.run(["wc", "-l", "--", str(_safe_target(filename))])` — so an injected `;` stays part of
one filename and never reaches a shell.

Re-run Round A: flags 1 & 2 should fail cleanly; flag 3 is the discussion — server hardening can't
remove it, because the danger lives in how the *consuming agent* treats tool output (your HITL policy).

✅ **Checkpoint:** your hardened server blocks traversal + injection, your `MY_FINDINGS.md` explains
each flag in your own words, and you can say why prompt injection isn't a server-side fix — it's an
orchestration / human-in-the-loop problem (the next workshop).

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

---

> 🛑 **When you're done:** stop every server and tunnel — `pkill -f my_masterschool_mcp_server`, and
> Ctrl-C any cloudflared/ngrok/localtunnel. Don't leave a file-reader listening on your network or
> the internet.
