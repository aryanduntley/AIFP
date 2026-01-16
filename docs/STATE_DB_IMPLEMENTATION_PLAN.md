# Implementation Plan: State Database Infrastructure

## ✅ IMPLEMENTATION COMPLETE (2026-01-16)

**Status**: All documentation, templates, and planning complete. Helper functions coded as part of `docs/HELPER_IMPLEMENTATION_PLAN.md`.

**What's Done**:
- ✅ Template files created (`runtime.db`, `README.md`, `state_operations.py`)
- ✅ Helper specifications added to JSON (4 helpers)
- ✅ Directives updated (project_init MD + JSON)
- ✅ System prompt updated
- ✅ FP directives updated (fp_state_elimination, project_file_write)
- ✅ Schema verified (infrastructure table)
- ✅ Implementation plan updated

**Remaining**: Helper function coding in `src/aifp/helpers/project/metadata.py` - See Phase 3 of `docs/HELPER_IMPLEMENTATION_PLAN.md`.

---

## Overview
Create FP-compliant runtime state database to replace mutable global variables. Auto-initialized during `project_init` in user's source directory.

---

## Phase 1: Pre-Made Template Files

### Create New Files

**Location**: `src/aifp/templates/state_db/`

1. **`runtime.db`** - SQLite database with schema pre-applied
   ```sql
   -- Schema to apply before saving:
   CREATE TABLE variables (
       var_name TEXT PRIMARY KEY,
       var_value TEXT NOT NULL,
       var_type TEXT,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );

   CREATE TRIGGER update_variable_timestamp
   AFTER UPDATE ON variables
   FOR EACH ROW
   BEGIN
       UPDATE variables SET updated_at = CURRENT_TIMESTAMP
       WHERE var_name = OLD.var_name;
   END;

   CREATE INDEX idx_variables_type ON variables(var_type);

   CREATE TABLE schema_version (
       id INTEGER PRIMARY KEY CHECK (id = 1),
       version TEXT NOT NULL DEFAULT '1.0',
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );

   INSERT INTO schema_version (id, version) VALUES (1, '1.0');
   ```

2. **`README.md`** - Documentation (full content from earlier conversation)
   - Explains purpose (FP mutable variable replacement)
   - Usage examples
   - When to use / not use
   - Schema reference
   - Extending instructions

3. **`state_operations.py`** - Python example with full CRUD operations
   - `set_var(var_name, value, var_type=None) -> Result`
   - `get_var(var_name) -> Result`
   - `delete_var(var_name) -> Result`
   - `increment_var(var_name, amount=1) -> Result`
   - `list_vars(var_type=None) -> Result`
   - Result dataclass for error handling
   - Full docstrings
   - Type hints
   - Path constant: `STATE_DB_PATH: Final[str] = ".state/runtime.db"`

---

## Phase 2: Helper Functions

### Update Existing File

**Location**: `src/aifp/helpers/project/metadata.py`

**Add New Functions**:

1. **`get_source_directory(db_path: str) -> SourceDirResult`**
   - Query: `SELECT value FROM infrastructure WHERE type='source_directory'`
   - Returns error if not found: "Source directory not configured. Must call add_source_directory() first."
   - Returns SourceDirResult with source directory path

2. **`add_source_directory(db_path: str, source_dir: str) -> SourceDirResult`**
   - Check if already exists (error if duplicate)
   - Validate source_dir (no absolute paths, no `..`)
   - Insert: `INSERT INTO infrastructure (type, value, description) VALUES ('source_directory', source_dir, 'Primary source code directory')`
   - Universal type name: `"source_directory"`

3. **`update_source_directory(db_path: str, new_source_dir: str) -> SourceDirResult`**
   - Check if exists (error if not found)
   - Validate new_source_dir
   - Update: `UPDATE infrastructure SET value=?, updated_at=CURRENT_TIMESTAMP WHERE type='source_directory'`

**Add Dataclass**:
```python
@dataclass(frozen=True)
class SourceDirResult:
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
```

