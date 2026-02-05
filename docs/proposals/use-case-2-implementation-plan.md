# Use Case 2 Routing Fix - Implementation Plan

**Date**: 2026-02-04
**Status**: Implementation Plan
**Based on**: `docs/proposals/use-case-2-routing-fix.md`

---

## Executive Summary

Use Case 2 (custom directive automation) currently has no reliable entry point. The system is entirely reactive - users must manually invoke each step. This implementation plan addresses the gap by:

1. Adding Case 2 detection during `project_discovery`
2. Creating a conversational onboarding flow for directive submission
3. Routing through the existing directive pipeline (parse → validate → implement → approve → activate)
4. Recognizing that `user_directive_implement` IS essentially Case 1 development

**Key Insight**: When a user selects Case 2, the AI doesn't just "run their directives" - it builds an entire software project (FP-compliant code in `src/`) that will execute those directives. The implementation phase uses all standard AIFP project management (file tracking, task creation, milestones). Only after the software is complete and user-approved does the system enter automated execution mode.

---

## The Complete Case 2 Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         CASE 2 DETECTION PHASE                             │
├────────────────────────────────────────────────────────────────────────────┤
│ project_discovery (blueprint discussion)                                    │
│   └─ AI detects automation BEHAVIOR (not software to build)                │
│   └─ Presents Case 1 vs Case 2 choice                                      │
│   └─ User selects Case 2                                                   │
│   └─ Sets user_directives_status = 'pending_discovery'                     │
│   └─ Adapts remaining discovery for automation context                     │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         ONBOARDING PHASE                                   │
├────────────────────────────────────────────────────────────────────────────┤
│ After discovery finalization:                                              │
│   └─ Sets user_directives_status = 'pending_parse'                         │
│   └─ Creates directives/ directory                                         │
│   └─ AI asks user: "Where are your directive files? Or would you like      │
│      help writing them?"                                                   │
│   └─ Discusses format options (YAML/JSON/plain text)                       │
│   └─ Reviews user's directive file(s)                                      │
│   └─ Helps refine if needed                                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         PARSING PHASE                                      │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_parse                                                       │
│   └─ Locates file (user provides path)                                     │
│   └─ Detects format (YAML/JSON/TXT)                                        │
│   └─ Parses content, extracts directives                                   │
│   └─ Identifies ambiguities (missing params, unclear triggers)             │
│   └─ Stores raw directives in user_directives.db                           │
│   └─ Sets user_directives_status = 'in_progress'                           │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION PHASE                                   │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_validate                                                    │
│   └─ Interactive Q&A to resolve ambiguities                                │
│   └─ "Which smart home platform?" / "Which specific lights?"               │
│   └─ Confirms understanding with user                                      │
│   └─ Stores validated_content in database                                  │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PHASE (Case 1 Mode)                      │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_implement                                                   │
│                                                                            │
│   THIS IS ESSENTIALLY CASE 1 DEVELOPMENT:                                  │
│   └─ Analyzes requirements (scheduler/service/handler/function)            │
│   └─ Handles dependencies (prompts user for package installation)          │
│   └─ Generates FP-compliant Python code                                    │
│   └─ Creates src/{module}.py with pure functions                           │
│   └─ Creates tests/test_{module}.py                                        │
│   └─ Creates helpers, schedulers, service configs                          │
│   └─ Updates requirements.txt                                              │
│                                                                            │
│   USES STANDARD PROJECT MANAGEMENT:                                        │
│   └─ project_file_write for all file creation                              │
│   └─ reserve → finalize flow for database IDs                              │
│   └─ project.db tracks files, functions, interactions                      │
│   └─ Tasks and milestones can be created for complex implementations       │
│                                                                            │
│   Status remains 'in_progress' until user approval                         │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         APPROVAL PHASE                                     │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_approve                                                     │
│   └─ User tests the generated implementation                               │
│   └─ "Have you tested it? Is it working?" (yes/no/needs_changes)           │
│   └─ If needs_changes: collect feedback, modify implementation             │
│   └─ If approved: marks directive approved, offers activation              │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         ACTIVATION PHASE                                   │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_activate                                                    │
│   └─ Verifies approval and implementation files                            │
│   └─ Deploys: scheduler/service/event_handler/function                     │
│   └─ Initializes execution tracking                                        │
│   └─ Sets user_directives_status = 'active'                                │
│   └─ System now RUNNING the automation                                     │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION PHASE                                    │
├────────────────────────────────────────────────────────────────────────────┤
│ user_directive_monitor / user_directive_update / user_directive_deactivate │
│   └─ Monitor: tracks executions, handles errors, health checks             │
│   └─ Update: detects source file changes, re-implements, re-approves       │
│   └─ Deactivate: stops execution, preserves implementation                 │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Schema Updates (Foundation)

