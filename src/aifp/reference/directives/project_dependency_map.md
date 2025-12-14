# Directive: project_dependency_map

**Type**: Project
**Level**: 3 (Dependency Management)
**Parent Directive**: project_dependency_sync
**Priority**: MEDIUM - Transparency and traceability

---

## Purpose

The `project_dependency_map` directive queries relationships between files, functions, flows, and tasks to produce a dependency graph for reasoning or visualization. This directive provides **dependency visibility**, enabling AI reasoning about project structure and helping developers understand component relationships.

Dependency mapping provides **relationship transparency**, enabling:
- **Function Dependencies**: Track which functions call which
- **File Dependencies**: Show module relationships
- **Task Dependencies**: Display task prerequisites
- **Flow Dependencies**: Map data flow through system
- **Impact Analysis**: Understand change ripple effects

This directive acts as a **relationship analyzer** providing complete project structure visibility.

---

## When to Apply

This directive applies when:
- **Understanding project structure** - Exploring component relationships
- **Impact analysis** - Determining change effects
- **Refactoring planning** - Understanding dependencies before changes
- **Documentation generation** - Creating architecture diagrams
- **Debugging** - Tracing function call paths
- **Called by other directives**:
  - `project_dependency_sync` - Generates map after sync
  - `project_compliance_check` - Analyzes dependencies for violations
  - `project_refactor_path` - Maps task dependencies
  - `aifp_status` - Shows current dependencies
  - Works with `fp_call_graph_generation` - Function-level call graphs

---

## Workflow

### Trunk: determine_map_scope

Determines what type of dependency map to generate.

**Steps**:
1. **Identify scope** - Functions, files, tasks, or flows?
2. **Query relationships** - Get relevant database tables
3. **Build graph structure** - Create dependency graph
4. **Route to appropriate branch** - Based on scope type

### Branches

**Branch 1: If function_dependencies_requested**
- **Then**: `generate_function_graph`
- **Details**: Map function call relationships
  - Query functions table for all functions
  - Query interactions table for call relationships
  - Build directed graph:
    - Nodes: functions
    - Edges: function calls
  - Include metadata:
    - Function purity level
    - Parameter types
    - Return types
  - Calculate metrics:
    - Function fan-in (callers)
    - Function fan-out (callees)
    - Cyclomatic complexity
  - Store graph in notes
  - Return graph structure
- **Result**: Function dependency graph

**Branch 2: If file_dependencies_requested**
- **Then**: `generate_file_graph`
- **Details**: Map file import relationships
  - Query files table for all files
  - Parse import/require statements
  - Query file_dependencies table
  - Build directed graph:
    - Nodes: files
    - Edges: imports/dependencies
  - Include metadata:
    - File language
    - Line count
    - Function count
  - Detect circular dependencies
  - Store graph in notes
  - Return graph structure
- **Result**: File dependency graph

**Branch 3: If task_dependencies_requested**
- **Then**: `generate_task_graph`
- **Details**: Map task prerequisite relationships
  - Query tasks table
  - Query subtasks table
  - Query task dependencies
  - Build directed graph:
    - Nodes: tasks/subtasks
    - Edges: prerequisites
  - Include metadata:
    - Task status
    - Priority
    - Milestone
  - Calculate critical path
  - Store graph in notes
  - Return graph structure
- **Result**: Task dependency graph

**Branch 4: If flow_dependencies_requested**
- **Then**: `generate_flow_graph`
- **Details**: Map data flow relationships
  - Query flows table
  - Query flow_dependencies
  - Query file_flows linking table
  - Build directed graph:
    - Nodes: flows
    - Edges: data dependencies
  - Include metadata:
    - Flow type
    - Associated files
    - Associated themes
  - Store graph in notes
  - Return graph structure
- **Result**: Flow dependency graph

**Branch 5: If linked_entities_found**
- **Then**: `store_dependency_map`
- **Details**: Persist dependency map
  - Format graph as JSON
  - Store in notes table
  - Generate visualization data
  - Create DOT format for graphviz
  - Log map generation
- **Result**: Dependency map stored

**Fallback**: `log_dependency_status`
- **Details**: No dependencies found
  - Log absence of dependencies
  - Return empty graph
  - Suggest dependency creation
- **Result**: Status logged

---

## Examples

### ✅ Compliant Usage

**Generate Function Dependency Graph (Compliant):**

```python
def generate_function_dependency_graph() -> Result[DependencyGraph, str]:
    """Generate function call dependency graph.

    Returns:
        Ok with dependency graph or Err if generation failed
    """
    return pipe(
        query_all_functions,
        lambda functions: query_function_interactions(functions),
        lambda interactions: build_function_graph(functions, interactions),
        lambda graph: add_function_metadata(graph),
        lambda graph: calculate_graph_metrics(graph),
        lambda graph: store_dependency_map(graph, "function"),
        lambda graph: Ok(graph)
    ).or_else(lambda err: Err(f"Graph generation failed: {err}"))

# ✅ Complete pipeline
# ✅ Metadata included
# ✅ Metrics calculated
# ✅ Persisted for future use
```

