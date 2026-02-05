# Implementation Plan: UNIQUE Constraint Removal + Getter/Setter Audit

**Date**: 2026-02-05
**Status**: COMPLETE
**Related**: `docs/MCP/MCP_IMPLEMENTATION_PLAN.md` (Milestone 1 prerequisite)
**Trigger**: UNIQUE constraint on `functions.name` blocked inserting `main()` for both `watchdog/__main__.py` (file 148) and `src/aifp/__main__.py` (file 203)

---

## Problem

The `functions` and `types` tables enforced `UNIQUE(name)` — a flat namespace constraint. This prevents:
- Two files from having a function named `main` (common in `__main__.py` files)
- Reusing type names across different files

Additionally, getter functions like `get_function_by_name` returned only a single result and didn't include file metadata, making it hard for AI to distinguish between multiple matches.

## Decision (REVISED)

**Original plan**: `UNIQUE(name)` → `UNIQUE(name, file_id)` (composite key)
**Final decision**: Remove UNIQUE constraint entirely — language already enforces per-file uniqueness (you can't have two functions named `main` in the same file — that's a compile error). DB constraint is redundant.

- **Functions**: `UNIQUE(name)` → REMOVED entirely
- **Types**: `UNIQUE(name)` → REMOVED entirely
- **Files**: NO CHANGE — `UNIQUE(path)` is sufficient
- **Getters**: Return lists + include file data (name, path) via JOIN
- **New**: Add `get_type_by_name` (didn't exist before — needed for parity)
- **Interactions**: `_get_function_id_by_name` needs disambiguation logic (see Step 3e)
- **Validators**: `id_in_name` checks in update functions must respect the `id_in_name` flag

---

## Step 1: Schema Changes — COMPLETE ✓

**File**: `src/aifp/database/schemas/project.sql`

- Removed `UNIQUE` from `name` on both `functions` and `types` tables (no constraint at all)
- Version bumped from 1.4 → 1.5
- Changelog added

## Step 2: Live DB Migration — COMPLETE ✓

**Target**: `.aifp/project.db`

- Recreated both tables without UNIQUE on name
- Verified: 289 functions preserved, 0 types, schema correct
- Version 1.5 confirmed

## Step 3: Helper Code Changes

### 3a. `src/aifp/helpers/project/files_1.py` — COMPLETE ✓

- Added `FilesQueryResult` dataclass (for multi-result returns):
  ```python
  @dataclass(frozen=True)
  class FilesQueryResult:
      success: bool
      files: Tuple[FileRecord, ...] = ()
      error: Optional[str] = None
  ```
- `FileQueryResult` kept for single-result lookups (e.g., `get_file_by_path`)
- `_get_file_by_name_effect`: removed `LIMIT 1`, now uses `fetchall()`, returns `List[sqlite3.Row]`
- `get_file_by_name`: return type changed to `FilesQueryResult`, builds tuple of records

### 3b. `src/aifp/helpers/project/functions_1.py` — COMPLETE ✓

- `FunctionRecord`: added `file_name: Optional[str]`, `file_path: Optional[str]`
- `FunctionQueryResult`: changed from `function: Optional[FunctionRecord]` to `functions: Tuple[FunctionRecord, ...]`
- `row_to_function_record`: added key checking for optional file_name/file_path:
  ```python
  keys = row.keys()
  file_name=row["file_name"] if "file_name" in keys else None,
  file_path=row["file_path"] if "file_path" in keys else None,
  ```
- `_get_function_by_name_effect`: now uses JOIN + fetchall():
  ```sql
  SELECT f.*, fi.name AS file_name, fi.path AS file_path
  FROM functions f
  LEFT JOIN files fi ON f.file_id = fi.id
  WHERE f.name = ?
  ```
- `get_function_by_name`: builds tuple from all rows

### 3c. `src/aifp/helpers/project/functions_2.py` — COMPLETE ✓

- `FunctionRecord`: synced with functions_1.py — added `id_in_name: bool`, `file_name: Optional[str]`, `file_path: Optional[str]`
- `row_to_function_record`: added key checking for optional fields
- `_get_functions_by_file_effect`: now uses JOIN:
  ```sql
  SELECT f.*, fi.name AS file_name, fi.path AS file_path
  FROM functions f
  LEFT JOIN files fi ON f.file_id = fi.id
  WHERE f.file_id = ?
  ORDER BY f.created_at
  ```
- `update_function_file_location`: added pre-move uniqueness check:
  ```python
  cursor = conn.execute(
      "SELECT id FROM functions WHERE name = (SELECT name FROM functions WHERE id = ?) AND file_id = ?",
      (function_id, new_file_id)
  )
  if cursor.fetchone():
      return LocationUpdateResult(success=False, error="Name conflict at destination file")
  ```

### 3d. `src/aifp/helpers/project/types_1.py` — COMPLETE ✓

- `TypeRecord`: added `file_name: Optional[str]`, `file_path: Optional[str]`
- `row_to_type_record`: added key checking for file_name/file_path
- Added `TypeQueryResult` dataclass with `types: Tuple[TypeRecord, ...]`
- Added `_get_type_by_name_effect`: JOIN with files table, fetchall()
- Added `get_type_by_name(db_path, type_name)` public function

### 3e. `src/aifp/helpers/project/interactions.py` — COMPLETE ✓

- Added `FunctionMatch` dataclass for disambiguation results
- Renamed `_get_function_id_by_name` → `_resolve_function_by_name`
- New function uses JOIN with files table, fetchall(), returns `(id_or_None, matches)`
- Updated `add_interaction` to handle disambiguation:
  - 0 matches → "not found" error
  - 1 match → continue as before
  - >1 matches → returns error listing all matches with IDs and file paths, instructs AI to use `add_interactions` with specific function ID

### 3f. Validators — `id_in_name` awareness — COMPLETE ✓

Three update functions validate `_id_XX` pattern unconditionally. They need to check the entity's `id_in_name` flag first:

1. **`files_2.py:update_file`** (line 417):
   ```python
   # BEFORE:
   if name is not None and not validate_file_id_pattern(name, file_id):

   # AFTER: Check id_in_name flag from DB before validating pattern
   ```

2. **`functions_2.py:update_function`** (line 557):
   ```python
   # Same pattern — check id_in_name before requiring _id_XX
   ```

3. **`types_1.py:update_type`** (line 953):
   ```python
   # Same pattern — check id_in_name before requiring _id_XX
   ```

For each: query `SELECT id_in_name FROM {table} WHERE id = ?`, only validate pattern if `id_in_name` is true.

---

## Step 4: Helper JSON Updates — COMPLETE ✓

### `dev/helpers-json/helpers-project-2.json` — `get_file_by_name`:
- Update parameters and return type to reflect list return
- Match code exactly

### `dev/helpers-json/helpers-project-3.json` — `get_function_by_name`:
- Update to reflect list return + JOIN with file data
- Match code exactly

### `dev/helpers-json/helpers-project-4.json`:
- Add new `get_type_by_name` entry (match code exactly)
- Update `add_interaction` to document disambiguation behavior

---

## Step 5: Core DB Rebuild — COMPLETE ✓

```bash
rm src/aifp/database/aifp_core.db
cd /home/eveningb4dawn/Desktop/Projects/AIFP
python dev/sync-directives.py
```

---

## Step 6: Insert Blocked Function Record — COMPLETE ✓

After constraint removal in `.aifp/project.db`:

```sql
INSERT INTO functions (name, file_id, purpose, is_reserved, id_in_name)
VALUES ('main', 203, 'Start the AIFP MCP server', 0, 0);
```

This was blocked before because `main` already exists for file 148 (watchdog `__main__.py`).

---

## Execution Order

1. ~~Edit `project.sql` schema~~ ✓
2. ~~Run live DB migration on `.aifp/project.db`~~ ✓
3. ~~Edit `files_1.py` (get_file_by_name → list)~~ ✓
4. ~~Edit `functions_1.py` (get_function_by_name → list + file data)~~ ✓
5. ~~Edit `functions_2.py` (FunctionRecord sync + file data + move check)~~ ✓
6. ~~Edit `types_1.py` (row_to_type_record + get_type_by_name)~~ ✓
7. ~~Edit `interactions.py` (disambiguation logic)~~ ✓
8. ~~Edit `files_2.py` (update_file id_in_name check)~~ ✓
9. ~~Edit `functions_2.py` (update_function id_in_name check)~~ ✓
10. ~~Edit `types_1.py` (update_type id_in_name check)~~ ✓
11. ~~Edit `helpers-project-2.json`~~ ✓
12. ~~Edit `helpers-project-3.json`~~ ✓
13. ~~Edit `helpers-project-4.json` (new get_type_by_name + update add_interaction)~~ ✓
14. ~~Delete `aifp_core.db` + run `sync-directives.py`~~ ✓ (221 helpers synced, integrity passed)
15. ~~Insert `main()` function record for file 203~~ ✓ (ID 292, file_id 203)

---

## Verification Checklist

- [x] `sqlite3 .aifp/project.db ".schema functions"` shows NO UNIQUE on name
- [x] `sqlite3 .aifp/project.db ".schema types"` shows NO UNIQUE on name
- [x] 289 functions preserved after migration
- [x] `get_type_by_name` exists in code and JSON
- [x] Insert `main` for file 203 succeeds (ID 292)
- [x] `python dev/sync-directives.py` completes without errors (221 helpers synced)
- [x] `src/aifp/database/aifp_core.db` exists after rebuild