**Files**:
- `src/aifp/database/schemas/project.sql` (line 26)
- `docs/db-schema/schemaExampleProject.sql` (line 14)

**Change**: Update CHECK constraint to add new status values:

```sql
-- FROM:
user_directives_status TEXT DEFAULT NULL CHECK (user_directives_status IN (NULL, 'in_progress', 'active', 'disabled'))

-- TO:
user_directives_status TEXT DEFAULT NULL CHECK (user_directives_status IN (NULL, 'pending_discovery', 'pending_parse', 'in_progress', 'active', 'disabled'))
```

**Status Value Semantics**:
| Status | Meaning |
|--------|---------|
| `NULL` | Use Case 1 project (regular software development) |
| `pending_discovery` | Case 2 selected during discovery, discovery still in progress |
| `pending_parse` | Discovery complete, waiting for user to provide directive files |
| `in_progress` | AI building/modifying automation code (implementation phase) |
| `active` | Directives running (execution phase) |
| `disabled` | Directives paused but implementation preserved |

---

### Phase 2: Helper Functions

**File**: `src/aifp/helpers/orchestrators/entry_points.py`

**IMPORTANT**: No file scanning helper is needed. The directive workflow is **conversational**:

1. AI discusses with user to find where their directive files are (user tells AI the path)
2. AI helps user create or improve directive files through discussion
3. AI understands user's intent through conversation
4. AI reviews, enhances, and creates clean optimized database entries - NOT raw user content

The raw user directive file is a starting point for discussion, not something to automatically parse and store verbatim.

#### 2.1 Add Case 2 phase/action helpers

```python
def _get_case_2_phase(status: str) -> str:
    """Pure: Get human-readable phase name for Case 2 status."""

def _get_case_2_next_action(status: str) -> str:
    """Pure: Get recommended next action for Case 2 status."""
```

#### 2.2 Update `aifp_status()` for Case 2 routing

Add `case_2_routing` to returned data when `user_directives_status` is not NULL:
- `is_case_2`: True
- `status`: Current status value
- `phase`: Human-readable phase description
- `next_action`: Recommended next step (conversational guidance)

#### 2.3 Update `aifp_run()` for Case 2 context

Around line 518-533, add Case 2 context bundling:

```python
# After supportive_context = _get_supportive_context_safe()
case_2_context = None
user_directives_status = status_data.get('user_directives_status')

if user_directives_status is not None:
    case_2_context = {
        'is_case_2': True,
        'status': user_directives_status,
        'phase': _get_case_2_phase(user_directives_status),
        'next_action': _get_case_2_next_action(user_directives_status),
        'pipeline': 'parse → validate → implement → approve → activate',
        'note': 'Implementation phase uses standard Case 1 development (file tracking, tasks, milestones)',
        'user_directive_names': (
            'user_directive_parse', 'user_directive_validate',
            'user_directive_implement', 'user_directive_approve',
            'user_directive_activate', 'user_directive_monitor',
            'user_directive_update', 'user_directive_deactivate',
            'user_directive_status'
        )
    }
```

---

### Phase 3: Directive Documentation Updates

#### 3.1 Update `project_discovery.md`

**File**: `src/aifp/reference/directives/project_discovery.md`

**Add Branch 2.5** (between Blueprint and Infrastructure):

```markdown
### Branch 2.5: Determine Project Type (Case 1 vs Case 2)

**Condition**: During blueprint discussion, before infrastructure mapping.

**Action**: Evaluate if user describes automation BEHAVIOR vs SOFTWARE to build.

**Detection Signals for Case 2 (Automation Behavior)**:
- User describes WHAT to automate, not software to build:
  - "Turn off lights at 5pm"
  - "Scale EC2 when CPU > 80%"
  - "Send notification when X happens"
  - "Every Monday generate a report"
  - "When the garage door opens after 10pm, alert me"
- Key phrases: "automate", "when X then Y", "schedule", "trigger", "monitor"
- User wants AI to build everything, not code together

**Detection Signals for Case 1 (Software Development)**:
- User describes SOFTWARE to build:
  - "A web server for..."
  - "A library that does..."
  - "A CLI tool for..."
  - "An automation tool" (they want to BUILD the tool, not USE automation)

**Steps**:
1. During blueprint discussion, evaluate user's project description
2. If Case 2 candidate detected, present explicit choice:
   ```
   "It sounds like you want to define automation rules and have the system
   execute them. Would you like AIFP to:

   A) Build the automation infrastructure from directive files you provide
      (Use Case 2 — you define WHAT to automate, AI builds everything)

   B) Help you build an automation application as a software project
      (Use Case 1 — you code together with AI assistance)"
   ```
3. **On Case 2 selection**:
   - Set `project.user_directives_status = 'pending_discovery'`
   - Create `directives/` directory in project root
   - Adapt remaining discovery branches for automation context

**Case 2 Adaptations for Downstream Branches**:
- **Infrastructure (Branch 3)**: Default Python, note scheduler/API client needs
- **Themes (Branch 4)**: Default to automation themes:
  - Trigger Handlers, Action Executors, Scheduling, Monitoring, Error Handling
- **Completion Path (Branch 5)**: Default automation stages:
  - Directive Setup, Implementation, Testing, Activation, Monitoring
- **Milestones (Branch 6)**: Derived from user's automation goals
```