**Constant**:
```python
INFRASTRUCTURE_TYPE_SOURCE_DIR: Final[str] = "source_directory"
```

**Note**: Delete functionality uses existing generic delete helper

---

### Update Helper JSON

**Location**: `docs/helpers/json/helpers-project-1.json`

**Add Four New Helper Entries**:

1. `get_source_directory` entry
2. `add_source_directory` entry
3. `update_source_directory` entry
4. `initialize_state_database` entry

(Full JSON structure provided in earlier conversation)

---

## Phase 3: Directive Updates

### 3.1: Update `project_init` Directive (Markdown)

**Location**: `src/aifp/reference/directives/project_init.md`

**Add New Step 3.5** (after "Step 3: Gather Project Information"):

```markdown
**Step 3.5: Determine Source Code Directory**

Purpose: Identify where source code will live (required for state database).

Workflow:
1. Check user settings: get_user_settings()['project_continue_without_user_interaction']
2. Scan for existing directories: src/, lib/, app/, pkg/, source/
3. Find directory with code files if exists
4. Check language conventions:
   - Python: src/ or root
   - Rust: src/ (cargo enforced)
   - Go: root or pkg/
   - JavaScript/TypeScript: src/ or lib/
5. Decision:
   - If existing source dir found → use it
   - If no code AND auto_proceed → default to src/
   - If no code AND user interaction → prompt user (default: src/)
6. Store: add_source_directory(project_db_path, source_dir)

Result: Source directory stored in infrastructure table with type='source_directory'
```

**Add New Step 9.5** (after "Step 9: Initialize user_preferences.db"):

```markdown
**Step 9.5: Initialize State Database Infrastructure**

Purpose: Create FP-compliant infrastructure for runtime mutable variables.

Prerequisites: Source directory determined in Step 3.5

Workflow:
1. Get source directory:
   - source_dir_result = get_source_directory(project_db_path)
   - If not success, return error

2. Get project language:
   - language = get_project_language() OR query infrastructure table

3. Call initialize_state_database helper:
   - result = initialize_state_database(project_root, source_dir, language)
   - Helper creates .state directory, copies template files
   - Returns StateInitResult with paths and needs_language_rewrite flag

4. If needs_language_rewrite is True (language != Python):
   - AI rewrites operations file to match project language:
     * Read state_operations.py to understand operations
     * Rewrite in target language using appropriate SQLite library
     * Use language conventions (naming, types, error handling)
     * Include: set_var, get_var, delete_var, increment_var, list_vars
     * Delete .py file, write new state_operations.{ext}

5. Update ProjectBlueprint.md:
   - Add "State Management" section
   - Document location: {source_dir}/.state/
   - Note: "Runtime mutable variable storage for FP compliance"

Result: State database ready at {source_dir}/.state/

Files created:
- {source_dir}/.state/runtime.db (ready to use)
- {source_dir}/.state/README.md (documentation)
- {source_dir}/.state/state_operations.{ext} (language-specific)
```

**Update "Files Created" List** (Step 10: Return Success):
- Add mention of `.state/` infrastructure

---

### 3.2: Update `project_init` Directive (JSON)

**Location**: `docs/directives-json/directives-project.json`

**Find**: `project_init` object

**Update Workflow**:
- Add branching logic for Step 3.5 (source directory determination)
- Add branching logic for Step 9.5 (state database initialization)

**Add to workflow.branches**:
```json
{
  "if": "source_directory_determined",
  "then": "store_in_infrastructure_table",
  "details": "Call add_source_directory(db_path, source_dir)"
},
{
  "if": "state_db_language_not_python",
  "then": "ai_rewrite_operations_file",
  "details": "AI rewrites state_operations.py to target language"
}
```

---

### 3.3: Check Directive Flows

**Location**: `docs/directives-json/directive_flow_project.json`

**Review**: No new flows needed (state DB creation happens within `project_init`)

**Confirm**: `project_init` → `aifp_status` completion loop still applies

---

## Phase 4: Schema Updates

### 4.1: Verify Infrastructure Table

