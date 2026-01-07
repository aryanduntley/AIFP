# Directive: project_file_read

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_file_write
**Priority**: MEDIUM - File access and context retrieval

---

## Purpose

The `project_file_read` directive handles reading files from the project with database-aware context. This directive serves as the **intelligent file reader**, providing not just file content but also metadata, dependencies, and context from `project.db`.

Key responsibilities:
- **Read file content** - Load source files from filesystem
- **Retrieve file metadata** - Get file info from `project.db` (language, checksum, version)
- **Load function context** - Retrieve functions defined in the file
- **Show dependencies** - Display function interactions and dependencies
- **Verify checksums** - Detect if file changed since last DB update
- **Provide context** - Include theme, flow, and task associations
- **Support multiple formats** - Handle source code, markdown, config files

This is the **context-aware file reader** - unlike basic file reading, this provides full project context.

---

## When to Apply

This directive applies when:
- **Code review** - Examining existing files with context
- **Debugging** - Understanding function dependencies and interactions
- **Refactoring** - Analyzing current state before modifications
- **Documentation** - Reviewing file structure and purpose
- **Called by other directives**:
  - `project_dependency_sync` - Reads files to compare with database
  - `fp_purity` - Analyzes file content for purity violations
  - `aifp_status` - Reads files to provide project context

---

## Workflow

### Trunk: validate_file_path

Ensures file exists and is accessible.

**Steps**:
1. **Validate path** - Check file path is valid and within project
2. **Check file exists** - Verify file is present on filesystem
3. **Query database** - Retrieve file metadata from `project.db`
4. **Read content** - Load file content from disk

### Branches

**Branch 1: If file_exists_in_db**
- **Then**: `load_with_context`
- **Details**: File is tracked in database, provide full context
  - Load file content from filesystem
  - Retrieve metadata from `files` table
  - Load functions from `functions` table
  - Load interactions from `interactions` table
  - Load theme/flow associations from `file_flows` table
  - Include task/item links if present
- **Query**:
  ```sql
  -- Get file metadata
  SELECT id, path, language, checksum, created_at, updated_at
  FROM files WHERE path = ? AND project_id = ?;

  -- Get functions in file
  SELECT name, purpose, purity_level, side_effects_json, parameters_json, return_type
  FROM functions WHERE file_id = ?;

  -- Get function dependencies
  SELECT i.interaction_type, tf.name as target_function
  FROM interactions i
  JOIN functions tf ON i.target_function_id = tf.id
  WHERE i.source_function_id IN (SELECT id FROM functions WHERE file_id = ?);

  -- Get theme/flow associations
  SELECT t.name as theme, f.name as flow
  FROM file_flows ff
  JOIN flows f ON ff.flow_id = f.id
  JOIN flow_themes ft ON f.id = ft.flow_id
  JOIN themes t ON ft.theme_id = t.id
  WHERE ff.file_id = ?;
  ```
- **Result**: File content + full database context

**Branch 2: If file_not_in_db_but_exists**
- **Then**: `load_without_context`
- **Details**: File exists but not tracked
  - Load file content from filesystem
  - Warn: "File not tracked in project.db"
  - Suggest: "Run project_file_write to track this file"
  - Provide basic file info (size, modified date)
- **Result**: File content + warning about missing tracking

**Branch 3: If file_not_exists**
- **Then**: `check_if_deleted`
- **Details**: File missing from filesystem
  - Check if file exists in database
  - If in DB: Warn about deleted file
  - Suggest running `project_dependency_sync` to update DB
  - Return error with last known metadata
- **Result**: Error with context about missing file

**Branch 4: If checksum_mismatch**
- **Then**: `warn_file_modified`
- **Details**: File changed since last DB update
  - Calculate current checksum
  - Compare with database checksum
  - Warn: "File modified outside AIFP. Checksum mismatch."
  - Suggest: "Run project_update_db to sync metadata"
  - Show last known state vs. current state
- **Result**: File content + warning about desync

**Branch 5: If read_with_line_numbers**
- **Then**: `format_with_line_numbers`
- **Details**: Format output like `cat -n`
  - Add line numbers to each line
  - Highlight function definitions
  - Show AIFP_METADATA at top
- **Result**: Formatted file content with line numbers

**Branch 6: If read_specific_function**
- **Then**: `extract_function_only`
- **Details**: Read only a specific function from file
  - Query database for function line range
  - Extract function from file
  - Include function metadata (purity, dependencies, purpose)
  - Show callers and callees
- **Query**:
  ```sql
  SELECT name, purpose, purity_level, side_effects_json, parameters_json, return_type
  FROM functions WHERE name = ? AND file_id = ?;
  ```
- **Result**: Function code + metadata

**Branch 7: If read_for_compliance_check**
- **Then**: `read_with_fp_context`
- **Details**: Read file with FP compliance focus
  - Load file content
  - Highlight potential violations:
    - Global variable access
    - Mutations
    - Side effects
    - OOP patterns
  - Include purity levels from database
  - Flag functions needing review
