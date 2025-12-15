# fp_dependency_tracking

## Purpose

The `fp_dependency_tracking` directive analyzes function call graphs and stores dependency metadata to enable intelligent reasoning, impact analysis, and code generation alignment. It traces which functions call which other functions, tracks import relationships, detects circular dependencies, and maintains a comprehensive dependency map in the project database. This provides AIFP with dependency awareness to improve reasoning efficiency, change impact analysis, and refactoring safety.

**Category**: Introspection
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`trace_function_calls`**: Scan all function bodies to identify function calls, method invocations, and import dependencies.

### Branches

1. **`dependency_detected`** → **`store_in_metadata`**
   - **Condition**: Function calls another function (direct dependency)
   - **Action**: Record dependency relationship in database
   - **Details**: Store caller → callee relationship with context
   - **Output**: Dependency record in interactions table

2. **`circular_dependency`** → **`alert_and_resolve`**
   - **Condition**: Detects circular call chain (A → B → A)
   - **Action**: Alert user and suggest refactoring
   - **Details**: Break cycle via dependency inversion or extraction
   - **Output**: Circular dependency report with resolution options

3. **`import_dependency`** → **`track_module_relationship`**
   - **Condition**: Module imports another module
   - **Action**: Record module-level dependency
   - **Details**: Track import statements and used symbols
   - **Output**: Module dependency graph

4. **`external_dependency`** → **`flag_external_call`**
   - **Condition**: Function calls external library or system API
   - **Action**: Flag as external dependency for tracking
   - **Details**: Document external dependencies for version management
   - **Output**: External dependency record

5. **`no_dependencies`** → **`mark_as_leaf`**
   - **Condition**: Function has no internal dependencies (leaf node)
   - **Action**: Mark as leaf function in call graph
   - **Output**: Leaf function metadata

6. **Fallback** → **`mark_as_clean`**
   - **Condition**: Dependency analysis complete
   - **Action**: Mark as analyzed

### Error Handling
- **On failure**: Prompt user with dependency analysis details
- **Low confidence** (< 0.7): Request review for ambiguous dependencies

---

## Refactoring Strategies

### Strategy 1: Build Call Graph
Construct complete call graph showing function relationships.

**Analysis Process**:
```python
# Source code
def calculate_total(items):
    subtotal = calculate_subtotal(items)
    tax = calculate_tax(subtotal)
    return subtotal + tax

def calculate_subtotal(items):
    return sum(item['price'] for item in items)

def calculate_tax(amount):
    return amount * TAX_RATE

# Generated Call Graph
# calculate_total → calculate_subtotal
# calculate_total → calculate_tax
# calculate_tax → TAX_RATE (constant dependency)
```

**Database Storage**:
```sql
-- Store function dependencies
INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description)
VALUES
    (fn_id('calculate_total'), fn_id('calculate_subtotal'), 'call', 'Calculates subtotal before tax'),
    (fn_id('calculate_total'), fn_id('calculate_tax'), 'call', 'Calculates tax on subtotal');
```

### Strategy 2: Detect Circular Dependencies
Identify and break circular dependency chains.

**Before (Circular - Non-Compliant)**:
```python
# user_service.py
from order_service import get_user_orders

def get_user_with_orders(user_id):
    user = fetch_user(user_id)
    orders = get_user_orders(user_id)  # Calls order_service
    return {**user, 'orders': orders}

# order_service.py
from user_service import get_user_with_orders

def get_order_with_user(order_id):
    order = fetch_order(order_id)
    user = get_user_with_orders(order['user_id'])  # Calls user_service!
    return {**order, 'user': user}

# Circular: user_service → order_service → user_service
```

**After (Resolved - Compliant)**:
```python
# user_service.py
def get_user(user_id: int) -> dict:
    """Pure: fetches user data only."""
    return fetch_user(user_id)

# order_service.py
def get_orders_for_user(user_id: int) -> list[dict]:
    """Pure: fetches orders for user."""
    return fetch_orders_by_user(user_id)

# composition_service.py (new layer)
from user_service import get_user
from order_service import get_orders_for_user

def get_user_with_orders(user_id: int) -> dict:
    """Compose user and orders (breaks circular dependency)."""
    user = get_user(user_id)
    orders = get_orders_for_user(user_id)
    return {**user, 'orders': orders}

def get_order_with_user(order_id: int) -> dict:
    """Compose order and user (breaks circular dependency)."""
    order = fetch_order(order_id)
    user = get_user(order['user_id'])
    return {**order, 'user': user}
```

### Strategy 3: Track Import Dependencies
Monitor module-level dependencies for impact analysis.

