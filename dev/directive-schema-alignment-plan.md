# Directive Schema Alignment Plan

**Purpose**: Align all directive JSON files with the aifp_core.db schema (v1.3) to ensure consistency between documentation and implementation.

**Date Created**: 2025-10-12
**Status**: In Progress

---

## Overview

We are aligning our directive JSON files with the database schema defined in `docs/schemaExampleMCP.sql`. This ensures that when we begin coding, the sync scripts can accurately populate the database without schema mismatches.

### Key Changes
1. Add missing fields to directive JSON entries
2. Remove obsolete graph file
3. Create separate interactions file
4. Validate all changes against schema

---

## Schema Requirements

Based on `docs/schemaExampleMCP.sql`, each directive must have:

### Required Fields (directives table)
- [x] `name` - Unique identifier
- [x] `type` - 'fp' or 'project'
- [x] `level` - Integer (0-4 for project, NULL for fp)
- [x] `parent_directive` - Optional reference to parent directive name
- [x] `description` - Human-readable purpose
- [x] `workflow` - JSON object with trunk/branches/error_handling
- [x] `md_file_path` - Path to detailed markdown file (e.g., 'directives/fp_purity.md')
- [x] `roadblocks_json` - Array of known issues and resolutions
- [x] `intent_keywords_json` - Array of keywords for intent matching
- [x] `confidence_threshold` - Float (0.0-1.0)
- [x] `notes` - Additional documentation (not in DB schema, but useful in JSON)

### Category Association
- [x] `category` - Object with name and description (maps to directive_categories table)

### Interactions (separate file)
- Relationships stored in `directives-interactions.json`
- Maps to `directives_interactions` table

---

## Tasks

### Phase 1: Cleanup and Preparation

#### Task 1.1: Remove Obsolete Files
- [x] Delete `docs/directives_project_graph.json`
  - **Reason**: Replaced by `directives-interactions.json`
  - **Action**: `rm docs/directives_project_graph.json`
  - **Files affected**: 1
  - **Validation**: File no longer exists

#### Task 1.2: Create Interactions File Structure
- [x] Create `docs/directives-interactions.json`
  - **Format**:
    ```json
    [
      {
        "source": "directive_name",
        "target": "directive_name",
        "relation_type": "triggers|depends_on|escalates_to|cross_link|fp_reference",
        "description": "Human-readable relationship description",
        "weight": 1,
        "active": true
      }
    ]
    ```
  - **Status**: Pending

---

### Phase 2: Update Directive JSON Files

#### Task 2.1: Add Missing Fields to FP Core Directives
**File**: `docs/directives-fp-core.json`
**Directives to update**: 18 directives

For each directive, add:
- [x] `parent_directive` field (NULL for most FP directives)
- [x] `md_file_path` field (e.g., `"directives/fp_purity.md"`)

**Example before**:
```json
{
  "name": "fp_purity",
  "type": "fp",
  "category": {...},
  "description": "...",
  ...
}
```

**Example after**:
```json
{
  "name": "fp_purity",
  "type": "fp",
  "parent_directive": null,
  "category": {...},
  "description": "...",
  "md_file_path": "directives/fp_purity.md",
  ...
}
```

**Directives**:
- [x] fp_purity
- [x] fp_state_elimination
- [x] fp_side_effect_detection
- [x] fp_immutability
- [x] fp_const_refactoring
- [x] fp_no_reassignment
- [x] fp_ownership_safety
- [x] fp_borrow_check
- [x] fp_no_oop
- [x] fp_wrapper_generation
- [x] fp_inheritance_flattening
- [x] fp_chaining
- [x] fp_currying
- [x] fp_pattern_matching
- [x] fp_tail_recursion
- [x] fp_type_safety
- [x] fp_type_inference
- [x] fp_side_effects_flag

---

#### Task 2.2: Add Missing Fields to FP Aux Directives
**File**: `docs/directives-fp-aux.json`
**Directives to update**: 10 directives

- [x] fp_guard_clauses
- [x] fp_conditional_elimination
- [x] fp_generic_constraints
- [x] fp_runtime_type_check
- [x] fp_io_isolation
- [x] fp_logging_safety
- [x] fp_parallel_purity
- [x] fp_task_isolation
- [x] fp_call_graph_generation
- [x] fp_reflection_limitation

---

#### Task 2.3: Add Missing Fields to Project Directives
**File**: `docs/directives-project.json`
**Directives to update**: 22 directives

For each directive, add:
- [x] `parent_directive` field (set appropriately based on hierarchy)
- [x] `md_file_path` field (e.g., `"directives/project_init.md"`)

**Parent Directive Mapping**:
- Level 0: `parent_directive: null`
- Level 1: `parent_directive: "aifp_run"`
- Level 2+: Set based on logical parent (refer to workflow dependencies)

