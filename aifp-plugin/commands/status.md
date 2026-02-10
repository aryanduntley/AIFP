---
description: Show current AIFP project status — active task, milestone, next steps.
argument-hint: [quick|summary|detailed]
---

Call the aifp_status MCP tool to get the current project state.

Pass the user's argument as the type parameter:
- "quick" — minimal status (current task only)
- "summary" — standard status (default if no argument given)
- "detailed" — full status with all context

Present the results to the user: current milestone, active task, recent notes, warnings, and suggested next steps.

If the user just asked "where are we" or "status" and you already have fresh context from a recent aifp_run call, answer from your existing context first — only call aifp_status if your context is stale (you can't recall the current milestone name or active task).