**Location**: `src/aifp/database/schemas/project.sql`

**Verify Table Exists**:
```sql
CREATE TABLE IF NOT EXISTS infrastructure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**If Missing**: Add to schema

**Note**: This table stores `source_directory` with universal type name

---

## Phase 5: System Prompt Updates

### 5.1: Update Main System Prompt

**Location**: `sys-prompt/aifp_system_prompt.txt`

**Find Section**: "Runtime State Management"

**Update To**:
```
**Runtime State Management**:
⚠️ Mutable global variables strongly discouraged

✅ **State database auto-created during project init:**
- Location: <source-dir>/.state/runtime.db
- Purpose: Replace mutable global variables with database-backed state
- Base operations: set_var(), get_var(), delete_var(), increment_var()
- Import from: from .state.state_operations import set_var, get_var
- Use cases: counters, toggles, runtime config, application state
- AI can extend schema with additional tables as needed

Example usage:
```python
from .state.state_operations import set_var, get_var, increment_var

# Set variable
result = set_var('counter', 0)

# Get variable
result = get_var('counter')
if result.success:
    print(result.data)

# Increment
result = increment_var('counter', 1)
```

Note: Session management, rate limiting, job queues should use separate
project-specific databases if needed, not the state runtime database.
```

---

## Phase 6: FP Directive Updates

### 6.1: Update `fp_state_elimination`

**Location**: `src/aifp/reference/directives/fp_state_elimination.md`

**Add at Top** (after Purpose section):

```markdown
## State Database Infrastructure

**Auto-Generated During Init**: AIFP creates `.state/runtime.db` during project
initialization with base operations in `state_operations.{ext}`.

**Use For**:
- Replacing mutable global variables
- Runtime configuration that changes during execution
- Application state (counters, toggles, flags)

**Import and Use**:
```python
from .state.state_operations import set_var, get_var, increment_var

# Instead of global variable:
# global counter  # ❌ Don't do this

# Use state database:
result = set_var('counter', 0)  # ✅ FP-compliant
result = increment_var('counter', 1)
```

**Location**: `<source-dir>/.state/runtime.db`
```

**Update Examples** (Strategy 3 in Branch 2):
- Add reference to using state database as alternative to functional state threading

---

### 6.2: Update `project_file_write`

**Location**: `src/aifp/reference/directives/project_file_write.md`

**Find Section**: "Code Organization and DRY Principle"

**Add Subsection** (after "Scope-Based Extraction Strategy"):

```markdown
### State Management Pattern

**State Database Available**: For runtime mutable state needs, use the auto-generated
state database instead of mutable globals.

**Location**: `<source-dir>/.state/runtime.db`

**Operations**: Import from `state_operations.{ext}`:
- `set_var(var_name, value)` - Store variable
- `get_var(var_name)` - Retrieve variable
- `delete_var(var_name)` - Remove variable
- `increment_var(var_name, amount)` - Increment counter

**When to Use**:
- ✅ Replacing mutable global variables
- ✅ Application state that changes at runtime
- ✅ Counters, toggles, runtime config