- **Result**: File content + FP compliance annotations

**Branch 8: If read_markdown_or_config**
- **Then**: `read_as_text`
- **Details**: Non-code files (README, config, etc.)
  - Load as plain text
  - No syntax analysis
  - Include file metadata if tracked
- **Result**: Text content

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: File not found, permission denied, path ambiguous

### Error Handling

**on_failure**: `prompt_user`
- If read fails, report error and suggest solutions
- Common issues: File locked, permission denied, binary file

---

## Examples

### Example 1: Read File with Full Context

**User**: "Read src/matrix.py"

**AI Execution**:
1. Validates path: `src/matrix.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database:
   - File ID: 15
   - Language: Python
   - Checksum: sha256:abc123...
   - Created: 2025-10-25
4. Retrieves functions:
   - `multiply_matrices` (pure, no side effects)
   - `validate_dimensions` (pure, no side effects)
   - `transpose` (pure, no side effects)
5. Retrieves dependencies:
   - `multiply_matrices` calls `validate_dimensions`
   - `transpose` called by `multiply_matrices` (in other file)
6. Retrieves theme/flow:
   - Theme: "Matrix Operations"
   - Flow: "Core Calculation Flow"
7. Reads file content
8. Calculates checksum: Matches database ✓
9. Returns:
   ```
   File: src/matrix.py
   Language: Python
   Created: 2025-10-25
   Checksum: ✓ Verified

   Theme: Matrix Operations
   Flow: Core Calculation Flow

   Functions (3):
   - multiply_matrices (pure)
   - validate_dimensions (pure)
   - transpose (pure)

   Dependencies:
   - multiply_matrices → validate_dimensions
   - transpose → multiply_matrices (called from elsewhere)

   Content:
   ───────────────────────────────────────────
   # AIFP_METADATA: {"function_names": ["multiply_matrices", "validate_dimensions", "transpose"], ...}

   def multiply_matrices(a: List[List[float]], b: List[List[float]]) -> Result[List[List[float]], str]:
       """Multiplies two matrices A and B."""
       ...
   ```

### Example 2: File Not Tracked in Database

**User**: "Read config/settings.json"

**AI Execution**:
1. Validates path: `config/settings.json` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: ✗ Not found
4. Reads file content
5. Returns:
   ```
   ⚠️  File: config/settings.json
   Status: Not tracked in project.db
   Suggestion: Run project_file_write to track this file

   Content:
   ───────────────────────────────────────────
   {
     "api_endpoint": "https://api.example.com",
     "timeout": 5000
   }
   ```

### Example 3: Checksum Mismatch (File Modified Externally)

**User**: "Read src/auth.py"

**AI Execution**:
1. Validates path: `src/auth.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: Found (ID: 8)
4. Reads file content
5. Calculates checksum: sha256:xyz789...
6. Compares with DB: sha256:abc123... ✗ Mismatch!
7. Returns:
   ```
   ⚠️  File: src/auth.py
   Status: Modified outside AIFP session
   Database checksum: sha256:abc123...
   Current checksum:  sha256:xyz789...
   Last updated in DB: 2025-10-26 14:30:00

   Suggestion: Run project_update_db to sync metadata

   Content:
   ───────────────────────────────────────────
   [File content shown]
   ```

### Example 4: Read Specific Function

**User**: "Read function multiply_matrices from src/matrix.py"

**AI Execution**:
1. Queries database for function:
   ```sql
   SELECT name, purpose, purity_level, parameters_json, return_type
   FROM functions f
   JOIN files fi ON f.file_id = fi.id
   WHERE f.name = 'multiply_matrices' AND fi.path = 'src/matrix.py';
   ```
2. Retrieves function metadata:
   - Purpose: "Multiplies two matrices"
   - Purity: pure
   - Parameters: a, b (List[List[float]])
   - Returns: Result[List[List[float]], str]
3. Queries dependencies:
   - Calls: `validate_dimensions`
   - Called by: `process_matrix_batch` (from src/batch.py)
4. Extracts function from file
5. Returns:
   ```
   Function: multiply_matrices
   File: src/matrix.py:15
   Purpose: Multiplies two matrices
   Purity: ✓ Pure (no side effects)

   Parameters:
   - a: List[List[float]]
   - b: List[List[float]]

   Returns: Result[List[List[float]], str]

   Dependencies:
   - Calls: validate_dimensions
   - Called by: process_matrix_batch (src/batch.py)

   Code:
   ───────────────────────────────────────────
   def multiply_matrices(a: List[List[float]], b: List[List[float]]) -> Result[List[List[float]], str]:
       """Multiplies two matrices A and B."""
       validation = validate_dimensions(a, b)
       if validation.is_err():
           return Err(validation.unwrap_err())

       rows_a, cols_a = len(a), len(a[0])
       rows_b, cols_b = len(b), len(b[0])

       result = [[sum(a[i][k] * b[k][j] for k in range(cols_a))
                  for j in range(cols_b)]
                 for i in range(rows_a)]

       return Ok(result)
   ```