**Directives**:
- [x] aifp_run (Level 0, parent: null)
- [x] project_init (Level 1, parent: "aifp_run")
- [x] project_task_decomposition (Level 2, parent: "aifp_run")
- [x] project_add_path (Level 2, parent: "project_task_decomposition")
- [x] project_file_write (Level 3, parent: "project_add_path")
- [x] project_update_db (Level 3, parent: "project_file_write")
- [x] project_compliance_check (Level 4, parent: "project_update_db")
- [x] project_completion_check (Level 4, parent: "project_compliance_check")
- [x] project_error_handling (Level 4, parent: "project_compliance_check")
- [x] project_evolution (Level 4, parent: "project_completion_check")
- [x] project_user_referral (Level 4, parent: "project_error_handling")
- [x] project_theme_flow_mapping (Level 3, parent: "project_file_write")
- [x] project_metrics (Level 4, parent: "project_completion_check")
- [x] project_performance_summary (Level 4, parent: "project_metrics")
- [x] project_dependency_sync (Level 3, parent: "project_update_db")
- [x] project_integrity_check (Level 4, parent: "project_dependency_sync")
- [x] project_auto_resume (Level 3, parent: "aifp_run")
- [x] project_backup_restore (Level 4, parent: "project_integrity_check")
- [x] project_archive (Level 4, parent: "project_completion_check")
- [x] project_refactor_path (Level 3, parent: "project_evolution")
- [x] project_dependency_map (Level 3, parent: "project_dependency_sync")
- [x] project_auto_summary (Level 4, parent: "project_metrics")

---

### Phase 3: Create Directive Interactions File

#### Task 3.1: Extract Interactions from directives_project_graph.json
- [x] Review `docs/directives_project_graph.json` for existing relationships
- [x] Map to new interaction format:
  - `triggers` → same
  - `depends_on` → same
  - `escalates_to` → same
  - `cross_links` → `cross_link` (singular)
  - `fp_links` → `fp_reference`

#### Task 3.2: Add FP Directive Interactions
- [x] Add FP → FP relationships (e.g., fp_purity → fp_immutability)
- [x] Add FP → Project references where needed
- [x] Document interaction rationale in description field

#### Task 3.3: Populate directives-interactions.json
**Estimated entries**: ~80-100 interactions

**Key relationships to capture**:
- [x] aifp_run triggers (project_init, project_task_decomposition, etc.)
- [x] project_file_write fp_references (fp_purity, fp_side_effect_detection)
- [x] project_compliance_check fp_references (fp_purity, fp_no_oop, etc.)
- [x] project_update_db fp_references (fp_dependency_tracking)
- [x] All escalates_to relationships (error handling paths)
- [x] All depends_on relationships (execution order)

---

### Phase 4: Validation

#### Task 4.1: Validate JSON Syntax
- [x] Run JSON linter on all directive files
  ```bash
  for file in docs/directives-*.json; do
    python -m json.tool "$file" > /dev/null && echo "✓ $file" || echo "✗ $file"
  done
  ```

#### Task 4.2: Validate Required Fields
- [x] Create validation script to check all required fields present
- [x] Verify parent_directive references exist
- [x] Verify md_file_path follows naming convention

#### Task 4.3: Validate Interactions
- [x] Verify all source/target directives exist
- [x] Verify relation_type values are valid
- [x] Check for circular dependencies

#### Task 4.4: Schema Compliance Check
- [x] Compare directive JSON structure against `schemaExampleMCP.sql`
- [x] Verify field types match (TEXT, JSON, REAL, INTEGER)
- [x] Document any intentional deviations

---

### Phase 5: Documentation Updates

#### Task 5.1: Update Blueprint Documentation
- [x] Update `docs/blueprint_fp_directives.md` to reflect new structure
- [x] Update `docs/blueprint_project_directives.md` to reflect new structure
- [x] Remove references to `directives_project_graph.json`

#### Task 5.2: Update notes.txt
- [x] Mark "Add cross-links between FP and Project directives" as complete
- [x] Add note about new interactions file
- [x] Document any outstanding questions

---

## Validation Checklist

Before marking this plan complete, verify:

- [x] All directive JSON files have required fields
- [x] All md_file_path values follow convention: `directives/<directive_name>.md`
- [x] All parent_directive values reference existing directives or are null
- [x] directives-interactions.json covers all major relationships
- [x] No references to directives_project_graph.json remain
- [x] JSON syntax is valid in all files
- [x] sync-directives.py can be updated to use new structure (next phase)

---

## Next Steps (After Completion)

1. Update `docs/sync-directives.py` to:
   - Use new field names
   - Load from `directives-interactions.json`
   - Handle parent_directive field
   - Populate md_file_path in database

2. Create `docs/extract-directives.py` to:
   - Extract directives from aifp_core.db
   - Generate JSON files in `extracted-directives/` folder
   - Split by type (fp-core, fp-aux, project)
   - Export interactions separately

3. Create markdown files for directives that need detailed documentation

---

## Notes

- **Design Decision**: Keep project directives in single file (22 directives is manageable)
- **FP directives remain split**: fp-core (18) and fp-aux (10) for better organization
- **Interactions**: Separate file provides cleaner separation of concerns
- **Schema alignment**: Critical for smooth transition to implementation phase