**When NOT to Use**:
- ❌ Session management (create separate DB)
- ❌ User data (use application database)
- ❌ Project-specific business logic (create separate DB)
```

---

## Phase 7: Documentation Updates

### 7.1: Update ProjectBlueprint Template

**Location**: `src/aifp/templates/` (if template exists)

**Add Section**: "State Management"
- Document `.state/` directory
- Explain runtime variable storage
- Reference operations file

---

### 7.2: Update README

**Location**: `README.md` (project root)

**Add to Features** (if state DB is mentioned):
- "Auto-generated state database for FP-compliant mutable variable management"

---

## Phase 8: Testing & Validation

### Test Cases

1. **Source Directory Detection**:
   - Empty project → defaults to `src/`
   - Existing `src/` with code → uses `src/`
   - Existing `lib/` with code → uses `lib/`
   - Multiple candidates → prompts user (or auto-selects based on language)

2. **State DB Creation**:
   - Python project → copies files as-is
   - JavaScript project → AI rewrites to JS
   - Rust project → AI rewrites to Rust
   - Verify all files copied to correct location

3. **Helper Functions**:
   - `add_source_directory()` → success
   - `add_source_directory()` again → error (duplicate)
   - `get_source_directory()` before add → error
   - `get_source_directory()` after add → returns path
   - `update_source_directory()` → success

4. **Infrastructure Table**:
   - Verify `source_directory` entry created
   - Verify universal type name used
   - Verify retrievable after init

---

## File Checklist

### New Files to Create
- [x] `src/aifp/templates/state_db/runtime.db` ✅
- [x] `src/aifp/templates/state_db/README.md` ✅
- [x] `src/aifp/templates/state_db/state_operations.py` ✅

### Files to Update
- [ ] `src/aifp/helpers/project/metadata.py` (add 4 functions) - **See HELPER_IMPLEMENTATION_PLAN.md**
- [x] `docs/helpers/json/helpers-project-1.json` (add 4 entries) ✅
- [x] `src/aifp/reference/directives/project_init.md` (add Steps 3.5 & 9.5) ✅
- [x] `docs/directives-json/directives-project.json` (update workflow) ✅
- [x] `sys-prompt/aifp_system_prompt.txt` (update state management section) ✅
- [x] `src/aifp/reference/directives/fp_state_elimination.md` (add state DB reference) ✅
- [x] `src/aifp/reference/directives/project_file_write.md` (add state management pattern) ✅

### Files to Review
- [x] `docs/directives-json/directive_flow_project.json` (confirmed no changes needed) ✅
- [x] `src/aifp/database/schemas/project.sql` (infrastructure table verified) ✅
- [ ] `README.md` (optional: mention feature) - **Not priority**

---

## Implementation Order

1. ✅ **Phase 1**: Create template files (runtime.db, README.md, state_operations.py)
2. ✅ **Phase 2**: Add helper JSON entries (coding deferred to HELPER_IMPLEMENTATION_PLAN.md)
3. ✅ **Phase 3**: Update project_init directive (MD and JSON)
4. ✅ **Phase 4**: Verify schema (infrastructure table)
5. ✅ **Phase 5**: Update system prompt
6. ✅ **Phase 6**: Update FP directives (fp_state_elimination, project_file_write)
7. ✅ **Phase 7**: Update documentation (STATE_DB_IMPLEMENTATION_PLAN.md, HELPER_IMPLEMENTATION_PLAN.md)
8. ⏳ **Phase 8**: Helper function coding - See `docs/HELPER_IMPLEMENTATION_PLAN.md` Phase 3, Schema/CRUD/Metadata section

**Note**: Helper function implementation (`get_source_directory`, `add_source_directory`, `update_source_directory`, `initialize_state_database`) will be completed as part of the main helper implementation workflow alongside the other 217 helpers.

---

## Key Decisions Summary

| Decision | Choice |
|----------|--------|
| **Database Location** | `<source-dir>/.state/runtime.db` |
| **Schema Storage** | Baked into runtime.db (no separate .sql file) |
| **Operations File** | Python example, AI rewrites for other languages |
| **Source Dir Entry** | Universal name: `"source_directory"` in infrastructure table |
| **Helper Location** | `src/aifp/helpers/project/metadata.py` |
| **Template Location** | `src/aifp/templates/state_db/` |
| **Init Step** | Step 3.5 (source dir), Step 9.5 (state DB) |

---

## Notes

- **No schema.sql needed**: Schema already applied to runtime.db
- **Language-agnostic**: AI handles rewriting for non-Python languages
- **Minimal scope**: Just variable storage, not sessions/queues/etc
- **Extensible**: AI can add tables for edge cases as needed
- **Universal naming**: `"source_directory"` in infrastructure table for consistency

---

## Full Content Templates

### Template: README.md (for .state/ directory)

```markdown
# State Database - Runtime Mutable Variables

**Purpose**: FP-compliant replacement for mutable global variables.

## What This Is

