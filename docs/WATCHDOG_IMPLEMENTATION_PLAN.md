# Watchdog Implementation Plan

## Purpose

A background Python process that monitors project source files for changes and writes actionable reminders to a JSON file. AI reads this file via `aifp_run` to stay on track during long directive chains, addressing the **directive chain depth confidence gap**.

The watchdog acts as an external memory — it never forgets, has no context window, and catches things AI might miss: unregistered functions, stale timestamps, files changed without DB updates.

---

## Architecture

### Location

```
src/aifp/watchdog/
├── __init__.py
├── __main__.py          # Entry point: python -m aifp.watchdog <project_root>
├── watcher.py           # File system observer (watchdog library)
├── analyzers.py         # File analysis: function diffing, timestamp checks
├── reminders.py         # Reminder generation and JSON file management
└── config.py            # Exclusion patterns, constants
```

**Not** inside the MCP server folder — this is a sibling module. Will be integrated into the MCP server when that gets built.

### Output Location

```
.aifp-project/watchdog/
├── reminders.json       # AI-readable reminders (cleared by aifp_run)
└── watchdog.pid         # PID of running watchdog process
```

---

## Reminders File Schema

**Path:** `<project_root>/.aifp-project/watchdog/reminders.json`

```json
{
  "generated_at": "2026-01-29T20:30:00Z",
  "reminders": [
    {
      "type": "missing_function",
      "severity": "warning",
      "file": "src/math/operations.py",
      "message": "Function 'multiply_matrices' found in file but not in database. Consider registering via project_function_create.",
      "timestamp": "2026-01-29T20:28:15Z"
    },
    {
      "type": "unregistered_file_change",
      "severity": "info",
      "file": "src/math/operations.py",
      "message": "File modified but updated_at in database is stale. Consider updating via project_file_update.",
      "timestamp": "2026-01-29T20:28:15Z"
    },
    {
      "type": "missing_db_function",
      "severity": "warning",
      "file": "src/math/operations.py",
      "message": "Database function 'f_12_add_matrices' not found in file. May have been removed or renamed.",
      "timestamp": "2026-01-29T20:28:15Z"
    }
  ]
}
```

### Reminder Types

| Type | Severity | Trigger |
|------|----------|---------|
| `timestamp_synced` | info | File modified, DB `updated_at` was stale — automatically corrected |
| `new_file_detected` | info | New file in source dir not registered in DB |
| `missing_function` | warning | Function-like pattern in file not in DB |
| `missing_db_function` | warning | DB function for file not found in actual file |
| `file_deleted` | warning | DB-registered file no longer exists on disk |

---

## Lifecycle

### Startup (via `aifp_run(is_new_session=True)`)

1. Read `project_root` from discovered project
2. Read `source_directory` from infrastructure table
3. If `source_directory` is empty/not set → skip watchdog, log warning
4. Check for existing watchdog process:
   - Read `.aifp-project/watchdog/watchdog.pid`
   - If PID exists and process is alive → kill it
5. Clear `reminders.json` (fresh session, fresh reminders)
6. Start new watchdog as **subprocess** of the calling process:
   - `subprocess.Popen([sys.executable, '-m', 'aifp.watchdog', project_root])`
   - Not detached, not daemon — inherits parent lifecycle
7. Write new PID to `watchdog.pid`

### Runtime

- Watchdog uses Python `watchdog` library to monitor `source_directory`
- On file change event → run analyzers → append to `reminders.json`
- File writes to `reminders.json` are atomic (write to temp file, rename)
- Watchdog writes to DB only for timestamp corrections (`files.updated_at`)

### Shutdown

- Automatic: parent process dies (MCP server exit, logout, restart) → watchdog dies
- Explicit: `aifp_run(is_new_session=True)` kills previous instance before starting new
- No cleanup needed — PID file and reminders are overwritten on next start

### Integration with `aifp_run`

Every `aifp_run` call (both `is_new_session=True` and `is_new_session=False`):

1. Read `.aifp-project/watchdog/reminders.json`
2. Include reminders in returned data under `watchdog_reminders` key
3. Clear the file (write empty `{"generated_at": "...", "reminders": []}`)
4. AI receives reminders as part of the standard `aifp_run` response

This ensures:
- Reminders don't accumulate indefinitely
- AI gets fresh, relevant reminders each check-in
- If AI hasn't called `aifp_run` in a while, reminders accumulate — correct behavior since that's when AI is most likely to have drifted

---

## File Watching Details