**Why Compliant**:
- Functional pipeline
- Complete metadata
- Error handling
- Persistence

---

**Build Dependency Graph Structure (Compliant):**

```python
@dataclass
class DependencyGraph:
    """Dependency graph structure."""
    nodes: list[Node]
    edges: list[Edge]
    metadata: dict

@dataclass
class Node:
    """Graph node."""
    id: str
    name: str
    type: str
    metadata: dict

@dataclass
class Edge:
    """Graph edge."""
    source: str
    target: str
    type: str
    metadata: dict

def build_function_graph(
    functions: list[Function],
    interactions: list[Interaction]
) -> DependencyGraph:
    """Build function dependency graph.

    Args:
        functions: List of all functions
        interactions: List of function calls

    Returns:
        Dependency graph structure
    """
    nodes = [
        Node(
            id=f"func_{f.id}",
            name=f.name,
            type="function",
            metadata={
                "purity_level": f.purity_level,
                "return_type": f.return_type,
                "file_id": f.file_id
            }
        )
        for f in functions
    ]

    edges = [
        Edge(
            source=f"func_{i.caller_id}",
            target=f"func_{i.callee_id}",
            type="calls",
            metadata={"call_count": i.count}
        )
        for i in interactions
    ]

    return DependencyGraph(
        nodes=nodes,
        edges=edges,
        metadata={
            "total_functions": len(functions),
            "total_calls": len(interactions),
            "generated_at": timestamp()
        }
    )

# ✅ Structured data types
# ✅ Complete metadata
# ✅ Pure function
# ✅ Immutable structures
```

**Why Compliant**:
- Proper data structures
- Pure function
- Complete metadata
- Type safety

---

**Detect Circular Dependencies (Compliant):**

```python
def detect_circular_dependencies(
    graph: DependencyGraph
) -> Result[list[list[str]], str]:
    """Detect circular dependencies in graph.

    Args:
        graph: Dependency graph to analyze

    Returns:
        Ok with list of cycles or Err if detection failed
    """
    # Use depth-first search to find cycles
    def find_cycles(node: str, visited: set, path: list) -> list[list[str]]:
        if node in path:
            # Cycle detected
            cycle_start = path.index(node)
            return [path[cycle_start:]]

        if node in visited:
            return []

        visited.add(node)
        path.append(node)

        # Get outgoing edges
        outgoing = [e for e in graph.edges if e.source == node]

        cycles = []
        for edge in outgoing:
            cycles.extend(find_cycles(edge.target, visited, path.copy()))

        return cycles

    all_cycles = []
    visited = set()

    for node in graph.nodes:
        cycles = find_cycles(node.id, visited, [])
        all_cycles.extend(cycles)

    return Ok(all_cycles)

# ✅ Pure algorithm
# ✅ Immutable data structures
# ✅ Complete cycle detection
# ✅ Result type
```

**Why Compliant**:
- Pure algorithm
- Immutable data
- Result type
- Complete detection

---

### ❌ Non-Compliant Code

**Build Graph Without Metadata (Violation):**

```python
# ❌ VIOLATION: Graph without metadata
def quick_graph(functions, interactions):
    graph = {"nodes": [], "edges": []}

    for f in functions:
        graph["nodes"].append({"id": f.id, "name": f.name})

    for i in interactions:
        graph["edges"].append({"from": i.caller_id, "to": i.callee_id})

    return graph

# Problem:
# - No metadata included
# - Mutable dict structure
# - No type information
# - Missing graph metrics
# - No error handling
```

**Why Non-Compliant**:
- Missing metadata
- Mutable structures
- No types
- No metrics

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete graph with metadata
def build_complete_graph(
    functions: list[Function],
    interactions: list[Interaction]
) -> Result[DependencyGraph, str]:
    """Build complete dependency graph with metadata.

    Args:
        functions: List of functions
        interactions: List of interactions

    Returns:
        Ok with complete graph or Err if build failed
    """
    return pipe(
        lambda: create_nodes_with_metadata(functions),
        lambda nodes: create_edges_with_metadata(interactions),
        lambda edges: DependencyGraph(
            nodes=nodes,
            edges=edges,
            metadata=calculate_graph_metrics(nodes, edges)
        ),
        lambda graph: Ok(graph)
    ).or_else(lambda err: Err(f"Graph build failed: {err}"))

# Complete metadata
# Immutable types
# Error handling
# Metrics included
```

---

**Mutating Graph During Analysis (Violation):**

```python
# ❌ VIOLATION: Mutating graph structure during analysis
def analyze_graph(graph):
    # Mutating original graph
    for node in graph["nodes"]:
        node["analyzed"] = True
        node["fan_in"] = count_incoming(node)

    return graph

