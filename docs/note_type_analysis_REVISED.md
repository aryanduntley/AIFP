# Note Type Analysis and Consolidation Proposal (REVISED)

**Date**: 2026-01-08
**Purpose**: Analyze note_type usage across the codebase and propose a consolidated list
**Revision**: Corrected architecture - separated project notes from tracking data

---

## Critical Discovery: Two Different Systems

After reviewing tracking directives (`tracking_toggle`, `project_compliance_check`, `user_preferences_learn`), I discovered that:

### **project.db notes table** is for:
- **Project management** - Critical decisions, clarifications, context
- **Session continuity** - AI memory across sessions
- **Decision traceability** - Why choices were made
- **NOT for debugging/logging** - That's opt-in in user_preferences.db

### **user_preferences.db tracking tables** are for:
- **fp_flow_tracking** - FP compliance analytics (opt-in, 5% token overhead)
- **ai_interaction_log** - User corrections and learning (opt-in, 3% token overhead)
- **issue_reports** - Bug report compilation (opt-in, 2% token overhead)
- **Logging/debugging** - All opt-in features disabled by default

---

## Current State Analysis

### Schema Definition (project.sql:228)
```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'clarification',    -- Used by project_notes_log
    'pivot',            -- Used by project_notes_log
    'research',         -- Used by project_notes_log
    'entry_deletion',   -- Not found in any directive
    'warning',          -- Severity level (should use severity field)
    'error',            -- Severity level (should use severity field)
    'info',             -- Severity level (should use severity field)
    'auto_summary'      -- Used by project_auto_summary
))
```

**Current Schema Count**: 8 types

### Correct Usage (per project_notes_log.md)

**Semantic Types** (what the note is about):
1. **clarification** - User-confirmed decisions, intent, requirements
2. **pivot** - Project direction changes
3. **research** - AI analysis, findings, refactoring reasoning
4. **auto_summary** - Automated project summaries

**Severity Levels** (should use severity field instead):
- **warning** - Should be `severity='warning'`
- **error** - Should be `severity='error'`
- **info** - Should be `severity='info'`

**Unknown**:
- **entry_deletion** - Not found in any directive

---

## Problem: Directives Reference 36+ Types

From searching directive documentation, I found 36+ note_type values that **don't belong in project.db**:

### FP Compliance/Analysis Types (belong in fp_flow_tracking):
- optimization, compliance, refactoring, cleanup, normalization
- determinism, validation, security, performance, documentation
- metadata, indexing, wrapper

### User Directive Types (belong in user_directives.db or ai_interaction_log):
- code_generation, validation_session, approval, rejection, feedback
- directive_parse

### Project Management Types (some belong in project.db):
- sidequest, sidequest_outcome, evolution, roadblock, completion
- dependency_map, path_refactoring, external_change
- backup, restore, archival

### Status Types (misusing note_type as status):
- success, failure, retry, formatting, reasoning_trace

---

## Root Cause Analysis

**Why 36+ types exist in directives but only 8 in schema?**

1. **Confusion about database separation**:
   - FP compliance tracking → Should go to `fp_flow_tracking` table (user_preferences.db)
   - User learning → Should go to `ai_interaction_log` table (user_preferences.db)
   - Project decisions → Should go to `notes` table (project.db)

2. **Severity vs Type confusion**:
   - `error`, `warning`, `info` are severity levels, NOT note types
   - Schema has `severity` field that should be used instead

3. **Status vs Note confusion**:
   - `success`, `failure`, `completion` are outcomes, NOT note types
   - Should be tracked in task/milestone status fields

---

## Correct Architecture

### project.db notes table (Project Management)
**Purpose**: Critical context for AI memory and project decisions

**Should contain**:
- User decisions and clarifications
- Project direction changes (pivots)
- AI analysis and reasoning
- Task/milestone context
- External changes affecting project

