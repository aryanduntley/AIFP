# Directive & Helper Mapping Implementation Plan

**Date**: 2025-12-17
**Purpose**: Comprehensive plan for mapping directives and helpers efficiently
**Status**: Planning phase

---

## Critical Architectural Decision: aifp_run Efficiency

### The Problem

`aifp_run` is called frequently throughout a session. If it always calls `aifp_status` to get comprehensive state, this becomes wasteful processing:

```
User: "Add authentication to the app"
AI: calls aifp_run → calls aifp_status (fetches full state)

User: "Now add a login page"
AI: calls aifp_run → calls aifp_status (fetches full state AGAIN - wasteful!)
```

### The Solution: Smart Status Management

**aifp_run as both directive AND helper with conditional status fetching**

#### Dual Role Design

**1. aifp_run as MCP Tool (Helper)**
- `is_tool = true`
- Callable directly by AI via MCP
- Parameters:
  ```json
  {
    "user_request": "string",
    "get_status": "boolean (default: false)"
  }
  ```

**2. aifp_run as Directive**
- Orchestration guidance document
- Workflow defines when to fetch status vs. use cached state

#### Workflow Logic

```
aifp_run(user_request, get_status=false)
  ├─ IF get_status=true:
  │    ├─ Call aifp_status helper
  │    ├─ Return comprehensive state
  │    └─ Return directive suggestions based on state
  │
  └─ IF get_status=false (default):
       ├─ Return common directive starting points
       ├─ Return guidance: "Use get_next_directives_from_status() if you have status cached"
       └─ Return guidance: "Call aifp_run(get_status=true) if you need fresh status"
```

#### When to Use get_status=true

**First interaction of session**:
```
AI: aifp_run(user_request="Initialize project", get_status=true)
Returns: Full status + directive suggestions
AI caches status in context
```

**After major state changes**:
- Project initialization complete
- Milestone marked complete
- Multiple tasks completed
- Long break between interactions

**When explicitly needed**:
- User asks "what's the status?"
- AI unsure of current state
- After errors/failures

#### When to Use get_status=false (default)

**Continuation work** (most common):
```
AI has status from previous aifp_run call
User: "Add login function"
AI: aifp_run(user_request="Add login function", get_status=false)
Returns: Common starting points + guidance to query directive_flow
AI uses cached status + directive_flow queries to determine path
```

---

## Architecture Overview

### Three Interconnected Systems

