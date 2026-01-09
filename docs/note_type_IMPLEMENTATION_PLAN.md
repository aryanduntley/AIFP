# Note Type Implementation Plan

**Date**: 2026-01-08
**Status**: Ready to implement
**Approach**: Expand schema (keep existing + add new), clean FP directives

---

## Schema Update: COMPLETE ✅

Updated `src/aifp/database/schemas/project.sql` with expanded note_type list:

### All 14 Types Now Supported

**Original types (kept for compatibility)**:
1. `clarification` - User-confirmed decisions, intent
2. `pivot` - Project direction changes
3. `research` - AI analysis, findings
4. `entry_deletion` - Entry removal tracking
5. `warning` - Severity level (consider using severity field instead)
6. `error` - Severity level (consider using severity field instead)
7. `info` - Severity level (consider using severity field instead)
8. `auto_summary` - Automated project summaries

**New semantic types (added for better categorization)**:
9. `decision` - User decisions, confirmations (broader than clarification)
10. `evolution` - Project direction changes, architecture shifts (broader than pivot)
11. `analysis` - AI research, findings, reasoning (broader than research)
12. `task_context` - Task/milestone/sidequest lifecycle context
13. `external` - Git changes, dependency updates, file system events
14. `summary` - Manual summaries (distinct from auto_summary)

**Design Philosophy**: AI will read the CHECK list and categorize appropriately. More types = better categorization.

---

## Critical Issue: FP Directives Cleanup

### The Problem

Many FP directives have examples like:
```sql
INSERT INTO notes (content, note_type) VALUES (..., 'optimization');
```

**These are WRONG for multiple reasons**:
1. ❌ `optimization` not in schema (fails CHECK constraint)
2. ❌ Implies logging to project.db (should be user_preferences.db)
3. ❌ Implies post-write validation (FP is baseline behavior)
4. ❌ Implies tracking is standard (it's opt-in, disabled by default)

### The Truth

**FP compliance is baseline behavior**:
- AI writes FP-compliant code naturally (pure functions, immutability, no OOP)
- NO post-write validation happens
- NO automatic logging to notes table
- FP directives are **reference documentation** consulted when uncertain

**FP tracking is opt-in**:
- Only enabled via `tracking_toggle` directive
- Logs to `fp_flow_tracking` table in **user_preferences.db**
- 5% token overhead per file write
- Disabled by default for cost reasons
- Primarily for AIFP development, not normal use

---

## FP Directive Cleanup Requirements

For EVERY FP directive that references note_type or logging:

### Step 1: Remove Erroneous SQL Examples

**Find and remove**:
```sql
-- ❌ REMOVE examples like this
INSERT INTO notes (content, note_type, source, severity)
VALUES ('Function optimized for purity', 'optimization', 'directive', 'info');
```

**These types are NOT in schema**:
- optimization, compliance, refactoring, cleanup, normalization
- validation, security, performance, documentation, metadata
- wrapper, formatting, determinism, indexing

### Step 2: Add Correct Tracking Context

**Replace with clear explanation**:
```markdown
## Database Operations

**FP Compliance Tracking** (Optional, Disabled by Default):

When `fp_flow_tracking` is enabled in user_preferences.db (via tracking_toggle):
- AI MAY log FP pattern usage to `fp_flow_tracking` table
- This is for analytics and development only
- Logs to user_preferences.db, NOT project.db
- Token overhead: ~5% per file write

**Note**: FP compliance is baseline behavior enforced by system prompt.
This directive is reference documentation consulted when AI is uncertain.
NO post-write validation occurs. NO automatic logging to project.db.

**Example** (only if tracking enabled):
```sql
-- Logs to user_preferences.db.fp_flow_tracking
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    issues_json
) VALUES (
    'calculate_total',
    'src/calculator.py',
    '["fp_purity", "fp_immutability"]',
    1.0,
    NULL
);
```
```

### Step 3: Clarify Directive Purpose

Add to Purpose section of EVERY FP directive:

```markdown
## Purpose

[Existing purpose text...]

**Important**: This directive is **reference documentation** for complex FP scenarios.
AI consults this when uncertain about implementation details, edge cases, or advanced patterns.

**NOT used for**:
- ❌ Post-write validation (FP is baseline, code is already compliant)
- ❌ Automatic checking (no validation loop after file writes)
- ❌ Standard logging (tracking is opt-in, disabled by default)

**When consulted**:
- ✅ Uncertainty about FP pattern implementation
- ✅ Complex edge cases requiring guidance
- ✅ Advanced scenarios not covered by baseline knowledge
```

### Step 4: Update Workflow Sections

Ensure workflows don't imply post-write validation:

**❌ Bad (implies validation loop)**:
```markdown
### Workflow
1. AI writes function
2. Check for purity violations ← WRONG! No post-write checking
3. Log compliance to notes table ← WRONG! No automatic logging
```

**✅ Good (reference consultation)**:
```markdown
### Workflow

This is reference guidance consulted DURING code writing when AI is uncertain.

**When to consult**:
- AI unsure about purity boundary
- Complex composition scenario
- Edge case not covered by baseline FP knowledge

**NOT a validation workflow**:
- FP compliance is baseline behavior
- No post-write checking occurs
- Tracking is opt-in (disabled by default)
```

---

## Implementation Checklist

### Phase 1: Schema (Complete ✅)
- [x] Update project.sql with expanded note_type CHECK list
- [x] Keep all original types
- [x] Add 6 new semantic types
- [x] Document distinction between auto_summary and summary

