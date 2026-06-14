# My findings — Task 3

Fill one block per flag. Write **Predict** *before* you run the attack; fill **Result** and
**Because** *after*. The **Because** line is the graded part — 1–2 sentences in your own words:
name the vulnerability class, and say which boundary failed. Then swap with your Task 2 partner and
check each other's "Because" lines.

(Example of a good block — replace with your own:)
> ## Flag 1 — path traversal
> Predict: Yes — read_workspace_file is open(path) with no checks, so "../" should escape server/.
> Result:  worked — read FLAG{path_traversal_pwned}
> Because: Path traversal (CWE-22). The sandbox boundary failed: open() honors any path the process
>          can reach, so "../" walks out of server/. A scoped list_workspace gave false confidence.

---

## Flag 1 — path traversal
Attack: read_workspace_file("../FLAG.txt")
Predict:
Result:
Because:

## Flag 2 — command injection
Attack: count_lines("workspace/notes.txt; whoami")   (after you add the count_lines tool)
Predict:
Result:
Because:

## Flag 3 — indirect prompt injection
Attack: have your agent read & summarize workspace/meeting_notes.txt
Predict:
Result:
Because:

---

## My human-in-the-loop (HITL) policy
Flag 3 can't be patched server-side — the danger is in how the agent treats tool output. Write the
rules a safe agent should follow (3 lines, your own words):
1.
2.
3.
