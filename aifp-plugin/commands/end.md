---
description: End the current AIFP session with audit and state verification.
---

Call the aifp_end MCP tool with the current project root.

This performs a comprehensive session audit:
1. Verifies all written files and functions are tracked in project.db
2. Reviews task and milestone progress
3. Stops the watchdog filesystem monitor if running
4. Logs a session summary to the notes table
5. Confirms to the user that it is safe to close the session

If there are untracked files or incomplete operations, report them to the user before confirming session end.
