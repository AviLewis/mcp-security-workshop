#!/usr/bin/env python
"""test_hardening.py — proves the Round-A attacks fail on the HARDENED server.

No pytest needed. Imports the hardened tool functions directly (the @mcp.tool()
decorator returns the original callable) and asserts the security properties.

Run:
    python test_hardening.py     # exits 0 if all checks pass, 1 otherwise
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server_hardened as h  # noqa: E402

results = []


def check(name: str, ok: bool) -> None:
    results.append(ok)
    print(f"{'✅ PASS' if ok else '❌ FAIL'}  {name}")


# --- legitimate use still works -------------------------------------------------
try:
    content = h.read_workspace_file("fake.env")
    check("legit: read_workspace_file('fake.env') works", "API_KEY" in content)
except Exception as e:
    check(f"legit: read_workspace_file('fake.env') works (raised {e!r})", False)

try:
    out = h.count_lines("notes.txt")
    check(
        "legit: count_lines('notes.txt') returns a count", any(c.isdigit() for c in out)
    )
except Exception as e:
    check(f"legit: count_lines('notes.txt') works (raised {e!r})", False)

# --- FLAG 1: path traversal is blocked -----------------------------------------
try:
    h.read_workspace_file("../FLAG.txt")
    check("flag1: '../FLAG.txt' traversal is blocked", False)
except ValueError:
    check("flag1: '../FLAG.txt' traversal is blocked", True)

try:
    h.read_workspace_file("../../../../etc/passwd")
    check("flag1: deep '../../../etc/passwd' traversal is blocked", False)
except ValueError:
    check("flag1: deep '../../../etc/passwd' traversal is blocked", True)

try:
    h.read_workspace_file("/etc/hosts")
    check("flag1: absolute path '/etc/hosts' is blocked", False)
except ValueError:
    check("flag1: absolute path '/etc/hosts' is blocked", True)

# --- FLAG 2: command injection is neutralized ----------------------------------
# Detect REAL execution: whoami's output must appear as a line of its own. A naive
# `me in out` check false-positives because the username is part of the echoed path
# (/Users/<user>/...) in wc's "No such file" error.
me = os.popen("whoami").read().strip()


def whoami_ran(output: str) -> bool:
    return bool(me) and any(line.strip() == me for line in output.splitlines())


out = h.count_lines("notes.txt; whoami")
check("flag2: 'notes.txt; whoami' does NOT execute whoami", not whoami_ran(out))

out = h.count_lines("$(whoami)")
check("flag2: '$(whoami)' substitution does NOT execute", not whoami_ran(out))

# --- FLAG 3 corollary: side effects are gated (HITL) ----------------------------
r = h.write_note("pwned.txt", "x", confirm=False)
check("hitl: write_note refuses without confirm=True", "Refused" in r)

# --- summary -------------------------------------------------------------------
passed, total = sum(results), len(results)
print(f"\n{passed}/{total} checks passed", "✅" if passed == total else "❌")
sys.exit(0 if passed == total else 1)
