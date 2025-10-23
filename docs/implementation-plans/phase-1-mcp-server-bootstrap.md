# AIFP MCP Server Implementation Plan
## Phase 1: Bootstrap and Foundation

**Version**: 1.0
**Created**: 2025-10-22
**Status**: Planning
**Target Completion**: 4-6 weeks

> **📋 Complete Project Overview**: See [overview-all-phases.md](./overview-all-phases.md) for the full implementation roadmap covering all 6 phases.

---

## Table of Contents

1. [Phase Context](#phase-context)
2. [Overview](#overview)
3. [Project Initialization](#project-initialization)
4. [Implementation Phases](#implementation-phases)
5. [Development vs Runtime Separation](#development-vs-runtime-separation)
6. [Testing Strategy](#testing-strategy)
7. [Success Criteria](#success-criteria)
8. [Risk Management](#risk-management)
9. [Next Phase](#next-phase)

---

## Phase Context

### Where This Fits

**Phase 1 of 6**: Foundation and Bootstrap

This phase establishes the foundational infrastructure for the AIFP MCP server. It is the **critical prerequisite** for all subsequent phases.

### Other Phases

- **Phase 2**: Directive System Expansion (6-8 weeks) - All FP & Project directives
- **Phase 3**: User Directive Automation (6-8 weeks) - User-defined automation system
- **Phase 4**: Advanced Features (4-6 weeks) - Git integration, analytics, optimization
- **Phase 5**: Packaging & Distribution (3-4 weeks) - PyPI release, documentation
- **Phase 6**: Community & Maintenance (Ongoing) - Community building, enhancements

See [overview-all-phases.md](./overview-all-phases.md) for complete details.

### Dependencies

**Prerequisites**: None (this is the foundation)

**Unlocks**:
- Phase 2 (Directive System)
- Phase 3 (User Directives)
- All subsequent phases

---

## Overview

### Purpose

Build the AIFP MCP server using functional programming principles, creating a meta-circular development environment where AIFP tracks its own development.

### Key Principles

1. **Pure FP Throughout**: All code follows FP directives (purity, immutability, explicit parameters)
2. **Meta-Circular Development**: Use `.aifp/` to track MCP server development
3. **Clear Separation**: Development `.aifp/` never interferes with user `.aifp-project/`
4. **Test-Driven**: Write tests before implementation
5. **Incremental Delivery**: Each phase produces working, tested code

### Technology Stack

**Core:**
- Python 3.11+
- MCP Python SDK (`mcp`)
- SQLite3 (built-in)

**FP Libraries:**
```python
dataclasses          # Immutable data structures (frozen=True)
typing              # Rigorous type hints
returns             # Result/Maybe monads for error handling
toolz               # Functional utilities (pipe, curry, compose)
```

**Testing:**
```python
pytest              # Testing framework
hypothesis          # Property-based testing
pytest-cov          # Coverage reporting
```

**Development:**
```python
ruff                # Fast linting and formatting
mypy                # Static type checking
pre-commit          # Git hooks for quality
```

---

## Project Initialization

### Step 1: Repository Setup

```bash
# Already in AIFP directory
cd /home/eveningb4dawn/Desktop/Projects/AIFP

# Initialize .aifp/ for meta-circular development
mkdir -p .aifp
touch .aifp/.gitkeep

# Create project structure
mkdir -p src/aifp/{core,database,helpers,directives,mcp_server,templates}
mkdir -p src/aifp/database/{schemas,queries,effects}
mkdir -p src/aifp/helpers/{mcp,project,preferences,user_directives}
mkdir -p src/aifp/directives/{fp,project,user_system}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p tests/unit/{helpers,directives,database}
mkdir -p tests/integration/{mcp_server,end_to_end}

# Create __init__.py files
touch src/aifp/__init__.py
touch src/aifp/core/__init__.py
touch src/aifp/database/__init__.py
touch src/aifp/helpers/__init__.py
touch src/aifp/directives/__init__.py
touch src/aifp/mcp_server/__init__.py
```

### Step 2: Python Project Configuration

**File: `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "aifp-mcp-server"
version = "0.1.0"
description = "AI Functional Procedural MCP server for database-driven FP development"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "AIFP Contributors"}
]
keywords = ["mcp", "functional-programming", "ai", "code-generation"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "mcp>=0.1.0",
    "returns>=0.22.0",
    "toolz>=0.12.0",
    "typing-extensions>=4.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "hypothesis>=6.92.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
]

[project.scripts]
aifp-server = "aifp.mcp_server.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
aifp = ["templates/*.sql", "templates/*.db"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src/aifp --cov-report=term-missing --cov-report=html"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "UP", "ANN", "B", "A", "C4", "DTZ", "T10", "ISC", "ICN", "PIE", "PT", "RET", "SIM", "ARG", "PTH", "ERA", "PL", "RUF"]
ignore = ["ANN101", "ANN102"]  # Ignore missing type annotations for self, cls

[tool.ruff.per-file-ignores]
"tests/*" = ["ANN", "PLR2004"]  # Allow magic values and missing annotations in tests
```

### Step 3: Development Environment

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### Step 4: Initialize AIFP Project Tracking

**Manually create `.aifp/project.db`** (will automate later):

```bash
# Copy schema
cp docs/db-schema/schemaExampleProject.sql .aifp/schema.sql

# Initialize database
sqlite3 .aifp/project.db < .aifp/schema.sql

# Insert project metadata
sqlite3 .aifp/project.db <<EOF
INSERT INTO project (name, purpose, goals_json, status, version)
VALUES (
    'AIFP-MCP-Server',
    'Build the AIFP MCP server using pure functional programming principles',
    '["Pure FP implementation", "Zero OOP", "Immutable data", "Explicit side effects", "Meta-circular development"]',
    'active',
    1
);
EOF
```

**Create `.aifp/ProjectBlueprint.md`**:

```markdown
# AIFP MCP Server - Project Blueprint

## Project Overview

**Name**: AIFP MCP Server
**Version**: 1.0
**Status**: Active (In Development)
**AIFP Compliance**: Strict

### Purpose

Build an MCP (Model Context Protocol) server that provides AI assistants with database-driven directives for functional programming and project management.

### Goals

1. Pure functional implementation (no OOP, no mutations)
2. Meta-circular development (AIFP building AIFP)
3. Immutable data structures throughout
4. Explicit side effect isolation
5. Comprehensive test coverage (>90%)

## Technical Architecture

### Language & Runtime

- Python 3.11+ (for improved type hints)
- Functional programming paradigm
- No classes except dataclasses (frozen=True)

### Core Technologies

- **MCP SDK**: Protocol implementation
- **SQLite3**: Database operations (pure query builders + effect isolation)
- **returns**: Result/Maybe monads for error handling
- **toolz**: Functional utilities (pipe, curry, compose)

### FP Patterns Used

1. **Immutable Data**: All dataclasses frozen
2. **Pure Functions**: Logic functions with no side effects
3. **Effect Isolation**: I/O confined to "effect" modules
4. **Monadic Error Handling**: Result types instead of exceptions
5. **Function Composition**: pipe/compose for data transformations

## Project Themes

1. **Database Operations** - Pure query builders + isolated effects
2. **Helper Functions** - 35 helpers organized by database
3. **Directive System** - FP + Project + User directive implementations
4. **MCP Server** - Protocol handlers and tool registration
5. **Testing Infrastructure** - Unit + integration + property-based tests

## Completion Path

### Stage 1: Foundation (Weeks 1-2)
- [x] Project initialization
- [ ] Database schemas and effects
- [ ] Core type definitions
- [ ] First helper function (get_all_directives)
- [ ] Testing infrastructure

### Stage 2: Core Helpers (Weeks 3-4)
- [ ] MCP database helpers (11 functions)
- [ ] Project database helpers (11 functions)
- [ ] Comprehensive test suites
- [ ] FP compliance verification

### Stage 3: MCP Server (Week 5)
- [ ] Server initialization
- [ ] Tool registration
- [ ] Prompt system
- [ ] Request handlers
- [ ] Integration tests

### Stage 4: Directives (Week 6+)
- [ ] aifp_run orchestrator
- [ ] aifp_status reporter
- [ ] project_init bootstrap
- [ ] Core FP directives
- [ ] End-to-end testing

## Development Notes

### Meta-Circular Development

This project uses `.aifp/` to track its own development. The `.aifp/` folder contains:
- `project.db` - Tracks files, functions, tasks, completion path
- `ProjectBlueprint.md` - This file

**IMPORTANT**: The development `.aifp/` is separate from user projects' `.aifp-project/`. Runtime path resolution always uses the user's working directory from MCP context.

### FP Compliance Checklist

Every function must satisfy:
- [ ] No mutations (all data frozen)
- [ ] No side effects in logic (effects isolated)
- [ ] Explicit parameters (no hidden state)
- [ ] Deterministic (same inputs → same outputs)
- [ ] Type hints on all parameters and return values
- [ ] Returns Result types for fallible operations

---

**Last Updated**: 2025-10-22
**Next Review**: After Stage 1 completion
```

---

## Implementation Phases

### Phase 1: Database Foundation (Week 1)

#### Milestone 1.1: Schema Creation and Initialization

**Deliverables:**
- `src/aifp/database/schemas/aifp_core.sql` (from schemaExampleMCP.sql)
- `src/aifp/database/schemas/project.sql` (from schemaExampleProject.sql)
- Database initialization scripts
- Schema validation tests

**Tasks:**

```markdown
1. Copy schema files to src/aifp/database/schemas/
   - [x] aifp_core.sql
   - [x] project.sql
   - [x] user_preferences.sql
   - [x] user_directives.sql

2. Create schema initialization module
   File: src/aifp/database/effects/init_schemas.py
   - [ ] create_aifp_core_db(db_path: Path) -> Result[None, str]
   - [ ] create_project_db(db_path: Path) -> Result[None, str]
   - [ ] validate_schema(db_path: Path, expected_tables: List[str]) -> Result[bool, str]

3. Populate aifp_core.db with directives
   File: src/aifp/database/effects/populate_directives.py
   - [ ] load_directives_from_json(json_files: List[Path]) -> List[DirectiveDict]
   - [ ] insert_directives(db_path: Path, directives: List[DirectiveDict]) -> Result[int, str]

4. Write tests
   File: tests/unit/database/test_init_schemas.py
   - [ ] test_create_aifp_core_db_creates_all_tables
   - [ ] test_create_project_db_creates_all_tables
   - [ ] test_validate_schema_detects_missing_tables
   - [ ] test_populate_directives_inserts_all_records
```

**FP Compliance:**
- ✅ All functions return Result types
- ✅ Schema files are data (pure)
- ✅ Side effects (DB writes) isolated in effect functions

**Success Criteria:**
- All tables created correctly
- Schema validation passes
- Tests cover all edge cases (missing file, existing db, etc.)
- No mutations, no exceptions (only Result types)

---

#### Milestone 1.2: Core Type Definitions

**Deliverables:**
- Immutable type definitions for all domain entities
- Result/Maybe type aliases
- Type validation tests

**Tasks:**

```markdown
1. Create core types module
   File: src/aifp/core/types.py

   Types to define:
   - [ ] Directive (frozen dataclass)
   - [ ] DirectiveWorkflow (frozen dataclass)
   - [ ] ProjectMetadata (frozen dataclass)
   - [ ] FileRecord (frozen dataclass)
   - [ ] FunctionRecord (frozen dataclass)
   - [ ] TaskRecord (frozen dataclass)
   - [ ] UserDirective (frozen dataclass)
   - [ ] DirectiveExecution (frozen dataclass)

2. Create result type aliases
   File: src/aifp/core/result.py

   - [ ] DatabaseResult[T] = Result[T, DatabaseError]
   - [ ] ValidationResult[T] = Result[T, ValidationError]
   - [ ] FileResult[T] = Result[T, FileError]
   - [ ] ParseResult[T] = Result[T, ParseError]

3. Write tests
   File: tests/unit/core/test_types.py
   - [ ] test_directive_is_immutable
   - [ ] test_directive_requires_all_fields
   - [ ] test_workflow_json_serialization
   - [ ] test_result_types_compose_correctly
```

**Example Implementation:**

```python
# src/aifp/core/types.py
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass(frozen=True)
class Directive:
    """Immutable directive representation."""
    id: int
    name: str
    type: str  # 'fp' or 'project'
    level: Optional[int]
    parent_directive: Optional[str]
    description: str
    workflow: Dict[str, Any]
    md_file_path: Optional[str]
    intent_keywords: List[str]
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime

    def is_fp_directive(self) -> bool:
        """Pure: Check if this is an FP directive."""
        return self.type == 'fp'

    def is_project_directive(self) -> bool:
        """Pure: Check if this is a project directive."""
        return self.type == 'project'

@dataclass(frozen=True)
class DirectiveWorkflow:
    """Immutable workflow representation."""
    trunk: str
    branches: List[Dict[str, Any]]
    error_handling: Dict[str, Any]

@dataclass(frozen=True)
class ProjectMetadata:
    """Immutable project metadata."""
    id: int
    name: str
    purpose: str
    goals: List[str]
    status: str
    version: int
    user_directives_status: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**FP Compliance:**
- ✅ All dataclasses frozen
- ✅ No mutable default arguments
- ✅ Methods are pure functions (no self-mutation)

---

#### Milestone 1.3: First Helper Function Implementation

**Deliverables:**
- Complete implementation of `get_all_directives()`
- Comprehensive test suite
- FP compliance verified

**Tasks:**

```markdown
1. Implement database effects
   File: src/aifp/database/effects/mcp_effects.py

   - [ ] execute_mcp_query(db_path: Path, query: str) -> DatabaseResult[List[Dict]]
   - [ ] get_mcp_connection(db_path: Path) -> DatabaseResult[Connection]
   - [ ] close_mcp_connection(conn: Connection) -> Result[None, str]

2. Implement pure query builders
   File: src/aifp/database/queries/mcp_queries.py

   - [ ] build_get_all_directives_query() -> str
   - [ ] build_get_directive_query(name: str) -> str
   - [ ] build_search_directives_query(keyword: str, category: Optional[str]) -> str

3. Implement pure row parsers
   File: src/aifp/database/queries/mcp_queries.py

   - [ ] parse_directive_row(row: Dict) -> Directive
   - [ ] parse_directive_rows(rows: List[Dict]) -> List[Directive]

4. Implement helper function
   File: src/aifp/helpers/mcp/get_all_directives.py

   - [ ] get_all_directives(db_path: Path) -> DatabaseResult[List[Directive]]

5. Write comprehensive tests
   File: tests/unit/helpers/mcp/test_get_all_directives.py

   - [ ] test_get_all_directives_returns_all_directives
   - [ ] test_get_all_directives_returns_immutable_objects
   - [ ] test_get_all_directives_handles_missing_db
   - [ ] test_get_all_directives_handles_corrupted_db
   - [ ] test_get_all_directives_parses_workflow_json
   - [ ] test_directive_types_correctly_identified

6. Write integration tests
   File: tests/integration/test_get_all_directives.py

   - [ ] test_get_all_directives_with_real_db
   - [ ] test_returns_correct_count_of_directives
```

**Example Implementation:**

```python
# src/aifp/database/queries/mcp_queries.py
from typing import Dict, List
from src.aifp.core.types import Directive
import json
from datetime import datetime

def build_get_all_directives_query() -> str:
    """
    Pure function: Build SQL query to fetch all directives.

    Returns:
        SQL query string
    """
    return """
        SELECT
            id, name, type, level, parent_directive,
            description, workflow, md_file_path,
            intent_keywords_json, confidence_threshold,
            created_at, updated_at
        FROM directives
        ORDER BY type, level, name
    """

def parse_directive_row(row: Dict) -> Directive:
    """
    Pure function: Parse database row into Directive object.

    Args:
        row: Database row as dictionary

    Returns:
        Immutable Directive object
    """
    return Directive(
        id=row['id'],
        name=row['name'],
        type=row['type'],
        level=row['level'],
        parent_directive=row['parent_directive'],
        description=row['description'],
        workflow=json.loads(row['workflow']),
        md_file_path=row['md_file_path'],
        intent_keywords=json.loads(row['intent_keywords_json']) if row['intent_keywords_json'] else [],
        confidence_threshold=row['confidence_threshold'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at'])
    )

# src/aifp/helpers/mcp/get_all_directives.py
from pathlib import Path
from typing import List
from returns.result import Result
from toolz import pipe

from src.aifp.core.types import Directive
from src.aifp.database.effects.mcp_effects import execute_mcp_query
from src.aifp.database.queries.mcp_queries import (
    build_get_all_directives_query,
    parse_directive_row
)

def get_all_directives(db_path: Path) -> Result[List[Directive], str]:
    """
    Get all directives from aifp_core.db.

    Composes pure functions with effects:
    1. Build query (pure)
    2. Execute query (effect)
    3. Parse rows (pure)

    Args:
        db_path: Path to aifp_core.db

    Returns:
        Result[List[Directive], str]: Success with directives or Failure with error
    """
    query = build_get_all_directives_query()  # Pure
    result = execute_mcp_query(db_path, query)  # Effect

    # Pure transformation on Result
    return result.map(lambda rows: [parse_directive_row(row) for row in rows])
```

**FP Compliance Verification:**

```python
# tests/unit/helpers/mcp/test_get_all_directives.py
import pytest
from dataclasses import FrozenInstanceError
from pathlib import Path

def test_directive_is_immutable(test_db_with_directives):
    """Verify returned directives are truly immutable."""
    result = get_all_directives(test_db_with_directives)

    assert result.is_success()
    directives = result.unwrap()

    directive = directives[0]

    # Attempt mutation should fail
    with pytest.raises(FrozenInstanceError):
        directive.name = "modified"

    with pytest.raises(FrozenInstanceError):
        directive.level = 99

def test_get_all_directives_is_deterministic(test_db_with_directives):
    """Verify function is deterministic (same inputs → same outputs)."""
    result1 = get_all_directives(test_db_with_directives)
    result2 = get_all_directives(test_db_with_directives)

    assert result1.unwrap() == result2.unwrap()

def test_get_all_directives_has_no_side_effects(test_db_with_directives):
    """Verify function has no side effects (db unchanged after call)."""
    # Get initial state
    initial_result = get_all_directives(test_db_with_directives)
    initial_count = len(initial_result.unwrap())

    # Call function multiple times
    for _ in range(10):
        get_all_directives(test_db_with_directives)

    # Verify state unchanged
    final_result = get_all_directives(test_db_with_directives)
    final_count = len(final_result.unwrap())

    assert initial_count == final_count
```

**Success Criteria:**
- ✅ Function returns Result type
- ✅ All directives retrieved correctly
- ✅ Objects are immutable (FrozenInstanceError on mutation)
- ✅ Function is deterministic
- ✅ No side effects on database
- ✅ Test coverage > 95%

---

### Phase 2: Core Helpers (Weeks 2-3)

#### Milestone 2.1: MCP Database Helpers (11 functions)

**Priority Order:**

1. ✅ `get_all_directives()` - Already implemented in Phase 1
2. `get_directive(name)` - Single directive lookup
3. `search_directives(keyword, category, type)` - Filtered search
4. `find_directive_by_intent(user_request, threshold)` - Intent matching
5. `query_mcp_db(sql)` - Advanced queries (use as last resort)

**Implementation Pattern (Repeat for Each):**

```markdown
For each helper function:

1. [ ] Write type signature and docstring
2. [ ] Implement pure query builder
3. [ ] Implement pure response parser
4. [ ] Compose with effects
5. [ ] Write unit tests (>95% coverage)
6. [ ] Write integration test with real DB
7. [ ] Verify FP compliance checklist
8. [ ] Update .aifp/project.db (track in functions table)
```

---

#### Milestone 2.2: Project Database Helpers (11 functions)

**Priority Order:**

1. `init_project_db()` - Critical for project initialization
2. `get_project_status()` - Used by almost all directives
3. `get_project_context()` - Session initialization
4. `get_project_files()` - File tracking
5. `get_project_functions()` - Function tracking
6. `get_project_tasks()` - Task management
7. `get_status_tree()` - Hierarchical status (complex)
8. `create_project_blueprint()` - Blueprint generation
9. `read_project_blueprint()` - Blueprint parsing
10. `update_project_blueprint_section()` - Blueprint updates
11. `query_project_db()` - Advanced queries

**Special Considerations:**

- These functions create/modify user project databases
- Must always use user's working directory from MCP context
- Never access MCP server's own `.aifp/` at runtime

**Example Path Resolution:**

```python
# src/aifp/helpers/project/init_project_db.py
from pathlib import Path
from returns.result import Result

def init_project_db(
    user_working_dir: Path,
    name: str,
    purpose: str,
    goals: List[str]
) -> Result[Path, str]:
    """
    Initialize project.db in USER's project directory.

    Args:
        user_working_dir: User's working directory (from MCP context)
        name: Project name
        purpose: Project purpose
        goals: Project goals

    Returns:
        Result[Path, str]: Path to created project.db or error
    """
    # Always resolve relative to USER's directory
    aifp_dir = user_working_dir / ".aifp-project"
    project_db_path = aifp_dir / "project.db"

    # Create directory
    aifp_dir.mkdir(parents=True, exist_ok=True)

    # Create and populate database (effect)
    result = create_database_from_schema(
        project_db_path,
        schema_path=Path(__file__).parent.parent / "database" / "schemas" / "project.sql"
    )

    if result.is_failure():
        return result

    # Insert project metadata (effect)
    return insert_project_metadata(project_db_path, name, purpose, goals).map(
        lambda _: project_db_path
    )
```

---

### Phase 3: MCP Server Framework (Week 4)

#### Milestone 3.1: Basic MCP Server

**Deliverables:**
- MCP server initialization
- Tool registration system
- Prompt registration system
- Request handler framework

**Tasks:**

```markdown
1. Implement server initialization
   File: src/aifp/mcp_server/server.py

   - [ ] create_aifp_server() -> Server
   - [ ] register_tools(server: Server) -> None
   - [ ] register_prompts(server: Server) -> None
   - [ ] start_server(server: Server) -> None

2. Implement tool definitions (pure configuration)
   File: src/aifp/mcp_server/tools.py

   - [ ] TOOL_DEFINITIONS: List[ToolDefinition] (immutable config)
   - [ ] tool_aifp_run
   - [ ] tool_get_all_directives
   - [ ] tool_get_project_status
   - [ ] tool_query_project_db

3. Implement request handlers (effect boundary)
   File: src/aifp/mcp_server/handlers.py

   - [ ] handle_tool_call(tool_name, args, context) -> Result[Any, str]
   - [ ] handle_prompt_request(prompt_name, args, context) -> Result[str, str]
   - [ ] extract_user_working_dir(context) -> Path

4. Write integration tests
   File: tests/integration/mcp_server/test_server.py

   - [ ] test_server_starts_successfully
   - [ ] test_tool_registration_complete
   - [ ] test_tool_invocation_routes_correctly
   - [ ] test_context_provides_user_working_dir
```

**Key Pattern: Effect Boundary**

```python
# src/aifp/mcp_server/handlers.py
from pathlib import Path
from typing import Any, Dict
from returns.result import Result, Success, Failure

def extract_user_working_dir(context: Dict[str, Any]) -> Result[Path, str]:
    """
    Pure function: Extract user's working directory from MCP context.

    Args:
        context: MCP request context

    Returns:
        Result[Path, str]: User's working directory or error
    """
    working_dir = context.get("working_directory")

    if not working_dir:
        return Failure("MCP context missing working_directory")

    return Success(Path(working_dir))

async def handle_tool_call(
    tool_name: str,
    arguments: Dict[str, Any],
    context: Dict[str, Any]
) -> Result[Any, str]:
    """
    Effect boundary: Handle tool invocation from AI.

    Args:
        tool_name: Tool being invoked
        arguments: Tool arguments from AI
        context: MCP request context

    Returns:
        Result with tool output or error
    """
    # Extract user's working directory (pure)
    user_dir_result = extract_user_working_dir(context)

    if user_dir_result.is_failure():
        return user_dir_result

    user_working_dir = user_dir_result.unwrap()

    # Route to appropriate handler (effect)
    if tool_name == "get_all_directives":
        aifp_core_db = user_working_dir / ".aifp-project" / "aifp_core.db"
        return get_all_directives(aifp_core_db)

    elif tool_name == "get_project_status":
        return get_project_status(user_working_dir)

    else:
        return Failure(f"Unknown tool: {tool_name}")
```

---

### Phase 4: Core Directives (Week 5-6)

#### Milestone 4.1: Essential Directives

**Priority Order:**

1. `aifp_status` - Simplest, read-only, good starting point
2. `project_init` - Critical for bootstrapping
3. `aifp_run` - Orchestrator, complex
4. `project_file_write` - Core functionality

**Implementation Pattern:**

```markdown
For each directive:

1. [ ] Read directive definition from JSON
2. [ ] Parse workflow (trunk → branches → fallback)
3. [ ] Implement workflow executor
4. [ ] Map workflow steps to helper function calls
5. [ ] Handle error paths
6. [ ] Write tests for all workflow branches
7. [ ] Integration test with MCP server
```

---

## Development vs Runtime Separation

### Critical Distinction

**Development Time:**
```
AIFP/
├── .aifp/                          # MCP server's own project tracking
│   ├── project.db                  # Tracks MCP server development
│   └── ProjectBlueprint.md         # MCP server blueprint
├── src/aifp/                       # MCP server source code
└── tests/                          # Test suite
```

**Runtime (User Projects):**
```
user-project/
├── .aifp-project/                  # User's project tracking
│   ├── project.db                  # User's project state
│   ├── user_preferences.db
│   ├── user_directives.db
│   └── aifp_core.db                # Copied from MCP templates
├── src/                            # User's code
└── (MCP server runs as external process)
```

### Path Resolution Rules

**Rule 1: Never Hardcode Paths**

```python
# ❌ WRONG - Hardcoded path
def get_project_status():
    project_db = Path(".aifp/project.db")  # This is MCP server's db!
    ...

# ✅ CORRECT - Always accept user's working directory
def get_project_status(user_working_dir: Path) -> Result[ProjectStatus, str]:
    project_db = user_working_dir / ".aifp-project" / "project.db"  # User's db
    ...
```

**Rule 2: MCP Context is Source of Truth**

```python
# All tool handlers receive context
async def handle_tool_call(tool_name: str, args: dict, context: dict):
    # Extract user's working directory from MCP context
    user_dir = Path(context["working_directory"])

    # ALL operations relative to user's directory
    result = some_helper_function(user_dir, **args)
    ...
```

**Rule 3: Templates are Static Data**

```python
# MCP server contains templates
TEMPLATES_DIR = Path(__file__).parent / "templates"

# When user initializes project, COPY template to their directory
def init_project(user_working_dir: Path):
    user_aifp_dir = user_working_dir / ".aifp-project"

    # Copy template aifp_core.db to user's project
    shutil.copy(
        TEMPLATES_DIR / "aifp_core.db",
        user_aifp_dir / "aifp_core.db"
    )
```

### Testing Path Separation

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_user_project(tmp_path):
    """Create temporary user project for testing."""
    user_project_dir = tmp_path / "user_project"
    user_project_dir.mkdir()

    # User's .aifp-project directory
    aifp_dir = user_project_dir / ".aifp-project"
    aifp_dir.mkdir()

    # Initialize user's databases
    init_test_databases(aifp_dir)

    return user_project_dir

def test_helper_uses_user_directory(temp_user_project):
    """Verify helper operates on user's directory, not MCP server's."""
    result = get_project_status(temp_user_project)

    assert result.is_success()
    status = result.unwrap()

    # Verify we read from user's db
    assert ".aifp-project" in str(status.db_path)
    assert str(temp_user_project) in str(status.db_path)
```

---

## Testing Strategy

### Test Pyramid

```
           /\
          /  \  E2E Tests (5%)
         /____\
        /      \  Integration Tests (20%)
       /________\
      /          \  Unit Tests (75%)
     /____________\
```

### Test Categories

#### 1. Unit Tests (75% of tests)

**Focus**: Pure functions, immutability, determinism

```python
# tests/unit/core/test_types.py
def test_directive_is_immutable():
    """Verify Directive objects cannot be mutated."""
    directive = Directive(...)

    with pytest.raises(FrozenInstanceError):
        directive.name = "changed"

# tests/unit/database/queries/test_mcp_queries.py
def test_build_get_all_directives_query_is_pure():
    """Verify query builder is deterministic."""
    query1 = build_get_all_directives_query()
    query2 = build_get_all_directives_query()

    assert query1 == query2

def test_parse_directive_row_handles_missing_fields():
    """Verify parser handles incomplete data gracefully."""
    row = {"id": 1, "name": "test"}  # Missing required fields

    with pytest.raises(KeyError):
        parse_directive_row(row)
```

#### 2. Integration Tests (20% of tests)

**Focus**: Database interactions, helper function composition

```python
# tests/integration/helpers/test_get_all_directives.py
def test_get_all_directives_with_real_database(real_aifp_core_db):
    """Test with actual populated database."""
    result = get_all_directives(real_aifp_core_db)

    assert result.is_success()
    directives = result.unwrap()

    # Verify we got all expected directives
    assert len(directives) >= 89

    # Verify structure
    assert all(isinstance(d, Directive) for d in directives)

def test_init_project_db_creates_all_tables(tmp_path):
    """Test project initialization creates complete schema."""
    result = init_project_db(
        user_working_dir=tmp_path,
        name="TestProject",
        purpose="Testing",
        goals=["Test goal"]
    )

    assert result.is_success()
    project_db_path = result.unwrap()

    # Verify all tables exist
    conn = sqlite3.connect(project_db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        "project", "files", "functions", "tasks",
        "milestones", "completion_path", "notes"
    ]

    for table in expected_tables:
        assert table in tables
```

#### 3. Property-Based Tests (Using Hypothesis)

**Focus**: Invariants, edge cases, random inputs

```python
# tests/unit/core/test_types_properties.py
from hypothesis import given
from hypothesis import strategies as st

@given(
    name=st.text(min_size=1, max_size=100),
    type_str=st.sampled_from(['fp', 'project']),
    level=st.one_of(st.none(), st.integers(min_value=0, max_value=4))
)
def test_directive_creation_never_mutates(name, type_str, level):
    """Property: Creating directives never causes mutations."""
    directive1 = Directive(
        id=1, name=name, type=type_str, level=level,
        description="test", workflow={}, ...
    )

    directive2 = Directive(
        id=1, name=name, type=type_str, level=level,
        description="test", workflow={}, ...
    )

    # Same inputs → same objects (deterministic)
    assert directive1 == directive2
```

#### 4. End-to-End Tests (5% of tests)

**Focus**: Full MCP server workflows

```python
# tests/integration/end_to_end/test_project_initialization.py
async def test_complete_project_init_workflow(mcp_test_client, tmp_path):
    """Test complete project initialization via MCP."""
    # Simulate AI calling project_init tool
    response = await mcp_test_client.call_tool(
        tool_name="project_init",
        arguments={
            "name": "TestProject",
            "purpose": "E2E test",
            "goals": ["goal1", "goal2"]
        },
        context={
            "working_directory": str(tmp_path)
        }
    )

    assert response.is_success()

    # Verify project structure created
    aifp_dir = tmp_path / ".aifp-project"
    assert aifp_dir.exists()
    assert (aifp_dir / "project.db").exists()
    assert (aifp_dir / "ProjectBlueprint.md").exists()

    # Verify project metadata
    status_response = await mcp_test_client.call_tool(
        tool_name="get_project_status",
        arguments={},
        context={"working_directory": str(tmp_path)}
    )

    status = status_response.unwrap()
    assert status["initialized"] == True
    assert status["project_name"] == "TestProject"
```

### Test Coverage Goals

- **Overall**: >90%
- **Pure functions**: 100%
- **Effect functions**: >85%
- **Error paths**: >80%

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run linting
        run: |
          ruff check src/ tests/

      - name: Run type checking
        run: |
          mypy src/

      - name: Run tests
        run: |
          pytest --cov=src/aifp --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Success Criteria

### Phase 1 Complete When:

- ✅ All database schemas created and validated
- ✅ Core types defined (immutable, type-hinted)
- ✅ First helper (`get_all_directives`) implemented and tested
- ✅ Test coverage >95% for implemented code
- ✅ FP compliance verified (no mutations, pure functions, explicit side effects)
- ✅ `.aifp/project.db` tracking MCP server development

### Phase 2 Complete When:

- ✅ All 11 MCP database helpers implemented
- ✅ All 11 Project database helpers implemented
- ✅ Each helper has comprehensive test suite
- ✅ Integration tests pass with real databases
- ✅ Path separation verified (dev `.aifp/` vs user `.aifp-project/`)

### Phase 3 Complete When:

- ✅ MCP server starts and accepts connections
- ✅ Tools registered and invocable
- ✅ Context provides user working directory
- ✅ Integration tests demonstrate tool invocation

### Phase 4 Complete When:

- ✅ Core directives implemented (`aifp_run`, `aifp_status`, `project_init`)
- ✅ Directive workflow execution functional
- ✅ End-to-end tests pass
- ✅ User can initialize AIFP project via MCP

---

## Risk Management

### Risk 1: Path Confusion (Dev vs User)

**Risk**: Helper functions accidentally access MCP server's `.aifp/` instead of user's `.aifp-project/`

**Mitigation**:
- ✅ All helpers require `user_working_dir` parameter
- ✅ No hardcoded paths
- ✅ Integration tests verify path resolution
- ✅ Code review checklist includes path verification

**Test Coverage**:
```python
def test_helper_never_accesses_dev_aifp_folder(temp_user_project):
    """Verify helpers never touch MCP server's .aifp/ folder."""
    with patch('pathlib.Path') as mock_path:
        # Make .aifp/ inaccessible
        mock_path.return_value = Path("/forbidden/.aifp")

        # Helper should still work with user's directory
        result = get_project_status(temp_user_project)
        assert result.is_success()
```

### Risk 2: Mutation Leakage

**Risk**: Accidentally introducing mutable state

**Mitigation**:
- ✅ All dataclasses frozen
- ✅ Pre-commit hook runs mypy with strict mode
- ✅ Property-based tests verify immutability
- ✅ Code review checklist includes mutation check

**Detection**:
```python
# pre-commit hook
ruff check --select=FBT003  # Detect mutable default arguments
mypy --strict                # Strict type checking
```

### Risk 3: Side Effect Leakage

**Risk**: Side effects in functions marked as pure

**Mitigation**:
- ✅ Naming convention: `*_effect.py` for effect functions
- ✅ Unit tests verify determinism
- ✅ Integration tests run functions multiple times, verify no state change
- ✅ Code review checklist

**Test Pattern**:
```python
def test_function_is_pure_deterministic(input_data):
    """Verify function is deterministic."""
    result1 = pure_function(input_data)
    result2 = pure_function(input_data)
    assert result1 == result2

def test_function_has_no_side_effects(db_path):
    """Verify function doesn't modify database."""
    initial_state = get_db_state(db_path)

    pure_function(db_path)

    final_state = get_db_state(db_path)
    assert initial_state == final_state
```

### Risk 4: Test Coverage Gaps

**Risk**: Missing edge cases, incomplete error handling tests

**Mitigation**:
- ✅ Mandatory test writing before implementation (TDD)
- ✅ Coverage gates in CI (fail if <90%)
- ✅ Property-based testing for invariants
- ✅ Mutation testing (using `mutmut`)

```bash
# Add to CI pipeline
mutmut run --paths-to-mutate=src/aifp
# Verify tests catch introduced mutations
```

---

## Next Steps

### Immediate Actions (This Week)

1. ✅ Create project structure
2. ✅ Set up `pyproject.toml`
3. ✅ Initialize virtual environment
4. ✅ Install dependencies
5. ✅ Initialize `.aifp/project.db` (manually for now)
6. ✅ Create `.aifp/ProjectBlueprint.md`
7. [ ] Copy schema files to `src/aifp/database/schemas/`
8. [ ] Implement first helper: `get_all_directives()`
9. [ ] Write comprehensive tests
10. [ ] Commit and push to Git

### Week 1 Deliverable

**Goal**: Working foundation with one complete helper function

**Acceptance Criteria**:
- Database schemas in place
- Core types defined and tested
- `get_all_directives()` fully implemented
- Test coverage >95%
- All tests passing
- FP compliance verified

---

## Appendix: Development Checklist Template

Use this checklist for **every new function**:

```markdown
## Function: [function_name]

### Planning
- [ ] Type signature defined
- [ ] Docstring written
- [ ] Pure vs effect function identified
- [ ] Dependencies identified

### Implementation
- [ ] Pure logic implemented
- [ ] Effect wrapper implemented (if needed)
- [ ] Type hints on all parameters
- [ ] Returns Result type for fallible operations
- [ ] No mutations
- [ ] No hidden state

### Testing
- [ ] Unit test: happy path
- [ ] Unit test: error paths
- [ ] Unit test: edge cases
- [ ] Integration test (if applicable)
- [ ] Property test (if applicable)
- [ ] Test coverage >95%

### FP Compliance
- [ ] Pure function (deterministic)
- [ ] Immutable data structures
- [ ] Explicit parameters
- [ ] Side effects isolated
- [ ] Type hints complete

### Documentation
- [ ] Function documented in helper-functions-reference.md
- [ ] Added to project.db functions table
- [ ] Code review completed
```

---

## Next Phase

Upon completion of Phase 1, proceed to:

**Phase 2: Directive System Expansion**
- Plan: [phase-2-directive-system.md](./phase-2-directive-system.md) *(to be created)*
- Focus: Implement all 60 FP directives + 22 Project directives
- Duration: 6-8 weeks
- Prerequisites: Phase 1 complete

See [overview-all-phases.md](./overview-all-phases.md) for the complete roadmap.

---

**Version**: 1.0
**Last Updated**: 2025-10-22
**Next Review**: After Phase 1 completion
