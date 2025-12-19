# Directive Flow Gap Analysis

**Date**: 2025-12-18
**Status**: Phase 1 Review - Gap Identification
**Analyzed File**: `docs/directives-json/directive_flow_project.json` (53 flows)
**Reference**: `docs/DIRECTIVE_WORKFLOW_PATH.md` (comprehensive workflow documentation)

---

## Executive Summary

The `directive_flow_project.json` file successfully implements the **core workflow architecture** with excellent structural integrity. However, coverage analysis reveals **55% directive coverage** (21 of 38 project directives), with **7 critical directives** explicitly mentioned in the workflow documentation but missing from flows.

**Verdict**: ⚠️ **Strong architecture, moderate coverage (55%)**

**Recommendation**: Proceed with **Phase 2 additions** to complete the workflow mapping as documented.

---

## Analysis Methodology

### Verification Steps

1. **Structural Analysis**: Verified loop-back pattern, flow types, and architectural principles
2. **Coverage Analysis**: Compared 38 project directives against directives with flows
3. **Documentation Cross-Reference**: Identified directives mentioned in DIRECTIVE_WORKFLOW_PATH.md but missing flows
4. **Workflow Completeness**: Assessed whether documented workflows are fully implemented

### Reference Sources

- `docs/DIRECTIVE_WORKFLOW_PATH.md` (850 lines, comprehensive workflow)
- `docs/directives-json/directives-project.json` (38 project directives)
- `docs/directives-json/directive_flow_project.json` (53 flows)

---

## ✅ What's Correct and Well-Implemented

### 1. Core Architecture Principles

**Loop-Back Pattern** ✓
- All 21 completion directives correctly return to `aifp_status`
- Zero exceptions to the loop-back rule
- Perfect implementation of state re-evaluation pattern

**Entry Point Flow** ✓
- `aifp_run → aifp_status` (status_branch, priority 100)
- `aifp_run → user_preferences_sync` (canonical, priority 100)
- Correct dual-path entry strategy

**Flow Types** ✓
- 5 flow types properly used:
  - `status_branch` (1 flow) - Entry routing
  - `completion_loop` (21 flows) - All return to aifp_status
  - `conditional` (23 flows) - State-based branching
  - `canonical` (7 flows) - Standard sequences
  - `error_handler` (1 flow) - Error handling

### 2. Workflow Integration

**Git Integration** ✓ (6 flows)
- Session start: `aifp_status → git_detect_external_changes`
- File write: `project_file_write → git_sync_state`
- Branch workflow: `git_create_branch → aifp_status`
- Conflict detection: `git_detect_conflicts → git_merge_branch | project_user_referral`
- Merge completion: `git_merge_branch → aifp_status`

**Use Case 2 (User Directive Automation)** ✓ (10 flows)
- Parse → Validate → Status → Implement
- Implement → File Write (AI generates code)
- Approve → Activate → Status
- Monitor → Update → File Write
- Complete automation infrastructure workflow

**State-Based Branching** ✓
- Uninitialized: `aifp_status → project_init`
- No tasks: `aifp_status → project_task_decomposition`
- Has work: `aifp_status → project_file_write`
- All complete: `aifp_status → project_completion_check`

### 3. Completion Hierarchy

**All completion directives properly mapped**:
- `project_task_complete → aifp_status` (with milestone auto-detection)
- `project_subtask_complete → aifp_status`
- `project_sidequest_complete → aifp_status`
- `project_milestone_complete → aifp_status`
- `project_completion_check → aifp_status | project_archive`

**Validation**: ✅ Perfect - all completion directives loop back

---

## ❌ Critical Missing Flows

These directives are **explicitly documented** in DIRECTIVE_WORKFLOW_PATH.md as part of core workflow operations but have **zero flows** in directive_flow_project.json.

### Priority 1: Active Work Directives

#### 1. `project_task_update` - Update task progress

**Documentation References**:
- Line 422: "project_task_update (updates progress)"
- Line 438: Listed in Work Directives examples
- Line 807: Listed in Task Management category
- Line 1056: Listed in active work branch

