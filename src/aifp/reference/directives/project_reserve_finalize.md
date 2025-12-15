# project_reserve_finalize

## Purpose

The `project_reserve_finalize` directive manages the reservation and finalization workflow for files, functions, and types in the project database. This workflow enables AI to reserve names BEFORE writing code, receive database IDs, embed those IDs in code for instant lookups, and finalize the reservations after implementation.

**Category**: Project
**Type**: Project
**Priority**: High
**Confidence Threshold**: 0.8

---

## Workflow

### Trunk
**`reserve_entities`**: Reserve names in database before writing code.

### Branches

1. **`reserving_file`** → **`reserve_file_name`**
   - **Condition**: Planning to create new file
   - **Action**: Reserve file name in database
   - **Details**: Call reserve_file(name, path, language)
   - **Output**: Returns file_id for embedding in filename

2. **`reserving_function`** → **`reserve_function_name`**
   - **Condition**: Planning to create new function
   - **Action**: Reserve function name in database
   - **Details**: Call reserve_function(name, file_id, purpose)
   - **Output**: Returns function_id for embedding in function name

3. **`reserving_type`** → **`reserve_type_name`**
   - **Condition**: Planning to create new type/ADT
   - **Action**: Reserve type name in database
   - **Details**: Call reserve_type(name, file_id, purpose)
   - **Output**: Returns type_id for embedding in type name

4. **`reserved_successfully`** → **`write_with_embedded_id`**
   - **Condition**: Reservation returned ID
   - **Action**: Write code with ID embedded in name
   - **Details**: Use naming conventions:
     - Files: `filename_id_42.py`
     - Functions: `function_name_id_99()`
     - Types: `TypeName_id_7`
   - Add ID comment: `# AIFP:FUNC:42` or `AIFP-ID: 42` in docstring
   - **Output**: Code written with embedded database ID

5. **`code_written`** → **`finalize_reservation`**
   - **Condition**: Code successfully written to filesystem
   - **Action**: Finalize reservation in database
   - **Details**: Call finalize_file(file_id), finalize_function(function_id), or finalize_type(type_id)
   - Updates name field to include embedded ID (e.g., `calculate_sum` → `calculate_sum_id_99`)
   - Sets is_reserved=FALSE
   - **Output**: Entity marked as implemented in database with ID in name

6. **Fallback** → **`prompt_user`**
   - **Condition**: Reservation failed or unclear
   - **Action**: Request clarification on entity details

### Error Handling
- **On reservation failure**: Check for naming collisions, suggest alternative names
- **On finalization failure**: Verify entity exists, check is_reserved flag

---

## Refactoring Strategies

### Strategy 1: Reserve File Before Creation

**Before (No Reservation)**:
```python
# AI writes file without ID
# File: calculator.py

def add(a, b):
    return a + b

# Later needs to query: "Get file by name 'calculator.py'" (string matching)
```

**After (With Reservation)**:
```python
# Step 1: Reserve
file_id = reserve_file(name='calculator', path='src/calculator_id_42.py', language='python')
# Returns: 42

# Step 2: Write with embedded ID
# File: calculator_id_42.py
# AIFP:FILE:42

def add_id_101(a, b):  # AIFP:FUNC:101
    return a + b

# Step 3: Finalize
finalize_file(42)

# Later: get_file(42) - instant integer lookup, no string matching
```

### Strategy 2: Reserve Function Before Implementation

**Before (No Reservation)**:
```python
# Function written directly
def process_payment(amount, user):
    # Implementation
    pass

# Database query needed: get_function_by_name('process_payment')
# Vulnerable to renames, requires string matching
```

**After (With Reservation)**:
```python
# Step 1: Reserve
function_id = reserve_function(
    name='process_payment',
    file_id=42,
    purpose='Process payment transaction'
)
# Returns: 203

# Step 2: Write with embedded ID
def process_payment_id_203(amount, user):
    """Process payment transaction.

    AIFP-ID: 203
    """
    # Implementation
    pass

# Step 3: Finalize
finalize_function(203)

# Later: get_function(203) - instant lookup
# Rename-proof: function can be renamed, ID relationships remain intact
```

### Strategy 3: Reserve Type Before Definition

**Before (No Reservation)**:
```python
# Type defined directly
class Result:
    """Result ADT for success/error handling."""
    pass

# Database: get_type_by_name('Result') - ambiguous, requires context
```

**After (With Reservation)**:
```python
# Step 1: Reserve
type_id = reserve_type(
    name='Result',
    file_id=42,
    purpose='Result ADT for success/error handling'
)
# Returns: 15

# Step 2: Write with embedded ID
class Result_id_15:  # AIFP:TYPE:15
    """Result ADT for success/error handling.

    AIFP-ID: 15
    """
    pass

# Step 3: Finalize
finalize_type(15)

# Later: get_type(15) - instant, unambiguous
```

---

## Examples

### Example 1: Complete File Creation Workflow

```python
# Planning phase
file_id = reserve_file(
    name='user_service',
    path='src/services/user_service_id_55.py',
    language='python'
)
# Returns: 55

# Reserve functions for this file
func1_id = reserve_function(name='get_user_id_88', file_id=55, purpose='Fetch user by ID')
func2_id = reserve_function(name='update_user_id_89', file_id=55, purpose='Update user data')
# Returns: 88, 89

# Write file with embedded IDs
write_file(
    path='src/services/user_service_id_55.py',
    content="""
# AIFP:FILE:55

def get_user_id_88(user_id):  # AIFP:FUNC:88
    \"\"\"Fetch user by ID.\"\"\"
    return query_database('users', user_id)

def update_user_id_89(user_id, data):  # AIFP:FUNC:89
    \"\"\"Update user data.\"\"\"
    return update_database('users', user_id, data)
"""
)

# Finalize all reservations
finalize_file(55)
finalize_function(88)
finalize_function(89)

# Now all lookups are instant:
# get_file(55), get_function(88), get_function(89)
```

