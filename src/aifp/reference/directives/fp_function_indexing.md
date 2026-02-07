# Directive: fp_function_indexing

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Enables database-driven project tracking

---

## Purpose

The `fp_function_indexing` directive automatically indexes all functions in project.db, tracking their metadata, dependencies, purity levels, and relationships. This directive provides **automatic function tracking** that enables database-driven project management and AI reasoning.

Function indexing provides **persistent function catalog**, enabling:
- **Instant Function Lookup**: Query functions without parsing code
- **Dependency Tracking**: Know what calls what
- **Purity Analysis**: Track pure vs impure functions
- **Theme/Flow Mapping**: Organize functions by project structure
- **AI Context**: Database provides function context to AI

This directive acts as a **function cataloging system** maintaining comprehensive function index.

---

## When to Apply

This directive applies when:
- **Writing new functions** - Index on creation
- **Updating existing functions** - Re-index on change
- **Project initialization** - Bulk index existing codebase
- **Git changes detected** - Re-index modified files
- **Called by project directives**:
  - `project_file_write` - Index functions after writing
  - `project_update_db` - Trigger indexing on database updates
  - `git_detect_external_changes` - Re-index modified functions
  - Works with `fp_metadata_annotation` - Extract metadata for indexing

---

## Workflow

### Trunk: index_functions

Parses code files, extracts function information, and stores in project.db.

**Steps**:
1. **Parse source file** - Build AST of code
2. **Extract functions** - Find all function definitions
3. **Extract metadata** - Parse AIFP_METADATA comments
4. **Analyze dependencies** - Identify function calls
5. **Determine purity** - Classify pure/IO/impure
6. **Insert to database** - Add to functions table
7. **Track interactions** - Add to interactions table

### Branches

**Branch 1: If new_function**
- **Then**: `insert_function_to_database`
- **Details**: Function not in database
  - Extract function signature
  - Parse metadata if present
  - Analyze purity level
  - Identify dependencies
  - INSERT into functions table
  - Create interaction entries
- **Result**: Returns indexed function

**Branch 2: If function_updated**
- **Then**: `update_function_in_database`
- **Details**: Function exists but changed
  - Compare with database version
  - Detect changes (signature, body, metadata)
  - UPDATE functions table
  - Update interactions if dependencies changed
  - Increment version number
- **Result**: Returns updated index

**Branch 3: If function_deleted**
- **Then**: `remove_function_from_database`
- **Details**: Function no longer in code
  - Mark as deleted (soft delete)
  - Or remove from database (hard delete)
  - Clean up interaction entries
  - Log deletion to notes
- **Result**: Returns cleanup status

**Branch 4: If function_already_indexed**
- **Then**: `verify_index_accuracy`
- **Details**: Function in database and unchanged
  - Verify metadata matches
  - Check dependencies still valid
  - No action needed
  - Mark as verified
- **Result**: Index is accurate

**Branch 5: If bulk_indexing**
- **Then**: `index_all_functions`
- **Details**: Indexing entire project
  - Scan all source files
  - Extract all functions
  - Batch insert to database
  - Build interaction graph
  - Log completion
- **Result**: Returns indexed count

**Fallback**: `prompt_user`
- **Details**: Ambiguous function structure
  - Cannot parse function clearly
  - Unclear dependencies
  - Ask user for clarification
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Function with Metadata (Indexed):**

```python
# File: src/calculations.py

# AIFP_METADATA
# function_name: calculate_total
# purity_level: pure
# parameters: items: list[float]
# return_type: float
# dependencies: []
# side_effects: none
# theme: calculations
# flow: invoice-processing
def calculate_total(items: list[float]) -> float:
    """Calculate total price of items."""
    return sum(items)

# After indexing, database contains:
# functions table:
# - id: 42
# - name: calculate_total
# - file_id: 5
# - purpose: Calculate total price of items
# - parameters: ["items: list[float]"]
# - return_type: float
# - purity_level: pure
# - side_effects_json: null
# - dependencies_json: []
# - theme: calculations
# - flow: invoice-processing

# ✅ Function fully indexed
# ✅ Metadata extracted and stored
# ✅ Available for database queries
```

**Why Compliant**:
- Function has metadata
- All information extracted
- Stored in database
- Queryable via SQL

---

**Function with Dependencies (Indexed):**

