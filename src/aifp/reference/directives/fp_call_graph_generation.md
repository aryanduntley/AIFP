# fp_call_graph_generation

## Purpose

The `fp_call_graph_generation` directive builds an internal representation of all function calls for dependency analysis, impact assessment, and debugging. It creates a directed graph where nodes represent functions and edges represent call relationships, enabling intelligent reasoning about code structure, refactoring safety, and change impact. This provides AIFP with visualization and analysis capabilities for the codebase call structure.

**Category**: Introspection
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`scan_for_function_calls`**: Analyze all source files to identify function definitions and call sites.

### Branches

1. **`function_call_detected`** → **`record_dependency`**
   - **Condition**: Function invokes another function
   - **Action**: Create edge in call graph from caller to callee
   - **Details**: Record call relationship with context (line, file)
   - **Output**: Call graph edge

2. **`graph_complete`** → **`store_in_metadata`**
   - **Condition**: All files analyzed, graph constructed
   - **Action**: Store call graph in database and generate visualization
   - **Details**: Save graph structure, generate DOT/GraphML export
   - **Output**: Persistent call graph data

3. **`cyclic_dependency`** → **`flag_cycle`**
   - **Condition**: Cycle detected in call graph
   - **Action**: Flag circular dependencies for review
   - **Details**: Identify cycle participants, suggest refactoring
   - **Output**: Cycle detection report

4. **`orphan_function`** → **`flag_as_unused`**
   - **Condition**: Function defined but never called
   - **Action**: Flag as potentially dead code
   - **Details**: Mark for review or removal
   - **Output**: Dead code candidates

5. **Fallback** → **`prompt_user`**
   - **Condition**: Graph generation issues
   - **Action**: Request clarification on ambiguous calls

### Error Handling
- **On failure**: Prompt user with graph generation details
- **Low confidence** (< 0.7): Request review for ambiguous relationships

---

## Refactoring Strategies

### Strategy 1: Basic Call Graph Construction
Build simple directed graph of function calls.

**Implementation (Python)**:
```python
from dataclasses import dataclass
from typing import Optional
import ast

@dataclass
class FunctionNode:
    name: str
    file_path: str
    line_number: int
    calls: list[str]  # Functions this function calls

@dataclass
class CallGraph:
    nodes: dict[str, FunctionNode]
    edges: list[tuple[str, str]]  # (caller, callee)

class CallGraphBuilder(ast.NodeVisitor):
    """AST visitor to build call graph."""

    def __init__(self):
        self.graph = CallGraph(nodes={}, edges=[])
        self.current_function: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Record function definition."""
        func_node = FunctionNode(
            name=node.name,
            file_path="<current_file>",
            line_number=node.lineno,
            calls=[]
        )
        self.graph.nodes[node.name] = func_node

        # Visit function body to find calls
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func

    def visit_Call(self, node: ast.Call):
        """Record function call."""
        if self.current_function and isinstance(node.func, ast.Name):
            callee = node.func.id

            # Add to current function's call list
            if self.current_function in self.graph.nodes:
                self.graph.nodes[self.current_function].calls.append(callee)

            # Add edge to graph
            self.graph.edges.append((self.current_function, callee))

        self.generic_visit(node)

def build_call_graph(source_code: str) -> CallGraph:
    """Build call graph from source code."""
    tree = ast.parse(source_code)
    builder = CallGraphBuilder()
    builder.visit(tree)
    return builder.graph
```

### Strategy 2: Visualize Call Graph
Generate visual representation using DOT format.

**Implementation**:
```python
def generate_dot_graph(graph: CallGraph) -> str:
    """Generate DOT format for Graphviz visualization."""
    lines = ['digraph CallGraph {']
    lines.append('    rankdir=LR;')
    lines.append('    node [shape=box, style=rounded];')

    # Add nodes
    for name, node in graph.nodes.items():
        label = f"{name}\\n({node.file_path}:{node.line_number})"
        lines.append(f'    "{name}" [label="{label}"];')

    # Add edges
    for caller, callee in graph.edges:
        lines.append(f'    "{caller}" -> "{callee}";')

    lines.append('}')
    return '\n'.join(lines)

def export_call_graph(graph: CallGraph, output_path: str):
    """Export call graph to DOT file."""
    dot_content = generate_dot_graph(graph)
    with open(output_path, 'w') as f:
        f.write(dot_content)
```

### Strategy 3: Detect Circular Dependencies
Find cycles in call graph using DFS.

