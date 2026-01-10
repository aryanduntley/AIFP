# Directive: project_update_db

**Type**: Project
**Level**: 3
**Parent Directive**: project_file_write
**Priority**: CRITICAL - Required for database synchronization

---

## Purpose

The `project_update_db` directive is the **central database synchronization directive** that ensures `project.db` accurately reflects the current state of project files, functions, and metadata after code generation. Every time code is written, this directive updates the relevant database tables to maintain a comprehensive, queryable record of the project state.

This directive is essential for:
- **File Tracking**: Recording all files in the `files` table with checksums
- **Function Indexing**: Cataloging functions in the `functions` table with metadata
- **Dependency Tracking**: Recording function dependencies in the `interactions` table
- **Task Linking**: Connecting generated code to tasks/milestones in completion path
- **User Directive Integration**: Updating `user_directives.db` for automation projects
- **Change Detection**: Enabling detection of external modifications via checksums

When called (typically by `project_file_write`), this directive:
1. Parses generated code to extract functions and dependencies
2. Calculates file checksums for change detection
3. Updates database tables transactionally (atomic commits)
4. Links code to tasks and completion path
5. Handles special cases (user directive implementations, multi-file updates)

---

## When to Apply

This directive applies when:
- **Called by `project_file_write`** - After writing new or modified files
- **Code generation complete** - Functions and files need to be tracked
- **User directive implementation** - Automation code generated
- **Manual sync needed** - User requests database synchronization
- **External changes detected** - Git integration calls to update DB
- **Refactoring complete** - Function signatures or dependencies changed

---

## Workflow

### Trunk: parse_content

Parses generated code to extract metadata for database updates.

**Steps**:
1. **Read file content** - Load file that was just written
2. **Parse AST** - Build abstract syntax tree for analysis
3. **Extract functions** - Find all function definitions
4. **Extract dependencies** - Identify function calls and imports
5. **Calculate checksum** - Compute file hash for change detection
6. **Determine update type** - New file vs existing file update

### Branches

**Branch 1: If user_directive_generated_file**
- **Then**: `update_user_directives_db`
- **Details**: Special handling for automation project files
  - Check if file path starts with `src/` in automation project
  - Update `directive_implementations` table in `user_directives.db`
  - Link file to source directive (e.g., lights.yaml → lights_controller.py)
  - Store file path and implementation status
  - Set `status = 'implemented'`
  - Continue to standard project.db update
- **Result**: User directives DB updated, proceeds to project.db

**Branch 2: If user_directive_implementation_updated**
- **Then**: `continue_with_project_db_update`
- **Details**: After user_directives.db updated, continue normal flow
  - Proceed to file, functions, interactions tables
  - Standard synchronization workflow
- **Result**: Both databases updated

**Branch 3: If new_file**
- **Then**: `update_files_table`
- **Details**: Insert new file record
  - INSERT INTO files (path, language, checksum, project_id)
  - Detect language from file extension
  - Store checksum for change detection
  - Return file_id for function linking
- **Result**: File record created in database

**Branch 4: If existing_file**
- **Then**: `update_files_table`
- **Details**: Update existing file record
  - UPDATE files SET checksum=?, updated_at=CURRENT_TIMESTAMP WHERE path=?
  - Update checksum for change detection
  - Delete old function records (will be re-inserted)
- **Result**: File record updated

**Branch 5: If new_function**
- **Then**: `update_functions_table`
- **Details**: Insert function records
  - For each extracted function:
    - INSERT INTO functions (name, file_id, purpose, parameters)
    - Extract function purpose from docstring
    - Store parameters as JSON array
    - Store purity_level and side_effects_json (from FP checks)
  - Return function_ids for dependency linking
- **Result**: Function records created

**Branch 6: If dependencies_found**
- **Then**: `update_interactions_table`
- **Details**: Record function dependencies
  - For each function call detected:
    - Find target function_id by name
    - INSERT INTO interactions (source_function_id, target_function_id, interaction_type)
    - interaction_type = 'call', 'chain', or 'compose'
  - Build call graph for dependency tracking
- **Result**: Dependencies recorded

**Branch 7: If task_related**
- **Then**: `update_items_subtasks`
- **Details**: Link code to completion path
  - Extract task_id from file metadata or context
  - Link file to task/subtask/item
  - Update task status if all items completed
  - Update milestone status if all tasks completed
- **Result**: Code linked to roadmap

**Fallback**: `prompt_user`
- **Details**: Unable to determine what to update
  - Ask: "Update DB for what component?"
  - Present options: file only, file+functions, full sync
  - Log to notes table with directive context