```python
# File: src/order_processing.py

# AIFP_METADATA
# function_name: process_order
# purity_level: pure
# parameters: order: Order, tax_rate: float
# return_type: ProcessedOrder
# dependencies: [calculate_subtotal, calculate_tax, apply_discount]
# side_effects: none
def process_order(order: Order, tax_rate: float) -> ProcessedOrder:
    """Process order with tax and discounts."""
    subtotal = calculate_subtotal(order.items)
    tax = calculate_tax(subtotal, tax_rate)
    discount = apply_discount(order.coupon, subtotal)
    total = subtotal + tax - discount

    return ProcessedOrder(
        order_id=order.id,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total
    )

# After indexing, database contains:
# functions table:
# - id: 43
# - name: process_order
# - dependencies_json: ["calculate_subtotal", "calculate_tax", "apply_discount"]
#
# interactions table:
# - source_function_id: 43, target_function_id: 15 (calculate_subtotal)
# - source_function_id: 43, target_function_id: 16 (calculate_tax)
# - source_function_id: 43, target_function_id: 17 (apply_discount)

# ✅ Dependencies extracted
# ✅ Interaction graph built
# ✅ Call relationships tracked
```

**Why Compliant**:
- Dependencies identified
- Stored in both dependencies_json and interactions table
- Call graph complete
- Enables dependency analysis

---

**Bulk Indexing (Compliant):**

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

**Why Compliant**:
- Entire project indexed
- All functions in database
- Dependencies tracked
- Enables project-wide queries

---

### ❌ Non-Compliant Code

**Function Not Indexed (Violation):**

```python
# File: src/utils.py

# ❌ VIOLATION: Function not in database
def calculate_discount(subtotal: float, rate: float) -> float:
    """Calculate discount amount."""
    return subtotal * rate

# Problem:
# - Function exists in code but not in database
# - Cannot be queried
# - Not tracked in project
# - AI has no context
# - Dependencies not tracked
```

**Why Non-Compliant**:
- Function not in database
- No project.db entry
- Cannot be queried
- Missing from function catalog

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Function indexed

# File: src/utils.py

# AIFP_METADATA
# function_name: calculate_discount
# purity_level: pure
# parameters: subtotal: float, rate: float
# return_type: float
# dependencies: []
# side_effects: none
# theme: calculations
def calculate_discount(subtotal: float, rate: float) -> float:
    """Calculate discount amount."""
    return subtotal * rate

# Indexing triggered by project_file_write:
# INSERT INTO functions (name, file_id, purpose, purity_level, ...)
# VALUES ('calculate_discount', 5, 'Calculate discount amount', 'pure', ...);

# Function now indexed and queryable
```

---

**Stale Index (Violation):**

```python
# ❌ VIOLATION: Function changed but database not updated

# File: src/calculations.py

# Code changed: New parameter added
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calculate total including tax."""
    subtotal = sum(items)
    return subtotal + (subtotal * tax_rate)

# Database still has old signature:
# parameters: ["items: list[float]"]  # ← Missing tax_rate
# dependencies_json: []                # ← Outdated

# Problem:
# - Function signature changed
# - Database not updated
# - Index stale
# - Queries return incorrect information
```

**Why Non-Compliant**:
- Database has stale information
- Signature doesn't match code
- Index out of sync
- Queries misleading

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Index updated

# File: src/calculations.py

# AIFP_METADATA updated
# function_name: calculate_total
# purity_level: pure
# parameters: items: list[float], tax_rate: float
# return_type: float
# dependencies: []
# side_effects: none
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calculate total including tax."""
    subtotal = sum(items)
    return subtotal + (subtotal * tax_rate)

# Re-indexing triggered:
# UPDATE functions
# SET parameters = '["items: list[float]", "tax_rate: float"]',
#     updated_at = CURRENT_TIMESTAMP
# WHERE id = 42;

# Index now accurate
```

---

**Missing Dependencies (Violation):**

```python
# ❌ VIOLATION: Dependencies not tracked

# File: src/invoices.py

def generate_invoice(order: Order) -> Invoice:
    """Generate invoice for order."""
    total = calculate_total(order.items)  # ← Dependency not tracked
    tax = calculate_tax(total)            # ← Dependency not tracked
    formatted = format_invoice(order, total, tax)  # ← Dependency not tracked
    return formatted

# Database has:
# dependencies_json: []  # ← Empty! Should have 3 dependencies

# Problem:
# - Function calls other functions
# - Dependencies not tracked
# - Cannot build call graph
# - Cannot analyze impact of changes
```

**Why Non-Compliant**:
- Dependencies not identified
- interactions table empty
- Call graph incomplete
- Cannot analyze dependencies

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Dependencies tracked

# File: src/invoices.py

# AIFP_METADATA
# function_name: generate_invoice
# purity_level: pure
# parameters: order: Order
# return_type: Invoice
# dependencies: [calculate_total, calculate_tax, format_invoice]
# side_effects: none
def generate_invoice(order: Order) -> Invoice:
    """Generate invoice for order."""
    total = calculate_total(order.items)
    tax = calculate_tax(total)
    formatted = format_invoice(order, total, tax)
    return formatted

# After re-indexing:
# UPDATE functions SET dependencies_json =
#   '["calculate_total", "calculate_tax", "format_invoice"]'
# WHERE id = 44;
#
# INSERT INTO interactions:
# (44 -> 42: calculate_total)
# (44 -> 45: calculate_tax)
# (44 -> 46: format_invoice)

# Dependencies now tracked
```