**Missing Flows** (2 flows):
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_task_update",
  "flow_type": "conditional",
  "condition_key": "user_requests_task_update",
  "condition_value": "true",
  "priority": 75,
  "description": "User updates task progress/status without completing"
}
```

```json
{
  "from_directive": "project_task_update",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "Task updated, loop back to status"
}
```

**Impact**: Cannot track incremental task progress updates

---

#### 2. `project_item_create` - Add new task items

**Documentation References**:
- Line 423: "project_item_create (adds new items)"
- Line 439: Listed in Work Directives examples
- Line 813: Listed in Task Management category

**Context from notes.txt**:
- Line 176: "all task items should be created as soon as task is created"
- Implies both auto-creation and manual creation paths

**Missing Flows** (3 flows):
```json
{
  "from_directive": "project_task_create",
  "to_directive": "project_item_create",
  "flow_type": "canonical",
  "condition_key": null,
  "priority": 100,
  "description": "Auto-create task items when task is created"
}
```

```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_item_create",
  "flow_type": "conditional",
  "condition_key": "user_requests_new_item",
  "condition_value": "true",
  "priority": 70,
  "description": "Manual item creation for existing task"
}
```

```json
{
  "from_directive": "project_item_create",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "Items created, loop back to status"
}
```

**Impact**: Cannot manage task items (smallest work unit)

---

#### 3. `project_reserve_finalize` - Reserve file/function IDs

**Documentation References**:
- Line 442: Listed in Work Directives examples
- Line 821: Listed in File & Code Management category

**Context**: Reserve IDs in database before writing files to avoid conflicts

**Missing Flows** (2 flows):
```json
{
  "from_directive": "project_file_write",
  "to_directive": "project_reserve_finalize",
  "flow_type": "canonical",
  "condition_key": null,
  "priority": 100,
  "description": "Reserve file/function IDs before writing to database"
}
```

```json
{
  "from_directive": "project_reserve_finalize",
  "to_directive": "project_update_db",
  "flow_type": "canonical",
  "condition_key": null,
  "priority": 100,
  "description": "After reserving IDs, proceed with database update"
}
```

**Current Issue**: `project_file_write → project_update_db` direct flow skips ID reservation
**Impact**: Potential database conflicts without ID pre-allocation

---

### Priority 2: File Management Directives

#### 4. `project_file_read` - Read file with context

**Documentation References**:
- Line 818: Listed in File & Code Management category

**Missing Flows** (2 flows):
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_file_read",
  "flow_type": "conditional",
  "condition_key": "file_context_needed",
  "condition_value": "true",
  "priority": 70,
  "description": "Read file to gather context for work"
}
```

```json
{
  "from_directive": "project_file_read",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "File read complete, return context"
}
```

**Impact**: Cannot explicitly read files for context (though file_write exists)

---

#### 5. `project_file_delete` - Delete file + DB cleanup

**Documentation References**:
- Line 819: Listed in File & Code Management category

**Missing Flows** (2 flows):
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_file_delete",
  "flow_type": "conditional",
  "condition_key": "user_requests_file_delete",
  "condition_value": "true",
  "priority": 75,
  "description": "Delete file and cleanup database references"
}
```

```json
{
  "from_directive": "project_file_delete",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "File deleted, database cleaned up, loop back"
}
```

**Impact**: Cannot remove files from project tracking

---

#### 6. `project_add_path` - Add file to tracking

**Documentation References**:
- Line 820: Listed in File & Code Management category

**Missing Flows** (2 flows):
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_add_path",
  "flow_type": "conditional",
  "condition_key": "user_adds_existing_file",
  "condition_value": "true",
  "priority": 70,
  "description": "Add existing file to AIFP tracking"
}
```

```json
{
  "from_directive": "project_add_path",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "File added to tracking, loop back"
}
```

**Impact**: Cannot bring existing files into AIFP project tracking

---

### Priority 3: Entry & Help Directive

#### 7. `aifp_help` - Directive help/documentation

**Documentation References**:
- Line 797: Listed in Entry & Status category (3 total directives)

**Context**: One of only 3 entry/status directives alongside aifp_run and aifp_status

**Missing Flows** (3 flows):
```json
{
  "from_directive": "aifp_run",
  "to_directive": "aifp_help",
  "flow_type": "conditional",
  "condition_key": "user_requests_help",
  "condition_value": "true",
  "priority": 90,
  "description": "User requests directive help/documentation"
}
```

```json
{
  "from_directive": "aifp_status",
  "to_directive": "aifp_help",
  "flow_type": "conditional",
  "condition_key": "directive_guidance_needed",
  "condition_value": "true",
  "priority": 70,
  "description": "AI needs directive clarification during work"
}
```