This directory contains a lightweight SQLite database for managing runtime mutable state in a functional programming context. Instead of using mutable global variables (which violate FP principles), use this database-backed state management.

## Why This Exists

In FP, functions should be pure (no side effects, no hidden state). However, real applications need mutable state (counters, toggles, runtime config). This database provides **explicit, traceable state mutations** while maintaining FP compliance.

## Usage

Import the state operations module in your source files:

```python
from .state import state_operations as state

# Set a variable
result = state.set_var('counter', 0)

# Get a variable
result = state.get_var('counter')
if result.success:
    print(f"Counter: {result.data}")

# Increment (common for counters)
result = state.increment_var('counter', 1)

# Delete a variable
result = state.delete_var('counter')
```

## Files

- **runtime.db**: SQLite database storing variable state
- **README.md**: This file
- **state_operations.{ext}**: CRUD helper functions for this database

## Schema

The database has a simple key-value structure:

```sql
CREATE TABLE variables (
    var_name TEXT PRIMARY KEY,
    var_value TEXT NOT NULL,
    var_type TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

## When to Use

- ✅ Replacing mutable global variables (`global counter`)
- ✅ Runtime configuration that changes during execution
- ✅ Application state that needs to persist across function calls
- ✅ Counters, toggles, flags

## When NOT to Use

- ❌ Session management (create separate database)
- ❌ User data storage (use application database)
- ❌ Rate limiting (create separate database)
- ❌ Job queues (create separate database)

## Extending

You can add tables to this database for additional state needs. AI can help extend the schema and operations as required.

---

**Generated by AIFP** during project initialization.
```

### Template: state_operations.py (Python example)

```python
# state_operations.py - Auto-generated state variable helpers
# Location: <source-dir>/.state/state_operations.py
# Generated by AIFP during project initialization

from typing import Final, Optional, Any
from dataclasses import dataclass
import sqlite3
import json
import os

# Read-only constant for database path
STATE_DB_PATH: Final[str] = os.path.join(os.path.dirname(__file__), "runtime.db")

@dataclass(frozen=True)
class Result:
    """Result type for explicit error handling."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# === Core Variable Operations ===

def set_var(var_name: str, value: Any, var_type: Optional[str] = None) -> Result:
    """
    Effect: Store variable in state database.

    Replaces mutable global variables with database-backed state.

    Args:
        var_name: Variable identifier (e.g., 'counter', 'config_debug_mode')
        value: Value to store (will be JSON-serialized)
        var_type: Optional type hint ('int', 'str', 'bool', 'dict', 'list')

    Returns:
        Result with success status
    """
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        # Serialize value
        if isinstance(value, (dict, list)):
            serialized_value = json.dumps(value)
            inferred_type = 'dict' if isinstance(value, dict) else 'list'
        elif isinstance(value, bool):
            serialized_value = json.dumps(value)
            inferred_type = 'bool'
        elif isinstance(value, (int, float)):
            serialized_value = str(value)
            inferred_type = 'int' if isinstance(value, int) else 'float'
        else:
            serialized_value = str(value)
            inferred_type = 'str'

        conn.execute(
            """INSERT OR REPLACE INTO variables (var_name, var_value, var_type, updated_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (var_name, serialized_value, var_type or inferred_type)
        )
        conn.commit()
        return Result(success=True)
    except Exception as e:
        return Result(success=False, error=f"Failed to set variable: {str(e)}")
    finally:
        conn.close()

def get_var(var_name: str) -> Result:
    """
    Effect: Retrieve variable from state database.

    Args:
        var_name: Variable identifier

    Returns:
        Result with deserialized value or error
    """
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        row = conn.execute(
            "SELECT var_value, var_type FROM variables WHERE var_name=?",
            (var_name,)
        ).fetchone()

        if not row:
            return Result(success=False, error=f"Variable '{var_name}' not found")

        value_str, var_type = row[0], row[1]

        # Deserialize based on type
        if var_type == 'int':
            value = int(value_str)
        elif var_type == 'float':
            value = float(value_str)
        elif var_type in ('bool', 'dict', 'list'):
            value = json.loads(value_str)
        else:
            value = value_str

        return Result(success=True, data=value)
    except Exception as e:
        return Result(success=False, error=f"Failed to get variable: {str(e)}")
    finally:
        conn.close()

def delete_var(var_name: str) -> Result:
    """
    Effect: Delete variable from state database.

    Args:
        var_name: Variable identifier

    Returns:
        Result with success status
    """
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        conn.execute("DELETE FROM variables WHERE var_name=?", (var_name,))
        conn.commit()

        if conn.total_changes == 0:
            return Result(success=False, error=f"Variable '{var_name}' not found")

        return Result(success=True)
    except Exception as e:
        return Result(success=False, error=f"Failed to delete variable: {str(e)}")
    finally:
        conn.close()

def increment_var(var_name: str, amount: int = 1) -> Result:
    """
    Effect: Increment numeric variable (creates if doesn't exist).

    Common use case for counters.

    Args:
        var_name: Variable identifier
        amount: Amount to increment by (default 1)

    Returns:
        Result with new value
    """
    result = get_var(var_name)

    if not result.success:
        # Create new counter starting at 0
        current_value = 0
    else:
        current_value = result.data
        if not isinstance(current_value, (int, float)):
            return Result(success=False, error=f"Variable '{var_name}' is not numeric")

    new_value = current_value + amount
    set_result = set_var(var_name, new_value, 'int')

    if not set_result.success:
        return set_result

    return Result(success=True, data=new_value)

def list_vars(var_type: Optional[str] = None) -> Result:
    """
    Effect: List all variables (optionally filtered by type).

    Args:
        var_type: Optional type filter ('int', 'str', 'bool', etc.)

    Returns:
        Result with list of variable names
    """
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        if var_type:
            rows = conn.execute(
                "SELECT var_name FROM variables WHERE var_type=? ORDER BY var_name",
                (var_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT var_name FROM variables ORDER BY var_name"
            ).fetchall()

        var_names = [row[0] for row in rows]
        return Result(success=True, data=var_names)
    except Exception as e:
        return Result(success=False, error=f"Failed to list variables: {str(e)}")
    finally:
        conn.close()
```