### Monitored Path

`source_directory` value from infrastructure table. Read once at startup.

### Exclusion Patterns

Two layers: hardcoded defaults in `config.py` + optional user settings from DB.

**Hardcoded defaults** (`config.py`):

```python
EXCLUDED_DIRS: Final[frozenset[str]] = frozenset([
    'node_modules',
    'venv',
    '.venv',
    'env',
    '.env',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    'target',          # Rust
    'build',
    'dist',
    '.tox',
    '.mypy_cache',
    '.pytest_cache',
    'vendor',          # Go, PHP
    '.next',           # Next.js
    '.nuxt',           # Nuxt.js
    'coverage',
    '.coverage',
    'htmlcov',
    '.aifp-project',   # Never watch ourselves
])

EXCLUDED_EXTENSIONS: Final[frozenset[str]] = frozenset([
    '.pyc', '.pyo', '.so', '.dll', '.dylib',
    '.class', '.o', '.obj', '.exe',
    '.lock', '.log',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot',
    '.zip', '.tar', '.gz', '.bz2',
])
```

**User settings entries** (in `user_preferences.db` → `user_settings` table):

| setting_key | setting_value | description |
|-------------|---------------|-------------|
| `watchdog_excluded_dirs` | JSON array, e.g. `["my_vendor", "generated"]` | Additional directories to exclude from watching |
| `watchdog_excluded_extensions` | JSON array, e.g. `[".gen.ts", ".auto.py"]` | Additional file extensions to exclude from watching |

At startup, watchdog queries `user_settings` for these keys. If entries exist, their values are parsed and merged (union) with the hardcoded defaults. If no entries exist, only hardcoded defaults apply.

### Event Handling

- **On file modified:** Run file write logic (see below) + function diff (if finalized functions exist for file)
- **On file created:** Run file write logic (see below)
- **On file deleted:** Check if file was registered in DB, flag as `file_deleted` reminder
- **On file moved:** Treat as delete + create
- **Debounce:** 2-second debounce per file to avoid rapid-fire events from editors (save, format, save)

### File Write Logic (modified + created)

On any file add or modify event:

1. **Check DB registration:** Query `files` table for file by path.
   - If **not found** and file is **not reserved** → write `new_file_detected` reminder for AI to register it
   - If **not found** but a reserved file entry exists (path matches reserved pattern) → skip, file is mid-reserve-finalize flow
   - If **found** → proceed to step 2

