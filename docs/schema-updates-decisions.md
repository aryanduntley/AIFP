# Schema Updates and Design Decisions
**Date**: 2025-11-24
**Status**: In Progress - Schemas Updated, Directives Review Pending

This document tracks all database schema updates, helper function reorganization, and design decisions made during the AIFP development process. Use this as a reference when reviewing and updating directives.

---

## Table of Contents
1. [Helper Files Reorganization](#helper-files-reorganization)
2. [Database Schema Changes](#database-schema-changes)
3. [CHECK Constraints Implementation](#check-constraints-implementation)
4. [Design Philosophy & Decisions](#design-philosophy--decisions)
5. [Next Steps](#next-steps)

---

## Helper Files Reorganization

### Files Consolidated
**Removed** old `additional-helpers-*.md` files (4 files deleted):
- `additional-helpers-mcp.md`
- `additional-helpers-project.md`
- `additional-helpers-preferences.md`
- `additional-helpers-user-directives.md`

**Reason**: These files contained made-up parameters/fields that didn't match actual database schemas, over-engineered proposals, and inconsistent field names.

### Current Helper Files (Authoritative)
- `info-helpers-project.txt` - Project database helpers
- `info-helpers-core.txt` - MCP/Core database helpers
- `info-helpers-user-settings.txt` - User preferences helpers
- `info-helpers-user-custom.txt` - User directives helpers

**Why These Are Better**:
- Match actual database schemas exactly
- Clear TOOLS vs HELPERS distinction (is_sub_helper flags)
- Include reservation system
- Practical, grounded in actual needs
- Use `(*Can Be Null)` notation for optional parameters

### Useful Content Added from Old Files

**Added to info-helpers-project.txt**:
- Flow-based work context helpers: `get_work_context()`, `get_files_by_flow_context()`
- All 10 git helpers: `get_current_commit_hash()`, `get_current_branch()`, `get_git_status()`, `detect_external_changes()`, `create_user_branch()`, `detect_conflicts_before_merge()`, `merge_with_fp_intelligence()`, `get_user_name_for_branch()`, `sync_git_state()`, `list_active_branches()`

**Added to info-helpers-core.txt**:
- Hierarchy navigation helpers: `get_directive_tree()`, `get_directive_branch()`, `get_directive_siblings()`, `get_directive_depth()`

---

## Database Schema Changes

### 1. aifp_core.db (v1.5 → v1.6)

**New Fields Added**:
- `helper_functions.return_statements` (JSON) - Array of guidance/suggestions for AI after execution
- `helper_functions.target_database` (TEXT) - Which database this helper operates on: 'core', 'project', 'user_preferences', 'user_directives'

**Fields Removed**:
- **All `created_at` and `updated_at` fields removed** from all tables
- **Reason**: Core database is immutable - only changes on AIFP version releases. Timestamp tracking is unnecessary for read-only reference data.

**CHECK Constraints Added**:
- `directives.type` IN ('fp', 'project', 'git', 'user_system', 'user_preference')

**Philosophy**: Core database is read-only reference data. No need for timestamp tracking.

---

### 2. project.db (v1.2 → v1.3)

**Major Changes**:

#### Reservation System Added
- `files.is_reserved` (BOOLEAN DEFAULT 0) - TRUE during reservation, FALSE after finalization
- `functions.is_reserved` (BOOLEAN DEFAULT 0)
- `types.is_reserved` (BOOLEAN DEFAULT 0)

**Purpose**: Allow AI to reserve file/function/type names during planning phase, preventing collisions before actual implementation.

#### New Fields Added
- `files.name` (TEXT) - File name separate from path (e.g., 'calculator-ID42.py')
- `functions.returns` (JSON) - Return value description: `{"type": "int", "description": "Sum of inputs"}`
- `types.file_id` (INTEGER) - File where type is defined

#### Fields Modified
- `functions.name` - Changed from `TEXT NOT NULL` to `TEXT NOT NULL UNIQUE`
  - **Reason**: FP flat namespace - no function overloading, forces descriptive naming

#### New Junction Table
- `types_functions` - Many-to-many relationship between types and functions
  - Fields: `type_id`, `function_id`, `role`, `created_at`
  - Role values: 'factory', 'transformer', 'operator', 'pattern_matcher', 'accessor', 'validator', 'combinator'
  - **FP-appropriate terminology** (no OOP 'constructor' or 'method' concepts)

#### Fields Removed
- **All `project_id` foreign keys removed** from:
  - `infrastructure`
  - `files`
  - `types`
  - `themes`
  - `flows`
  - `completion_path`
- **Reason**: One project per database. No need for foreign keys to single-row table.

- `types.linked_function_id` - Removed redundant field
  - **Reason**: types_functions junction table properly handles many-to-many relationships. Having both would create two sources of truth and potential inconsistency.

#### Field Standardization
- `tasks.priority` changed from INTEGER to TEXT
- All priority fields now use: 'low', 'medium', 'high', 'critical'
- Consistent across: tasks, subtasks, sidequests

#### Comprehensive Timestamp Triggers Added
Added automatic timestamp update triggers for **all 15 mutable tables**:
- project, infrastructure, files, functions, types, interactions
- themes, flows, completion_path, milestones, tasks, subtasks
- sidequests, items, notes

#### CHECK Constraints Added
See [CHECK Constraints](#check-constraints-implementation) section for complete list.

---

### 3. user_preferences.db (v1.0 → v1.1)

**Field Renamed**:
- `ai_interaction_log.directive_context` → `ai_interaction_log.directive_name`
- **Reason**: Consistency with other tables and clarity

**CHECK Constraints Added**:
- `user_settings.scope` IN ('project', 'global')
- `ai_interaction_log.interaction_type` IN ('preference_learned', 'correction', 'clarification')
- `issue_reports.report_type` IN ('bug', 'feature_request', 'directive_issue')
- `issue_reports.status` IN ('draft', 'submitted', 'resolved')

**Index Updated**:
- `idx_ai_interaction_log_directive` now references `directive_name` (was `directive_context`)

---

### 4. user_directives.db (v1.0 - No Version Change)

**CHECK Constraint Added**:
- `user_directives.action_type` IN ('api_call', 'script_execution', 'function_call', 'command', 'notification')

**Note**: This database already had comprehensive CHECK constraints. Only minor addition needed.

**Language Field Decision**: `directive_implementations.language` field intentionally left **without** CHECK constraints. Open-ended to support any programming language users want to implement directives in (Python, JS, Rust, Go, etc.).

---

## CHECK Constraints Implementation

### Why CHECK Constraints Are Critical

**Problem Solved**:
- Prevents arbitrary values: "complete" vs "completed" vs "done"
- Makes helper function getters reliable: `get_tasks_by_status('completed')` always works
- Eliminates guesswork for AI when setting field values
- Enforces consistency across the entire system

### Complete List of CHECK Constraints

#### project.db
| Table | Field | Allowed Values |
|-------|-------|----------------|
| project | status | 'active', 'paused', 'completed', 'abandoned' |
| project | user_directives_status | NULL, 'in_progress', 'active', 'disabled' |
| types_functions | role | 'factory', 'transformer', 'operator', 'pattern_matcher', 'accessor', 'validator', 'combinator' |
| interactions | interaction_type | 'call', 'chain', 'borrow', 'compose', 'pipe' |
| completion_path | status | 'pending', 'in_progress', 'completed' |
| milestones | status | 'pending', 'in_progress', 'completed', 'blocked' |
| tasks | status | 'pending', 'in_progress', 'completed', 'blocked' |
| tasks | priority | 'low', 'medium', 'high', 'critical' |
| subtasks | status | 'pending', 'in_progress', 'completed', 'blocked' |
| subtasks | priority | 'low', 'medium', 'high', 'critical' |
| sidequests | status | 'pending', 'in_progress', 'completed' |
| sidequests | priority | 'low', 'medium', 'high', 'critical' |
| items | status | 'pending', 'in_progress', 'completed' |
| items | reference_table | 'tasks', 'subtasks', 'sidequests' |
| notes | note_type | 'clarification', 'pivot', 'research', 'entry_deletion', 'warning', 'error', 'info' |
| notes | source | 'ai', 'user', 'directive' |
| notes | severity | 'info', 'warning', 'error' |
| work_branches | status | 'active', 'merged', 'abandoned' |

#### aifp_core.db
| Table | Field | Allowed Values |
|-------|-------|----------------|
| directives | type | 'fp', 'project', 'git', 'user_system', 'user_preference' |

#### user_preferences.db
| Table | Field | Allowed Values |
|-------|-------|----------------|
| user_settings | scope | 'project', 'global' |
| ai_interaction_log | interaction_type | 'preference_learned', 'correction', 'clarification' |
| issue_reports | report_type | 'bug', 'feature_request', 'directive_issue' |
| issue_reports | status | 'draft', 'submitted', 'resolved' |

#### user_directives.db
Already comprehensive. Only added:
| Table | Field | Allowed Values |
|-------|-------|----------------|
| user_directives | action_type | 'api_call', 'script_execution', 'function_call', 'command', 'notification' |

---

## Design Philosophy & Decisions

### 1. FP (Functional Programming) Terminology Only

**Decision**: No OOP concepts in an FP project.

**Incorrect (OOP)**:
- 'constructor'
- 'method'
- 'class'

**Correct (FP)**:
- 'factory' (creates instances of types)
- 'transformer' (transforms one type to another)
- 'operator' (operates on types)
- 'pattern_matcher' (pattern matches on ADT variants)
- 'accessor' (extracts data from types)
- 'validator' (validates types)
- 'combinator' (combines instances of types)

**Applied To**: `types_functions.role` field in project.db

---

### 2. One Project Per Database

**Decision**: Remove all `project_id` foreign keys from project.db tables.

**Reason**:
- Each `.aifp-project/` directory has its own project.db
- Only ever one project per database
- Unnecessary foreign key complexity
- Simpler queries (no JOIN on project table needed)

**Impact**: Removed from infrastructure, files, types, themes, flows, completion_path tables.

---

### 3. Core Database is Immutable

**Decision**: Remove all timestamp fields from aifp_core.db tables.

**Reason**:
- Core database is read-only reference data
- Only changes during AIFP version releases
- Tracking individual row updates is meaningless
- Schema version table tracks overall version changes

**Impact**: All `created_at` and `updated_at` fields removed from directives, categories, helper_functions, directive_helpers, directives_interactions.

---

### 4. Priority: TEXT Over INTEGER

**Decision**: Use TEXT for priority fields with descriptive values.

**Reasoning**:
- Self-documenting: "high" is clearer than "2"
- No arbitrary mapping confusion (is 0 lowest or highest?)
- Consistent with status fields pattern
- Intuitive for helper function getters

**Values**: 'low', 'medium', 'high', 'critical'

**Applied To**: tasks, subtasks, sidequests in project.db

---

### 5. Directive-Helper References via Database, Not Files

**Decision**: Use `directive_helpers` table for mapping directives to helper functions.

**Reason**:
- Avoid scattered references throughout directive files/data
- Easier to maintain and update when helpers change
- Single source of truth for directive-helper relationships
- No need to update multiple directive files when helper is renamed/refactored

**Impact**: When updating directives, avoid adding helper/tool references directly in directive content. Use the database table instead.

---

### 6. return_statements for AI Guidance

**Decision**: Add `return_statements` JSON field to helper_functions.

**Purpose**:
- Provide post-execution guidance to AI
- Suggest next steps after helper completes
- Code FP "purity" verification reminders
- Directive chaining suggestions
- Constant AI guidance with every helper/tool call

**Format**: JSON array of strings with suggestions, warnings, verification steps.

**Example Use Cases**:
- "Verify function purity before marking as complete"
- "Consider chaining with X directive for full workflow"
- "Check if dependent functions need updates"

**Status**: Field added to schema, needs to be fleshed out during helper JSON creation.

---

### 7. Unique Function Names (FP Flat Namespace)

**Decision**: Make all function names UNIQUE across the entire project.

**Reasoning**:
- **FP philosophy**: Flat namespace without class-based overloading
- **Forces descriptive naming**: Can't have 3 functions called `process()` - must be `process_user()`, `process_payment()`, `process_data()`
- **Prevents confusion**: No ambiguity about which function is which
- **Simplifies lookups**: Even without embedded IDs, name lookup is unambiguous
- **Better code quality**: Encourages clear, descriptive function names (FP best practice)

**Applied To**: `functions.name` field in project.db now has UNIQUE constraint

**Note**: File context is available via `file_id` if needed, but the function name itself must be globally unique.

---

### 8. Types-Functions Junction Table (Remove Redundancy)

**Decision**: Remove `linked_function_id` from types table, use `types_functions` junction table exclusively.

**Reasoning**:
- **Eliminates redundancy**: Single source of truth for type-function relationships
- **Prevents inconsistency**: Two fields for same relationship = potential conflicts
- **More flexible**: Junction table supports true many-to-many (one type can have multiple factory functions, accessors, validators, etc.)
- **Cleaner design**: Entity attributes in entity tables, relationships in junction tables
- **Proper normalization**: Standard database design pattern

**Applied To**: types table in project.db

**Relationship Examples**:
- Result type → `create_success()` (factory), `create_error()` (factory), `is_ok()` (validator), `unwrap()` (accessor)
- All tracked in types_functions with appropriate role values

---

### 9. Reservation System for Files/Functions/Types

**Decision**: Add `is_reserved` boolean to files, functions, types tables.

**Workflow**:
1. AI plans implementation → reserves names (is_reserved=TRUE)
2. AI implements code → finalizes reservations (is_reserved=FALSE)
3. Prevents naming collisions during multi-step processes

**Purpose**:
- Allow AI to claim names before writing code
- Prevent concurrent directive conflicts
- Track what's planned vs implemented
- Enable rollback if implementation fails

**Fields Added**: `is_reserved` to files, functions, types in project.db

---

### 10. Embedded Database IDs for Efficiency

**Decision**: Embed database IDs directly in code as comments for instant lookups.

**Efficiency Gains**:
- **Without IDs**: AI must query by name → get ID → use ID (3+ queries)
- **With IDs**: AI parses comment → direct integer lookup (1 query)
- **Batch operations**: Scan file for all IDs, single batch query
- **Rename-proof**: Function can be renamed, ID relationships remain intact
- **Type/Function cross-refs**: Instant relationship lookups

**ID Format Standards**:
```python
# File-level (top of file)
# AIFP:FILE:10

# Function
def calculate_sum(a, b):  # AIFP:FUNC:42
    """Sum two numbers."""
    return a + b

# Type/ADT
class Result:  # AIFP:TYPE:7
    """Result ADT"""
```

**Alternative Format** (in docstrings):
```python
def calculate_sum(a, b):
    """Sum two numbers.

    AIFP-ID: 42
    """
    return a + b
```

**Integration with Reservation System**:
1. AI reserves: `reserve_function(name='calculate_sum', file_id=10)` → returns function_id=42
2. AI writes code with ID embedded: `def calculate_sum(a, b):  # AIFP:FUNC:42`
3. AI finalizes: `finalize_function(42)` → sets is_reserved=FALSE
4. Later access: `get_function(42)` - instant, no name lookup needed

**Benefits**:
- Massive API/query savings (especially for batch operations)
- Unambiguous references (no string matching needed)
- Works across renames
- Supports offline code analysis (IDs visible in code)

**Concerns & Mitigations**:
- **Database rebuild**: Create `verify_ids` directive to detect/repair mismatches
- **Code pollution**: Minimal, standardized format, unobtrusive
- **Manual edits**: Non-AIFP edits don't break system, just less optimal until next verification

**Directives Needed**:
1. `reserve_finalize` - Main workflow for reservation with ID embedding
2. `verify_ids` - Periodic verification that code IDs match database
3. `repair_ids` - Fix ID mismatches when detected

**Status**: Design approved, directives pending creation

---

## Next Steps

### 1. ✅ Completed Tasks
- [x] Consolidate helper files
- [x] Remove outdated documentation
- [x] Update all 4 database schemas
- [x] Add CHECK constraints to all status/priority fields
- [x] Standardize priority field (INT → TEXT)
- [x] Remove unnecessary project_id foreign keys
- [x] Add reservation system fields
- [x] Add return_statements field to helper_functions

### 2. 🔄 In Progress - Directives Review

**Goal**: Update all existing directives based on new schema changes.

**Key Considerations**:
- Incorporate reservation system workflow
- Reference file_id in types table
- Update for removed project_id fields
- Ensure FP terminology (no OOP concepts)
- **Minimize direct helper references** in directive content
- Use `directive_helpers` table for directive-to-helper mappings

**Approach**:
- Don't rush - review systematically
- Avoid playing catchup later
- Update directives AND their matching .md files
- Keep directive files clean of scattered helper references

### 3. ⏳ Pending - return_statements Field

**Goal**: Flesh out return_statements for all helper functions.

**Purpose**:
- AI guidance and next-step suggestions
- FP purity verification reminders
- Directive chaining suggestions
- Error prevention and best practices

**Deliverable**: Comprehensive examples of useful return_statements content.

### 4. ⏳ Pending - Helper Functions JSON

**Goal**: Create comprehensive JSON representation of all helper functions.

**Must Include**:
- name
- file_path
- parameters (with types and descriptions)
- return values (with types and descriptions)
- return_statements (detailed AI guidance)
- is_tool flag
- is_sub_helper flag
- target_database
- purpose
- error_handling
- used_by (which directives use this helper)

**Reference**: Use `docs/directives-json/helpers_parsed.json` as starting point, but verify against actual schemas.

---

## Changelog Summary

| Date | Component | Change | Version |
|------|-----------|--------|---------|
| 2025-11-24 | aifp_core.db | Added return_statements, target_database; removed timestamps | 1.5 → 1.6 |
| 2025-11-24 | project.db | Reservation system, removed project_id, unique function names, removed linked_function_id, standardized priority, triggers | 1.2 → 1.3 |
| 2025-11-24 | user_preferences.db | Renamed directive_context → directive_name, CHECK constraints | 1.0 → 1.1 |
| 2025-11-24 | user_directives.db | Added action_type CHECK constraint | 1.0 (minor) |
| 2025-11-24 | Helper files | Consolidated to 4 authoritative files, removed 4 outdated files | N/A |
| 2025-11-24 | CHECK constraints | Added to ALL status/priority/select fields across all databases | N/A |

---

## Notes for Future Sessions

1. **When updating directives**: Always check this file first for schema changes
2. **Helper references**: Use directive_helpers database table, not scattered references
3. **FP terminology**: No OOP concepts (constructor → factory, method → transformer, etc.)
4. **Priority consistency**: Always use 'low', 'medium', 'high', 'critical'
5. **Reservation workflow**: Plan → Reserve → Implement → Finalize
6. **return_statements**: Critical for AI guidance - needs thorough implementation
7. **CHECK constraints**: All status/priority fields are now enforced - no arbitrary values
8. **Function names must be UNIQUE**: FP flat namespace - no overloading, forces descriptive names
9. **Type-function relationships**: Use types_functions junction table exclusively (linked_function_id removed)
10. **Embedded IDs**: Files/functions/types will have database IDs embedded as comments for efficiency

---

**Last Updated**: 2025-11-24
**Document Status**: Active Reference - Update as schema evolves