---

## 🎉 Implementation Status: COMPLETE

**Completed**: 2026-01-16

### What Was Accomplished

**Infrastructure Created**:
- ✅ 3 template files in `src/aifp/templates/state_db/`
- ✅ Pre-built SQLite database with schema
- ✅ Complete documentation (README.md)
- ✅ Python example code (state_operations.py)

**Documentation Updated**:
- ✅ 4 helper specifications added to `helpers-project-1.json`
- ✅ Helper count: 218 → 222 total helpers
- ✅ `project_init` directive: Added Steps 3.5 and 9.5
- ✅ Directive JSON: Added 2 workflow branches
- ✅ System prompt: Updated Runtime State Management section
- ✅ FP directives: Added state DB guidance
- ✅ Helper implementation plan: Updated counts and sections

**Schema Verified**:
- ✅ `infrastructure` table supports `source_directory` storage
- ✅ Universal entry name: `type='source_directory'`

### What's Next

**Helper Function Coding**: The 4 new helper functions will be implemented as part of the main helper coding workflow:

1. `get_source_directory()` - Retrieve from infrastructure table
2. `add_source_directory()` - Store with validation
3. `update_source_directory()` - Update existing entry
4. `initialize_state_database()` - Copy templates and setup

See `docs/HELPER_IMPLEMENTATION_PLAN.md` → Phase 3 → Schema, CRUD, & Metadata section.

---

## Summary

The state database infrastructure is **fully specified and ready for use**. When `project_init` is executed after helper implementation:

1. AI determines source directory (Step 3.5)
2. AI calls `initialize_state_database()` (Step 9.5)
3. Templates copied to `<source-dir>/.state/`
4. Operations file rewritten if language != Python
5. ProjectBlueprint.md updated with State Management section

Users will have **automatic FP-compliant mutable variable management** out of the box.