**Implementation**:
```python
from typing import Set

def detect_cycles(graph: CallGraph) -> list[list[str]]:
    """Detect circular dependencies in call graph."""
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: list[str]):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        # Get callees
        if node in graph.nodes:
            for callee in graph.nodes[node].calls:
                if callee not in visited:
                    dfs(callee, path)
                elif callee in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(callee)
                    cycle = path[cycle_start:] + [callee]
                    cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    for node_name in graph.nodes:
        if node_name not in visited:
            dfs(node_name, [])

    return cycles
```

### Strategy 4: Find Dead Code
Identify functions that are never called.

**Implementation**:
```python
def find_unused_functions(graph: CallGraph, entry_points: list[str]) -> list[str]:
    """Find functions that are never called from entry points."""
    # Start from entry points, traverse reachable functions
    reachable = set()

    def dfs(node: str):
        if node in reachable or node not in graph.nodes:
            return

        reachable.add(node)
        for callee in graph.nodes[node].calls:
            dfs(callee)

    # Traverse from all entry points
    for entry in entry_points:
        dfs(entry)

    # Functions not reachable are potentially unused
    all_functions = set(graph.nodes.keys())
    unused = all_functions - reachable

    return list(unused)
```

### Strategy 5: Calculate Impact Radius
Determine which functions are affected by changes to a target function.

**Implementation**:
```python
def calculate_impact(
    graph: CallGraph,
    target_function: str
) -> dict[str, int]:
    """Calculate impact radius: functions affected by changes to target."""
    # Build reverse graph (who calls this function)
    callers = {}
    for caller, callee in graph.edges:
        if callee not in callers:
            callers[callee] = []
        callers[callee].append(caller)

    # BFS to find all functions that depend on target
    impact = {target_function: 0}  # Distance from target
    queue = [(target_function, 0)]
    visited = {target_function}

    while queue:
        current, distance = queue.pop(0)

        if current in callers:
            for caller in callers[current]:
                if caller not in visited:
                    visited.add(caller)
                    impact[caller] = distance + 1
                    queue.append((caller, distance + 1))

    return impact
```

---

## Examples

### Example 1: Simple Call Graph

**Source Code**:
```python
def main():
    result = calculate(10)
    display(result)

def calculate(x):
    doubled = double(x)
    incremented = increment(doubled)
    return incremented

def double(x):
    return x * 2

def increment(x):
    return x + 1

def display(value):
    print(f"Result: {value}")
```

**Generated Call Graph**:
```
main
├── calculate
│   ├── double
│   └── increment
└── display

Edges:
main -> calculate
main -> display
calculate -> double
calculate -> increment
```

### Example 2: Cycle Detection

**Source with Cycle**:
```python
def a():
    return b() + 1

def b():
    return c() + 2

def c():
    return a() + 3  # Cycle: a -> b -> c -> a
```

**Detection Result**:
```
Cycles detected:
  1. a -> b -> c -> a
```

### Example 3: Impact Analysis

**Source Code**:
```python
def api_handler():
    data = fetch_data()
    return process_data(data)

def fetch_data():
    return query_database()

def query_database():
    # Database query
    return {"id": 1, "value": 100}

def process_data(data):
    return transform(data)

def transform(data):
    return data["value"] * 2
```

**Impact of Changing `query_database`**:
```
Modifying query_database affects:
  - fetch_data (distance: 1)
  - api_handler (distance: 2)
```

---

## Edge Cases

### Edge Case 1: Dynamic Function Calls
**Scenario**: Functions called via getattr, eval, or string names
**Issue**: Static analysis cannot detect
**Handling**:
- Flag dynamic calls for manual review
- Use naming conventions to hint relationships
- Document dynamic call patterns

### Edge Case 2: Method Calls on Objects
**Scenario**: Object method calls (OOP code)
**Issue**: Requires object type resolution
**Handling**:
- Track method calls separately
- Use type inference to resolve
- Focus on module-level functions for FP

### Edge Case 3: Higher-Order Functions
**Scenario**: Functions passed as parameters
**Issue**: Callee depends on runtime argument
**Handling**:
- Mark as polymorphic dependency
- Record potential callees based on type hints
- Use call-site analysis

### Edge Case 4: Recursive Calls
**Scenario**: Function calls itself
**Issue**: Self-loop in graph
**Handling**:
- Represent as self-edge
- Mark as recursive
- Validate tail recursion

### Edge Case 5: Cross-Module Calls
**Scenario**: Functions call functions in other modules
**Issue**: Must analyze entire project
**Handling**:
- Build project-wide call graph
- Track import relationships
- Support incremental updates

---

## Database Operations

### Store Call Graph