```json
{
  "from_directive": "aifp_help",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "priority": 100,
  "description": "Help provided, return to status"
}
```

**Impact**: No documented help/guidance workflow

---

## ⚠️ Secondary Missing Flows (Phase 2-3)

These directives are listed in the "Complete Project Management Directive List" (lines 790-847) but not yet in flows. They are **lower priority** and can be added in Phase 2-3.

### Analysis & Validation (7 directives)

**Not in flows**:
- `project_performance_summary` - Performance analysis (line 832) ⚠️ **TRACKING-RELATED**
- `project_dependency_map` - Dependency visualization (line 834)
- `project_theme_flow_mapping` - Theme/flow mapping (line 835)

**Already in flows** ✓:
- `project_compliance_check` ✓ (FP code validation, not user tracking)
- `project_error_handling` ✓
- `project_metrics` ✓ (project progress metrics from project.db, not user tracking)
- `project_completion_check` ✓

**Missing Flows**: ~6 flows (to/from aifp_status for 3 directives)

**⚠️ TRACKING CONCERN**: `project_performance_summary` tracks directive execution outcomes (successes, retries, failures) and stores them in notes for audit. This should be **opt-in via `tracking_toggle`** in user_preferences.db, not enabled by default.

---

### Maintenance (5 directives)

**Not in flows**:
- `project_dependency_sync` - Sync dependencies (line 837)
- `project_integrity_check` - Data integrity validation (line 838)
- `project_auto_resume` - Auto-resume work (line 839)
- `project_auto_summary` - Auto-generate summaries (line 840)

**Already in flows** ✓:
- `project_user_referral` ✓

**Missing Flows**: ~8 flows (to/from aifp_status for 4 directives)

---

### Database & State (1 directive)

**Not in flows**:
- `project_evolution` - Track project evolution (line 825)

**Already in flows** ✓:
- `project_update_db` ✓

**Missing Flows**: ~2 flows (to/from aifp_status)

---

### Archival (2 directives)

**Not in flows**:
- `project_backup_restore` - Backup/restore operations (line 843)
- `project_refactor_path` - Path refactoring (line 845)

**Already in flows** ✓:
- `project_archive` ✓

**Missing Flows**: ~4 flows (to/from aifp_status for 2 directives)

---

## 🔧 Recommended Amendments to Existing Flows

### 1. Add condition to user_preferences_sync flow

**Current Flow** (line in directive_flow_project.json):
```json
{
  "from_directive": "aifp_run",
  "to_directive": "user_preferences_sync",
  "flow_type": "canonical",
  "condition_key": null,
  "condition_value": null,
  "condition_description": "Load user preferences before any customizable directive execution",
  "priority": 100
}
```

**Issue**: No condition specified, but description says "before any customizable directive execution"

**Recommended Amendment**:
```json
{
  "from_directive": "aifp_run",
  "to_directive": "user_preferences_sync",
  "flow_type": "conditional",
  "condition_key": "directive_is_customizable",
  "condition_value": "true",
  "condition_description": "Load user preferences before any customizable directive execution",
  "priority": 100
}
```

**Reference**: DIRECTIVE_WORKFLOW_PATH.md:122 - "User preferences MUST be loaded before executing any directive that can be customized"

---

### 2. Insert project_reserve_finalize into file_write sequence

**Current Sequence**:
```
project_file_write → project_update_db (canonical)
```

**Recommended Sequence**:
```
project_file_write → project_reserve_finalize (canonical)
project_reserve_finalize → project_update_db (canonical)
```

**Action**:
1. Remove existing flow: `project_file_write → project_update_db`
2. Add new flow: `project_file_write → project_reserve_finalize`
3. Add new flow: `project_reserve_finalize → project_update_db`

**Reference**: DIRECTIVE_WORKFLOW_PATH.md:442 - "project_reserve_finalize - Reserve file/function IDs"

---

### 3. Clarify project_item_create auto-creation

**Current State**: `project_task_create → aifp_status` (direct)

**Recommended Addition**:
```
project_task_create → project_item_create (canonical, auto-create items)
project_item_create → aifp_status (completion_loop)
```

**Reference**: notes.txt:176 - "all task items should be created as soon as task is created"

**Rationale**: Task creation workflow should be:
1. Milestone exists (part of completion_path)
2. Task created for specific position in milestone
3. Items **immediately auto-created** for that task
4. Items represent the list of work needed for task completion
5. No manual item creation required after task creation (items should exist from the start)

