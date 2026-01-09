# Note Type Analysis and Consolidation Proposal

**Date**: 2026-01-08
**Purpose**: Analyze note_type usage across the codebase and propose a consolidated list

---

## Current State

### Schema Definition (project.sql:228)
```sql
note_type TEXT NOT NULL CHECK (note_type IN ('clarification', 'pivot', 'research', 'entry_deletion', 'warning', 'error', 'info', 'auto_summary'))
```

**Count**: 8 types

### Note Types Found in Directive Documentation
From searching `src/aifp/reference/directives/` and `docs/directives-json/`:

1. **optimization** - Performance improvements (lazy computation, constant folding, parallel evaluation, function inlining, lazy evaluation)
2. **compliance** - FP compliance issues (purity, immutability, Result types, Option types, Try monad, no OOP)
3. **external_change** - Git external changes detected
4. **cleanup** - Dead code elimination
5. **dependency_map** - Dependency mapping storage
6. **sidequest** - Sidequest creation
7. **sidequest_outcome** - Sidequest completion
8. **refactoring** - Code refactoring (error pipelines, keyword alignment, map/reduce, syntax normalization, data filtering, pattern unpacking, list operations, language standardization, monadic composition, recursion enforcement)
9. **metadata** - Metadata generation
10. **archival** - Project archival
11. **normalization** - Syntax normalization
12. **determinism** - Evaluation order control
13. **validation** - Symbol map validation, directive validation
14. **validation_session** - User directive validation sessions
15. **indexing** - Function indexing operations
16. **path_refactoring** - Path refactoring operations
17. **backup** - Backup operations
18. **restore** - Restore operations
19. **user_referral** - User referrals to directives
20. **performance** - Performance/cost analysis
21. **documentation** - Documentation issues (missing docstrings)
22. **security** - Security issues (reflection violations)
23. **reasoning_trace** - AI reasoning traces
24. **wrapper** - Wrapper generation
25. **code_generation** - Code generation from user directives
26. **approval** - User directive approval
27. **rejection** - User directive rejection
28. **feedback** - User directive feedback
29. **directive_parse** - Directive parsing
30. **success** - Successful operations
31. **completion** - Task/milestone completion
32. **failure** - Failed operations
33. **retry** - Retry attempts
34. **roadblock** - Blocking issues
35. **evolution** - Project evolution tracking
36. **formatting** - Formatting fixes

**Count**: 36 types (!)

### Types in Schema but NOT in Directives
- **clarification** - Used in project_notes_log examples only
- **pivot** - Not found in any directive
- **research** - Used in project_notes_log examples only
- **entry_deletion** - Not found in any directive

---

## Problem Summary

1. **Massive Disconnect**: Schema has 8 types, directives reference 36+ types
2. **Schema Types Unused**: 4 of 8 schema types are not used by any directive
3. **Directive Types Unsupported**: 32 types referenced in directives are NOT in schema
4. **No Clear Taxonomy**: Types are inconsistent - some are outcomes (success/failure), some are purposes (refactoring/optimization), some are sources (external_change)

---

## Usage Pattern Analysis

### By Frequency Category

**High-Frequency Types** (used across many directives):
- **compliance** - Used by 10+ FP directives for violations
- **refactoring** - Used by 12+ FP directives for transformations
- **optimization** - Used by 6+ FP directives for performance
- **error** - Universal error logging
- **warning** - Universal warning logging
- **info** - Universal informational logging

**Medium-Frequency Types** (used by specific directive groups):
- **validation** - Used by validation directives
- **code_generation** - Used by user directive system
- **success/failure/completion** - Used by project metrics/performance directives
- **auto_summary** - Used by project_auto_summary
- **external_change** - Used by git_detect_external_changes

**Low-Frequency Types** (single directive usage):
- dependency_map, path_refactoring, backup, restore, reasoning_trace, wrapper, etc.

### By Purpose Category

**Severity/Level Types**:
- error, warning, info

**Project Management Types**:
- clarification, pivot, research, sidequest, sidequest_outcome, evolution, roadblock, completion

**FP Compliance Types**:
- compliance, refactoring, optimization, cleanup, normalization, determinism, validation, security

**User Directive System Types**:
- code_generation, validation_session, approval, rejection, feedback, directive_parse

**Tracking/Analysis Types**:
- dependency_map, indexing, metadata, reasoning_trace, performance, documentation

**Git/External Types**:
- external_change, backup, restore

**Status/Outcome Types**:
- success, failure, retry, completion

**Specialized Types**:
- archival, path_refactoring, wrapper, user_referral, formatting, entry_deletion

---

## Consolidation Strategy

### Design Principles

1. **Broad Categories**: Keep types general enough to cover multiple use cases
2. **Severity Separation**: Use `severity` field (info/warning/error) for logging levels, NOT note_type
3. **Semantic Meaning**: Types should describe WHAT the note is about, not HOW severe it is
4. **Project Context**: Focus on types useful for project tracking, not debugging
5. **Cost-Conscious**: Most detailed tracking is opt-in anyway (disabled by default)

### Recommendation: Two-Tier System

**Core Types** (always supported, used for project management):
1. **status** - General status updates, evolution tracking
2. **decision** - Architectural decisions, pivots, clarifications
3. **task** - Task/milestone/sidequest lifecycle events
4. **code** - Code-related events (file creation, refactoring, generation)
5. **external** - External changes (Git, file system, dependencies)