```
┌─────────────────────────────────────────────────────────────┐
│                    aifp_core.db                             │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │  directives  │  │ helper_functions│  │ directive_flow │ │
│  └───────┬──────┘  └────────┬────────┘  └───────┬────────┘ │
│          │                  │                    │          │
│          └──────────────────┴────────────────────┘          │
│                             │                               │
│                  ┌──────────▼──────────┐                   │
│                  │  directive_helpers  │                   │
│                  │  (junction table)   │                   │
│                  └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Mapping Relationships

**1. Directive Flow** (`directive_flow` table)
- **Question**: "After this directive, what can come next?"
- **Maps**: directive → directive (many-to-many)
- **Attributes**: flow_type, conditions, priority

**2. Directive-Helper Usage** (`directive_helpers` table via helper JSON files)
- **Question**: "What helpers does this directive use?"
- **Maps**: directive → helper (many-to-many)
- **Attributes**: execution_context, sequence_order, is_required

**3. Helper File Paths** (helper JSON files)
- **Question**: "Where does this helper live in the codebase?"
- **Maps**: helper → file_path (one-to-one)

---

## Implementation Phases

### Phase 0: Fix aifp_run Architecture (1 day) ⚡ ✅ COMPLETE

**Task**: Update aifp_run helper and directive definitions

**Status**: ✅ COMPLETE - 2025-12-17
**Completion Report**: `docs/PHASE_0_COMPLETE.md`

**A. Update Helper JSON** (`docs/helpers/json/helpers-orchestrators.json`):

```json
{
  "name": "aifp_run",
  "file_path": "helpers/orchestrators/orchestrators.py",
  "parameters": [
    {
      "name": "user_request",
      "type": "string",
      "required": true,
      "default": null,
      "description": "The user's natural language request"
    },
    {
      "name": "get_status",
      "type": "boolean",
      "required": false,
      "default": false,
      "description": "Whether to fetch comprehensive status. Use true for first interaction or after major state changes. Use false (default) for continuation work."
    }
  ],
  "purpose": "Main entry point orchestrator. Routes requests and optionally fetches comprehensive status.",
  "error_handling": "Returns error message if database not accessible. Returns empty suggestions if no directives match.",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "If get_status=true: Returns comprehensive project state from aifp_status",
    "If get_status=false: Returns common directive starting points only",
    "Always includes: Guidance on querying directive_flow table with get_next_directives_from_status()",
    "Always includes: Suggestion on when to call aifp_run(get_status=true) for fresh status",
    "Directive suggestions based on user_request keywords"
  ],
  "target_database": "orchestrator",
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "self_invocation",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "aifp_run directive uses aifp_run helper as entry point"
    }
  ]
}
```

**B. Update Directive JSON** (`docs/directives-json/directives-project.json`, aifp_run directive):

Add to workflow trunk:
```json
{
  "step": "evaluate_get_status_parameter",
  "description": "Check if fresh status needed",
  "branches": [
    {
      "if": "get_status=true",
      "then": "fetch_comprehensive_status",
      "details": {
        "call_helper": "aifp_status",
        "cache_in_context": true,
        "return_with_suggestions": true
      }
    },
    {
      "if": "get_status=false",
      "then": "return_common_starting_points",
      "details": {
        "include_directive_flow_guidance": true,
        "assume_ai_has_cached_status": true,
        "suggest_directive_flow_queries": [
          "get_next_directives_from_status()",
          "get_conditional_work_paths()",
          "get_completion_loop_target()"
        ]
      }
    }
  ]
}
```

**C. Update System Prompt** (`sys-prompt/aifp_system_prompt.txt`):

Add guidance:
```
When calling aifp_run:
- First interaction: aifp_run(user_request, get_status=true)
- Continuation work: aifp_run(user_request, get_status=false) [default]
- After major changes: aifp_run(user_request, get_status=true)

Cache status in your context. Don't re-fetch unless needed.
```

**Success Criteria**:
- [x] Helper JSON updated with get_status parameter ✅
- [x] Directive JSON workflow includes status evaluation logic ✅
- [x] System prompt includes usage guidance ✅
- [x] Implementation note created for future coding phase ✅
- [x] Documentation clarifies aifp_status can be called independently ✅

---

### Phase 1: Map Core Workflow Path (2-3 days) ⚡ ✅ COMPLETE

**Goal**: Create the foundational directive flow representing the standard project workflow path

**Status**: ✅ COMPLETE - 2025-12-17
**Completion Report**: `docs/PHASE_1_COMPLETE.md`

**Input Files**:
- `docs/notes.txt` (workflow thinking)
- `docs/directives-json/directives-project.json` (project directives)

**Output Files**:
- `docs/DIRECTIVE_WORKFLOW_PATH.md` (comprehensive documentation) ✅ CREATED
- `docs/directives-json/directive_flow_project.json` (53 project flows) ✅ CREATED

**File Organization** (verified 2025-12-18):
- **directive_flow_project.json** - Complete project management workflow (53 flows)
  - Includes: Project directives, orchestrators (aifp_run/aifp_status), git integration (6 flows), Use Case 2 flows (10 flows)
  - Git and orchestrators stay here (they ARE the project workflow, not separate)
- **directive_flow_user_preferences.json** - User preference meta-directives (Phase 7, ~8-12 flows)
- **directive_flow_fp.json** - FP directive reference flows (Phase 4, ~5-10 flows)
- **directive_flow_core.json** - Core MCP operations if needed (TBD, ~3-5 flows)

#### Workflow Path Structure

**1. Entry → Status** (always first)
```
aifp_run (entry point, get_status parameter determines next step)
  ↓