### Phase 2: FP Directives Cleanup (Critical)

**For EACH FP directive file in `src/aifp/reference/directives/`**:

- [ ] Search for `INSERT INTO notes` with non-schema types
- [ ] Remove SQL examples with invalid note_types
- [ ] Add "Database Operations" section with correct tracking context
- [ ] Update "Purpose" section to clarify reference vs. validation
- [ ] Update "Workflow" section to remove validation implications
- [ ] Ensure "When to Apply" clarifies consultation triggers
- [ ] Add note about fp_flow_tracking being opt-in

**FP directive files to clean** (estimated 60+ files):
- All files in `src/aifp/reference/directives/fp_*.md`
- Priority: Core FP directives (purity, immutability, no_oop, result_types)

### Phase 3: Project Directives Update

**For project directives that reference notes**:

- [ ] `project_notes_log.md` - Update examples with new types
- [ ] `project_task_create.md` - Use `task_context` type
- [ ] `project_task_complete.md` - Use `task_context` type
- [ ] `project_milestone_complete.md` - Use `task_context` type
- [ ] `project_evolution.md` - Use `evolution` type
- [ ] `project_auto_summary.md` - Keep `auto_summary` type
- [ ] `git_detect_external_changes.md` - Use `external` type

### Phase 4: Tracking Directives Update

- [ ] `tracking_toggle.md` - Add note about fp_flow_tracking table usage
- [ ] `project_compliance_check.md` - Clarify it logs to fp_flow_tracking
- [ ] `user_preferences_learn.md` - Clarify it logs to ai_interaction_log

### Phase 5: Helper Functions

- [ ] Find all helpers that insert notes
- [ ] Update to use valid note_types from schema
- [ ] Add parameter validation against schema types

### Phase 6: Documentation

- [ ] Update README.md if it references note types
- [ ] Update system prompt if it references note types
- [ ] Create migration guide for existing databases
- [ ] Update ProjectBlueprint.md with note type taxonomy

---

## FP Directive Cleanup Script

To find all problematic references:

```bash
# Find FP directives with INSERT INTO notes
cd src/aifp/reference/directives/
grep -r "INSERT INTO notes" fp_*.md | grep -E "(optimization|compliance|refactoring|cleanup)"

# Find FP directives with note_type references
grep -r "note_type.*=" fp_*.md

# Count files needing cleanup
grep -l "INSERT INTO notes" fp_*.md | wc -l
```

**Expected findings**: ~30-40 FP directive files need cleanup

---

## Template for FP Directive Cleanup

Use this template when cleaning each FP directive:

### Remove This:
```markdown
## Database Operations

- **`notes`**: Logs optimization opportunities with `note_type = 'optimization'`
```

### Replace With This:
```markdown
## Database Operations

**Project Notes**: This directive does NOT automatically log to project.db notes table.

**FP Compliance Tracking** (Optional - Disabled by Default):

If `fp_flow_tracking` is enabled in user_preferences.db:
- AI may log FP pattern usage to `fp_flow_tracking` table
- Located in user_preferences.db, NOT project.db
- Token overhead: ~5% per file write
- Enable via: `tracking_toggle` directive

**Important**:
- FP compliance is baseline behavior (enforced by system prompt)
- This directive is reference documentation (not validation)
- No post-write checking occurs
- Tracking is opt-in for development/debugging only

**Example** (only if tracking explicitly enabled):
```sql
-- user_preferences.db.fp_flow_tracking
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    created_at
) VALUES (
    'function_name',
    'src/file.py',
    '["fp_purity", "fp_immutability"]',
    1.0,
    CURRENT_TIMESTAMP
);
```
```

---

## Validation Tests

After cleanup, verify:

1. **Schema Validation**
   ```python
   # All note types in directives must be in schema
   schema_types = get_note_types_from_schema()
   directive_types = get_note_types_from_directives()
   invalid = directive_types - schema_types
   assert len(invalid) == 0, f"Invalid types: {invalid}"
   ```

2. **No project.db FP Logging**
   ```python
   # FP directives should NOT reference project.db notes for tracking
   fp_directives = glob("src/aifp/reference/directives/fp_*.md")
   for directive in fp_directives:
       content = read(directive)
       assert "INSERT INTO notes" not in content or "tracking" in content
   ```

3. **Tracking Context Present**
   ```python
   # FP directives should mention fp_flow_tracking
   for directive in fp_directives:
       content = read(directive)
       if "INSERT INTO" in content:
           assert "fp_flow_tracking" in content
           assert "user_preferences.db" in content
           assert "opt-in" in content or "disabled by default" in content
   ```

---

## Timeline Estimate

- **Phase 1** (Schema): Complete ✅
- **Phase 2** (FP Cleanup): 4-6 hours (30-40 files)
- **Phase 3** (Project Directives): 1-2 hours (10 files)
- **Phase 4** (Tracking Directives): 30 minutes (3 files)
- **Phase 5** (Helpers): 1-2 hours (find and update)
- **Phase 6** (Documentation): 1 hour

**Total**: ~8-12 hours

---

## Next Steps

1. **Immediate**: Run grep commands to identify all FP directives needing cleanup
2. **Priority**: Clean core FP directives first (purity, immutability, no_oop, result_types)
3. **Batch**: Process remaining FP directives in groups of 10
4. **Validate**: Run tests after each batch
5. **Document**: Update any cross-references as you go

---

**Ready to start Phase 2 (FP Directive Cleanup)?**
