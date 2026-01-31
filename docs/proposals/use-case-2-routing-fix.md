# Use Case 2 Routing Fix — Problem Analysis & Proposed Solution

**Date**: 2026-01-31
**Status**: Proposal
**Affects**: project_discovery, project_init, aifp_status, aifp_run, directive flows, system prompt, supportive context

---

## 1. The Problem

Use Case 2 (custom directive automation) has a comprehensive execution pipeline (parse → validate → implement → approve → activate → monitor), but **no reliable way to enter it**. The system is entirely reactive — the user must manually invoke each step. For a tool designed around proactive AI behavior, this is a fundamental contradiction.

### Current Flow (Broken)

```
project_init
  → project_discovery (branches 1-7: blueprint, infra, themes, milestones)
    → aifp_status
      → project_progression (Case 1 work loop)
```

Use Case 2 never enters the picture unless the user explicitly says "parse my directive file." The discovery conversation has **zero awareness** of Use Case 2. The project_init creates a `logs/` directory for automation projects but never sets `user_directives_status`, so the project is permanently treated as Case 1.

### Specific Gaps

1. **`project_discovery` has no Use Case 2 branch.** The 7 branches cover blueprint, infrastructure, themes, flows, completion path, milestones, and finalization. None ask "what kind of project is this?" in a way that forks to Case 2.

2. **`project_init` doesn't set `user_directives_status`.** Even when it detects "automation" keywords and creates `logs/`, the status stays NULL. The only thing that sets it is `user_directive_parse`, which requires manual invocation.

3. **`aifp_status` has a flow to `user_directive_parse`** (condition: `null_and_directive_files_exist`) but this condition is never evaluated — there's no helper that scans for directive files.

4. **`aifp_run` checks `user_directives_status`** on every call, but since it's never set, the check always returns NULL = Case 1.

5. **No forced loading of user_directive_* directives.** Even if Case 2 is detected at session start, the AI isn't required to read the Case 2 directive documentation.

---

## 2. The Key Insight

The user pointed out the critical distinction: during `project_discovery`, when the user describes what they want to build, the AI must recognize the **fork point** between:

- **Case 1**: "I want to build an automation tool" → User wants a software project. AI helps them write the code. Standard development workflow.
- **Case 2**: "I want to automate my home lights" → User wants automation behavior, not a codebase. AI builds everything. User provides directive definitions (what to automate), AI generates the implementation.

This distinction happens naturally in the discovery conversation. The AI just needs to be explicitly told to look for it and act on it.

---

## 3. Proposed Solution

### 3.1. Add Use Case Detection to `project_discovery`

Insert a new **Branch 2.5** (between current Branch 2: Blueprint and Branch 3: Infrastructure) or integrate into Branch 2:

**New Branch: Determine Project Type (Case 1 vs Case 2)**

During the blueprint discussion, when the user describes their project's purpose, the AI must evaluate:

```
IF user describes BEHAVIOR they want automated:
  - "Turn off lights at 5pm"
  - "Scale EC2 when CPU > 80%"
  - "Send notification when X happens"
  - "Every Monday generate a report"

  → This is a Case 2 candidate.
  → AI asks: "It sounds like you want to define automation rules and have
     the system execute them. Would you like AIFP to:

     A) Build the automation infrastructure for you from directive files
        you provide (Use Case 2 — you define WHAT, AI builds HOW)
     B) Help you build an automation application as a software project
        (Use Case 1 — you code together with AI assistance)"

IF user describes SOFTWARE they want to build:
  - "A web server for..."
  - "A library that does..."
  - "A CLI tool for..."

  → This is Case 1. Proceed normally.
```

**On Case 2 selection:**

1. Set `project.user_directives_status = 'pending_discovery'` immediately
2. Modify the remaining discovery branches to be Case 2-aware:
   - **Infrastructure**: AI pre-selects Python (or asks), notes automation-specific needs (scheduler, API clients)
   - **Themes**: Default to automation themes (Trigger Handlers, Action Executors, Scheduling, Monitoring)
   - **Completion Path**: Default to automation stages (Directive Parsing → Implementation → Testing → Activation → Monitoring)
   - **Milestones**: Derived from user's automation goals, not software features
3. After discovery finalization, route to **Case 2 onboarding** instead of standard progression

### 3.2. Add Case 2 Onboarding Flow

After `project_discovery` completes for a Case 2 project, instead of routing to `aifp_status → project_progression`, route to a new sequence:

```
project_discovery (Case 2 detected)
  → Set user_directives_status = 'pending_parse'
  → Create directives/ directory in project root
  → AI tells user:
      "Project configured for automation. Next steps:
       1. Create your directive files in directives/ (YAML, JSON, or plain text)
       2. Tell me when ready and I'll parse them
       — OR describe what you want to automate and I'll help you write the directive files"
  → aifp_status (which now detects user_directives_status = 'pending_parse')
```

### 3.3. Update `aifp_status` to Handle Case 2 States

Add explicit routing for the new status values:

