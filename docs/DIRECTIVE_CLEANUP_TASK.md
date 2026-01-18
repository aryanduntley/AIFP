# Directive Architecture Cleanup - Task Document

**Date**: 2026-01-17
**Status**: Cleanup Required
**Priority**: High - Architectural consistency and maintainability
**Scope**: Remove outdated patterns, establish helper-based architecture

---

## Executive Summary

The directive documentation contains outdated architectural patterns that conflict with the current helper-based MCP system:

1. **36 references to `aifp.scripts`** - non-existent module from pre-MCP planning
2. **Direct SQL queries in directives** - violates helper abstraction layer
3. **Missing orchestrator helpers** - `project_init` and others not defined
4. **Inconsistent directive → helper mappings** - some use `module:`, some use `helper:`

**Goal**: Align all directive documentation with the current MCP helper-based architecture.

---

## Issue 1: Direct SQL Queries in Directives

### Problem

Directives contain raw SQL queries that should be abstracted into helper functions.

### Example Found

**File**: `docs/directives-json/directives-project.json`
**Line**: 1911

```json
{
  "if": "infrastructure_loaded",
  "then": "load_infrastructure_context",
  "details": {
    "query": "SELECT type, value, description FROM infrastructure WHERE project_id = ?"
  }
}
```

**Issues**:
1. ❌ Direct SQL in directive (violates abstraction)
2. ❌ References `project_id` column (removed - one project per database)
3. ❌ Doesn't reference helper function

### Required Fix

Replace with:
```json
{
  "if": "infrastructure_loaded",
  "then": "load_infrastructure_context",
  "details": {
    "helper": "get_all_infrastructure",
    "note": "Returns all infrastructure rows - helpers change frequently, query database for correct helper name if needed"
  }
}
```

### Action Items