**Analysis**:
```python
# File: src/processors/data_processor.py
from src.utils.validation import validate_schema
from src.utils.transform import normalize_data
from src.models.user import User
import json
import logging

# Dependencies tracked:
# data_processor → validation (internal)
# data_processor → transform (internal)
# data_processor → user (internal)
# data_processor → json (stdlib)
# data_processor → logging (stdlib)
```

**Database Storage**:
```sql
-- Store module dependencies
INSERT INTO module_dependencies (source_module, target_module, dependency_type, symbols_used)
VALUES
    ('src.processors.data_processor', 'src.utils.validation', 'internal', '["validate_schema"]'),
    ('src.processors.data_processor', 'src.utils.transform', 'internal', '["normalize_data"]'),
    ('src.processors.data_processor', 'src.models.user', 'internal', '["User"]'),
    ('src.processors.data_processor', 'json', 'stdlib', '["loads", "dumps"]'),
    ('src.processors.data_processor', 'logging', 'stdlib', '["getLogger"]');
```

### Strategy 4: Dependency Inversion for Decoupling
Use dependency injection to break tight coupling.

**Before (Tight Coupling)**:
```python
# Direct dependency on concrete implementation
def process_payment(amount):
    gateway = StripePaymentGateway()  # Hard-coded dependency
    return gateway.charge(amount)
```

**After (Dependency Injection)**:
```python
from typing import Protocol

class PaymentGateway(Protocol):
    """Interface for payment processing."""
    def charge(self, amount: float) -> bool: ...

def process_payment(amount: float, gateway: PaymentGateway) -> bool:
    """Dependency injected: testable, flexible."""
    return gateway.charge(amount)

# Usage: dependency provided by caller
stripe_gateway = StripePaymentGateway()
result = process_payment(100.0, stripe_gateway)
```

### Strategy 5: Layered Architecture Enforcement
Ensure dependencies flow in one direction (no backwards dependencies).

**Architecture Layers**:
```
Presentation Layer (UI, API handlers)
    ↓
Business Logic Layer (domain logic)
    ↓
Data Access Layer (repositories, databases)
    ↓
Infrastructure Layer (external services, I/O)
```

**Validation**:
```python
# Detect violations: Data layer should NOT call Business layer
def check_layered_architecture(call_graph):
    """Validate dependencies flow downward only."""
    violations = []

    for caller, callee in call_graph.edges:
        caller_layer = get_layer(caller)
        callee_layer = get_layer(callee)

        if layer_rank(caller_layer) > layer_rank(callee_layer):
            violations.append(f"{caller} (layer {caller_layer}) calls {callee} (layer {callee_layer})")

    return violations
```

---

## Examples

### Example 1: Simple Call Graph

**Code**:
```python
def main():
    data = load_data()
    processed = process_data(data)
    save_results(processed)

def load_data():
    return read_file('input.txt')

def process_data(data):
    return transform(data)

def save_results(results):
    write_file('output.txt', results)

def read_file(path):
    # ... implementation
    pass

def write_file(path, content):
    # ... implementation
    pass

def transform(data):
    return [item.upper() for item in data]
```

**Call Graph**:
```
main
├── load_data
│   └── read_file
├── process_data
│   └── transform
└── save_results
    └── write_file
```

**Database Representation**:
```sql
-- Interactions table
-- main → load_data, process_data, save_results
-- load_data → read_file
-- process_data → transform
-- save_results → write_file
```

### Example 2: Detecting Circular Dependency

**Code (Circular)**:
```python
# a.py
from b import helper_b

def function_a():
    return helper_b() + 1

# b.py
from a import function_a

def helper_b():
    if some_condition():
        return function_a()  # Circular!
    return 42
```

**Detection**:
```python
# Circular dependency detected:
# a.function_a → b.helper_b → a.function_a
# ALERT: Circular dependency found
# Resolution: Extract shared logic to new module 'c'
```

### Example 3: Impact Analysis

**Scenario**: User wants to modify `calculate_tax` function

**Impact Analysis Query**:
```sql
-- Find all functions that depend on calculate_tax
WITH RECURSIVE dependents AS (
    -- Base case: direct callers
    SELECT source_function_id, 1 as depth
    FROM interactions
    WHERE target_function_id = fn_id('calculate_tax')

    UNION ALL

    -- Recursive case: indirect callers
    SELECT i.source_function_id, d.depth + 1
    FROM interactions i
    JOIN dependents d ON i.target_function_id = d.source_function_id
    WHERE d.depth < 5
)
SELECT DISTINCT f.name, f.file_id, d.depth
FROM dependents d
JOIN functions f ON f.id = d.source_function_id
ORDER BY d.depth;

-- Result:
-- calculate_total (depth 1) - direct caller
-- process_invoice (depth 2) - calls calculate_total
-- generate_report (depth 3) - calls process_invoice
```