```
user_directives_status = NULL          → Case 1 (standard progression)
user_directives_status = 'pending_discovery' → Discovery in progress, Case 2 selected but not finalized
user_directives_status = 'pending_parse'     → Waiting for user directive files
user_directives_status = 'in_progress'       → AI is building/modifying automation code
user_directives_status = 'active'            → Directives running
user_directives_status = 'disabled'          → Paused
```

When `aifp_status` detects `pending_parse`:
- Check `directives/` directory for files
- If files found: Proactively offer to parse them → route to `user_directive_parse`
- If no files: Remind user to create directive files or offer to help write them

### 3.4. Force Case 2 Directive Loading at Session Start

When `aifp_run(is_new_session=true)` detects `user_directives_status` is not NULL:

1. **Automatically load all `user_directive_*` directive documentation** via `get_directive_content()` for each of the 9 directives
2. Include a `case_2_context` key in the session bundle with:
   - Current `user_directives_status` value
   - Count of parsed/active/pending directives
   - Next recommended action based on status
   - The full pipeline reminder: parse → validate → implement → approve → activate
3. Add to `aifp_run(is_new_session=false)` return:
   - "This is a Use Case 2 project. user_directive_* directives apply."
   - Current status and next action

### 3.5. Add Directive Flow Entries

**New flows in `directive_flow_project.json`:**

```
project_discovery → user_directive_parse
  condition: user_selects_case_2 AND directive_files_exist
  priority: 100
  description: "Case 2 selected during discovery with existing directive files"

project_discovery → aifp_status
  condition: user_selects_case_2 AND no_directive_files
  priority: 95
  description: "Case 2 selected, waiting for user to provide directive files"

aifp_status → user_directive_parse
  condition: user_directives_status = 'pending_parse' AND directive_files_exist
  priority: 100
  description: "Directive files detected, parse them"
```

### 3.6. Update System Prompt and Supportive Context

**System prompt** — Add to behavioral rules:

```
**9. Use Case 2 Detection During Discovery**
During project_discovery, evaluate if user describes automation BEHAVIOR
(what they want automated) vs SOFTWARE (what they want to build).
If automation behavior: Present Case 1 vs Case 2 choice.
If Case 2 selected: Set user_directives_status, adapt discovery for automation,
route to Case 2 onboarding.
When user_directives_status is not NULL at session start: This is a Case 2 project.
user_directive_* directives are your primary workflow.
```

**Supportive context** — Add Case 2 detection section with example conversations showing the fork point.

---

## 4. New Status Value: `pending_discovery`

The current status values are: NULL, in_progress, active, disabled.

**Add**: `pending_discovery` and `pending_parse`

```
NULL               → Not a Case 2 project (Case 1)
pending_discovery  → User selected Case 2 during discovery, discovery still in progress
pending_parse      → Discovery complete, waiting for directive files
in_progress        → AI is building/modifying automation code (parse started)
active             → Directives running
disabled           → Paused
```

This gives `aifp_status` clear routing signals at every stage.

---

## 5. Files That Need Changes

| File | Change |
|---|---|
| `src/aifp/reference/directives/project_discovery.md` | Add Case 2 detection branch, modify downstream branches for Case 2 awareness |
| `src/aifp/reference/directives/project_init.md` | Document that init does NOT determine Case 1 vs 2 — discovery does |
| `src/aifp/reference/directives/aifp_status.md` | Add routing for `pending_discovery`, `pending_parse` statuses |
| `src/aifp/reference/directives/aifp_run.md` | Add forced Case 2 directive loading at session start |
| `docs/directives-json/directives-project.json` | Update aifp_run, aifp_status directive definitions |
| `docs/directives-json/directives-user-system.json` | Update status_semantics with new values |
| `docs/directives-json/directive_flow_project.json` | Add new flows for Case 2 routing |
| `docs/db-schema/schemaExampleProject.sql` | Update CHECK constraint for user_directives_status to include new values |
| `sys-prompt/aifp_system_prompt.txt` (or proposed) | Add behavioral rule 9 |
| `src/aifp/reference/guides/supportive_context.txt` | Update Use Case 2 section with detection details |
| `src/aifp/helpers/orchestrators/entry_points.py` | Update `aifp_run` to load Case 2 directives when detected |

---

## 6. Summary

The fix is architecturally simple: **project_discovery is the natural fork point**. During the blueprint conversation, the AI already asks "what is this project's purpose?" — it just needs to recognize automation-behavior answers as Case 2 candidates and present the explicit choice.

Once chosen, the system sets `user_directives_status` immediately (not waiting for parse), which cascades through all the existing routing infrastructure (`aifp_status`, `aifp_run`, directive flows) that already checks this field — it just never gets set today.

The forced loading of Case 2 directives at session start ensures the AI doesn't drift back to Case 1 behavior in long sessions. The new `pending_discovery` and `pending_parse` statuses give `aifp_status` clear signals for routing at every stage of the Case 2 lifecycle.