aifp_status (when get_status=true - comprehensive state fetch)
```

**2. Initialization Branch** (project not initialized)
```
aifp_status
  ↓ (if project_initialized=false)
project_init
  ↓ (loop back)
aifp_status
  ↓
project_task_decomposition (create initial tasks)
  ↓ (loop back)
aifp_status
```

**3. Active Work Branch** (project initialized, has tasks)
```
aifp_status
  ↓ (if has_incomplete_items)
[work directives]
  ├─→ project_file_write
  ├─→ project_task_update
  └─→ [other work directives]
  ↓ (when item/task/milestone complete)
[completion directives]
  ├─→ project_task_complete
  ├─→ project_subtask_complete
  ├─→ project_sidequest_complete
  └─→ project_milestone_complete
  ↓ (always loop back)
aifp_status (re-evaluate state)
```

**4. No Work Branch** (no incomplete items)
```
aifp_status
  ↓ (if no_incomplete_items)
project_task_decomposition (create new tasks)
  ↓ OR
project_completion_check (if all done)
  ↓
project_archive
```

**5. Loop-Back Pattern** (critical for all completion directives)
```
ALL completion directives → aifp_status
- project_task_complete → aifp_status
- project_subtask_complete → aifp_status
- project_sidequest_complete → aifp_status
- project_milestone_complete → aifp_status
- project_completion_check → aifp_status
```

#### Concrete Steps

**Step 1.1**: Document comprehensive workflow path
- Create `docs/DIRECTIVE_WORKFLOW_PATH.md`
- Include state diagrams
- Document all conditional branches
- Explain loop-back pattern
- Reference notes.txt thinking

**Step 1.2**: Translate to directive_flow_project.json ✅ COMPLETE
- ✅ Added 53 core flow entries (exceeded 20-30 target)
- ✅ Set priorities (100 for critical paths, 90-80 for alternatives, 70-60 for optional)
- ✅ Documented conditions clearly
- ✅ Used flow_types: status_branch, completion_loop, conditional, canonical, error_handler

**Step 1.3**: Create helper to query directive_flow
- Ensure helpers exist (already defined in core helpers):
  - `get_next_directives_from_status(current_directive, state_object)`
  - `get_conditional_work_paths(state_object)`
  - `get_completion_loop_target(completion_directive_name)`

**Success Criteria**:
- [x] DIRECTIVE_WORKFLOW_PATH.md created with full path documentation ✅
- [x] directive_flow_project.json has 53 core flow entries (exceeded 20-30 target) ✅
- [x] All completion directives have loop-back to aifp_status ✅
- [x] All conditional branches documented with conditions ✅
- [x] Priority values assigned (100 = primary, 90-80 = secondary, etc.) ✅
- [x] User preferences integration documented ✅
- [x] Git integration documented as standard workflow (6 flows included) ✅
- [x] Use Case 2 complete workflow documented (10 flows included) ✅
- [x] FP directives reference flow documented ✅
- [x] All 38 project directives listed and categorized ✅
- [x] File organization verified (git/orchestrators stay in project file) ✅

---

### Phase 2: Map Core Directive Details (1-2 weeks) ✅ COMPLETE

**Goal**: Complete mapping for the ~20-30 core directives used in the workflow path

**Status**: COMPLETE (2025-12-19) - Week 1: 7 critical + 2 amendments, Week 2: 10 secondary
**Progress**: 53 → 89 flows (+36), 55% → 100% directive coverage

**Directives to Map** (in priority order):

**Tier 1: Entry & Status** (2 directives)
1. aifp_run
2. aifp_status

**Tier 2: Initialization** (3 directives)
3. project_init
4. project_blueprint_read
5. project_task_decomposition

**Tier 3: Core Work** (8 directives)
6. project_file_write
7. project_task_create
8. project_task_update
9. project_subtask_create
10. project_sidequest_create
11. project_item_create
12. project_update_db
13. project_reserve_finalize

**Tier 4: Completion** (5 directives)
14. project_task_complete
15. project_subtask_complete
16. project_sidequest_complete
17. project_milestone_complete
18. project_completion_check

**Tier 5: Additional Flows** (5 directives)
19. project_blueprint_update
20. project_evolution
21. project_compliance_check
22. project_error_handling
23. aifp_help

#### Process Per Directive

For each directive:

**A. Read Directive JSON**
```bash
cat docs/directives-json/directives-project.json | jq '.[] | select(.name=="project_file_write")'
```

**B. Analyze Workflow**
- What does this directive do?
- What are the trunk steps?
- What are the branch conditions?
- What helpers does it call? (look for database operations, queries, etc.)

**C. Map Additional Directive Flows** (add to directive_flow_project.json)
- What directives can this flow to? (beyond core path)
- What are the conditions?
- What are the priorities?
- Error paths? Alternative paths?

**D. Identify Helpers Used**
- Database queries (get_* helpers)
- Database writes (add_*, update_*, delete_* helpers)
- Orchestration helpers (aifp_status, get_current_progress, etc.)
- Validation helpers

**E. Update Helper JSON Files**

For each helper used, add entry to its `used_by_directives` array:

```json
{
  "directive_name": "project_file_write",
  "execution_context": "reserve_file_before_write",
  "sequence_order": 1,
  "is_required": true,
  "parameters_mapping": {
    "file_name": "workflow.file_name",
    "file_path": "workflow.file_path"
  },
  "description": "Reserves file entry in database to get ID before writing file content"
}
```

**F. Update Tracking Checklist**
- Mark directive as complete in `DIRECTIVES_MAPPING_PROGRESS.md`
- Mark helpers as complete in `HELPER_FUNCTIONS_MAPPING_PROGRESS.md`

**Week 1 Complete** (2025-12-19):
- [x] 7 critical directives added (task_update, item_create, reserve_finalize, file_read, file_delete, add_path, aifp_help)
- [x] 2 critical amendments (user_preferences_sync condition, compliance_check opt-in clarification)
- [x] directive_flow_project.json: 53 → 69 flows (+16)
- [x] Project directive coverage: 55% → 74% (21 → 28 of 38)
- [x] Category coverage improvements:
  - Entry & Status: 67% → 100%
  - Task Management: 80% → 100%
  - File & Code: 20% → 100%

**Week 2 Complete** (2025-12-19):
- [x] 10 secondary directives (auto_resume, auto_summary, backup_restore, dependency_map, dependency_sync, evolution, integrity_check, performance_summary, refactor_path, theme_flow_mapping)
- [x] 20 additional flows added → 89 total flows
- [x] directive_flow_project.json complete (100% coverage)

**Success Criteria**:
- [x] 7/7 critical directives mapped (Week 1) ✅
- [x] 10/10 secondary directives mapped (Week 2) ✅
- [x] directive_flow_project.json: 89 total flows (v1.2.0) ✅
- [x] 100% project directive coverage (38/38) ✅
- [ ] Core helpers have used_by_directives populated (Phase 8)
- [ ] Tracking checklists updated (in progress)

---

### Phase 3: Map Remaining Project Directives ✅ MERGED WITH PHASE 2

**Goal**: Complete mapping for all remaining project management directives

**Status**: COMPLETE (merged into Phase 2-3) - All project directives now have flows

**All Directives Mapped** (38/38):
- ✅ All critical directives (Phase 2 Week 1)
- ✅ All secondary directives (Phase 2 Week 2)
- ✅ All categories at 100% coverage

**Success Criteria**:
- [x] All project directives mapped ✅
- [x] directive_flow_project.json: 89 total flows (v1.2.0) ✅
- [x] 100% project directive coverage ✅
- [ ] Project helpers have used_by_directives populated (Phase 8)

---

### Phase 4: Map FP Reference Consultation Flows (2-3 days) ⚡ UPDATED SCOPE

**Goal**: Create FP reference consultation flows (NOT execution flows)

**Key Architectural Clarification** (2025-12-19):

**FP Compliance Already Handled**:
- `project_compliance_check` flows already in directive_flow_project.json (5 flows, all opt-in)
- ALL compliance checking is opt-in only (default = AI writes FP code automatically)
- FP enforcement directives do NOT need separate flows

**FP Directives = Reference Documentation**:
- 65 FP directives (29 core + 36 aux) are **reference material only**
- AI consults them inline when uncertain (via search/lookup helpers)
- They do NOT execute as part of workflow
- They do NOT have traditional directive flows

**New Approach**:

**Create directive_flow_fp.json** with consultation pattern flows (~5-10 flows):
- Reference lookup patterns (not directive → directive flows)
- Consultation flows (when/how AI queries FP references)
- Example patterns:
  - AI uncertain about currying → search_fp_directives(keyword="currying")
  - Need monad composition guidance → get_directive_content("fp_monadic_composition")
  - Wrapping OOP library → get_directive_content("fp_wrapper_generation")
- Map minimal helper usage:
  - `query_core` (to query FP directive content)
  - `get_directive_content` (to load MD documentation)
  - `search_fp_directives` (keyword search)
  - Optional: `add_note` if fp_flow_tracking enabled (opt-in)

**Success Criteria**:
- [ ] directive_flow_fp.json created with ~5-10 consultation pattern flows
- [ ] All 65 FP directives documented with reference lookup patterns
- [ ] FP reference helpers mapped with used_by_directives
- [ ] Clear separation: FP compliance (opt-in, in project) vs FP reference (consultation, in fp)

---

### Phase 5: Map User System Directives (2-3 days) ✅ COMPLETE (in directive_flow_project.json)

**Goal**: Map user directive automation system directives (9 directives)

**Status**: COMPLETE - All 9 user-system directives already integrated in directive_flow_project.json (Phase 1)

**Directives**:
- user_directive_parse
- user_directive_validate
- user_directive_implement
- user_directive_approve
- user_directive_activate
- user_directive_monitor
- user_directive_update
- user_directive_deactivate
- user_directive_status

**Key**: These follow a linear workflow:
```
user_directive_parse → validate → implement → approve → activate → monitor
                                                  ↓
                                        update (re-parse, re-validate, re-approve)
                                                  ↓
                                              deactivate