- **Result**: User guidance requested

---

## Examples

### ✅ Compliant Usage

**Standard File Write with DB Update:**
```python
# After project_file_write completes
file_content = """
def calculate_total(items: tuple[float, ...], tax_rate: float) -> float:
    '''Calculate total with tax.'''
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)

def format_currency(amount: float) -> str:
    '''Format amount as currency.'''
    return f"${amount:.2f}"
"""

# project_update_db called automatically
result = project_update_db(
    file_path="src/calc.py",
    content=file_content,
    project_root="/path/to/project"
)

# Database updates (transactional):
# 1. INSERT INTO files (path='src/calc.py', language='python', checksum='abc123', project_id=1)
#    → Returns file_id=5
#
# 2. INSERT INTO functions (name='calculate_total', file_id=5, purpose='Calculate total with tax',
#                            parameters='["items: tuple[float, ...]", "tax_rate: float"]')
#    → Returns func_id=42
#
# 3. INSERT INTO functions (name='format_currency', file_id=5, purpose='Format amount as currency',
#                            parameters='["amount: float"]')
#    → Returns func_id=43
#
# 4. No dependencies detected (no function calls between them)
#
# Result: {success: true, file_id: 5, functions: [42, 43], interactions: []}
```

---

**User Directive Implementation (Automation Project):**
```python
# In automation project, user_directives.db exists
file_content = """
# Generated from directives/lights.yaml
from phue import Bridge

def turn_off_lights(bridge_ip: str, group_name: str) -> Result[None, str]:
    '''Turn off lights in group.'''
    try:
        bridge = Bridge(bridge_ip)
        group = bridge.get_group(group_name)
        bridge.set_light(group['lights'], 'on', False)
        return Success(None)
    except Exception as e:
        return Failure(str(e))
"""

result = project_update_db(
    file_path="src/lights_controller.py",
    content=file_content,
    project_root="/home/automation",
    user_directive_context="lights.yaml"
)

# Updates user_directives.db first:
# UPDATE directive_implementations
# SET file_path='src/lights_controller.py', status='implemented'
# WHERE source_file='directives/lights.yaml'

# Then standard project.db update
# INSERT INTO files, functions, etc.

# Result: {success: true, user_directive_updated: true, file_id: 8, functions: [50]}
```

---

### ❌ Non-Compliant Usage

**Not Using Transactions:**
```python
# ❌ Updates without transaction
conn.execute("INSERT INTO files VALUES (?)", (path,))
conn.execute("INSERT INTO functions VALUES (?)", (name,))
# If second insert fails, database left inconsistent
```

**Why Non-Compliant**:
- Not atomic - partial updates if error occurs
- Database can be left in inconsistent state
- No rollback on failure

**Corrected (Transactional):**
```python
# ✅ Use transaction
conn.execute("BEGIN TRANSACTION")
try:
    file_id = conn.execute("INSERT INTO files VALUES (?)RETURNING id", (path,)).fetchone()[0]
    conn.execute("INSERT INTO functions VALUES (?, ?)", (name, file_id))
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise
```

---

**Forgetting to Calculate Checksum:**
```python
# ❌ No checksum
conn.execute("INSERT INTO files (path, language) VALUES (?, ?)", (path, lang))
# External changes won't be detected
```

**Why Non-Compliant**:
- Can't detect if file modified externally
- Git integration won't work correctly
- Change detection broken

**Corrected:**
```python
# ✅ Include checksum
import hashlib
checksum = hashlib.sha256(content.encode()).hexdigest()
conn.execute("INSERT INTO files (path, language, checksum) VALUES (?, ?, ?)",
             (path, lang, checksum))
```

---

## Edge Cases

### Edge Case 1: Duplicate File Path

**Issue**: File already exists in database

**Handling**:
- UPDATE existing record instead of INSERT
- Recalculate checksum
- Delete old function records (CASCADE delete)
- Re-insert updated functions
- Preserve file creation timestamp

```python
# Check if file exists
existing = conn.execute("SELECT id FROM files WHERE path=?", (path,)).fetchone()
if existing:
    file_id = existing[0]
    # Update
    conn.execute("UPDATE files SET checksum=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (checksum, file_id))
    # Functions auto-deleted by CASCADE
else:
    # Insert new
    file_id = conn.execute("INSERT INTO files (path, language, checksum, project_id)
                            VALUES (?, ?, ?, ?) RETURNING id",
                            (path, lang, checksum, 1)).fetchone()[0]
```

---