**Add Branch 7.5** (Case 2 Onboarding):

```markdown
### Branch 7.5: Case 2 Onboarding (after finalization if Case 2)

**Condition**: `project.user_directives_status = 'pending_discovery'`

**Action**: Complete Case 2 setup and begin directive discussion.

**Steps**:
1. Update `project.user_directives_status = 'pending_parse'`
2. Ensure `directives/` directory exists
3. Begin conversational onboarding:
   ```
   "Project configured for automation. Now let's set up your directives.

   Do you already have directive files written?
   - If yes: Tell me where they are (e.g., 'directives/lights.yaml')
   - If no: Describe what you want to automate and I'll help you write them

   Supported formats: YAML, JSON, or plain text descriptions."
   ```
4. If user has files: Route to `user_directive_parse`
5. If user needs help: Collaboratively create directive files, then parse
6. Route to `aifp_status` when ready
```

#### 3.2 Update `aifp_status.md`

**File**: `src/aifp/reference/directives/aifp_status.md`

Add routing documentation for new status values:

```markdown
### User Directives Status Routing (Case 2 Projects)

When `user_directives_status` is not NULL, this is a Case 2 project:

| Status | Phase | AI Behavior |
|--------|-------|-------------|
| `pending_discovery` | Discovery in progress | Continue discovery with automation context |
| `pending_parse` | Waiting for directives | Ask user for directive file location or help create |
| `in_progress` | Implementation phase | Building automation code (uses Case 1 development) |
| `active` | Execution phase | Monitor directives, handle updates |
| `disabled` | Paused | Offer to reactivate or modify |

**pending_parse routing**:
- Scan for directive files in `directives/`, `automations/`, project root
- If files found: Proactively offer to parse them → `user_directive_parse`
- If no files: Ask user where files are or offer to help create them
```

#### 3.3 Update `aifp_run.md`

**File**: `src/aifp/reference/directives/aifp_run.md`

Add Case 2 directive loading documentation.

---

### Phase 4: Directive Flow Updates

**File**: `docs/directives-json/directive_flow_project.json`

Add new flows after line 90:

```json
{
  "from_directive": "project_discovery",
  "to_directive": "user_directive_parse",
  "flow_type": "conditional",
  "condition_key": "case_2_selected_and_files_exist",
  "condition_value": "true",
  "condition_description": "User selected Case 2 during discovery AND directive files already exist",
  "priority": 100,
  "description": "Case 2 with existing files - proceed to parsing",
  "flow_category": "project"
},
{
  "from_directive": "project_discovery",
  "to_directive": "aifp_status",
  "flow_type": "conditional",
  "condition_key": "case_2_selected_no_files",
  "condition_value": "true",
  "condition_description": "User selected Case 2 but no directive files exist yet",
  "priority": 95,
  "description": "Case 2 onboarding - help user create directive files",
  "flow_category": "project"
},
{
  "from_directive": "aifp_status",
  "to_directive": "user_directive_parse",
  "flow_type": "conditional",
  "condition_key": "pending_parse_and_files_exist",
  "condition_value": "true",
  "condition_description": "Status is pending_parse AND directive files detected",
  "priority": 100,
  "description": "Directive files ready for parsing",
  "flow_category": "project"
}
```

---

### Phase 5: JSON Directive Definition Updates

**File**: `docs/directives-json/directives-user-system.json`

Update `status_semantics` (lines 6-11):

```json
"status_semantics": {
  "NULL": "No user directives initialized (Use Case 1)",
  "pending_discovery": "Case 2 selected during discovery, discovery still in progress",
  "pending_parse": "Discovery complete, AI discussing directive files with user",
  "in_progress": "AI building automation code (Case 1 development mode)",
  "active": "User approved, directives executing",
  "disabled": "Directives paused, implementation preserved"
}
```

**File**: `docs/directives-json/directives-project.json`