### Example 2: Type with Associated Functions

```python
# Reserve type
type_id = reserve_type(name='Option', file_id=10, purpose='Optional value ADT')
# Returns: 20

# Reserve factory functions
some_id = reserve_function(name='Some_id_41', file_id=10, purpose='Create Some variant')
none_id = reserve_function(name='None_id_42', file_id=10, purpose='Create None variant')
# Returns: 41, 42

# Write code
write_file(
    path='src/types/option_id_10.py',
    content="""
# AIFP:FILE:10

class Option_id_20:  # AIFP:TYPE:20
    \"\"\"Optional value ADT.\"\"\"
    pass

def Some_id_41(value):  # AIFP:FUNC:41
    \"\"\"Create Some variant.\"\"\"
    return Option_id_20(value=value, is_some=True)

def None_id_42():  # AIFP:FUNC:42
    \"\"\"Create None variant.\"\"\"
    return Option_id_20(value=None, is_some=False)
"""
)

# Finalize
finalize_type(20)
finalize_function(41)
finalize_function(42)

# Create type-function relationships
add_type_function(type_id=20, function_id=41, role='factory')
add_type_function(type_id=20, function_id=42, role='factory')
```

---

## Edge Cases

### Edge Case 1: Reservation Failure (Name Collision)
**Scenario**: Name already reserved or exists
**Issue**: Cannot reserve duplicate name
**Handling**:
- Check database for existing names
- Suggest numbered suffix: `process_user_v2`, `process_user_alt`
- Prompt user for alternative name

### Edge Case 2: Implementation Fails After Reservation
**Scenario**: Code fails to write after reservation
**Issue**: Database has reserved entry, no actual code
**Handling**:
- Cleanup: Delete reservation or mark as abandoned
- Log reason for failure
- Retry with corrected code

### Edge Case 3: Finalization Without Reservation
**Scenario**: Attempt to finalize non-reserved entity
**Issue**: is_reserved flag already FALSE or entity doesn't exist
**Handling**:
- Verify entity exists in database
- Check is_reserved status
- If already finalized, skip (idempotent)

### Edge Case 4: ID Embedding Format Inconsistent
**Scenario**: Multiple ID embedding styles in same project
**Issue**: Some use `# AIFP:FUNC:42`, others use docstring format
**Handling**:
- Standardize on one format per project
- Document choice in ProjectBlueprint.md
- Maintain consistency across all files

### Edge Case 5: Database Rebuild
**Scenario**: Project database rebuilt from scratch
**Issue**: Code has embedded IDs that may not match new database
**Handling**:
- Use verify_ids directive to detect mismatches
- Use repair_ids directive to fix discrepancies
- Maintain mapping of old_id → new_id during migration

---

## Database Operations

### Reserve File
```sql
INSERT INTO files (name, path, language, is_reserved, created_at)
VALUES ('calculator', 'src/calculator_id_42.py', 'python', 1, CURRENT_TIMESTAMP);
-- Returns: file_id
```

### Reserve Function
```sql
INSERT INTO functions (name, file_id, purpose, is_reserved, created_at)
VALUES ('add_numbers', 42, 'Sum two numbers', 1, CURRENT_TIMESTAMP);
-- Returns: function_id
```

### Reserve Type
```sql
INSERT INTO types (name, file_id, purpose, is_reserved, created_at)
VALUES ('Result', 42, 'Result ADT for error handling', 1, CURRENT_TIMESTAMP);
-- Returns: type_id
```

### Finalize Reservation
Updates name to include embedded ID and sets is_reserved to FALSE:

```sql
-- Finalize file: Update name and path with ID, set is_reserved=0
UPDATE files
SET name = 'calculator_id_42.py',
    path = 'src/calculator_id_42.py',
    is_reserved = 0,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 42;

-- Finalize function: Update name with ID, set is_reserved=0
UPDATE functions
SET name = 'add_numbers_id_99',
    is_reserved = 0,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 99;

-- Finalize type: Update name with ID, set is_reserved=0
UPDATE types
SET name = 'Result_id_15',
    is_reserved = 0,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 15;
```

---

## Related Directives

### Project Directives
- **project_file_write**: Uses reservations when creating new files
- **project_update_db**: Updates metadata after finalization
- **project_integrity_check**: Verifies reservation consistency

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.

---

## Intent Keywords

- `reserve`
- `finalize`
- `embed ID`
- `database ID`
- `collision prevention`

---

## Confidence Threshold

**0.8** - High confidence for reservation workflow execution.

---

## Notes

- Reservation workflow prevents naming collisions during multi-step implementations
- Embedded IDs enable instant database lookups (bypass string matching)
- IDs are rename-proof: function name can change, relationships stay intact
- Finalization updates name with embedded ID and sets is_reserved=FALSE, marking entity as fully implemented
- ID formats: `# AIFP:FILE:42`, `# AIFP:FUNC:99`, `# AIFP:TYPE:15`
- Alternative: Embed in docstring `AIFP-ID: 42`
- Reservation enables batch operations: reserve multiple entities, write all, finalize all
- Database IDs save API costs: single integer lookup vs multiple string queries
- Benefits compound in large codebases with hundreds of functions/types