```

**Process**: Map as a distinct sub-workflow within directive_flow_project.json (already partially complete - 10 flows exist)

**Success Criteria**:
- [x] User directive sub-workflow documented in directive_flow_project.json (10 flows) ✅
- [x] All 9 user system directives integrated in project flows ✅
- [ ] User custom helpers have used_by_directives populated (Phase 8 - helper mapping)

---

### Phase 6: Map Git Directives (1-2 days) ✅ COMPLETE (in directive_flow_project.json)

**Goal**: Map Git integration directives (6 directives)

**Status**: COMPLETE - All 6 git directives already integrated in directive_flow_project.json (Phase 1)

**Directives**:
- git_init
- git_detect_external_changes
- git_create_branch
- git_detect_conflicts
- git_merge_branch
- git_sync_state

**Key**: These are invoked alongside project directives:
```
project_file_write → git_sync_state (update last_known_git_hash)
git_detect_external_changes (on session start)
git_merge_branch → git_detect_conflicts → FP-powered resolution
```

**Success Criteria**:
- [x] Git integration workflows documented in directive_flow_project.json (6 flows) ✅
- [x] All 6 git directives integrated as standard workflow (not conditional) ✅
- [ ] Git helpers have used_by_directives populated (Phase 8 - helper mapping)

---

### Phase 7: Map User Preference Directives (1 day)

**Goal**: Map user preference management directives (7 directives)

**Directives**:
- user_preferences_sync
- user_preferences_update
- user_preferences_learn
- user_preferences_export
- user_preferences_import
- project_notes_log
- tracking_toggle

**Key**: These are meta-directives (they modify AI behavior for other directives)

**Success Criteria**:
- [ ] All 7 user preference directives mapped
- [ ] directive_flow_user_preferences.json created (~8-12 flows)
- [ ] Settings helpers have used_by_directives populated

---

### Phase 8: Finalize & Validate (2-3 days)

**Goal**: Complete all remaining mappings and validate integrity

**Tasks**:

**A. Fill Missing Helper Mappings**
- Review all 201 helpers
- Ensure all have at least one used_by_directives entry
- Document helpers that truly have zero directive usage (should be rare)

**B. Assign File Paths**
- Replace all `TODO_helpers/core/module.py` placeholders
- Finalize actual file structure in `src/aifp/helpers/`
- Update all helper JSON files

**C. Validate Data Integrity**
- All directive references in used_by_directives exist in directive JSON files
- All helper references in directive_flow exist in helper JSON files
- All condition_keys reference valid state object fields
- All flow_types use valid enum values

**D. Create Validation Script**
```python
# docs/directives-json/validate_mappings.py
# Validates:
# - All directive names in used_by_directives exist
# - All helper names in directive_flow exist
# - No orphaned entries
# - All required fields present
```

**E. Update Documentation**
- Final statistics (X flows mapped, Y helpers mapped)
- Coverage report (% of directives with flows, % of helpers with directive usage)

**Success Criteria**:
- [ ] All 201 helpers have file_path assigned
- [ ] All 201 helpers have at least one used_by_directives entry (or documented as unused)
- [ ] directive_flow.json complete (estimated 120-150 flows)
- [ ] Validation script passes
- [ ] Coverage report shows >95% mapping completion

---

## File Structure After Completion

```
docs/
├── DIRECTIVE_WORKFLOW_PATH.md           ✅ CREATED - Phase 1
├── DIRECTIVE_HELPER_MAPPING_COMPLETE.md ⚡ NEW - Phase 8 (completion report)
├── helpers/
│   └── json/
│       ├── helpers-index.json           ✅ file_path + used_by_directives complete
│       ├── helpers-core.json            ✅ file_path + used_by_directives complete
│       ├── helpers-git.json             ✅ file_path + used_by_directives complete
│       ├── helpers-orchestrators.json   ✅ file_path + used_by_directives complete
│       ├── helpers-project-1.json       ✅ file_path + used_by_directives complete
│       ├── helpers-project-2.json       ✅ file_path + used_by_directives complete
│       ├── helpers-project-3.json       ✅ file_path + used_by_directives complete
│       ├── helpers-settings.json        ✅ file_path + used_by_directives complete
│       └── helpers-user-custom.json     ✅ file_path + used_by_directives complete
└── directives-json/
    ├── directive_flow_project.json      ✅ 53 flows (Phase 1), target 100-120 total
    ├── directive_flow_user_preferences.json ⚡ Phase 7 (~8-12 flows)
    ├── directive_flow_fp.json           ⚡ Phase 4 (~5-10 flows)
    ├── directive_flow_core.json         ⚡ TBD (~3-5 flows if needed)
    ├── validate_mappings.py             ⚡ NEW - Phase 8
    └── Tasks/
        ├── DIRECTIVES_MAPPING_PROGRESS.md  ✅ All checked
        └── HELPER_FUNCTIONS_MAPPING_PROGRESS.md ✅ All checked
