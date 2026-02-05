# Session Changes — 2026-02-05

## Context
Working on MCP_IMPLEMENTATION_PLAN.md Milestone 1: Package Foundation + Minimal Server.
Dogfooding AIFP by tracking all new files in `.aifp/project.db`.

---

## Files Created This Session

### 1. `pyproject.toml` (project root)
- Tracked in project.db as file ID **201**, `id_in_name=0`, `is_reserved=0`
- Package config: name=aifp, version=0.1.0, requires-python>=3.11
- Single runtime dependency: `mcp>=1.26.0`
- Dev deps: pytest, ruff, mypy, hypothesis

### 2. `src/aifp/__init__.py`
- Tracked in project.db as file ID **202**, `id_in_name=0`, `is_reserved=0`
- Package docstring + `__version__ = "0.1.0"`

### 3. `src/aifp/__main__.py`
- Tracked in project.db as file ID **203**, `id_in_name=0`, `is_reserved=0`
- Entry point: `from .mcp_server import run_server` → `run_server()`
- **NOTE**: `main()` function record NOT YET inserted into project.db — blocked by UNIQUE constraint on `functions.name` (conflicts with watchdog's `main` at file 148, function ID 34). This is the trigger for the UNIQUE_CONSTRAINT_PLAN.

### 4. `docs/MCP/UNIQUE_CONSTRAINT_PLAN.md`
- Implementation plan for relaxing UNIQUE constraints on functions/types tables
- NOT tracked in project.db (documentation file)

---

## Database Changes (`.aifp/project.db`)

### Fixed stale paths (3 files):
| File ID | Old Path | New Path |
|---------|----------|----------|
| 190 | `src/aifp/helpers/global/__init__.py` | `src/aifp/helpers/shared/__init__.py` |
| 191 | `src/aifp/helpers/global/database_info.py` | `src/aifp/helpers/shared/database_info.py` |
| 192 | `src/aifp/helpers/global/supportive_context.py` | `src/aifp/helpers/shared/supportive_context.py` |

### Inserted new file records:
| File ID | Name | Path | id_in_name |
|---------|------|------|------------|
| 201 | pyproject.toml | pyproject.toml | 0 |
| 202 | __init__.py | src/aifp/__init__.py | 0 |
| 203 | __main__.py | src/aifp/__main__.py | 0 |

### Functions inserted for new files:
- **File 203 (`__main__.py`)**: `main()` — **BLOCKED** by UNIQUE constraint. Pending UNIQUE_CONSTRAINT_PLAN execution.
- Files 201 and 202 have no functions to track.

### DB state after session:
- 203 files, 289 functions, 0 types
- No completion path/milestones/tasks set up yet
- No project metadata row yet

---

## Decisions Made

1. **`skip_id_naming=True`** for all new AIFP package files — this is a distributable package, not a user project. All 203 files have `id_in_name=0`.

2. **`skip_id_naming=False` stays as DEFAULT** for user projects — ID embedding is the core feature for AI-maintained codebases with thousands of files.

3. **UNIQUE constraint change approved**: `UNIQUE(name)` → `UNIQUE(name, file_id)` for both functions and types tables. Files table keeps `UNIQUE(path)` unchanged (path includes filename).

4. **Getter changes approved**: `get_function_by_name` and `get_file_by_name` must return lists. Function/type query results must include file data (file_name, file_path) via JOIN.

---

## What's Next (not started)

1. Execute UNIQUE_CONSTRAINT_PLAN.md (13 steps)
2. After constraint fix, insert `main()` for file 203
3. Continue Milestone 1 steps 4-11:
   - `src/aifp/wrappers/mcp_sdk.py`
   - `src/aifp/mcp_server/errors.py`
   - `src/aifp/mcp_server/schema.py`
   - `src/aifp/mcp_server/serialization.py`
   - `src/aifp/mcp_server/registry.py`
   - `src/aifp/mcp_server/server.py`
   - `src/aifp/mcp_server/__init__.py`