# Problem:
# - Mutates original graph
# - Side effect during analysis
# - No new graph returned
# - Not pure
```

**Why Non-Compliant**:
- Mutates input
- Side effects
- Not pure
- Modifies original data

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Pure analysis with new graph
def analyze_graph_pure(
    graph: DependencyGraph
) -> DependencyGraph:
    """Analyze graph and return new graph with analysis data.

    Args:
        graph: Original dependency graph

    Returns:
        New graph with analysis metadata
    """
    analyzed_nodes = [
        Node(
            id=node.id,
            name=node.name,
            type=node.type,
            metadata={
                **node.metadata,
                "analyzed": True,
                "fan_in": count_incoming_edges(node, graph.edges),
                "fan_out": count_outgoing_edges(node, graph.edges)
            }
        )
        for node in graph.nodes
    ]

    return DependencyGraph(
        nodes=analyzed_nodes,
        edges=graph.edges,
        metadata={
            **graph.metadata,
            "analyzed_at": timestamp()
        }
    )

# ✅ Pure function
# ✅ New graph returned
# ✅ Original unchanged
# ✅ Complete analysis
```

---

## Edge Cases

### Edge Case 1: Circular Dependencies

**Issue**: Graph contains circular dependencies

**Handling**:
```python
def handle_circular_deps(
    graph: DependencyGraph
) -> Result[DependencyGraph, str]:
    """Handle circular dependencies in graph.

    Args:
        graph: Dependency graph to check

    Returns:
        Ok with graph (annotated with cycles) or Err if critical cycle
    """
    cycles = detect_circular_dependencies(graph)

    if cycles.is_err():
        return Err("Cycle detection failed")

    if len(cycles.unwrap()) > 0:
        # Annotate graph with cycle information
        annotated_graph = annotate_with_cycles(graph, cycles.unwrap())
        return Ok(annotated_graph)

    return Ok(graph)

# Detect and annotate cycles
```

**Directive Action**: Detect circular dependencies and annotate graph.

---

### Edge Case 2: Large Graph

**Issue**: Graph too large to visualize or process

**Handling**:
```python
def handle_large_graph(
    graph: DependencyGraph
) -> DependencyGraph:
    """Handle large graph by creating summary.

    Args:
        graph: Large dependency graph

    Returns:
        Summarized graph
    """
    if len(graph.nodes) > 1000:
        # Create summary graph
        return create_summary_graph(graph)
    else:
        return graph

# Summarize large graphs
```

**Directive Action**: Create summary view for large graphs.

---

## Related Directives

- **Depends On**:
  - `project_dependency_sync` - Sync before mapping
  - `fp_call_graph_generation` - Function-level call graphs
- **Triggers**:
  - None
- **Called By**:
  - `project_dependency_sync` - After sync
  - `project_compliance_check` - For dependency analysis
  - `project_refactor_path` - For task dependencies
  - `aifp_status` - For current state
- **Escalates To**:
  - `project_user_referral` - If mapping fails

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive queries the following tables:

- **`functions`**: All function definitions
- **`interactions`**: Function call relationships
- **`files`**: File information
- **`file_dependencies`**: File import relationships
- **`tasks`**: Task definitions
- **`task_dependencies`**: Task prerequisites
- **`flows`**: Flow definitions
- **`flow_dependencies`**: Flow relationships

This directive updates:

- **`notes`**: Stores dependency map with `note_type = 'dependency_map'`

---

## Testing

How to verify this directive is working:

1. **Generate function graph**
   ```python
   graph = generate_function_dependency_graph()
   assert len(graph.nodes) > 0
   assert len(graph.edges) > 0
   ```

2. **Check for circular dependencies**
   ```python
   cycles = detect_circular_dependencies(graph)
   # Verify cycles detected if present
   ```

3. **Verify graph stored**
   ```sql
   SELECT content
   FROM notes
   WHERE note_type = 'dependency_map'
   ORDER BY created_at DESC
   LIMIT 1;
   ```

---

## Common Mistakes

- ❌ **Graph without metadata** - Include complete metadata
- ❌ **Mutating graph during analysis** - Create new graph
- ❌ **No circular dependency detection** - Always check for cycles
- ❌ **Missing graph metrics** - Calculate fan-in, fan-out, etc.
- ❌ **Not storing graph** - Persist for future reference

---

## Roadblocks and Resolutions

### Roadblock 1: missing_links
**Issue**: Functions or files not linked in database
**Resolution**: Rebuild function-to-task relationships using project_dependency_sync

### Roadblock 2: circular_dependencies
**Issue**: Circular dependencies detected in graph
**Resolution**: Annotate graph with cycle information, alert user

### Roadblock 3: large_graph
**Issue**: Graph too large to process or visualize
**Resolution**: Create summary graph with aggregated nodes

### Roadblock 4: query_failed
**Issue**: Database query failed
**Resolution**: Retry query, check database integrity

---

## References

None
---

*Part of AIFP v1.0 - Project directive for dependency mapping and visualization*