### Edge Case 2: Function Dependency Not Yet in Database

**Issue**: Function A calls function B, but B not yet indexed

**Handling**:
- Defer dependency recording
- Store unresolved dependencies temporarily
- Resolve when target function added
- Or: require functions inserted in dependency order

```python
# Try to find target function
target_func = conn.execute("SELECT id FROM functions WHERE name=?", (dep_name,)).fetchone()
if target_func:
    # Insert interaction
    conn.execute("INSERT INTO interactions (source_function_id, target_function_id, interaction_type)
                  VALUES (?, ?, 'call')", (source_id, target_func[0]))
else:
    # Log unresolved dependency
    conn.execute("INSERT INTO notes (content, note_type, reference_table, reference_id)
                  VALUES (?, 'unresolved_dependency', 'functions', ?)",
                  (f"Function {source_name} calls undefined {dep_name}", source_id))
```

---

### Edge Case 3: No Functions in File

**Issue**: File contains only data, constants, or comments

**Handling**:
- Still insert file record
- Don't attempt function extraction
- Mark file_type appropriately
- No function or interaction records

```python
# Extract functions
functions = extract_functions(ast)
if not functions:
    # Just file record, no functions
    conn.execute("INSERT INTO files (path, language, checksum, project_id) VALUES (?, ?, ?, ?)",
                 (path, lang, checksum, 1))
    return {"file_id": file_id, "functions": [], "note": "No functions in file"}
```

---

### Edge Case 4: Multi-File Update (Refactoring)

**Issue**: Refactoring moves functions between files

**Handling**:
- Update all affected files
- Move function records to new file_id
- Update interaction references
- Maintain referential integrity

```python
# Function moved from file_a to file_b
# 1. Update function's file_id
conn.execute("UPDATE functions SET file_id=? WHERE id=?", (new_file_id, func_id))

# 2. Update file checksums
conn.execute("UPDATE files SET checksum=?, updated_at=CURRENT_TIMESTAMP WHERE id IN (?, ?)",
             (checksum_a, checksum_b, file_a_id, file_b_id))

# 3. Interactions automatically follow (reference func_id, not file_id)
```

---

## Related Directives

- **Called By**:
  - `project_file_write` - Primary caller after file write
  - `git_detect_external_changes` - Syncs DB after external edits
- **Calls**:
  - `parse_file_ast()` - Extract functions from code
  - `calculate_checksum()` - Compute file hash
  - `query_project_db()` - Check existing records
- **Related**:
  - `project_reserve_finalize` - Finalize reservations after file write to update names with IDs and set is_reserved=FALSE
  - `project_blueprint_update` - Updates blueprint after major changes

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.

---

## Database Operations

This directive updates the following tables:

- **`files`**: INSERT or UPDATE file records with path, language, checksum
- **`functions`**: INSERT function records with name, purpose, parameters, purity
- **`interactions`**: INSERT dependency records (function call relationships)
- **`tasks/subtasks/items`**: UPDATE status when linked code completed
- **`notes`**: INSERT clarifications for unresolved dependencies or issues
- **`directive_implementations`** (user_directives.db): UPDATE for automation projects

---

## Testing

How to verify this directive is working:

1. **Write file and check DB** → Verify file record created
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

2. **Check functions extracted** → Verify function records
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

3. **Check dependencies** → Verify interactions table
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

4. **Update existing file** → Verify UPDATE, not duplicate INSERT
   ```python
   # Write file again with changes
   # Check database
   SELECT COUNT(*) FROM files WHERE path='src/calc.py';
   -- Expected: 1 (not 2)
   ```

---

## Common Mistakes

- ❌ **Not using transactions** - Partial updates leave inconsistent state
- ❌ **Forgetting checksums** - Change detection won't work
- ❌ **Duplicate file inserts** - Check existence before INSERT
- ❌ **Orphaned function records** - Use CASCADE DELETE or manual cleanup
- ❌ **Ignoring user directive context** - Automation projects need special handling

---

## Roadblocks and Resolutions

### Roadblock 1: missing_metadata
**Issue**: Can't extract function metadata from code
**Resolution**: Parse again with relaxed rules or prompt user for function metadata

### Roadblock 2: checksum_mismatch
**Issue**: File checksum doesn't match expected value
**Resolution**: Recalculate checksum and resync file entry

### Roadblock 3: user_directive_not_found
**Issue**: File appears to be user directive implementation but no directive found
**Resolution**: Parse file for directive reference or prompt user to link manually

---

## References

None

---

*Part of AIFP v1.0 - Critical Project directive for database synchronization*
