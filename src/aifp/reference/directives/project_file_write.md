# Directive: project_file_write

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_add_path
**Priority**: HIGH - Core file generation and database synchronization

---

## Purpose

The `project_file_write` directive handles writing new or modified files using AIFP-compliant patterns, validates code through FP directives, and updates `project.db` accordingly. This directive serves as the **bridge between code generation and database synchronization**, ensuring that every file written is tracked and compliant.

Key responsibilities:
- **Apply user preferences** from `directive_preferences` table (docstrings, max function length, guard clauses, code style)
- **Validate FP compliance** by calling `fp_purity`, `fp_immutability`, `fp_side_effect_detection`
- **Track user directive implementations** when path starts with `.aifp-project/user-directives/generated/`
- **Update project.db** with file metadata, functions, interactions, and dependencies
- **Link to tasks** via AIFP_METADATA for completion tracking

This is the **central file generation directive** - all code writing flows through here to maintain consistency and traceability.

---

## When to Apply

This directive applies when:
- **Writing new files** - Creating new source files in the project
- **Modifying existing files** - Updating or refactoring existing code
- **Generating from user directives** - Creating automation code from YAML/JSON/TXT directives
- **Called by other directives**:
  - `project_task_decomposition` - When task requires new file creation
  - `user_directive_implement` - Generates FP-compliant automation code
  - `project_refactor_path` - When refactoring creates new file versions

**User Preferences Integration**:
- Before writing, calls `user_preferences_sync` to load customizations
- Applies preferences like `always_add_docstrings`, `prefer_guard_clauses`, `max_function_length`
- Respects `code_style`, `indent_style` settings

---

## Workflow

### Trunk: check_user_preferences

Loads and applies user-defined preferences for file writing.

**Steps**:
1. **Query directive_preferences** - Load settings for `project_file_write`
2. **Apply to code generation context** - Configure code generator with preferences
3. **Fallback to defaults** - Use system defaults if preferences missing

### Branches

**Branch 1: If directive_preferences_exist**
- **Then**: `load_and_apply_preferences`
- **Details**: Query user preferences and apply to code generation
  - `always_add_docstrings` - Add function docstrings automatically
  - `max_function_length` - Warn if function exceeds line limit
  - `prefer_guard_clauses` - Use guard clauses instead of nested ifs
  - `code_style` - Apply specific coding style (e.g., "compact", "verbose")
  - `indent_style` - Use tabs or spaces
- **Query**: `SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_file_write' AND active=1`
- **Result**: Preferences loaded and ready to apply

**Branch 2: If preferences_applied**
- **Then**: `generate_file_with_preferences`
- **Details**: Generate code respecting user settings
  - Apply all loaded preferences to code generation
  - Fallback to defaults if specific preference missing
- **Result**: Code generated according to user customization