---

## Edge Cases

### Edge Case 1: Dynamic Function Calls
**Scenario**: Function called via string or reflection
**Issue**: Static analysis cannot detect call
**Handling**:
- Flag dynamic calls for manual review
- Use naming conventions to hint at dynamic dependencies
- Document dynamic call patterns in metadata

**Example**:
```python
# Dynamic call - hard to detect
function_name = "process_data"
result = globals()[function_name]()  # Dynamic call!

# Better: Dispatch table (statically analyzable)
HANDLERS = {
    "process_data": process_data,
    "transform_data": transform_data,
}

def dispatch(operation: str):
    handler = HANDLERS.get(operation)
    if handler:
        return handler()
```

### Edge Case 2: Higher-Order Functions
**Scenario**: Function passed as parameter
**Issue**: Call graph depends on runtime arguments
**Handling**:
- Track function parameter types (Callable annotations)
- Record potential callees based on usage patterns
- Mark as polymorphic dependency

**Example**:
```python
from typing import Callable

def apply_operation(data: list, operation: Callable[[int], int]) -> list:
    """Dependency on 'operation' parameter (polymorphic)."""
    return [operation(item) for item in data]

# Usage reveals dependencies
result = apply_operation([1, 2, 3], lambda x: x * 2)
```

### Edge Case 3: Conditional Dependencies
**Scenario**: Function call depends on runtime condition
**Issue**: Call may or may not happen
**Handling**:
- Record as conditional dependency
- Mark probability/condition in metadata
- Include in call graph with conditional edge

**Example**:
```python
def process(data, use_cache=False):
    if use_cache:
        load_from_cache()  # Conditional dependency
    return transform(data)  # Unconditional dependency
```

### Edge Case 4: External Library Dependencies
**Scenario**: Dependency on third-party library
**Issue**: No source code to analyze
**Handling**:
- Record external dependency with version
- Document API usage patterns
- Flag for version compatibility checks

### Edge Case 5: Transitive Dependency Explosion
**Scenario**: Deep call chains create huge dependency graphs
**Issue**: Graph becomes unmanageable
**Handling**:
- Limit traversal depth for visualization
- Aggregate dependencies by module
- Focus on direct dependencies for most analysis

---

## Database Operations

### Store Function Dependencies

```sql
-- Record function call dependency
INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description, call_count)
VALUES (
    (SELECT id FROM functions WHERE name = 'calculate_total' AND file_id = 42),
    (SELECT id FROM functions WHERE name = 'calculate_tax' AND file_id = 43),
    'call',
    'Calculates tax as part of total computation',
    1
);

-- Update call count on subsequent analysis
UPDATE interactions
SET call_count = call_count + 1, updated_at = CURRENT_TIMESTAMP
WHERE source_function_id = ? AND target_function_id = ?;
```

### Query Dependency Graph

```sql
-- Get all dependencies for a function
SELECT
    f_target.name as calls,
    f_target.file_id,
    i.interaction_type,
    i.description
FROM interactions i
JOIN functions f_source ON i.source_function_id = f_source.id
JOIN functions f_target ON i.target_function_id = f_target.id
WHERE f_source.name = 'calculate_total'
ORDER BY i.created_at;
```

### Detect Circular Dependencies

```sql
-- Find circular dependencies (simplified 2-cycle detection)
SELECT
    f1.name as function_a,
    f2.name as function_b
FROM interactions i1
JOIN interactions i2
    ON i1.source_function_id = i2.target_function_id
    AND i1.target_function_id = i2.source_function_id
JOIN functions f1 ON i1.source_function_id = f1.id
JOIN functions f2 ON i1.target_function_id = f2.id
WHERE i1.source_function_id < i1.target_function_id;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Pure functions simplify dependency reasoning
- **fp_function_composition**: Tracks composed function dependencies

### Project Directives
- **project_compliance_check**: Uses dependency info for impact analysis
- **project_update_db**: Stores dependency metadata
- **project_file_write**: Checks dependencies before code changes

---

## Helper Functions

### `build_call_graph(project_files) -> CallGraph`
Constructs complete call graph from all project files.

**Signature**:
```python
def build_call_graph(project_files: list[str]) -> CallGraph:
    """
    Analyzes all files to build complete call graph.
    Returns directed graph with functions as nodes, calls as edges.
    """