---

## Indexing Process

### Step 1: Parse Source File

```python
import ast

def parse_file(file_path: str) -> ast.Module:
    """Parse Python source file to AST."""
    with open(file_path, 'r') as f:
        source = f.read()
    return ast.parse(source)
```

### Step 2: Extract Functions

```python
def extract_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """Extract all function definitions from AST."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
    return functions
```

### Step 3: Extract Metadata

```python
def extract_metadata(func: ast.FunctionDef, source: str) -> dict:
    """Extract AIFP metadata from function."""
    # Find metadata comment above function
    # Parse fields
    # Return structured metadata
    return {
        'name': func.name,
        'purity_level': 'pure',
        'parameters': [...],
        'return_type': ...,
        'dependencies': [...],
        'side_effects': 'none',
    }
```

### Step 4: Analyze Dependencies

```python
def analyze_dependencies(func: ast.FunctionDef) -> list[str]:
    """Extract function calls from function body."""
    dependencies = []
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                dependencies.append(node.func.id)
    return dependencies
```

### Step 5: Insert to Database

```python
def index_function(func_metadata: dict, file_id: int):
    """Insert function into database."""
    conn.execute("""
        INSERT INTO functions (
            name, file_id, purpose, parameters, return_type,
            purity_level, side_effects_json, dependencies_json, theme, flow
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        func_metadata['name'],
        file_id,
        func_metadata['purpose'],
        json.dumps(func_metadata['parameters']),
        func_metadata['return_type'],
        func_metadata['purity_level'],
        func_metadata['side_effects'],
        json.dumps(func_metadata['dependencies']),
        func_metadata.get('theme'),
        func_metadata.get('flow')
    ))
```

---

## Database Schema

### functions Table

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### interactions Table

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Query Examples

### Find All Pure Functions

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Find Functions by Theme

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Find Dependency Graph

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Find Functions with Most Dependencies

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Edge Cases

### Edge Case 1: Nested Functions

**Issue**: Functions defined inside other functions

**Handling**:
```python
def outer_function():
    """Outer function."""

    def inner_function():
        """Inner helper."""
        pass

    return inner_function()

# Indexing:
# - Index outer_function normally
# - Index inner_function with parent reference
# - Mark inner_function as nested/private
```

**Directive Action**: Index nested functions with parent relationship tracked.

---

### Edge Case 2: Decorated Functions

**Issue**: Functions with decorators

**Handling**:
```python
@memoize
@tail_recursive
def fibonacci(n: int) -> int:
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Indexing:
# - Index function normally
# - Track decorators in metadata
# - Note optimization hints
```

**Directive Action**: Track decorators in function metadata.

---

### Edge Case 3: Method Functions (Classes)

**Issue**: Functions inside classes (should convert to standalone)

**Handling**:
```python
# ❌ OOP class (should be refactored)
class Calculator:
    def add(self, x, y):
        return x + y

# After fp_no_oop refactoring:
# ✅ Standalone function
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y

# Index standalone function normally
```

**Directive Action**: Only index after OOP elimination converts methods to functions.

---

## Related Directives

- **Depends On**:
  - `fp_metadata_annotation` - Provides metadata to index
  - `fp_purity` - Determines purity level
  - `fp_side_effect_detection` - Identifies side effects
- **Triggers**:
  - `project_update_db` - Updates database after indexing
- **Called By**:
  - `project_file_write` - Index functions after writing file
  - `git_detect_external_changes` - Re-index modified files
  - Works with `fp_dependency_tracking` - Builds dependency graph
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Inserts or updates function entries with complete metadata
- **`interactions`**: Creates entries for function call relationships
- **`notes`**: Logs indexing operations with `note_type = 'indexing'`

---

## Testing

How to verify this directive is working:

1. **New function written** → Automatically indexed in database
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

2. **Function modified** → Database updated
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

3. **Check index completeness**
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Function not indexed** - Written but not added to database
- ❌ **Stale index** - Function changed but database not updated
- ❌ **Missing dependencies** - Function calls not tracked
- ❌ **Incorrect metadata** - Database has wrong information
- ❌ **Orphaned entries** - Database has deleted functions

---

## Roadblocks and Resolutions

### Roadblock 1: new_function
**Issue**: Function exists in code but not in database
**Resolution**: Parse function, extract metadata, insert into functions table with complete information

### Roadblock 2: function_updated
**Issue**: Function modified but database has stale information
**Resolution**: Re-analyze function, compare with database, update changed fields

### Roadblock 3: function_deleted
**Issue**: Function removed from code but still in database
**Resolution**: Soft delete (mark as deleted) or hard delete (remove from database)

### Roadblock 4: bulk_indexing_needed
**Issue**: Entire project needs indexing from scratch
**Resolution**: Scan all source files, batch insert all functions, build interaction graph

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for automatic function indexing*