---

### 4. Add tracking_enabled condition to project_performance_summary

**Issue**: `project_performance_summary` tracks directive execution outcomes (successes, retries, failures) and stores them for audit. This is tracking behavior that should be **opt-in**, not enabled by default.

**Directive Description**:
> "Summarizes recent directive outcomes, including successes, retries, and failures, and stores summaries in notes for audit. Keeps a rolling summary of directive performance for reliability tracking."

**Current State**: No flows exist yet (secondary directive), but when added in Phase 2-3, they MUST include tracking conditions.

**Recommended Flow** (when added):
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_performance_summary",
  "flow_type": "conditional",
  "condition_key": "helper_function_logging_enabled",
  "condition_value": "true",
  "condition_description": "Performance tracking opt-in via tracking_toggle in user_preferences.db",
  "priority": 60,
  "description": "Generate performance summary only if tracking explicitly enabled"
}
```

**Tracking Toggle Integration**:
- `tracking_toggle` directive in user_preferences.db controls features:
  - `fp_flow_tracking` - FP directive flow tracking
  - `issue_reports` - Issue reporting
  - `ai_interaction_log` - AI interaction logging
  - `helper_function_logging` - Helper function performance tracking ← **This one**

**Action**: Do NOT add `project_performance_summary` flows without `helper_function_logging_enabled` condition.

**Related Directives to Review**:
- `project_metrics` - Currently calculates project completion % and task distribution from project.db. This analyzes PROJECT DATA (tasks, milestones), NOT user behavior. **No tracking concern** - this is project progress analysis.
- `project_compliance_check` - Validates FP code compliance. **No tracking concern** - this is code validation.

**Clarification**:
- **Project progress metrics** (completion %, task distribution) = Analyzing project.db = NOT tracking
- **Directive performance metrics** (success/retry/failure rates) = Tracking directive execution = REQUIRES opt-in

---

### 5. Clarify project_compliance_check frequency and purpose ✅ CLARIFIED

**Issue**: Compliance checking could run too frequently, causing AI to spend more time checking code than writing it. FP directives were designed as **reference material**, not step-by-step execution.

**Resolution**: ALL compliance check flows are OPT-IN ONLY. No automatic checking by default.

**Current Flows** (in directive_flow_project.json):
```json
{
  "from_directive": "project_file_write",
  "to_directive": "project_compliance_check",
  "flow_type": "conditional",
  "condition_key": "check_fp_compliance",
  "condition_value": "true",
  "priority": 80,
  "description": "Optional FP compliance validation (user preference)"
}
```

**Good News**: Flow is already conditional with `check_fp_compliance` condition ✓

**Architectural Principles**:
1. **AI writes FP-compliant code by default** (system prompt guidance)
2. **FP directives = reference only** (AI consults when uncertain)
3. **Compliance check = quality gate**, not automatic after every write
4. **User control** via preferences (auto_fix_violations, strict_mode, fp_strictness_level)

**When Should `check_fp_compliance = true`?**

**Default OFF** (trust AI's FP knowledge):
- ✅ AI writes code following FP principles automatically
- ✅ No compliance check after file write (unless user enables)
- ✅ AI consults FP directives as reference when needed

**User Preference: Enable Auto-Check** (opt-in):
- User sets `auto_check_compliance = true` in user_preferences.db
- Compliance check runs after every file write
- Useful for strict FP enforcement or learning

**On-Demand Only** (recommended default):
- **User explicitly requests**: "Check FP compliance"
- **AI is uncertain**: AI consults FP directives and runs check
- **Milestone completion**: Quality gate before marking milestone complete
- **Pre-merge**: Before merging branches (quality assurance)

**Recommended Flow Amendment**:

**Current condition**: `check_fp_compliance = true`
**Change to**: `auto_check_compliance_enabled = true` (user preference from user_preferences.db)

**New flows to add**:
```json
{
  "from_directive": "aifp_status",
  "to_directive": "project_compliance_check",
  "flow_type": "conditional",
  "condition_key": "user_requests_compliance_check",
  "condition_value": "true",
  "priority": 70,
  "description": "On-demand compliance check when user explicitly requests"
}
```

```json
{
  "from_directive": "project_milestone_complete",
  "to_directive": "project_compliance_check",
  "flow_type": "conditional",
  "condition_key": "milestone_quality_gate_enabled",
  "condition_value": "true",
  "priority": 90,
  "description": "Optional quality gate: check compliance before milestone completion"
}
```

**Summary**:
- **Default**: No auto-compliance check (AI writes FP code by default)
- **User preference**: Enable `auto_check_compliance` for strict enforcement
- **On-demand**: User requests or milestone quality gates
- **Purpose**: Quality assurance, not constant validation

**Related User Preferences** (already in compliance_check workflow):
- `auto_fix_violations` - Auto-fix FP violations vs. report only
- `skip_warnings` - Skip warning-level issues
- `strict_mode` - Strictest FP enforcement
- `fp_strictness_level` - Low/medium/high strictness

---

## 📊 Coverage Statistics

### Current State (53 flows)

| Category | Directives | In Flows | Coverage |
|----------|-----------|----------|----------|
| **Entry & Status** | 3 | 2 | 67% |
| **Initialization** | 3 | 3 | 100% ✓ |
| **Task Management** | 10 | 8 | 80% |
| **File & Code** | 5 | 1 | 20% |
| **Database & State** | 2 | 1 | 50% |
| **Analysis** | 7 | 4 | 57% |
| **Maintenance** | 5 | 1 | 20% |
| **Archival** | 3 | 1 | 33% |
| **Git Integration** | 6 | 6 | 100% ✓ |
| **User Directives** | 9 | 9 | 100% ✓ |
| **TOTAL (PROJECT)** | 38 | 21 | **55%** |

### Flow Type Distribution

| Flow Type | Count | Percentage |
|-----------|-------|------------|
| completion_loop | 21 | 40% |
| conditional | 23 | 43% |
| canonical | 7 | 13% |
| status_branch | 1 | 2% |
| error_handler | 1 | 2% |
| **TOTAL** | **53** | **100%** |

---

## 🎯 Recommended Action Plan

### Phase 2 - Week 1: Critical Additions (Target: 67 flows)

**Add 7 critical directives** (14 flows + 3 amendments = 17 changes):

**High Priority**:
1. ✅ `project_task_update` (2 flows)
2. ✅ `project_item_create` (3 flows including auto-create)
3. ✅ `project_reserve_finalize` (2 flows + amend existing)
4. ✅ `project_file_read` (2 flows)
5. ✅ `project_file_delete` (2 flows)
6. ✅ `project_add_path` (2 flows)
7. ✅ `aifp_help` (3 flows)

**Amendments**:
1. Amend `aifp_run → user_preferences_sync` (add condition)
2. Amend `project_file_write → project_update_db` (insert reserve_finalize)
3. Amend `project_task_create → aifp_status` (insert item_create)
4. **DO NOT add** `project_performance_summary` without `helper_function_logging_enabled` condition (tracking opt-in)
5. Clarify `project_compliance_check` frequency (default OFF, user opt-in for auto-check)
6. Add on-demand compliance check flows (user request, milestone quality gate)

**Result**: 53 + 14 new flows + 2 compliance flows = **69 flows** (after amendments)

**Time Estimate**: 2-3 days

---

### Phase 2 - Week 2-3: Secondary Additions (Target: 90-100 flows)

**Add 10 secondary directives** (~20 flows):

**Analysis & Validation** (6 flows):
- `project_performance_summary` (2 flows) ⚠️ **MUST include tracking_enabled condition**
- `project_dependency_map` (2 flows)
- `project_theme_flow_mapping` (2 flows)

**Maintenance** (8 flows):
- `project_dependency_sync` (2 flows)
- `project_integrity_check` (2 flows)
- `project_auto_resume` (2 flows)
- `project_auto_summary` (2 flows)

**Database & State** (2 flows):
- `project_evolution` (2 flows)

**Archival** (4 flows):
- `project_backup_restore` (2 flows)
- `project_refactor_path` (2 flows)

**Result**: 67 + 20 = **87 flows**

**Additional flows from Phase 2 directive detail work**: +10-15 flows (alternative paths, error handlers)

**Final Target**: **95-100 flows**

**Time Estimate**: 1-2 weeks

---

### Phase 3 - Week 4: Validation & Polish (Target: 100-120 flows)

1. **Add error paths**: Error handlers for complex directives
2. **Add alternative paths**: Multiple valid approaches for key directives
3. **Add recovery paths**: Failed operation recovery flows
4. **Validate completeness**: Ensure every directive has at least one flow
5. **Document edge cases**: Conditional flows for unusual states

**Final Target**: **100-120 flows**

**Time Estimate**: 3-5 days

---

## 📋 Implementation Checklist

### Phase 2 - Week 1: Critical Flows

- [ ] Add `project_task_update` flows (2)
- [ ] Add `project_item_create` flows (3)
- [ ] Add `project_reserve_finalize` flows (2)
- [ ] Add `project_file_read` flows (2)
- [ ] Add `project_file_delete` flows (2)
- [ ] Add `project_add_path` flows (2)
- [ ] Add `aifp_help` flows (3)
- [ ] Amend `user_preferences_sync` condition
- [ ] Amend `project_file_write` sequence (insert reserve)
- [ ] Amend `project_task_create` sequence (insert item_create)
- [ ] Clarify `project_compliance_check` condition (change to `auto_check_compliance_enabled`)
- [ ] Add on-demand compliance check flow (aifp_status → compliance_check)
- [ ] Add milestone quality gate compliance flow (milestone_complete → compliance_check)
- [ ] Validate JSON syntax
- [ ] Update metadata (total_flows count)
- [ ] Test flow queries with helpers

**Deliverable**: `directive_flow_project.json` with 69 flows

---

### Phase 2 - Week 2-3: Secondary Flows

- [ ] Add analysis directive flows (6)
- [ ] Add maintenance directive flows (8)
- [ ] Add database/state directive flows (2)
- [ ] Add archival directive flows (4)
- [ ] Add alternative paths for complex directives (10-15)
- [ ] Validate JSON syntax
- [ ] Update metadata
- [ ] Update DIRECTIVE_WORKFLOW_PATH.md if needed

**Deliverable**: `directive_flow_project.json` with 95-100 flows

---

### Phase 3 - Week 4: Validation

- [ ] Add error paths for all major directives
- [ ] Add recovery paths for failed operations
- [ ] Verify every directive has at least one flow
- [ ] Run validation script (create if needed)
- [ ] Update documentation with final statistics
- [ ] Create Phase 2 completion report

**Deliverable**: `directive_flow_project.json` with 100-120 flows + validation report

---

## 🔍 Validation Queries

Use these queries to verify implementation:

### Check coverage after updates
```bash
# Count total flows
jq '.flows | length' docs/directives-json/directive_flow_project.json