```

### `detect_circular_dependencies(call_graph) -> list[Cycle]`
Identifies circular dependency chains in call graph.

**Signature**:
```python
def detect_circular_dependencies(call_graph: CallGraph) -> list[Cycle]:
    """
    Uses cycle detection algorithm (DFS-based) to find cycles.
    Returns list of circular dependency chains.
    """
```

### `calculate_impact(function_name, call_graph) -> ImpactReport`
Computes change impact for modifying a function.

**Signature**:
```python
def calculate_impact(
    function_name: str,
    call_graph: CallGraph
) -> ImpactReport:
    """
    Traces all functions that depend on target function.
    Returns impact report with affected functions and depth.
    """
```

### `extract_import_dependencies(file_path) -> list[Dependency]`
Extracts import statements and module dependencies.

**Signature**:
```python
def extract_import_dependencies(file_path: str) -> list[Dependency]:
    """
    Parses file for import statements.
    Returns list of module dependencies with used symbols.
    """
```

---

## Testing

### Test 1: Build Call Graph
```python
def test_build_call_graph():
    source = """
def main():
    result = calculate(10)
    print(result)

def calculate(x):
    return double(x) + 5

def double(x):
    return x * 2
"""

    graph = fp_dependency_tracking.build_graph(source)

    assert graph.has_edge('main', 'calculate')
    assert graph.has_edge('calculate', 'double')
    assert graph.has_edge('main', 'print')  # Built-in
```

### Test 2: Detect Circular Dependency
```python
def test_detect_circular():
    source = """
def a():
    return b() + 1

def b():
    return c() + 2

def c():
    return a() + 3  # Circular!
"""

    cycles = fp_dependency_tracking.detect_cycles(source)

    assert len(cycles) > 0
    assert 'a' in cycles[0] and 'b' in cycles[0] and 'c' in cycles[0]
```

### Test 3: Impact Analysis
```python
def test_impact_analysis():
    source = """
def leaf():
    return 42

def middle():
    return leaf() * 2

def top():
    return middle() + 1
"""

    impact = fp_dependency_tracking.impact_analysis(source, 'leaf')

    assert 'middle' in impact.affected_functions
    assert 'top' in impact.affected_functions
    assert impact.max_depth == 2
```

---

## Common Mistakes

### Mistake 1: Missing Indirect Dependencies
**Problem**: Only tracking direct calls, missing transitive dependencies

**Solution**: Build complete transitive closure of dependencies

```python
# Track not just calculate_total → calculate_tax
# But also: anything that calls calculate_total is transitively affected
```

### Mistake 2: Ignoring Import Side Effects
**Problem**: Module imports can have side effects

**Solution**: Track import execution order and side effects

```python
# ❌ Import with side effect (missed dependency)
# config.py
DATABASE_URL = initialize_database()  # Side effect on import!

# ✅ Explicit initialization function
# config.py
def initialize_config():
    return {"database_url": get_database_url()}
```

### Mistake 3: Not Updating Dependency Graph
**Problem**: Graph becomes stale as code changes

**Solution**: Update dependencies on every file change

```python
# After modifying function, re-analyze dependencies
def on_file_save(file_path):
    old_dependencies = get_dependencies(file_path)
    new_dependencies = analyze_dependencies(file_path)

    # Update changed dependencies
    update_dependency_changes(old_dependencies, new_dependencies)
```

---

## Roadblocks

### Roadblock 1: Circular Dependency
**Issue**: Functions form circular call chain
**Resolution**: Refactor to break cycle via extraction or dependency inversion

### Roadblock 2: Dynamic Function Calls
**Issue**: Function called dynamically (reflection, eval)
**Resolution**: Flag for manual review, use dispatch tables where possible

### Roadblock 3: Large Dependency Graph
**Issue**: Too many dependencies to visualize or analyze
**Resolution**: Aggregate by module, limit traversal depth, focus on critical paths

---

## Integration Points

### With `project_compliance_check`
Uses dependency info to validate architectural rules.

### With `project_update_db`
Stores all dependency metadata in database.

---

## Intent Keywords

- `dependency`
- `import`
- `call graph`
- `impact analysis`
- `circular dependency`

---

## Confidence Threshold

**0.7** - High confidence required for accurate dependency tracking.

---

## Notes

- Dependency tracking enables intelligent refactoring suggestions
- Call graphs help identify unused functions (dead code)
- Circular dependencies indicate architectural issues
- Transitive dependencies critical for change impact analysis
- Track both function-level and module-level dependencies
- External dependencies should include version information
- Update dependency graph incrementally on file changes
- Use graph algorithms (DFS, BFS) for cycle detection and traversal
- Visualize call graphs for architectural understanding
- Dependency tracking is foundation for many other directives