```

---

## Timeline Estimate (Updated 2025-12-19)

| Phase | Duration | Status | Deliverable |
|-------|----------|--------|-------------|
| Phase 0: Fix aifp_run | 1 day | ✅ COMPLETE | aifp_run helper/directive updated |
| Phase 1: Core workflow path | 2-3 days | ✅ COMPLETE | directive_flow_project.json (53 flows) |
| **Phase 2-3: All project directives** | **1 day** | **✅ COMPLETE** | **directive_flow_project.json (89 flows, 100% coverage)** |
| Phase 4: FP reference flows | 2-3 days | ⚡ NEXT | directive_flow_fp.json (~5-10 flows) |
| Phase 5: User system directives | ~~2-3 days~~ | ✅ IN PHASE 1 | Already in project flows |
| Phase 6: Git directives | ~~1-2 days~~ | ✅ IN PHASE 1 | Already in project flows |
| Phase 7: User preference directives | 1 day | ⚡ PENDING | directive_flow_user_preferences.json (~8-12 flows) |
| Phase 8: Finalize & validate | 2-3 days | ⚡ PENDING | Helper mapping, file paths, validation |
| **TOTAL** | **~1 week remaining** | **70% COMPLETE** | **3 flow files total** |

**Completed Phases**:
- ✅ Phase 0-1: Complete (aifp_run optimization + core workflow)
- ✅ Phase 2-3: Complete (all 38 project directives, 89 flows, v1.2.0)
- ✅ Phase 5-6: Complete (integrated in Phase 1)

**Remaining Phases**:
- ⚡ Phase 4: FP reference consultation flows (2-3 days)
- ⚡ Phase 7: User preference flows (1 day)
- ⚡ Phase 8: Helper mapping + validation (2-3 days)

---

## Key Principles

### 1. Status Efficiency
- **Cache status** in AI context
- **Don't re-fetch** unless needed
- **Use get_status parameter** to control when status is fetched

### 2. Independent Mapping
- **Directives standalone**: Each directive can be understood independently
- **Helpers standalone**: Each helper documents its own purpose and usage
- **Flow standalone**: directive_flow provides navigation without needing full directive details

### 3. Conjunction Mapping
- **Directives reference helpers**: via used_by_directives field in helper JSON
- **Directives reference directives**: via directive_flow.json
- **System prompt coordinates**: Tells AI when to query which system

### 4. Progressive Enhancement
- **Core path first**: Get the happy path working
- **Details later**: Add alternative paths, error paths, edge cases
- **Validate continuously**: Use validation script throughout

---

## Deliverables Checklist

### Phase 0 (Prerequisite)
- [ ] aifp_run helper JSON updated with get_status parameter
- [ ] aifp_run directive JSON updated with status evaluation logic
- [ ] System prompt updated with usage guidance
- [ ] Implementation note created

### Phase 1 (Foundation)
- [ ] DIRECTIVE_WORKFLOW_PATH.md created
- [ ] directive_flow.json created with 20-30 core flows
- [ ] Core path documented and validated

### Phases 2-7 (Detailed Mapping)
- [ ] All 125 directives mapped in tracking checklist
- [ ] All 201 helpers have used_by_directives populated
- [ ] All 201 helpers have file_path assigned
- [ ] directive_flow.json has 120-150 flow entries

### Phase 8 (Finalization)
- [ ] validate_mappings.py script created and passing
- [ ] DIRECTIVE_HELPER_MAPPING_COMPLETE.md report created
- [ ] Coverage report shows >95% completion
- [ ] All TODO placeholders resolved

---

## Success Metrics

**Completeness**:
- ✅ 125/125 directives evaluated (100%)
- ✅ 201/201 helpers have file_path (100%)
- ✅ 195+/201 helpers have directive usage (>95%)
- ✅ 120-140 directive flows mapped across multiple files:
  - directive_flow_project.json: 100-120 flows
  - directive_flow_user_preferences.json: 8-12 flows
  - directive_flow_fp.json: 5-10 flows
  - directive_flow_core.json: 3-5 flows (if needed)

**Quality**:
- ✅ Validation script passes (no orphaned references)
- ✅ All core workflow paths documented
- ✅ All loop-back patterns implemented
- ✅ All priorities assigned logically

**Efficiency**:
- ✅ aifp_run optimized with get_status parameter
- ✅ Status caching guidance in system prompt
- ✅ directive_flow queries minimize directive lookup overhead

---

## Next Immediate Action

**Start with Phase 0: Fix aifp_run Architecture**

This is the prerequisite that addresses your efficiency concern. Once complete, we can proceed with confidence to Phase 1.

**Estimated Time**: 1 day
**Output**: Updated aifp_run helper JSON, directive JSON, and system prompt guidance

Ready to begin Phase 0?

---

**Plan Created**: 2025-12-17
**Status**: Ready for execution
**First Phase**: Phase 0 (aifp_run optimization)