### Example 5: Read for Compliance Check

**User**: "Check FP compliance in src/auth.py"

**AI Execution**:
1. Reads file with FP context enabled
2. Analyzes functions:
   - `hash_password` - pure ✓
   - `validate_token` - has side effect (logs) ⚠️
   - `save_user` - has side effect (database write) ⚠️
3. Returns:
   ```
   File: src/auth.py
   FP Compliance Analysis:

   Functions (3):
   ✓ hash_password (pure)
   ⚠️  validate_token (side effect: logging detected)
   ⚠️  save_user (side effect: database write)

   Suggested Actions:
   - validate_token: Isolate logging to separate effect function
   - save_user: Already effect function, ensure clearly marked

   Content:
   ───────────────────────────────────────────
   [File content with violations highlighted]
   ```

### Example 6: File Deleted but in Database

**User**: "Read src/old_code.py"

**AI Execution**:
1. Validates path: `src/old_code.py` ✓ Valid
2. Checks file exists: ✗ Not found
3. Queries database: Found (ID: 23)
4. Returns:
   ```
   ❌ File: src/old_code.py
   Status: File deleted but still in database
   Last tracked: 2025-10-20 09:15:00

   Metadata:
   - Language: Python
   - Functions: 2 (process_data, validate_input)
   - Theme: Data Processing

   Suggestion: Run project_dependency_sync to clean up database

   Error: File not found on filesystem
   ```

---

## Integration with Other Directives

### Called By:
- `project_dependency_sync` - Compares files with database
- `fp_purity` - Analyzes function purity
- `aifp_status` - Provides file context
- User directly - Manual file inspection

### Calls:
- `project_update_db` - Suggests sync on checksum mismatch
- `project_dependency_sync` - Suggests cleanup on deleted files

---

## Database Queries

### Tables Read:

**project.db**:
```sql
-- Get file metadata
SELECT id, path, language, checksum, created_at, updated_at
FROM files WHERE path = ? AND project_id = ?;

-- Get functions in file
SELECT name, purpose, purity_level, side_effects_json, parameters_json, return_type
FROM functions WHERE file_id = ?;

-- Get function dependencies
SELECT i.interaction_type, sf.name as source, tf.name as target
FROM interactions i
JOIN functions sf ON i.source_function_id = sf.id
JOIN functions tf ON i.target_function_id = tf.id
WHERE sf.file_id = ? OR tf.file_id = ?;

-- Get theme/flow associations
SELECT t.name as theme, f.name as flow
FROM file_flows ff
JOIN flows f ON ff.flow_id = f.id
JOIN flow_themes ft ON f.id = ft.flow_id
JOIN themes t ON ft.theme_id = t.id
WHERE ff.file_id = ?;

-- Get task associations
SELECT t.name as task, i.name as item
FROM items i
JOIN tasks t ON i.task_id = t.id
WHERE i.reference_table = 'files' AND i.reference_id = ?;
```

---

## Roadblocks and Resolutions

### Roadblock 1: file_not_found
**Issue**: File path doesn't exist on filesystem
**Resolution**: Check database for last known state, suggest file may have been deleted

### Roadblock 2: checksum_mismatch
**Issue**: File modified outside AIFP session
**Resolution**: Show file content, warn about desync, suggest `project_update_db`

### Roadblock 3: permission_denied
**Issue**: Cannot read file due to permissions
**Resolution**: Report error, suggest checking file permissions

### Roadblock 4: binary_file
**Issue**: Attempting to read binary file as text
**Resolution**: Detect binary content, suggest appropriate tool

### Roadblock 5: file_too_large
**Issue**: File exceeds reasonable size for display
**Resolution**: Offer to read specific range or function only

---

## Intent Keywords

- "read file"
- "show file"
- "view file"
- "cat"
- "display file"
- "read function"
- "show code"

**Confidence Threshold**: 0.8

---

## Related Directives

- `project_file_write` - Writes files and tracks in database
- `project_update_db` - Syncs file metadata
- `project_dependency_sync` - Compares files with database
- `fp_purity` - Analyzes function purity

---

## Output Format Options

**Standard**:
- File path, metadata, theme/flow, functions, dependencies, content

**With Line Numbers**:
- Format like `cat -n` with line numbers

**Function Only**:
- Extract and display specific function with metadata

**FP Compliance**:
- Annotate content with purity levels and violations

**Metadata Only**:
- Show file info without full content

---

## Notes

- **Always verify checksums** - Detect external modifications
- **Provide full context** - Include database metadata, not just file content
- **Suggest sync on mismatch** - Help maintain database accuracy
- **Support multiple formats** - Code, markdown, config files
- **Handle missing files gracefully** - Provide last known state from DB
- **Enable compliance checking** - Integrate with FP directives
