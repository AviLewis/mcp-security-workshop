# Sample Workspace (Task 1)

This file exists so `read_workspace_file` has something real to return.

When the agent reads this, the bytes you're looking at now travel back through the
MCP loop and land in the agent's context. That round trip — prompt to bytes-in-context —
is the whole point of Task 1.

Try editing this line, then re-run the client. The change shows up immediately because
the tool reads the file fresh on every call.