2. **Timestamp sync:** Compare `files.updated_at` in DB with file's actual last-modified timestamp from OS.
   - If DB timestamp is **stale** (older than file's mtime) → update `files.updated_at` in DB to match → write `timestamp_synced` reminder noting the discrepancy was detected and fixed automatically
   - If timestamps are consistent → no action

3. **Function diff** (only if file is registered and has finalized functions):
   - Run function diffing logic (see Function Diffing section below)

---

## Function Diffing Logic

### When to Diff

Only after finalize. Reserved functions don't have final names yet. The AIFP convention is that finalized functions have the DB ID prepended (e.g., `f_42_calculate_total`).

### Algorithm

On file change for a file registered in DB:

1. **Get DB functions:** Query all finalized functions for this file from DB
2. **Check DB functions exist in file:** For each DB function, search file content for the ID-prefixed name pattern. Flag any missing as `missing_db_function`.
3. **Scan for unregistered functions:** Search file for function-like patterns not matching any DB entry. Flag as `missing_function`.

### Function Pattern Detection

Language-agnostic patterns (configurable in `config.py`):

```python
FUNCTION_PATTERNS: Final[dict[str, str]] = {
    'python': r'^\s*def\s+(\w+)\s*\(',
    'javascript': r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    'typescript': r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    'rust': r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)',
    'go': r'func\s+(?:\([^)]+\)\s+)?(\w+)',
    'java': r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\(',
}
```

Primary language is read from infrastructure table to select the appropriate pattern.

---

## Database Access

**Mostly read, minimal writes.** The watchdog reads extensively but only writes to fix timestamp discrepancies.

Reads from `project.db`:
- `infrastructure` table: `project_root`, `source_directory`, `primary_language`
- `files` table: registered files, paths, `updated_at`
- `functions` table: registered functions, `file_id`, `name`, `is_reserved`

Reads from `user_preferences.db`:
- `user_settings` table: `watchdog_excluded_dirs`, `watchdog_excluded_extensions`

Writes to `project.db`:
- `files.updated_at` — only when a stale timestamp is detected and corrected

The watchdog does **not** create, delete, or register files/functions. It only syncs timestamps. All other issues are written to `reminders.json` for AI to handle.

Connection opened once at startup, refreshed periodically or on error.

---

## Startup Arguments

```
python -m aifp.watchdog <project_root>
```

The script:
1. Receives `project_root` as the single argument
2. Opens `<project_root>/.aifp-project/project.db`
3. Reads `source_directory` from infrastructure table
4. If `source_directory` is empty → exit with error message
5. Creates `.aifp-project/watchdog/` directory if not exists
6. Writes PID to `watchdog.pid`
7. Starts file observer on `source_directory`

---

## Integration Points

### Files to Modify

| File | Change |
|------|--------|
| `src/aifp/helpers/orchestrators/entry_points.py` | `aifp_run`: start/stop watchdog on `is_new_session`, read+clear reminders on every call |
| `docs/helpers/json/helpers-orchestrators.json` | `aifp_run` entry: add `watchdog_reminders` to response schema |

### New Files

| File | Purpose |
|------|---------|
| `src/aifp/watchdog/__init__.py` | Module init |
| `src/aifp/watchdog/__main__.py` | CLI entry point |
| `src/aifp/watchdog/watcher.py` | File system observer using `watchdog` library |
| `src/aifp/watchdog/analyzers.py` | File analysis: timestamp checks, function diffing |
| `src/aifp/watchdog/reminders.py` | Reminder generation, JSON read/write/clear |
| `src/aifp/watchdog/config.py` | Constants: exclusions, patterns, paths |

### Directive Updates

| Directive | Change |
|-----------|--------|
| `aifp_run.md` | Document watchdog startup on `is_new_session`, reminders in response data |
| `aifp_status.md` | Note that watchdog reminders are included via `aifp_run` |

### Dependencies

- `watchdog` Python package (file system monitoring, OS-agnostic)
- Add to project requirements/dependencies

---

## Implementation Order

1. **`config.py`** — Constants, exclusion patterns, function patterns, paths
2. **`reminders.py`** — JSON read/write/clear operations
3. **`analyzers.py`** — File analysis functions (timestamp check, function diff)
4. **`watcher.py`** — File system observer, event handling, debounce
5. **`__main__.py`** — CLI entry point, DB reads, observer startup
6. **`entry_points.py`** — Integrate start/stop/read/clear into `aifp_run`
7. **Directive updates** — `aifp_run.md`, `aifp_status.md`
8. **Testing** — Manual verification with a test project

---

## Design Principles

- **FP compliant** — Pure functions for analysis/diffing, effects isolated to clearly marked I/O boundaries (DB reads/writes, file writes). Same patterns as helpers: `_effect_` prefix or `Effect:` docstrings for side-effecting internals, pure logic separated.
- **Minimal DB writes** — Watchdog only corrects stale timestamps. All other issues go to reminders for AI to handle.
- **High signal, low noise** — Only report actionable findings. No "just checking" messages.
- **Ephemeral reminders** — Cleared on read by `aifp_run`. No accumulation problem.
- **No detached processes** — Dies with parent. Clean lifecycle.
- **Language-agnostic where possible** — Pattern-based, not AST-based. ID-prefix convention enables this.
- **Part of MCP package** — Lives in `src/aifp/watchdog/`. Not user-editable. Will integrate into MCP server when built.

---

## Integration Notes

### `aifp_end` Session Termination

The `aifp_end` helper (`src/aifp/helpers/orchestrators/entry_points.py`) already has watchdog shutdown code stubbed in `_stop_watchdog()`. When watchdog is implemented, verify:

1. **PID file format** — `_stop_watchdog` reads `.aifp-project/watchdog/watchdog.pid` and expects a single integer (PID). Ensure `__main__.py` writes the PID file in this format.
2. **Signal handling** — `_stop_watchdog` sends `SIGTERM`. Ensure `watcher.py` handles `SIGTERM` for graceful shutdown (flush pending reminders, close observers).
3. **Reminders file** — `_stop_watchdog` reads `.aifp-project/watchdog/reminders.json` before killing the process. Ensure the file is valid JSON even mid-write (atomic write pattern recommended).
4. **PID file cleanup** — `_stop_watchdog` removes the PID file after stopping. Ensure `__main__.py` also removes it on clean exit to avoid stale PID files.

Search for `TODO: Watchdog not yet implemented` in `entry_points.py` to find the integration point.