**Should NOT contain**:
- Debug logs (that's tracking, opt-in)
- FP compliance analytics (that's fp_flow_tracking)
- User corrections (that's ai_interaction_log)
- Helper function logs (that's helper_function_logging)

### user_preferences.db tracking tables (Opt-In Features)
**Purpose**: Optional debugging, analytics, and learning

**fp_flow_tracking** (5% token overhead):
- FP directive consultation patterns
- Compliance analytics
- Optimization suggestions
- Refactoring statistics

**ai_interaction_log** (3% token overhead):
- User corrections
- Clarification requests
- Learning patterns
- Preference inference data

**issue_reports** (2% token overhead):
- Bug compilation
- Context linking
- Error aggregation

---

## Proposed Consolidation

### Option A: Semantic Types (Recommended)

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    -- Core project management types
    'decision',        -- User decisions, confirmations, clarifications
    'evolution',       -- Project direction changes, pivots, architecture shifts
    'analysis',        -- AI research, findings, reasoning, refactoring notes
    'task_context',    -- Task/milestone/sidequest lifecycle context
    'external',        -- Git changes, dependency updates, file system events
    'summary'          -- Auto-generated project summaries
))
```

**Mapping**:
- `clarification` → `decision`
- `pivot` → `evolution`
- `research` → `analysis`
- `auto_summary` → `summary`
- `sidequest`, `completion` → `task_context`
- `external_change`, `backup`, `restore` → `external`
- `error`, `warning`, `info` → Use `severity` field instead
- `entry_deletion` → Remove (unused)

**All FP compliance types** (optimization, compliance, refactoring, etc.) → `fp_flow_tracking` table

**All user correction types** (approval, rejection, feedback) → `ai_interaction_log` table

---

### Option B: Expanded for Granularity

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    -- Project management
    'clarification',   -- User-confirmed decisions
    'pivot',           -- Direction changes
    'evolution',       -- Architecture shifts

    -- AI analysis
    'research',        -- AI findings, analysis
    'reasoning',       -- Directive decision reasoning

    -- Task management
    'task_lifecycle',  -- Task/milestone/sidequest events
    'roadblock',       -- Blocking issues

    -- External integration
    'external_change', -- Git, file system, dependencies
    'backup_restore',  -- Backup/restore operations

    -- Automation
    'summary'          -- Auto-generated summaries
))
```

---

### Option C: Minimal Core (5 types)

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'decision',        -- All decisions, clarifications, confirmations
    'evolution',       -- All project changes (pivots, architecture)
    'context',         -- All AI analysis, reasoning, task context
    'external',        -- All external events (git, dependencies, file system)
    'summary'          -- Auto-generated summaries
))
```

---

## Recommendation: Option A (Semantic Types)

**Why Option A?**

1. ✅ **Clear separation** - Project management vs. tracking
2. ✅ **Right granularity** - 6 types cover all use cases
3. ✅ **Semantic clarity** - Each type has clear meaning
4. ✅ **Query-friendly** - Easy to filter by category
5. ✅ **Uses severity field** - Separates severity from type
6. ✅ **Moves tracking elsewhere** - FP analytics go to fp_flow_tracking

---

## Implementation Plan

### Step 1: Update project.sql Schema

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'decision',        -- User decisions, confirmations, clarifications
    'evolution',       -- Project direction changes, pivots, architecture shifts
    'analysis',        -- AI research, findings, reasoning, refactoring notes
    'task_context',    -- Task/milestone/sidequest lifecycle context
    'external',        -- Git changes, dependency updates, file system events
    'summary'          -- Auto-generated project summaries
))
```

### Step 2: Update Directive Documentation

**Project directives** (use notes table):
- `project_notes_log` - Update examples to use new types
- `project_task_create/complete` - Use `task_context`
- `project_evolution` - Use `evolution`
- `project_auto_summary` - Use `summary`
- `git_detect_external_changes` - Use `external`

**FP directives** (use fp_flow_tracking if tracking enabled):
- Remove all `INSERT INTO notes` from FP directives
- Add conditional: "If fp_flow_tracking enabled, log to user_preferences.db"
- Document that FP compliance is baseline, tracking is optional

**User directives** (use ai_interaction_log if tracking enabled):
- `user_directive_parse/validate/approve` - Use ai_interaction_log
- Document that these are opt-in features

### Step 3: Create Migration Script

```python
def migrate_note_types():
    """Migrate existing notes to new type system"""
    migrations = {
        'clarification': 'decision',
        'pivot': 'evolution',
        'research': 'analysis',
        'auto_summary': 'summary',
        'entry_deletion': 'analysis',  # Rare, treat as analysis
        # Severity types - migrate to severity field
        'error': ('analysis', 'error'),   # type + severity
        'warning': ('analysis', 'warning'),
        'info': ('analysis', 'info'),
    }

    for old_type, new_value in migrations.items():
        if isinstance(new_value, tuple):
            new_type, severity = new_value
            execute_sql(f"""
                UPDATE notes
                SET note_type = '{new_type}', severity = '{severity}'
                WHERE note_type = '{old_type}'
            """)
        else:
            execute_sql(f"""
                UPDATE notes
                SET note_type = '{new_value}'
                WHERE note_type = '{old_type}'
            """)
```

