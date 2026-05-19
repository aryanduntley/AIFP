---
name: aimfp-mode
description: >
  AIMFP (AI Modular Functional Procedural) setup bootstrap. Loads when the
  AIMFP MCP server is connected. Its only job: make sure the AIMFP system
  prompt is installed in this project's instructions, then start an AIMFP
  session. All behavioral rules live in the system prompt and the runtime
  supportive context — never duplicated here.
user-invocable: false
---

# AIMFP — Setup Bootstrap (setup only)

This skill is intentionally tiny. AIMFP's behavior is defined by the AIMFP
**system prompt** (the project's record-keeping backbone — loaded every turn
once installed) and the **supportive context** loaded on demand by `aimfp_run`.
Those are the single source of truth; this file deliberately does **not**
restate them, to avoid duplicating that content into every session.

When the AIMFP MCP server is connected, do exactly two things:

1. **Ensure the system prompt is installed.** If this project's instructions
   (`CLAUDE.md`, or the client's custom-instructions field) do not already
   contain the AIMFP system prompt, call the **`get_system_prompt`** tool and
   place it exactly as that tool instructs (AIMFP content first; never discard
   existing content). This is required — without it, AIMFP behavior is
   undefined.

2. **Start the session.** Call **`aimfp_run(is_new_session=true)`** once. From
   then on, follow the installed system prompt and `aimfp_run`'s guidance.

Nothing else belongs here. Do not infer AIMFP rules from this file — act on the
installed system prompt and the supportive context `aimfp_run` provides.