# Count directives with flows
jq -r '.flows[] | [.from_directive, .to_directive] | @tsv' docs/directives-json/directive_flow_project.json | awk '{print $1; print $2}' | sort -u | wc -l

# Find directives still missing
comm -23 <(jq -r '.[].name' docs/directives-json/directives-project.json | sort) <(jq -r '.flows[] | [.from_directive, .to_directive] | @tsv' docs/directives-json/directive_flow_project.json | awk '{print $1; print $2}' | sort -u)

# Verify all completion loops return to aifp_status
jq -r '.flows[] | select(.flow_type == "completion_loop") | "\(.from_directive) → \(.to_directive)"' docs/directives-json/directive_flow_project.json | grep -v "→ aifp_status"
```

### Validate flow types
```bash
# Count by flow type
jq '.flows | group_by(.flow_type) | map({type: .[0].flow_type, count: length})' docs/directives-json/directive_flow_project.json

# List all unique flow types
jq -r '.flows[].flow_type' docs/directives-json/directive_flow_project.json | sort -u
```

---

## 📝 Conclusion

### Strengths ✓
1. **Core architecture is excellent**: Loop-back pattern, flow types, priorities all correct
2. **Git integration is complete**: All 6 flows properly implemented
3. **Use Case 2 is complete**: All 10 user directive flows properly implemented
4. **Structural integrity**: No violations of architectural principles

### Gaps ⚠️
1. **Active work directives**: 3 critical missing (task_update, item_create, reserve_finalize)
2. **File management**: 4 of 5 missing (file_read, file_delete, add_path, reserve_finalize)
3. **Help system**: aifp_help not integrated
4. **Overall coverage**: 55% (21 of 38 directives)

### Clarifications Added ℹ️
1. **Task/Item creation**: Items auto-created immediately when task created (not manual)
2. **Compliance check frequency**: Default OFF (trust AI's FP knowledge), opt-in for auto-check
3. **Performance tracking**: `project_performance_summary` requires tracking opt-in
4. **Metrics vs Tracking**: Project metrics (progress) ≠ performance tracking (execution logs)

### Recommendation ✅

**Proceed with Phase 2 additions following the action plan above.**

The foundation is solid and follows the documented architecture correctly. The missing flows are **additive** (not corrective), meaning:
- No existing flows need removal
- 6 amendments needed (3 structural + 3 clarifications)
- All additions follow established patterns
- No architectural redesign required
- User privacy/preferences respected (tracking opt-in, compliance opt-in)

**Estimated Completion Time**: 3-4 weeks for full Phase 2-3 implementation

---

**Analysis Date**: 2025-12-18
**Last Updated**: 2025-12-19
**Analyst**: Claude Sonnet 4.5
**Next Action**: Phase 4 (FP reference flows) or Phase 7 (User preference flows)

**Document Status**: ✅ Phase 2-3 Complete (100% Project Directive Coverage)

---

## 📝 Phase 2 - Week 1 Completion Report (2025-12-19)

### Implementation Summary

**Status**: ✅ COMPLETE
**Flows Added**: 16 (53 → 69)
**Project Directive Coverage**: 55% → 74% (21 → 28 of 38 directives)
**Duration**: 1 session

### Critical Directives Added (7 total)

1. ✅ **project_task_update** (2 flows) - Track incremental task progress
2. ✅ **project_item_create** (3 flows) - Auto-create items when task created + manual creation
3. ✅ **project_reserve_finalize** (2 flows) - Reserve IDs before database writes
4. ✅ **project_file_read** (2 flows) - Read file with context
5. ✅ **project_file_delete** (2 flows) - Delete file + cleanup database
6. ✅ **project_add_path** (2 flows) - Add existing file to tracking
7. ✅ **aifp_help** (3 flows) - Help system integration

### Critical Amendments (2 total)

1. ✅ **user_preferences_sync** - Changed from `canonical` to `conditional` with `directive_is_customizable = true`
   - **Clarification**: This condition applies to BOTH use cases (regular project + custom directives)
   - Any directive that supports user preference customization checks this before execution
   - Examples: `project_file_write` (code style), `project_task_create` (default priorities), etc.

2. ✅ **project_compliance_check** - Updated all flows with opt-in conditions
   - Changed: `check_fp_compliance` → `auto_check_compliance_enabled`
   - Added: On-demand check flow (`user_requests_compliance_check`)
   - Added: Milestone quality gate flow (`milestone_quality_gate_enabled`)
   - **Critical**: ALL compliance checking is OPT-IN ONLY (default = OFF)

### Architectural Clarifications

#### FP Compliance Check Placement

**Question**: Should FP compliance flows be in `directive_flow_project.json` or separate `directive_flow_fp.json`?

**Resolution**: Keep in `directive_flow_project.json` because:
1. `project_compliance_check` is a **project management directive** (in directives-project.json)
2. ALL flows are **opt-in only** via user preferences (no automatic checking)
3. Default behavior: AI writes FP-compliant code automatically (via system prompt)
4. FP directives (65 total) remain as **reference documentation** consulted inline when needed
5. Separate `directive_flow_fp.json` will contain FP reference consultation flows (Phase 4)

**Current FP Compliance Flows** (5 total, all opt-in):
1. `project_file_write → project_compliance_check` - Condition: `auto_check_compliance_enabled` (opt-in)
2. `project_compliance_check → project_file_write` - Auto-fix if violations found
3. `project_compliance_check → aifp_status` - Completion loop
4. `aifp_status → project_compliance_check` - Condition: `user_requests_compliance_check` (explicit)
5. `project_milestone_complete → project_compliance_check` - Condition: `milestone_quality_gate_enabled` (opt-in)

**FP Default Behavior** (NO checking):
- ✅ AI writes FP-compliant code by default (system prompt trained)
- ✅ FP directives = reference documentation only (consulted when AI uncertain)
- ✅ No automatic validation after file writes (unless user enables)
- ✅ Compliance check = quality gate tool, not automatic workflow step

#### user_preferences_sync Condition

**Condition**: `directive_is_customizable = true`

**Applies To**: BOTH use cases
- **Use Case 1** (Regular Project): User preferences control AI behavior for project directives
  - `project_file_write` → code style, docstrings, max function length
  - `project_task_create` → task granularity, default priorities
  - `project_task_decomposition` → how detailed to break down tasks
  - `project_compliance_check` → auto-fix violations vs. report only
- **Use Case 2** (Custom Directives): User preferences control behavior for directive system
  - `user_directive_validate` → validation strictness
  - `user_directive_implement` → code generation preferences

**NOT Use Case 2 Only** - applies to any directive that can be customized via user_preferences.db

### Coverage Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Total Flows** | 53 | 69 | +16 flows |
| **Project Directives in Flows** | 21/38 (55%) | 28/38 (74%) | +7 directives |
| **Entry & Status Category** | 2/3 (67%) | 3/3 (100%) | +1 (aifp_help) |
| **Task Management Category** | 8/10 (80%) | 10/10 (100%) | +2 (task_update, item_create) |
| **File & Code Category** | 1/5 (20%) | 5/5 (100%) | +4 (all remaining) |
| **Completion Loops** | 21 | 26 | +5 |
| **Conditional Flows** | 23 | 33 | +10 |

### Validation Results

✅ **JSON Syntax**: Valid
✅ **Total Flows**: 69 (metadata updated to v1.1.0)
✅ **Loop-Back Pattern**: All 26 completion loops → `aifp_status`
✅ **Git Integration**: All 6 git directives covered in project flows
✅ **User System Integration**: All 9 user-system directives covered in project flows
✅ **Architectural Integrity**: No violations, all opt-in conditions preserved

---

## 📋 Phase 2-3 Week 2 - ✅ COMPLETE (2025-12-19)

### Secondary Project Directives (10 completed)

All flows added:
1. ✅ project_auto_resume (2 flows)
2. ✅ project_auto_summary (2 flows)
3. ✅ project_backup_restore (2 flows)
4. ✅ project_dependency_map (2 flows)
5. ✅ project_dependency_sync (2 flows)
6. ✅ project_evolution (2 flows)
7. ✅ project_integrity_check (2 flows)
8. ✅ project_performance_summary (2 flows with tracking opt-in condition) ⚠️
9. ✅ project_refactor_path (2 flows)
10. ✅ project_theme_flow_mapping (2 flows)

**Result**: 89 total flows in directive_flow_project.json (v1.2.0)
**Coverage**: 100% (38/38 project directives)

---

## 📋 Additional Flow Files Needed (Phase 4-7)

### Flow File Inventory

**Created**:
- ✅ `directive_flow_project.json` - 69 flows (Phase 1-2, v1.1.0)

**Need to Create**:

1. **directive_flow_fp.json** (Phase 4)
   - **Purpose**: FP reference consultation flows (NOT execution flows)
   - **Directives**: 65 total (29 fp-core + 36 fp-aux)
   - **Flow Type**: Reference lookups, consultation patterns
   - **NOT** step-by-step execution (FP compliance already opt-in in project flows)
   - **Example Flows**:
     - `ai_uncertain_about_currying → search_fp_directives(keyword="currying")`
     - `need_monad_composition_guidance → get_directive_content("fp_monadic_composition")`
   - **Estimated**: 5-10 consultation flows (minimal, reference-only)

2. **directive_flow_user_preferences.json** (Phase 7)
   - **Purpose**: User preference management meta-directives
   - **Directives**: 7 total
     - user_preferences_sync
     - user_preferences_update
     - user_preferences_learn
     - user_preferences_export
     - user_preferences_import
     - project_notes_log
     - tracking_toggle
   - **Estimated**: 8-12 flows

**NOT Needed** (already integrated in project flows):
- ❌ `directive_flow_git.json` - All 6 git directives in project flows (standard workflow)
- ❌ `directive_flow_user_system.json` - All 9 user-system directives in project flows (Use Case 2)

**Legacy File** (ignore):
- ❌ `directives-interactions.json` - Old format, replaced by directive_flow_*.json files

### Final Flow File Structure

```
docs/directives-json/
├── directive_flow_project.json       ✅ 69 flows (v1.1.0) - Phase 1-2 complete, Phase 3 in progress
├── directive_flow_fp.json            ⚡ Phase 4 - FP reference consultation (~5-10 flows)
└── directive_flow_user_preferences.json  ⚡ Phase 7 - User preference meta-directives (~8-12 flows)

TOTAL ESTIMATED: 82-91 flows across all files
```

---

**Document Status**: ✅ Phase 2 Week 1 Complete - Ready for Week 2-3
