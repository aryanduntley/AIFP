---
description: Start or continue an AIMFP session. Call on every interaction.
argument-hint: [--new]
---

Call the aimfp_run MCP tool to begin or continue an AIMFP session.

If the user passed "--new" as an argument, or this is the very first interaction of the session, call aimfp_run with is_new_session=true. This returns a full session bundle (~15-20k tokens) containing project status, settings, directive names, supportive context, and guidance.

Otherwise, call aimfp_run with is_new_session=false (the default). This returns lightweight continuation guidance (~2k tokens).

After receiving the response, follow the AIMFP behavior loop:
1. Check project state from the response
2. If .aimfp-project/ is missing → offer aimfp_init or check for backup
3. If project exists → identify next action from status
4. Present context and act proactively — don't wait for further commands