```sql
-- Store call graph edges
CREATE TABLE IF NOT EXISTS call_graph (
    id INTEGER PRIMARY KEY,
    caller_function_id INTEGER,
    callee_function_id INTEGER,
    call_count INTEGER DEFAULT 1,
    file_id INTEGER,
    line_number INTEGER,
    FOREIGN KEY (caller_function_id) REFERENCES functions(id),
    FOREIGN KEY (callee_function_id) REFERENCES functions(id),
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- Insert call relationship
INSERT INTO call_graph (caller_function_id, callee_function_id, file_id, line_number)
SELECT
    (SELECT id FROM functions WHERE name = 'main' AND file_id = 1),
    (SELECT id FROM functions WHERE name = 'calculate' AND file_id = 1),
    1,
    5;

-- Query call graph
SELECT
    f_caller.name as caller,
    f_callee.name as callee,
    cg.call_count
FROM call_graph cg
JOIN functions f_caller ON cg.caller_function_id = f_caller.id
JOIN functions f_callee ON cg.callee_function_id = f_callee.id
ORDER BY f_caller.name, f_callee.name;
```

### Find Function Dependencies

```sql
-- Get all functions called by a specific function
SELECT f.name as called_function
FROM call_graph cg
JOIN functions f ON cg.callee_function_id = f.id
WHERE cg.caller_function_id = (
    SELECT id FROM functions WHERE name = 'main'
);

-- Get all functions that call a specific function
SELECT f.name as calling_function
FROM call_graph cg
JOIN functions f ON cg.caller_function_id = f.id
WHERE cg.callee_function_id = (
    SELECT id FROM functions WHERE name = 'calculate'
);
```

---

## Related Directives

### FP Directives
- **fp_dependency_tracking**: Complementary directive for dependency metadata
- **fp_purity**: Pure functions simplify call graph analysis

### Project Directives
- **project_compliance_check**: Uses call graph for impact analysis
- **project_update_db**: Stores call graph metadata

---

## Helper Functions

### `parse_function_calls(file_path) -> list[tuple[str, str]]`
Extracts function calls from source file.

**Signature**:
```python
def parse_function_calls(file_path: str) -> list[tuple[str, str]]:
    """
    Parses file to find function calls.
    Returns list of (caller, callee) tuples.
    """
```

### `merge_call_graphs(graphs) -> CallGraph`
Combines multiple call graphs into one.

**Signature**:
```python
def merge_call_graphs(graphs: list[CallGraph]) -> CallGraph:
    """
    Merges call graphs from multiple files.
    Returns unified project call graph.
    """
```

---

## Testing

### Test 1: Graph Construction
```python
def test_build_call_graph():
    source = """
def main():
    helper()

def helper():
    pass
"""

    graph = build_call_graph(source)

    assert 'main' in graph.nodes
    assert 'helper' in graph.nodes
    assert ('main', 'helper') in graph.edges
```

### Test 2: Cycle Detection
```python
def test_detect_cycle():
    source = """
def a():
    return b()

def b():
    return a()
"""

    graph = build_call_graph(source)
    cycles = detect_cycles(graph)

    assert len(cycles) > 0
    assert 'a' in cycles[0] and 'b' in cycles[0]
```

---

## Common Mistakes

### Mistake 1: Missing Import Resolution
**Problem**: Not resolving imported functions

**Solution**: Track imports and resolve fully qualified names

### Mistake 2: Ignoring Method Calls
**Problem**: Only tracking top-level functions

**Solution**: Include method calls in graph

### Mistake 3: No Cross-File Analysis
**Problem**: Only analyzing single file at a time

**Solution**: Build project-wide call graph

---

## Roadblocks

### Roadblock 1: Unresolved Symbol
**Issue**: Function call cannot be resolved
**Resolution**: Link or flag for manual analysis

### Roadblock 2: Dynamic Calls
**Issue**: Runtime-determined function calls
**Resolution**: Flag as dynamic, document pattern

---

## Integration Points

### With `fp_dependency_tracking`
Call graph is foundation for dependency tracking.

### With `project_compliance_check`
Enables impact analysis and dead code detection.

---

## Intent Keywords

- `call graph`
- `dependency map`
- `function calls`
- `impact analysis`

---

## Confidence Threshold

**0.7** - High confidence for accurate call graph generation.

---

## Notes

- Call graph enables intelligent refactoring
- Visualize with Graphviz (DOT format)
- Detect circular dependencies
- Find dead/unused code
- Calculate change impact radius
- Support incremental updates
- Cross-module analysis for completeness
- Track call frequency for optimization
- Export for external tools
- Foundation for many analysis tasks