### Step 4: Update Helper Functions

Update all helpers that insert notes:
- Check which note_type they should use
- Ensure they use new types
- Add severity parameter where needed

### Step 5: Clean Up Directive Workflows

**Remove from project directives**:
- All references to FP compliance note types (optimization, refactoring, etc.)
- All references to user directive note types (validation_session, approval, etc.)

**Add to tracking directives**:
- Document that fp_flow_tracking stores FP analytics
- Document that ai_interaction_log stores user corrections
- Show examples of correct table usage

---

## Examples: Correct Usage

### Project Management Note
```sql
-- User confirms architectural decision
INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity)
VALUES (
    'User confirmed: Use pure Python, no NumPy dependency',
    'decision',  -- Clear decision type
    'project',
    1,
    'user',
    'info'       -- Severity in separate field
);
```

### Project Evolution Note
```sql
-- Project direction changes
INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity)
VALUES (
    'Pivoting from CLI tool to web API. Infrastructure will change.',
    'evolution',  -- Clear evolution type
    'project',
    1,
    'ai',
    'warning'     -- Higher severity for pivots
);
```

### AI Analysis Note
```sql
-- AI documents refactoring reasoning
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name, severity)
VALUES (
    'Function refactored for purity: eliminated mutation in calculate_total',
    'analysis',   -- AI analysis type
    'functions',
    42,
    'directive',
    'project_file_write',
    'info'
);
```

### FP Compliance Tracking (DIFFERENT TABLE!)
```sql
-- FP compliance analytics (only if tracking enabled)
-- Goes to user_preferences.db, NOT project.db
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    issues_json,
    created_at
) VALUES (
    'calculate_total',
    'src/calculator.py',
    '["fp_purity", "fp_immutability"]',
    1.0,
    NULL,
    CURRENT_TIMESTAMP
);
```

---

## Testing Plan

1. **Schema Migration Test**
   ```python
   # Insert old types, verify migration
   INSERT INTO notes (content, note_type) VALUES ('test', 'clarification');
   run_migration()
   assert query("SELECT note_type FROM notes")[0] == 'decision'
   ```

2. **New Type Validation Test**
   ```python
   # Try to insert invalid type
   try:
       INSERT INTO notes (content, note_type) VALUES ('test', 'optimization');
       assert False, "Should have failed CHECK constraint"
   except IntegrityError:
       pass  # Expected
   ```

3. **Tracking Separation Test**
   ```python
   # Verify FP tracking goes to correct table
   write_file_with_tracking_enabled()
   assert query("SELECT * FROM notes WHERE note_type='compliance'") == []
   assert query("SELECT * FROM fp_flow_tracking") != []
   ```

---

## Summary

### Before (Current Problem)
- Schema: 8 types (3 are severity levels, 1 unused)
- Directives: Reference 36+ types
- Confusion: FP tracking mixed with project notes
- Severity: Mixed into note_type instead of using severity field

### After (Proposed Solution)
- Schema: 6 semantic types (decision, evolution, analysis, task_context, external, summary)
- Directives: Use correct table for tracking vs. notes
- Separation: FP tracking → fp_flow_tracking, project context → notes
- Severity: Always use severity field (info/warning/error)

### Migration Impact
- Update 1 schema file (project.sql)
- Update ~20 directive MD files (remove FP tracking from notes examples)
- Create migration script for existing databases
- Update helper functions that insert notes
- Total effort: ~4-6 hours

---

## Questions for Review

1. ✅ **Confirmed**: FP compliance tracking goes to fp_flow_tracking (user_preferences.db)
2. ✅ **Confirmed**: User corrections go to ai_interaction_log (user_preferences.db)
3. ✅ **Confirmed**: Project decisions go to notes (project.db)
4. ❓ **Decision needed**: 6 types (Option A) vs. 10 types (Option B) vs. 5 types (Option C)?
5. ❓ **Decision needed**: Keep `entry_deletion` or remove as unused?
6. ❓ **Decision needed**: Should `roadblock` be separate type or use `task_context` + severity='error'?

---

**Ready to implement Option A (6 semantic types) pending approval.**