Update `project_discovery` workflow to include Case 2 detection branch.

---

### Phase 6: System Prompt and Supportive Context

**File**: `sys-prompt/aifp_system_prompt.txt`

Add behavioral rule (after line 117):

```
8. **Use Case 2 Detection During Discovery**
   During project_discovery, evaluate if user describes automation BEHAVIOR
   (what they want automated) vs SOFTWARE (what they want to build).

   Case 2 signals: "turn off lights", "scale when", "notify when", "every Monday"
   Case 1 signals: "build a server", "create a library", "make a CLI tool"

   If Case 2 detected: Present explicit A/B choice.
   If Case 2 selected:
   - Set user_directives_status = 'pending_discovery'
   - Adapt discovery for automation context
   - After discovery: Discuss directive files with user (where are they, help write them)
   - Route through: parse → validate → implement → approve → activate

   Key insight: The implementation phase IS Case 1 development. AI builds
   FP-compliant software in src/ that will execute the directives. Use all
   standard project management (file tracking, tasks, milestones).

   When user_directives_status is not NULL at session start: This is a Case 2
   project. user_directive_* directives are your primary workflow.
```

**File**: `src/aifp/reference/guides/supportive_context.txt`

Update Section 8 (Use Case 2) to include:
- Detection signals and example conversation
- Status progression diagram
- Emphasis that implementation phase uses Case 1 development

---

## Files Summary (Implementation Order)

| Order | File | Change |
|-------|------|--------|
| 1 | `src/aifp/database/schemas/project.sql` | Add pending_discovery, pending_parse to CHECK |
| 2 | `docs/db-schema/schemaExampleProject.sql` | Mirror schema change |
| 3 | `src/aifp/helpers/orchestrators/entry_points.py` | Add scan_for_directive_files(), update aifp_status/aifp_run |
| 4 | `src/aifp/reference/directives/project_discovery.md` | Add Branch 2.5 (Case 2 detection) and Branch 7.5 (onboarding) |
| 5 | `src/aifp/reference/directives/aifp_status.md` | Add routing for new status values |
| 6 | `src/aifp/reference/directives/aifp_run.md` | Add Case 2 context loading docs |
| 7 | `docs/directives-json/directive_flow_project.json` | Add 3 new flows for Case 2 routing |
| 8 | `docs/directives-json/directives-project.json` | Update project_discovery workflow |
| 9 | `docs/directives-json/directives-user-system.json` | Update status_semantics |
| 10 | `sys-prompt/aifp_system_prompt.txt` | Add behavioral rule 8 |
| 11 | `src/aifp/reference/guides/supportive_context.txt` | Update Use Case 2 section |

---

## Verification Approach

### Unit Tests

1. **Schema test**: Verify new status values accepted by CHECK constraint
2. **Helper test**: Test `scan_for_directive_files()` with various directory structures
3. **Status routing test**: Verify correct routing for each status value

### Integration Tests

1. **Case 2 detection flow**:
   - Start new project
   - Describe automation behavior during blueprint discussion
   - Verify Case 1 vs Case 2 choice is presented
   - Select Case 2
   - Verify status transitions: `NULL → pending_discovery → pending_parse`

2. **Directive file handling**:
   - With `pending_parse` status, add directive file
   - Verify `scan_for_directive_files()` detects it
   - Verify routing to `user_directive_parse`

3. **Session resume**:
   - Create Case 2 project at various statuses
   - Call `aifp_run(is_new_session=true)`
   - Verify `case_2_context` present in bundle
   - Verify correct phase and next_action

4. **Full pipeline**:
   - Go through entire: detect → parse → validate → implement → approve → activate
   - Verify each status transition
   - Verify implementation creates files in src/ tracked in project.db

### Manual Verification

1. Start discovery, describe "automate my home lights"
2. Verify AI presents Case 1 vs Case 2 choice
3. Select Case 2, verify directory creation and status
4. Verify AI asks about directive files
5. Create directive file, verify AI offers to parse
6. Complete pipeline to activation
7. Verify directives executing

---

## Key Architectural Decisions

1. **Detection happens during discovery, not init** - `project_init` is mechanical; `project_discovery` is conversational where the fork naturally occurs

2. **Two new intermediate statuses** - `pending_discovery` and `pending_parse` provide clear routing signals at every stage

3. **Implementation IS Case 1** - `user_directive_implement` uses all standard AIFP project management. The generated code is tracked in project.db like any software project.

4. **Conversational onboarding** - AI doesn't just wait for files; it actively discusses with user where files are, helps write them if needed, reviews them before parsing

5. **Explicit user choice** - When Case 2 is detected, user must explicitly choose (not automatic) to prevent confusion