- [ ] Search all directive JSON files for `"query":` keys
- [ ] Identify each direct SQL query
- [ ] Determine appropriate helper function (create if doesn't exist)
- [ ] Replace SQL with helper reference
- [ ] Update implementation to call helper instead of executing SQL

### Commands to Find All Direct Queries

```bash
# Find all direct SQL queries in directives
grep -r '"query":' /home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/ \
  --include="*.json" -n

# Find SQL keywords in directives
grep -r '\(SELECT\|INSERT\|UPDATE\|DELETE\|WHERE\)' \
  /home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/ \
  --include="*.json" -n | grep -v "description"
```

---

## Issue 2: `aifp.scripts` References (Non-existent Module)

### Problem

**36 references** to `aifp.scripts.init_aifp_project` - a module that was **planned but never implemented**.

### Origin

From `docs/updates-summaries/init-script-planning.md`:
- **Date**: 2025-10-25
- **Purpose**: Pre-MCP standalone initialization script
- **Status**: Planning document only - never implemented

### Current Reality

- ✅ **MCP server IS implemented** (current system)
- ✅ **Helper-based architecture IS the standard**
- ❌ **`aifp.scripts` directory exists but is empty**
- ❌ **No code implementation for standalone script**

### Files Containing `aifp.scripts` References

```
docs/directives-json/directives-project.json (4 references)
docs/helpers/DIRECTIVE_NAMES_REFERENCE.md
docs/COMPLETE/helpers/helper-functions-reference.md
docs/updates-summaries/session-updates-summary.md
docs/updates-summaries/init-script-planning.md
docs/directive-review-plan.md
docs/implementation-plans/phase-1-mcp-server-bootstrap.md
docs/directives-json/Tasks/DIRECTIVE_CLEANUP_TASK.md
docs/directives-json/backups/directives-project_20251207_164554.json (3 files)
```

### Example References in `directives-project.json`

**Line 246**:
```json
{
  "if": "source_directory_determined",
  "then": "create_project_structure",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {"target_path": "user_working_dir"},
    "note": "Uses standalone initialization script helper function"
  }
}
```

**Line 261**:
```json
{
  "if": "structure_created",
  "then": "generate_project_blueprint",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {"aifp_dir": ".aifp-project/", "metadata": "from_prompts"},
    "note": "Uses standalone initialization script helper function"
  }
}
```

**Line 275**:
```json
{
  "if": "blueprint_generated",
  "then": "initialize_databases",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {"aifp_dir": ".aifp-project/", "project_metadata": "from_prompts"},
    "note": "Uses standalone initialization script helper functions"
  }
}
```

**Line 295**:
```json
{
  "if": "databases_initialized",
  "then": "validate_initialization",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {"aifp_dir": ".aifp-project/"},
    "note": "Validates complete initialization using script function"
  }
}
```

### Required Fix

Replace all `"module": "aifp.scripts.init_aifp_project"` with orchestrator/helper references:

```json
{
  "if": "ready_to_initialize",
  "then": "execute_initialization",
  "details": {
    "helper": "project_init",
    "note": "Orchestrator coordinates all initialization sub-helpers internally"
  }
}
```

### Action Items

- [ ] **Search and document all `aifp.scripts` references** (36 total)
- [ ] **Categorize by function** (init, validation, blueprint generation, etc.)
- [ ] **Map to existing or new helpers** (see Issue 3 below)
- [ ] **Replace all references** with helper-based approach
- [ ] **Archive planning documents** (mark as "outdated - pre-MCP planning")
- [ ] **Update README.md** if it references `aifp init` CLI command

### Commands to Find All References

```bash
# Find all aifp.scripts references
grep -r "aifp\.scripts" /home/eveningb4dawn/Desktop/Projects/AIFP/docs/ \
  --include="*.json" --include="*.md" -n

# Count total references
grep -r "aifp\.scripts" /home/eveningb4dawn/Desktop/Projects/AIFP/docs/ \
  --include="*.json" --include="*.md" | wc -l

# List unique files
grep -r "aifp\.scripts" /home/eveningb4dawn/Desktop/Projects/AIFP/docs/ \
  --include="*.json" --include="*.md" -l
```

---

## Issue 3: Missing Orchestrator Helpers

### Problem

Directives reference orchestrators that don't exist in `helpers-orchestrators.json`.

### Current Orchestrators (Verified)

From `docs/helpers/json/helpers-orchestrators.json`:

1. ✅ `aifp_run` - Main entry point orchestrator
2. ✅ `aifp_status` - Status orchestrator
3. ✅ `validate_initialization` - Validation helper
4. ✅ `get_work_context` - Work context loader
5. ✅ `get_project_status` - Status sub-helper
6. ✅ `get_project_context` - Context loader
7. ✅ `get_status_tree` - Status tree builder
8. ✅ `get_files_by_flow_context` - Flow file loader

### Missing Orchestrators

Based on directive workflow analysis:

1. ❌ **`project_init`** - Complete project initialization orchestrator
2. ❌ **`project_blueprint_generate`** - Blueprint generation orchestrator (if complex)
3. ❌ **`project_restore`** - Restore from .git/.aifp backup (if needed)

### Required: `project_init` Orchestrator

**Purpose**: Coordinate complete project initialization workflow.

**Responsibilities**:
1. Check if already initialized → error if exists
2. Scan for OOP patterns → abort if detected
3. Gather project info from user (name, purpose, goals)
4. Determine source directory
5. Create directory structure (`.aifp-project/`, `backups/`)
6. Initialize databases (project.db, user_preferences.db)
   - Load schemas
   - Insert project metadata
   - **Execute `standard_infrastructure.sql`**
   - Insert default completion path
7. Generate ProjectBlueprint.md
8. Initialize state database (`.state/` in source directory)
9. Validate initialization
10. Return success with guidance for AI

**Key Principle**: Init operations can execute directly in orchestrator
- Schema loading → execute directly
- SQL file execution → execute directly
- Database creation → execute directly
- File writes → execute directly

**Why**: Init only happens once. No need for individual helpers for these operations.

**Helper Definition**:

```json
{
  "name": "project_init",
  "file_path": "helpers/orchestrators/orchestrators.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "description": "Path to project root directory"
    },
    {
      "name": "project_name",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project name (NULL = infer from directory)"
    },
    {
      "name": "project_purpose",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project purpose (NULL = prompt user)"
    },
    {
      "name": "goals",
      "type": "array",
      "required": false,
      "default": [],
      "description": "Array of project goals"
    }
  ],
  "purpose": "Complete project initialization orchestrator. Coordinates all initialization steps including OOP scan, directory creation, database setup, blueprint generation, and state DB initialization. Ensures project is only initialized once.",
  "error_handling": "Return detailed error if: already initialized, OOP detected, directory permissions denied, database creation failed",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Project initialized successfully",
    "Created: .aifp-project/project.db, user_preferences.db, ProjectBlueprint.md, {source}/.state/",
    "Standard infrastructure entries created with empty values (6 entries)",
    "AI MUST now populate infrastructure values:",
    "  1. Detect from codebase: primary_language, build_tool, test_framework, runtime_version",
    "  2. Prompt user for confirmation or missing values",
    "  3. Update via: update_project_entry('infrastructure', id, {'value': '...'})",
    "Call get_all_infrastructure() to retrieve entries with IDs for updating"
  ],
  "target_database": "orchestrator",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "main_orchestrator",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "project_init directive calls project_init orchestrator to perform complete initialization workflow"
    }
  ],
  "implementation_notes": [
    "ORCHESTRATOR - executes initialization directly (no sub-helpers for one-time operations)",
    "Step 1: Check initialization status - query for .aifp-project/ existence",
    "Step 1.1: If exists, return error: 'Project already initialized. Use aifp_status to view.'",
    "Step 2: Scan for OOP patterns - search .py/.js/.ts files for class/self/this",
    "Step 2.1: If OOP detected (3+ patterns), abort with detailed error message",
    "Step 3: Gather project info - prompt user or infer from directory/files",
    "Step 3.5: Determine source directory - scan for src/lib/app, ask user if ambiguous",
    "Step 4: Create directories - .aifp-project/, backups/, logs/ (if automation)",
    "Step 5: Initialize project.db",
    "  - Load schema: schemas/project.sql",
    "  - INSERT project metadata",
    "  - Execute: initialization/standard_infrastructure.sql (6 entries with empty values)",
    "  - INSERT default completion_path (Setup, Development, Testing, Finalization)",
    "Step 6: Initialize user_preferences.db",
    "  - Load schema: schemas/user_preferences.sql",
    "  - INSERT default tracking_settings (all disabled)",
    "Step 7: Generate ProjectBlueprint.md from template",
    "Step 8: Create .gitkeep files",
    "Step 9.5: Initialize state database",
    "  - Call: initialize_state_database(project_root, source_dir, language)",
    "  - Creates: {source}/.state/runtime.db, README.md, state_operations.{ext}",
    "Step 10: Validate - check all files/databases exist and have expected structure",
    "Returns: {success: true, project_name, files_created[], next_steps[]}",
    "ERROR HANDLING: If any step fails, clean up partial initialization",
    "CRITICAL: Only executes if .aifp-project/ does NOT exist"
  ]
}
```

### Sub-Helpers Called by `project_init`

Some operations ARE worth extracting as helpers (reusable or complex):

1. ✅ **`initialize_state_database`** - ALREADY EXISTS (helpers-project-1.json)
2. ✅ **`add_source_directory`** - ALREADY EXISTS (helpers-project-1.json)
3. ✅ **`get_source_directory`** - ALREADY EXISTS (helpers-project-1.json)
4. ❌ **`scan_for_oop_patterns`** - NEEDS CREATION (reusable for validation)

**Not needed as separate helpers** (execute directly in orchestrator):
- Schema loading (one-time, simple file read)
- SQL execution (direct sqlite3 calls)
- Directory creation (simple os.makedirs)
- File writes (simple file operations)

---

## Issue 4: Helper Function System as Primary Interface

### Problem

Directives contain mixed patterns for referencing implementation:
- Some use `"module": "aifp.scripts.X"`
- Some use `"helper": "X"`
- Some use `"call_helper": "X()"`
- Some have no reference at all

### Standard Pattern

**Directives** = High-level guidance on WHAT and WHEN
**Helpers** = Implementation of HOW

### Required Pattern in Directives

```json
{
  "if": "condition",
  "then": "action_name",
  "details": {
    "helper": "helper_name",
    "note": "Additional context for AI",
    "ai_responsibilities": [
      "What AI should do before/after calling helper",
      "Decision points AI must handle"
    ]
  }
}
```

### Anti-Patterns to Remove

❌ **Direct module references**:
```json
"module": "aifp.scripts.init_aifp_project"  // Non-existent
```

❌ **Direct SQL queries**:
```json
"query": "SELECT * FROM infrastructure WHERE ..."  // Violates abstraction
```

❌ **Implementation details**:
```json
"implementation": "conn.execute(...)"  // Belongs in helper code, not directive
```

❌ **Python code in directives**:
```python
# ❌ Don't do this in directive docs
init_result = initialize_project_databases(...)
```

### Action Items

- [ ] Audit all directive JSON files for mixed patterns
- [ ] Standardize on `"helper": "name"` pattern
- [ ] Remove implementation details from directives
- [ ] Move implementation guidance to helper definitions
- [ ] Update directive markdown files to remove code examples

---

## Issue 5: Init-Specific Considerations

### Principle: Init Happens Once

**Implications**:
1. Schema execution → orchestrator can execute directly
2. File creation → orchestrator can write directly
3. SQL inserts → orchestrator can execute directly
4. No need for helpers like `create_directory()`, `load_schema()`, `insert_project_metadata()`

**Why**: These operations are:
- Non-reusable (only used during init)
- Simple (straightforward file/DB operations)
- Sequential dependencies (each step depends on previous)
- Better kept together for atomic initialization

### Init Safety Check

**CRITICAL**: `project_init` orchestrator MUST check if project already initialized.

```python
def project_init(project_root: str, **kwargs) -> dict:
    """Initialize new AIFP project."""

    # CRITICAL: Check if already initialized
    aifp_dir = os.path.join(project_root, '.aifp-project')

    if os.path.exists(aifp_dir):
        # Check if it's a valid AIFP project
        project_db = os.path.join(aifp_dir, 'project.db')
        if os.path.exists(project_db):
            return {
                "success": False,
                "error": "project_already_initialized",
                "message": "Project already initialized. Use aifp_status to view current state.",
                "existing_db": project_db,
                "recommendation": "Do not re-initialize. Data loss may occur."
            }

    # Proceed with initialization...
```

### What CAN Be Helpers in Init Context

**Extractable as helpers** (reusable or complex logic):

1. ✅ **`scan_for_oop_patterns(project_root)`** - Reusable for validation
2. ✅ **`detect_primary_language(project_root)`** - Reusable for analysis
3. ✅ **`detect_build_tool(project_root)`** - Reusable for analysis
4. ✅ **`initialize_state_database(...)`** - Already exists, complex operation
5. ✅ **`add_source_directory(...)`** - Already exists, updates DB
6. ✅ **`generate_blueprint_from_template(...)`** - Reusable for blueprint operations

**Execute directly in orchestrator** (one-time, simple):
- Load schema SQL file
- Execute schema SQL
- Create directories
- Execute standard_infrastructure.sql
- Insert project metadata
- Insert completion path
- Write .gitkeep files

---

## Issue 6: Other Directives Using `aifp.scripts`

### Analysis Needed

**Question**: What other operations were planned for `aifp.scripts` that need helpers?

### Commands to Analyze

```bash
# Extract all unique operations referenced via aifp.scripts
grep -r "aifp\.scripts" /home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/ \
  --include="*.json" -A 5 -B 5 | \
  grep -E '"then"|"note"|"purpose"'

# Check what each reference was meant to do
grep -r "aifp\.scripts" /home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json \
  -B 3 -A 10
```

### From Initial Analysis

**Operations found in `directives-project.json`**:

1. **`create_project_structure`** (line 246)
   - **Replace with**: Direct execution in `project_init` orchestrator
   - **Reason**: Simple directory creation (os.makedirs)

2. **`generate_project_blueprint`** (line 261)
   - **Replace with**: Helper `generate_blueprint_from_template()`
   - **Reason**: Reusable for blueprint updates

3. **`initialize_databases`** (line 275)
   - **Replace with**: Direct execution in `project_init` orchestrator
   - **Reason**: One-time schema loading and execution

4. **`validate_initialization`** (line 295)
   - **Replace with**: Existing helper `validate_initialization()` (already in helpers-orchestrators.json)
   - **Reason**: Already exists as helper

### Potential New Helpers Needed

Based on `aifp.scripts` functionality:

1. ❌ **`scan_for_oop_patterns(project_root)`**
   - **Purpose**: Detect OOP patterns to abort init
   - **Location**: helpers/project/validation.py
   - **Used by**: `project_init` orchestrator

2. ❌ **`detect_primary_language(project_root)`**
   - **Purpose**: Infer language from file extensions
   - **Location**: helpers/project/analysis.py
   - **Used by**: `project_init` orchestrator, AI post-init

3. ❌ **`detect_build_tool(project_root)`**
   - **Purpose**: Detect build tool from config files
   - **Location**: helpers/project/analysis.py
   - **Used by**: AI post-init infrastructure population

4. ❌ **`generate_blueprint_from_template(aifp_dir, metadata)`**
   - **Purpose**: Generate ProjectBlueprint.md from template
   - **Location**: helpers/project/blueprint.py
   - **Used by**: `project_init` orchestrator, blueprint updates

5. ❌ **`get_all_infrastructure()`**
   - **Purpose**: Return all infrastructure table rows
   - **Location**: helpers/project/metadata.py
   - **Used by**: `aifp_run`, AI infrastructure population

---

## Summary of Required Changes

### 1. Create New Files

- [ ] `src/aifp/database/initialization/standard_infrastructure.sql` - Standard infrastructure inserts
- [ ] Helper definitions for missing orchestrators/helpers in JSON

### 2. Update Existing Files

- [ ] `docs/helpers/json/helpers-orchestrators.json`
  - Add `project_init` orchestrator definition
  - Update `aifp_run` to include `infrastructure_data` in bundle

- [ ] `docs/helpers/json/helpers-project-1.json` (or new file)
  - Add `get_all_infrastructure()` helper
  - Add `scan_for_oop_patterns()` helper
  - Add `detect_primary_language()` helper
  - Add `detect_build_tool()` helper
  - Add `generate_blueprint_from_template()` helper

- [ ] `docs/directives-json/directives-project.json`
  - Remove all `"module": "aifp.scripts.init_aifp_project"` (4 occurrences)
  - Replace with `"helper": "project_init"`
  - Remove direct SQL queries
  - Replace with `"helper": "get_all_infrastructure"`

- [ ] `src/aifp/reference/directives/project_init.md`
  - Remove Python code examples
  - Make steps high-level conceptual guidance
  - Document AI's post-init responsibilities

### 3. Archive/Mark Outdated

- [ ] `docs/updates-summaries/init-script-planning.md` - Mark as "Outdated - Pre-MCP Planning"
- [ ] `docs/implementation-plans/phase-1-mcp-server-bootstrap.md` - Update or mark sections outdated
- [ ] Other planning docs referencing `aifp.scripts`

### 4. Search and Replace Operations

```bash
# Step 1: Find and document all aifp.scripts references
grep -r "aifp\.scripts" docs/ --include="*.json" --include="*.md" > aifp_scripts_references.txt

# Step 2: Find all direct SQL queries
grep -r '"query":.*SELECT' docs/directives-json/ --include="*.json" > direct_queries.txt

# Step 3: Find all module references
grep -r '"module":' docs/directives-json/ --include="*.json" > module_references.txt
```

---

## Acceptance Criteria

### Phase 1: Documentation Cleanup
- [ ] Zero references to `aifp.scripts` in active directives
- [ ] Zero direct SQL queries in directives
- [ ] All directives reference helpers using standard pattern
- [ ] All planning docs marked with appropriate status (active/outdated)

### Phase 2: Helper Definitions
- [ ] `project_init` orchestrator defined with complete implementation notes
- [ ] `get_all_infrastructure()` helper defined
- [ ] New analysis helpers defined (OOP scan, language detection, build tool detection)
- [ ] All helpers have `used_by_directives` mappings

### Phase 3: Implementation
- [ ] `standard_infrastructure.sql` created with 6 INSERT statements
- [ ] `project_init` orchestrator implemented (code)
- [ ] `get_all_infrastructure()` implemented (code)
- [ ] Analysis helpers implemented (code)
- [ ] Tests passing for initialization workflow

---

## Priority Order

### High Priority (Blocks infrastructure goals)
1. ✅ Create `standard_infrastructure.sql`
2. ✅ Define `project_init` orchestrator in helpers JSON
3. ✅ Define `get_all_infrastructure()` helper
4. ✅ Update `aifp_run` to include infrastructure in bundle
5. ✅ Replace `aifp.scripts` in `directives-project.json`

### Medium Priority (Consistency)
6. Remove direct SQL queries from directives
7. Add missing helper definitions (OOP scan, language detection)
8. Update directive markdown files to remove code examples

### Low Priority (Cleanup)
9. Archive outdated planning documents
10. Update README if referencing `aifp init` CLI
11. Document migration path for existing projects

---

## Next Steps

1. Review this document with team
2. Prioritize which changes to implement first
3. Create implementation tasks for each change
4. Begin with high-priority items (infrastructure goals)
5. Test initialization workflow with new architecture
