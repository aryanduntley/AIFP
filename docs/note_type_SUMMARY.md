# Note Type Consolidation - Executive Summary

**Date**: 2026-01-08
**Analysis**: Complete review of note_type usage across all directives and schemas

---

## TL;DR

**The Problem**: Schema defines 8 note types, but directives reference 36+ types. Massive disconnect.

**Root Cause**: Confusion about which database to use - **tracking data was being mixed with project notes**.

**Solution**: Consolidate project.db notes to **6 semantic types** and move tracking data to user_preferences.db.

---

## Key Discovery

After reviewing `tracking_toggle`, `project_compliance_check`, and `user_preferences_learn` directives, I found:

### Two Separate Systems That Got Mixed Up

**project.db notes table** = AI memory for project management
- User decisions and clarifications
- Project direction changes
- AI analysis and reasoning
- Task/milestone context
- External events

**user_preferences.db tracking tables** = Opt-in debugging/analytics (ALL disabled by default)
- `fp_flow_tracking` - FP compliance analytics (5% token overhead)
- `ai_interaction_log` - User corrections (3% token overhead)
- `issue_reports` - Bug compilation (2% token overhead)

### The Confusion

Many directives were trying to insert FP compliance notes like:
- `note_type='compliance'`
- `note_type='optimization'`
- `note_type='refactoring'`

**These don't belong in project.db notes!** They belong in `fp_flow_tracking` table (and only if tracking is enabled).

---

## Current State

### Schema (project.sql:228)
```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'clarification',   -- ✅ Used correctly
    'pivot',           -- ✅ Used correctly
    'research',        -- ✅ Used correctly
    'entry_deletion',  -- ❌ Never used
    'warning',         -- ❌ Should use severity field
    'error',           -- ❌ Should use severity field
    'info',            -- ❌ Should use severity field
    'auto_summary'     -- ✅ Used correctly
))
```

**Issues**:
1. 3 of 8 types are severity levels (should use `severity` field)
2. 1 type is completely unused
3. Only 4 types are actually semantic note types

### Directives Reference 36+ Types

All these types are referenced in directive docs:
- optimization, compliance, refactoring, cleanup, normalization
- validation, security, performance, documentation, metadata
- code_generation, approval, rejection, feedback
- success, failure, retry, completion
- sidequest, roadblock, external_change, backup, etc.

**None of these 36+ types are in the schema!**

---

## Recommended Solution

### New Schema (6 Semantic Types)

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'decision',        -- User decisions, confirmations, clarifications
    'evolution',       -- Project direction changes, pivots, architecture
    'analysis',        -- AI research, findings, reasoning
    'task_context',    -- Task/milestone/sidequest events
    'external',        -- Git, dependencies, file system changes
    'summary'          -- Auto-generated project summaries
))
```

### Type Mapping

**Current → New**:
- `clarification` → `decision`
- `pivot` → `evolution`
- `research` → `analysis`
- `auto_summary` → `summary`
- `error`, `warning`, `info` → Use `severity` field instead
- `entry_deletion` → Remove (unused)

**36+ directive types**:
- All FP compliance types (optimization, refactoring, etc.) → `fp_flow_tracking` table
- All user directive types (validation, approval, etc.) → `ai_interaction_log` table
- All status types (success, failure, etc.) → Task/milestone status fields

---

## Benefits

### ✅ Clear Separation
- Project management notes in project.db
- Tracking/analytics in user_preferences.db
- No confusion about which database

### ✅ Semantic Clarity
- 6 types that clearly describe WHAT the note is about
- Severity field for HOW important it is
- No mixing of concepts

### ✅ Query-Friendly
- Easy to filter by note purpose
- Easy to find decisions vs. analysis vs. context
- Clear taxonomy

### ✅ Respects Opt-In Philosophy
- FP tracking is opt-in (disabled by default)
- Notes table only has essential project data
- Cost-conscious design preserved

### ✅ Migration-Friendly
- Clear mapping from old to new types
- Simple migration script
- Backward compatible queries

---

## Implementation Checklist

- [ ] Update `src/aifp/database/schemas/project.sql` with new CHECK constraint
- [ ] Create migration script for existing databases
- [ ] Update `project_notes_log.md` with new types and examples
- [ ] Update all project directives to use new types
- [ ] Remove FP compliance notes from FP directive examples
- [ ] Add examples to tracking directives showing fp_flow_tracking usage
- [ ] Update helper functions that insert notes
- [ ] Test migration on sample database
- [ ] Update system prompt if it references note types

**Estimated effort**: 4-6 hours

---

## Examples

### Before (Mixed Up)
```sql
-- FP compliance being logged to notes table (WRONG!)
INSERT INTO notes (content, note_type, source, severity)
VALUES (
    'Function optimized for purity',
    'optimization',  -- Not in schema, fails CHECK constraint
    'directive',
    'info'
);
```

### After (Correct)
```sql
-- Project decision in notes table
INSERT INTO notes (content, note_type, source, severity)
VALUES (
    'User confirmed: Use pure Python only',
    'decision',  -- Clear semantic type
    'user',
    'info'       -- Severity in separate field
);

-- FP tracking in tracking table (if enabled)
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score
) VALUES (
    'calculate_total',
    'src/calculator.py',
    '["fp_purity", "fp_immutability"]',
    1.0
);
```

---

## Files for Review

1. **docs/note_type_analysis_REVISED.md** - Full detailed analysis
2. **docs/note_type_SUMMARY.md** - This document (executive summary)

---

## Decision Needed

**Approve Option A (6 semantic types)?**

- `decision`, `evolution`, `analysis`, `task_context`, `external`, `summary`

Or prefer:
- **Option B**: 10 types (more granular)
- **Option C**: 5 types (more minimal)

See full analysis document for details on all options.

---

**Recommendation: Approve Option A and implement immediately.**

This will:
1. Fix the schema disconnect
2. Clarify which database to use for what
3. Make querying easier
4. Preserve opt-in tracking philosophy
5. Reduce cognitive load (6 clear types vs. 36+ scattered types)
