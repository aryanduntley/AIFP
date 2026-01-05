# Project Compliance Check - Cleanup and Modification Plan

**Date**: 2026-01-04
**Purpose**: Document all references to `project_compliance_check` and plan for removal/modification
**Status**: Analysis Complete - Ready for Execution

---

## Executive Summary

`project_compliance_check` is currently defined as a **Project-type directive** that validates FP compliance after code writes. However, this contradicts the new architecture where **FP is baseline behavior** (enforced via system prompt, not post-write validation).

**Recommendation**:
- **Remove from project directives** (it's not project management)
- **Optional**: Repurpose as FP-type directive for consultation/validation (not automatic checking)

---

## Current State Analysis

### Directive Definition

**File**: `src/aifp/reference/directives/project_compliance_check.md`

**Current Classification**:
- Type: Project
- Level: 4
- Parent: project_update_db
- Priority: CRITICAL

**Purpose (as currently documented)**:
- "Validation gatekeeper" that checks FP compliance AFTER code writes
- Prevents non-compliant code from entering project
- Runs comprehensive FP compliance checks
- Auto-fixes violations if preferences allow

**Problems with Current Approach**:
1. ❌ **Too slow** - Checking after every file/function/line write would never complete work
2. ❌ **Wrong paradigm** - FP is now baseline (system prompt), not something checked after the fact
3. ❌ **Misclassified** - This is FP validation, not project management
4. ❌ **Redundant** - If AI writes FP code naturally, what is there to "check"?

---

## References Found

### 1. JSON Directive Files

#### directive_flow_fp.json (2 references)
**Lines 13, 949**: Notes that compliance checking exists separately in project flows
```json
"FP compliance checking (project_compliance_check) is separate - already in directive_flow_project.json"
```

**Status**: ✅ **CORRECT CLASSIFICATION** - Acknowledges it should be in FP, but notes it's currently in project

#### directives-project.json (3 references)
**Lines 877-894**: Full directive definition
- Directive name: "project_compliance_check"
- Settings: auto_fix_violations, skip_warnings, strict_mode (all removed from settings spec)
- MD file path reference

**Lines 960, 1016**: Listed as parent directive for:
- project_error_handling
- project_completion_check

**Status**: ❌ **SHOULD REMOVE** - Not a project management directive

#### directive_flow_project.json (5 references)
**Flow connections**:
- Line 621: `project_update_db` → `project_compliance_check` (conditional)
- Line 631: `project_compliance_check` → `fp_purity` (if violations)
- Line 642: `project_compliance_check` → `proceed` (if passed)
- Line 654: `project_file_write` → `project_compliance_check` (validation)
- Line 665: `git_merge_branch` → `project_compliance_check` (pre-merge)

**Status**: ❌ **SHOULD REMOVE ALL** - These flows represent post-write validation (wrong paradigm)

---

### 2. Markdown Directive Files (References to Remove)

#### user_preferences_import.md (2 references)
- Line 127: Lists `project_compliance_check.strict_mode` as example preference
- Line 332: Comment referencing same setting

**Action**: ❌ Remove references - strict_mode setting removed from spec

---

#### git_detect_external_changes.md (3 references)
- Line 142: Suggests running compliance check after detecting external changes
- Line 197: Comment about compliance recheck
- Line 374: Lists as related directive

**Action**: ❌ Remove references - External changes don't need compliance checks if FP is baseline

---

#### project_update_db.md (2 references)
- Line 376: Lists as caller (updates metadata after compliance fixes)
- Line 383: Lists as validator (validates before DB update)

**Action**: ❌ Remove references - No need to validate before DB updates if code is already FP-compliant

---

#### project_dependency_map.md (2 references)
- Line 35: Lists as directive that analyzes dependencies for violations
- Line 547: Lists as related directive

**Action**: ❌ Remove references - Dependency mapping doesn't need compliance checking

---

#### project_archive.md (1 reference)
- Line 428: "Final compliance check" before archiving

**Action**: ❌ Remove reference - No need for final check if code is always compliant

---

#### project_task_update.md (2 references)
- Line 37: "Updates tasks based on validation results"
- Line 375: Listed as related directive

**Action**: ❌ Remove references - Task updates don't need compliance validation

---

#### project_error_handling.md (3 references)
- Line 5: **Parent Directive**: project_compliance_check
- Line 324: Directive heading
- Line 494: Uses error handling for validation failures

**Action**: ⚠️ **CRITICAL** - Error handling has compliance check as PARENT
- **Must reassign parent** or remove parent relationship

---

#### project_file_read.md (3 references)
- Line 36: Reads files to validate FP adherence
- Line 392: Reads files for validation
- Line 485: Validates FP adherence

**Action**: ❌ Remove references - File reading doesn't need compliance validation

---

#### project_blueprint_read.md (1 reference)
- Line 251: Suggests running compliance check to verify consistency

**Action**: ❌ Remove reference - Blueprint reading doesn't need compliance checks

---

#### project_completion_check.md (2 references)
- Line 5: **Parent Directive**: project_compliance_check
- Line 476: Parent directive validates FP compliance before completion

**Action**: ⚠️ **CRITICAL** - Completion check has compliance as PARENT
- **Must reassign parent** or remove parent relationship

---

#### tracking_toggle.md (1 reference)
- Line 510: Can log to fp_flow_tracking if enabled

**Action**: ⚠️ **MAYBE KEEP** - If repurposed as FP directive, tracking may be valid

---

## Modification Steps

### Phase 1: Update JSON Directive Files

#### 1.1 directives-project.json
```
Action: REMOVE entire project_compliance_check directive (lines ~877-900)
- Remove directive definition
- Remove all 3 settings (already removed from settings spec)
- Remove MD file path reference
```

#### 1.2 directive_flow_project.json
```
Action: REMOVE all 5 flow connections
- Line 621: project_update_db → project_compliance_check
- Line 631: project_compliance_check → fp_purity
- Line 642: project_compliance_check → proceed
- Line 654: project_file_write → project_compliance_check
- Line 665: git_merge_branch → project_compliance_check

Impact: Check if any of these flows need alternative connections
- project_update_db: Should proceed directly (no validation needed)
- project_file_write: Should proceed directly (no validation needed)
- git_merge_branch: Should proceed directly (no validation needed)
```

#### 1.3 directive_flow_fp.json
```
Action: UPDATE notes (lines 13, 949)
- Change: "already in directive_flow_project.json"
- To: "removed - FP is now baseline behavior (system prompt)"

Optional: If repurposing as FP directive, add consultation flows
```

---

### Phase 2: Fix Parent Directive Relationships

#### 2.1 project_error_handling.md
```
Current: Parent Directive: project_compliance_check
Options:
  A) Remove parent relationship (standalone directive)
  B) Reassign parent to: project_update_db or project_file_write
  C) Reassign parent to: aifp_run (top-level)

Recommendation: Option A (standalone) - Error handling is generic utility
```

#### 2.2 project_completion_check.md
```
Current: Parent Directive: project_compliance_check
Options:
  A) Remove parent relationship (standalone directive)
  B) Reassign parent to: aifp_status or aifp_run
  C) Reassign parent to: project_milestone_complete

Recommendation: Option C (milestone_complete) - Completion is end of milestone
```

---

### Phase 3: Clean Up Markdown References

#### Remove all references from:
- [ ] user_preferences_import.md (2 lines)
- [ ] git_detect_external_changes.md (3 lines)
- [ ] project_update_db.md (2 lines)
- [ ] project_dependency_map.md (2 lines)
- [ ] project_archive.md (1 line)
- [ ] project_task_update.md (2 lines)
- [ ] project_file_read.md (3 lines)
- [ ] project_blueprint_read.md (1 line)

#### Update parent references in:
- [ ] project_error_handling.md (reassign parent)
- [ ] project_completion_check.md (reassign parent)

#### Review for potential keep:
- [ ] tracking_toggle.md (if repurposing as FP directive)

---

### Phase 4: Handle project_compliance_check.md

#### Option A: DELETE FILE
```
Reason: FP is baseline, no need for post-write validation
Impact: Complete removal from project directives
```

#### Option B: MOVE TO FP DIRECTIVES
```
Location: Move to FP directive category
Rename: fp_compliance_validate or fp_validation_check
Purpose: CONSULTATION ONLY (not automatic post-write checking)
Type: Change from "Project" to "FP"
Level: Change from 4 to appropriate FP level
Parent: Remove project_update_db parent
Usage: AI queries this directive when UNCERTAIN about FP compliance
      NOT automatically executed after every write
```

#### Option C: REPURPOSE AS USER TOOL
```
Purpose: Manual validation tool user can invoke
Usage: User explicitly requests "validate FP compliance"
Execution: On-demand only, not automatic
```

**Recommendation**: **Option B** (Move to FP directives, consultation only)
- Preserves knowledge about FP validation
- Available for AI to consult when uncertain
- Removes automatic post-write checking
- Aligns with FP directive purpose (guidance, not execution)

---

## Flow Connection Analysis

### Flows to Remove
All 5 flows currently connect compliance checking into project workflows:

```
1. project_update_db → project_compliance_check [REMOVE]
   New flow: project_update_db → proceed (direct)

2. project_file_write → project_compliance_check [REMOVE]
   New flow: project_file_write → proceed (direct)

3. git_merge_branch → project_compliance_check [REMOVE]
   New flow: git_merge_branch → proceed (direct)

4. project_compliance_check → fp_purity [REMOVE]
   Reason: No longer auto-fixing violations

5. project_compliance_check → proceed [REMOVE]
   Reason: Directive removed from workflow
```

### Flows to Verify Don't Break
After removal, ensure these directives still have valid exit paths:
- ✓ project_update_db
- ✓ project_file_write
- ✓ git_merge_branch

---

## Settings Already Removed

These settings have been removed from settings-specification.json v3.1:
- ✅ fp_strictness_level (global)
- ✅ project_compliance_check.auto_fix_violations
- ✅ project_compliance_check.skip_warnings
- ✅ project_compliance_check.strict_mode

No action needed - settings already handled.

---

## Repurposing Recommendation (If Option B)

### New FP Directive Specification

**Name**: `fp_compliance_validate` (or keep project_compliance_check if moving to FP category)

**Type**: FP (changed from Project)

**Purpose**:
- Reference guide for FP validation patterns
- CONSULTATION ONLY - AI queries when uncertain
- NOT automatic post-write execution
- User can manually invoke for project-wide audit

**When AI Consults**:
- Uncertain if code pattern is FP-compliant
- User explicitly requests validation
- Complex FP scenario needs clarification
- Refactoring legacy code to FP

**When AI Does NOT Consult**:
- After every file write (too slow)
- After every function write (unnecessary)
- During normal coding (FP is baseline)

**Changes Needed**:
1. Update header: Type: Project → Type: FP
2. Remove: Parent Directive field
3. Update: Priority from CRITICAL to Medium/Low
4. Update: "When to Apply" section (consultation not execution)
5. Remove: All workflow branches (trunk, branches, fallback)
6. Replace with: Consultation guidelines
7. Keep: Examples section (valuable reference)
8. Keep: Edge cases section (valuable guidance)
9. Update: Related Directives (remove "Called By", keep "Escalates To" as "See Also")

---

## Execution Checklist

### JSON Files (High Priority)
- [ ] directive_flow_fp.json - Update notes (2 lines)
- [ ] directives-project.json - Remove directive definition (~25 lines)
- [ ] directive_flow_project.json - Remove 5 flow connections

### Parent Relationships (Critical)
- [ ] project_error_handling.md - Reassign parent
- [ ] project_completion_check.md - Reassign parent

### MD File References (Medium Priority)
- [ ] user_preferences_import.md - Remove 2 references
- [ ] git_detect_external_changes.md - Remove 3 references
- [ ] project_update_db.md - Remove 2 references
- [ ] project_dependency_map.md - Remove 2 references
- [ ] project_archive.md - Remove 1 reference
- [ ] project_task_update.md - Remove 2 references
- [ ] project_file_read.md - Remove 3 references
- [ ] project_blueprint_read.md - Remove 1 reference

### Main Directive File (Decision Required)
- [ ] project_compliance_check.md - DELETE, MOVE, or REPURPOSE (see Option B)

### Verification
- [ ] Verify no broken flow connections
- [ ] Verify all parent relationships resolved
- [ ] Verify no orphaned references
- [ ] Update directive count in documentation

---

## Risk Assessment

### Low Risk
- Removing references from MD files (documentation only)
- Removing flows (FP is baseline, no validation needed)
- Updating notes in directive_flow_fp.json

### Medium Risk
- Removing directive from directives-project.json (affects directive count/index)
- Reassigning parent directives (affects hierarchy)

### High Risk
- NONE - FP is already baseline behavior, removing post-write validation is correct approach

---

## Validation Tests

After cleanup, verify:
1. ✅ No references to project_compliance_check in project directive files
2. ✅ project_error_handling and project_completion_check have valid parents
3. ✅ All project directive flows have valid exit paths
4. ✅ directive_flow_fp.json notes are accurate
5. ✅ Settings specification has no compliance check settings (already done)
6. ✅ System prompt doesn't reference post-write compliance checking

---

## Timeline Estimate

- Phase 1 (JSON files): ~30 minutes
- Phase 2 (Parent relationships): ~15 minutes
- Phase 3 (MD references): ~45 minutes
- Phase 4 (Main directive decision): ~30 minutes
- Verification: ~20 minutes

**Total**: ~2.5 hours

---

## Notes

- This cleanup aligns with the FP baseline architecture (FP in system prompt, not post-write validation)
- Removing automatic compliance checking will significantly improve performance
- The knowledge in project_compliance_check.md is valuable and should be preserved (Option B)
- This is part of the larger settings cleanup that reduced settings from 18 to 12

---

**Status**: Ready for execution
**Decision Required**: Choose Option A, B, or C for project_compliance_check.md
**Recommended**: Option B (Move to FP directives, consultation only)