**Branch 3: If file_path_starts_with_.aifp-project/user-directives/generated/**
- **Then**: `mark_as_user_directive_implementation`
- **Details**: Identify as user directive generated code
  - Set metadata tag: `user_directive_generated`
  - Still apply FP compliance checks
  - Track in both `project.db` AND `user_directives.db`
- **Result**: File marked for dual database tracking

**Branch 4: If user_directive_file_and_compliant**
- **Then**: `write_file_and_link_to_directive`
- **Details**: Write file and update both databases
  - Write to filesystem
  - Update `project.db` (files, functions, interactions)
  - Update `user_directives.db` (directive_implementations table)
  - Link to parent user directive
- **Result**: File written and tracked in both databases

**Branch 5: If code_compliant**
- **Then**: `write_file`
- **Details**: Standard file write with tracking
  - Include AIFP_METADATA in file header
  - Write to filesystem
  - Update `project.db` tables:
    - `files` - file path, language, checksum, project_id
    - `functions` - function names, purposes, purity levels
    - `interactions` - function dependencies
    - `file_flows` - theme/flow associations
  - Mark associated task/item as completed if linked
- **Result**: File written and fully tracked

**Branch 6: If non_compliant**
- **Then**: `fp_compliance_check`
- **Details**: Escalate to FP directives for correction
  - Call `fp_purity` - Check for side effects
  - Call `fp_immutability` - Check for mutations
  - Call `fp_side_effect_detection` - Identify and isolate effects
  - If correctable: Apply automatic refactoring
  - If uncertain: Prompt user for guidance
- **Result**: Code refactored to meet FP compliance or user clarifies

**Branch 7: If low_confidence**
- **Then**: `prompt_user`
- **Details**: Uncertain about file write operation
  - Present analysis findings
  - Ask: "Should I write this file? Is it compliant?"
  - Log uncertainty to `notes` table
- **Result**: User confirms or provides corrections

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Log to `notes` for future reference

### Error Handling

**on_failure**: `prompt_user`
- If file write fails, present error and ask user to resolve
- Common issues: File permissions, path invalid, compliance violations

---

## Examples

### Example 1: Writing a Pure Function with User Preferences

**User Preference**:
```sql
INSERT INTO directive_preferences (directive_name, preference_key, preference_value)
VALUES ('project_file_write', 'always_add_docstrings', 'true');
```

**User Request**: "Write multiply_matrices function"

**AI Execution**:
1. Calls `user_preferences_sync`
2. Loads preference: `always_add_docstrings = true`
3. Generates code with docstring:

```python
# AIFP_METADATA: {"function_names": ["multiply_matrices"], "deps": ["validate_dimensions"], "theme": "matrix_operations", "flow": "calculation_flow", "version": 1, "task_id": 15}

def multiply_matrices(a: List[List[float]], b: List[List[float]]) -> Result[List[List[float]], str]:
    """
    Multiplies two matrices A and B.

    Args:
        a: First matrix (m x n)
        b: Second matrix (n x p)

    Returns:
        Result containing product matrix (m x p) or error message
    """
    # Validate dimensions
    validation = validate_dimensions(a, b)
    if validation.is_err():
        return Err(validation.unwrap_err())

    # Pure multiplication logic
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])

    result = [[sum(a[i][k] * b[k][j] for k in range(cols_a))
               for j in range(cols_b)]
              for i in range(rows_a)]

    return Ok(result)
```

4. Validates with FP directives:
   - `fp_purity`: ✓ Pure (no side effects, deterministic)
   - `fp_immutability`: ✓ No mutations
5. Writes file to `src/matrix.py`
6. Updates `project.db`:
   - `files` table: New entry for `src/matrix.py`
   - `functions` table: `multiply_matrices` with purity_level='pure'
   - `interactions` table: Depends on `validate_dimensions`

### Example 2: User Directive Implementation

**User Directive File**: `directives/lights.yaml`
```yaml
name: turn_off_lights_5pm
trigger:
  type: time
  time: "17:00"
action:
  type: api_call
  api: homeassistant
```

**AI Generates**: `.aifp-project/user-directives/generated/lights_controller.py`

**Workflow**:
1. Path detected: `.aifp-project/user-directives/generated/` → Mark as user directive
2. Generate FP-compliant code
3. Validate with FP directives
4. Write to filesystem
5. Update `project.db` (files, functions)
6. Update `user_directives.db` (directive_implementations table)
7. Link to parent directive: `turn_off_lights_5pm`

### Example 3: Compliance Failure and Correction

**Initial Code** (non-compliant):
```python
global config

def process_order(order):
    discount = config['discount']  # External state access
    order['total'] = order['total'] * (1 - discount)  # Mutation
    save_to_db(order)  # Side effect
    return order
```

**AI Detection**:
1. `fp_purity` detects: Global state access, side effect
2. `fp_immutability` detects: Mutation of `order` dict
3. Non-compliant → Trigger refactoring

**Refactored Code** (compliant):
```python
def process_order(order: Dict[str, Any], discount: float) -> Dict[str, Any]:
    """Pure function: Calculate discounted order total."""
    return {
        **order,
        'total': order['total'] * (1 - discount)
    }

def save_order_effect(order: Dict[str, Any]) -> Result[None, str]:
    """Effect function: Save order to database (isolated side effect)."""
    try:
        save_to_db(order)
        return Ok(None)
    except Exception as e:
        return Err(str(e))
```

4. Validates again: ✓ Compliant
5. Writes refactored file
6. Updates database with corrected functions

---

## Integration with Other Directives

### Called By:
- `project_task_decomposition` - Creates files for new tasks
- `user_directive_implement` - Generates automation code
- `project_refactor_path` - Updates files during refactoring

### Calls:
- `user_preferences_sync` - Loads user customizations
- `fp_purity` - Validates function purity
- `fp_immutability` - Checks for mutations
- `fp_side_effect_detection` - Identifies side effects
- `project_update_db` - Syncs file metadata to database
- `project_metadata_sync` - Ensures DB-file consistency

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Insert new file
INSERT INTO files (path, language, checksum, project_id, created_at, updated_at)
VALUES ('src/matrix.py', 'python', 'abc123...', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert functions
INSERT INTO functions (name, file_id, purpose, purity_level, side_effects_json, parameters_json, return_type)
VALUES ('multiply_matrices', 1, 'Multiply two matrices', 'pure', 'null', '[{"name": "a", "type": "List[List[float]]"}, ...]', 'Result[List[List[float]], str]');

-- Insert interactions (dependencies)
INSERT INTO interactions (source_function_id, target_function_id, interaction_type)
VALUES (1, 2, 'call');

-- Link to flow
INSERT INTO file_flows (file_id, flow_id)
VALUES (1, 3);
```

**user_directives.db** (if user directive generated):
```sql
-- Link implementation to directive
INSERT INTO directive_implementations (user_directive_id, file_path, entry_point, deployed, created_at)
VALUES (1, '.aifp-project/user-directives/generated/lights_controller.py', 'handle_lights_5pm', 0, CURRENT_TIMESTAMP);
```

---

## Roadblocks and Resolutions

### Roadblock 1: missing_metadata
**Issue**: Generated code lacks AIFP_METADATA header
**Resolution**: Add AIFP_METADATA automatically, infer from context, prompt user if uncertain

### Roadblock 2: fp_violation
**Issue**: Code violates FP principles (mutations, side effects, etc.)
**Resolution**: Trigger `fp_compliance_check`, apply automatic refactoring, or prompt user

### Roadblock 3: user_directive_link_missing
**Issue**: User directive implementation file but no link to parent directive
**Resolution**: Parse file for directive reference in AIFP_METADATA, or prompt user to link manually

### Roadblock 4: database_update_failed
**Issue**: File written but database update fails
**Resolution**: Rollback file write, log error, prompt user to resolve DB issue

---

## Intent Keywords

- "create file"
- "write code"
- "generate file"
- "write function"
- "implement"
- "add file"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_reserve_finalize` - Reserve names BEFORE writing to get database IDs for embedding
- `project_update_db` - Synchronizes file metadata to database
- `project_task_decomposition` - Creates files for tasks
- `fp_purity` - Validates function purity
- `fp_immutability` - Checks immutability
- `fp_side_effect_detection` - Identifies side effects
- `user_directive_implement` - Generates user automation code
- `user_preferences_sync` - Loads user customizations

---

## Notes

- **Always apply user preferences** before generating code
- **Dual database tracking** for user directive implementations
- **AIFP_METADATA required** in all generated files
- **FP compliance mandatory** - no exceptions
- **Transactional updates** - rollback on failure
- **Link to tasks** via `task_id` in metadata for completion tracking