**Extended Types** (opt-in tracking features only):
6. **fp_analysis** - FP compliance, optimization, refactoring suggestions
7. **validation** - Validation sessions, checks, approvals
8. **debug** - Debugging info (reasoning traces, dependency maps, metadata)

### Alternative: Minimal Core Set

If we want to be even more minimal, collapse to 5 core types:

1. **project** - Status, decisions, clarifications, evolution
2. **task** - All task/milestone/sidequest events
3. **code** - All code events (creation, refactoring, generation, deletion)
4. **external** - Git, file system, dependency changes
5. **tracking** - All opt-in tracking (FP analysis, validation, debugging)

Use `severity` field for info/warning/error distinction.

---

## Proposed Schema Update

### Option A: Two-Tier System (8 types)
```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'status',          -- General status, evolution
    'decision',        -- Decisions, pivots, clarifications
    'task',            -- Task/milestone/sidequest events
    'code',            -- Code creation, refactoring, generation
    'external',        -- Git, file system, dependency changes
    'fp_analysis',     -- FP compliance, optimization (opt-in)
    'validation',      -- Validation, approvals (opt-in)
    'debug'            -- Debugging traces, metadata (opt-in)
))
```

### Option B: Minimal Core (5 types)
```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    'project',         -- Project status, decisions, clarifications
    'task',            -- Task/milestone/sidequest lifecycle
    'code',            -- All code-related events
    'external',        -- Git, file system, dependencies
    'tracking'         -- All opt-in tracking features
))
```

### Option C: Expanded Set (12 types)
Keep more granularity for better querying:

```sql
note_type TEXT NOT NULL CHECK (note_type IN (
    -- Core project management (always on)
    'status',          -- General status updates
    'decision',        -- Architectural decisions
    'clarification',   -- Clarifications, research notes
    'task',            -- Task/milestone/sidequest events

    -- Code management (always on)
    'code_write',      -- File creation, updates
    'code_refactor',   -- Refactoring operations
    'code_delete',     -- File/function deletions

    -- External integration (always on)
    'git',             -- Git operations, external changes
    'dependency',      -- Dependency changes, sync

    -- Opt-in tracking (disabled by default)
    'fp_compliance',   -- FP compliance analysis
    'validation',      -- Validation sessions
    'debug'            -- Debug traces, metadata
))
```

---

## Migration Mapping

How to map existing 36+ types to proposed types:

### To Option A (Two-Tier)
```
status:
  - auto_summary, evolution, entry_deletion

decision:
  - clarification, pivot, research, user_referral

task:
  - sidequest, sidequest_outcome, completion, roadblock

code:
  - code_generation, refactoring, cleanup, formatting, wrapper,
    archival, path_refactoring, backup, restore

external:
  - external_change, dependency_map

fp_analysis:
  - compliance, optimization, normalization, determinism, security,
    performance, documentation, metadata, indexing

validation:
  - validation, validation_session, approval, rejection, feedback

debug:
  - reasoning_trace, directive_parse

(error/warning/info → use severity field instead)
(success/failure/retry → use severity + content instead)
```

### To Option B (Minimal Core)
```
project:
  - auto_summary, evolution, clarification, pivot, research,
    user_referral, entry_deletion

task:
  - sidequest, sidequest_outcome, completion, roadblock

code:
  - code_generation, refactoring, cleanup, formatting, wrapper,
    archival, path_refactoring, backup, restore

external:
  - external_change, dependency_map

tracking:
  - compliance, optimization, normalization, determinism, security,
    performance, documentation, metadata, indexing, validation,
    validation_session, approval, rejection, feedback, reasoning_trace,
    directive_parse

(error/warning/info → use severity field instead)
(success/failure/retry → use severity + content instead)
```

---

## Recommendation

**Go with Option A (Two-Tier System, 8 types)** because:

1. ✅ **Clear Semantics**: Each type has clear meaning
2. ✅ **Right Granularity**: Not too broad, not too specific
3. ✅ **Separation of Concerns**: Core project types vs. opt-in tracking types
4. ✅ **Query-Friendly**: Easy to query by category
5. ✅ **Migration-Friendly**: Clear mapping from existing 36+ types
6. ✅ **Future-Proof**: Can add types without breaking existing queries
7. ✅ **Severity Separation**: Uses severity field for error/warning/info

### Implementation Steps

1. Update schema in `src/aifp/database/schemas/project.sql`
2. Update all directive JSON files to use new types
3. Update all directive MD files to use new types
4. Create migration script for existing databases
5. Update helper functions that query notes by type
6. Update documentation with new type definitions

---

## Questions for Discussion

1. **Granularity**: Is 8 types too many? Too few?
2. **Naming**: Are the names clear and intuitive?
3. **Opt-in vs Core**: Should we separate opt-in types more explicitly?
4. **Migration**: Should we support old types temporarily with a migration period?
5. **Querying**: Do we need junction tables to support multi-type notes?

---

## Next Steps

1. **Decision**: Choose Option A, B, or C (or modify)
2. **Schema Update**: Update project.sql CHECK constraint
3. **Directive Update**: Mass update all directive files
4. **Documentation**: Update all references
5. **Migration**: Create migration script for existing notes
6. **Testing**: Verify all queries still work with new types
