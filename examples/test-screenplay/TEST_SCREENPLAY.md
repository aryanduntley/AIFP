# AIFP MCP Server — Test Screenplay

**Purpose**: Step-by-step testing guide for verifying the AIFP MCP server works correctly end-to-end. Covers the full project lifecycle from installation through completion.

**Audience**: Developers testing before submission, and Anthropic reviewers evaluating the server.

**Time estimate**: 15-30 minutes of interactive work.

---

## Prerequisites

- Python 3.11+
- Claude Desktop (MCPB bundle) or Claude Code (stdio transport)
- An empty folder to use as the test project directory

---

## Setup

### Option A: Claude Desktop (MCPB Bundle)

1. Install the MCPB bundle:
   - Open Claude Desktop
   - File > Install Extension > select `aifp.mcpb`
   - Or: drag `aifp.mcpb` onto the Claude Desktop window

2. Add the system prompt:
   - Open Claude Desktop Settings > Custom Instructions
   - Paste the full contents of `sys-prompt/aifp_system_prompt.txt`
   - Save

3. Create an empty test project folder:
   ```bash
   mkdir ~/aifp-test-project
   ```

4. Open Claude Desktop and start a new conversation.

### Option B: Claude Code (stdio)

1. **Choose a scope**, then add the MCP server.

   AIFP enforces a strict functional programming style and actively rejects OOP codebases. If you work on other projects that use OOP or don't need AIFP, avoid `--scope user` (which enables the server globally). Use `--scope project` or `--scope local` to keep AIFP active only where you want it.

   | Scope | Effect | Best for |
   |---|---|---|
   | `--scope project` (Recommended) | Creates `.mcp.json` in the current directory. Shareable via git. | Teams and per-project control |
   | `--scope local` | Stored in `~/.claude.json` keyed to the current directory. Private. | Personal per-project use |
   | `--scope user` | Available in every project you open. | Developers who use AIFP for all projects |

   Run the add command **from within the project folder** (for `project` or `local` scope):

   **pip install (system-wide):**
   ```bash
   cd ~/aifp-test-project
   claude mcp add --transport stdio --scope project aifp -- python3 -m aifp
   ```

   **pip install (virtual environment)** — use the venv's Python path directly:
   ```bash
   claude mcp add --transport stdio --scope project aifp -- /path/to/venv/bin/python3 -m aifp
   ```
   When Claude Code spawns the MCP server, it needs to use the venv's Python (which knows its own `site-packages`). A bare `python3` would resolve to the system Python, which won't have the package.

   **Manual install or running from source** — set `PYTHONPATH` to the parent of the `aifp/` folder:
   ```bash
   claude mcp add --transport stdio --scope project --env PYTHONPATH=/path/to/parent-of-aifp aifp -- python3 -m aifp
   ```
   For example, if the package is at `~/mcp-servers/aifp/`, use `PYTHONPATH=~/mcp-servers`. If running from the repo, use `PYTHONPATH=/path/to/AIFP/src`.

   > **Note**: All flags (`--transport`, `--scope`, `--env`) must come **before** the server name `aifp`. The `--` separates the server name from the command.

2. Create an empty test project folder:
   ```bash
   mkdir ~/aifp-test-project
   cd ~/aifp-test-project
   ```

3. Add the system prompt to the project:
   ```bash
   python3 -m aifp --system-prompt > ~/aifp-test-project/CLAUDE.md
   ```
   This writes the built-in system prompt to `CLAUDE.md`. The system prompt is shipped with the package — no separate file or download needed.

4. Start Claude Code in the test project folder:
   ```bash
   claude
   ```

### Verify MCP Connection

Before starting, confirm the server is connected:
- **Claude Desktop**: Check that AIFP tools appear in the tools list (hammer icon)
- **Claude Code**: Run `/mcp` and verify the aifp server shows as connected

If the server is not connected, check your configuration and try again before proceeding.

---

## The Test Project

**Project**: Temperature Converter
**Language**: Python 3.11+
**Description**: A pure functional library that converts temperatures between Celsius, Fahrenheit, and Kelvin, with input validation and formatted output.

This project is intentionally simple so the test focuses on AIFP behavior, not code complexity.

---

## Act 1: First Contact

### What You Say

Start the conversation with a natural message. Do NOT mention any tool names or AIFP internals. Speak as a regular user:

```
I want to build a temperature converter in Python.
```

### What Should Happen

Claude should immediately and proactively:

1. **Call `aifp_run(is_new_session=true)`** as its very first action — before analyzing your message, before responding. This is the #1 behavioral requirement.

2. **Detect no `.aifp-project/` directory** in the project folder and offer to initialize.

3. **Call `aifp_init`** after you confirm (or automatically if context is clear).

4. **Report successful initialization** and transition into project discovery.

### What You Say Next

If Claude asks for confirmation to initialize:
```
Yes, go ahead and initialize.
```

If Claude skips straight to initialization (proactive behavior), that is also acceptable.

### Verification Checklist — Act 1

After this act, check the following:

**Files created:**
- [ ] `.aifp-project/` directory exists in the test project folder
- [ ] `.aifp-project/project.db` exists (SQLite database)
- [ ] `.aifp-project/user_preferences.db` exists (SQLite database)
- [ ] `.aifp-project/ProjectBlueprint.md` exists (template with `[BRACKET]` placeholders)

**Database state** (optional — run these from terminal):
```bash
cd ~/aifp-test-project

# Project table should have a row
sqlite3 .aifp-project/project.db "SELECT name, status FROM project;"

# Infrastructure should have default entries
sqlite3 .aifp-project/project.db "SELECT type, value FROM infrastructure;"

# User settings should have defaults
sqlite3 .aifp-project/user_preferences.db "SELECT setting_key, setting_value FROM user_settings;"

# Tracking should all be disabled by default
sqlite3 .aifp-project/user_preferences.db "SELECT feature_name, is_enabled FROM tracking_settings;"
```

**Behavioral checks:**
- [ ] Claude called `aifp_run` FIRST (check tool call log)
- [ ] Claude detected missing `.aifp-project/` and acted on it
- [ ] Claude did NOT wait passively for you to ask it to initialize
- [ ] Claude transitioned to asking about the project (discovery phase)

---

## Act 2: Project Discovery

### What Happens

After initialization, the directive flow is: `aifp_init` -> `project_discovery`. Claude should begin a collaborative conversation to understand your project. It should ask about:

- Project purpose and goals
- Technical details (language, dependencies, structure)
- Scope and constraints
- Use Case 1 (software dev) vs Use Case 2 (automation) — it should identify this as Use Case 1

### What You Say

When Claude asks about the project, paste this description:

```
Project: Temperature Converter

A pure functional Python library for converting between temperature scales.

Features:
- Convert between Celsius, Fahrenheit, and Kelvin
- Validate inputs (reject negative Kelvin, non-numeric values)
- Batch conversion (convert a list of temperatures at once)
- Format results with configurable decimal precision

No external dependencies. Pure functions only. Should have tests.

Language: Python 3.11+
Source directory: src/
Test directory: tests/
```

### What Claude Should Do

During discovery, Claude should:

1. **Discuss and populate the ProjectBlueprint.md** with real project data (replacing all `[BRACKET]` placeholders)

2. **Set up infrastructure** in the database (language: Python, version: 3.11+, etc.)

3. **Define themes** — logical groupings such as:
   - Core Conversions (the conversion functions)
   - Validation (input checking)
   - Output/Formatting (result formatting, batch processing)

   (Exact theme names may vary — what matters is that themes are created)

4. **Define flows** — operational sequences such as:
   - Conversion Flow (validate -> convert -> format)

   (Exact flow names may vary)

5. **Define a completion path** with stages — for example:
   - Stage 1: Foundation (core conversions + validation)
   - Stage 2: Extended Features (batch conversion, formatting)
   - Stage 3: Testing & Finalization

   (Exact stage names may vary)

6. **Define milestones** within each stage — concrete, verifiable goals. For example:
   - Milestone 1: Core Conversion Functions
   - Milestone 2: Input Validation
   - Milestone 3: Batch Processing & Formatting
   - Milestone 4: Test Suite

   (Exact milestones may vary — what matters is they exist and are reasonable)

7. **NOT create tasks yet** — tasks are created incrementally during progression, not all at once during discovery

8. **Log evolution notes** for the blueprint changes

### Interaction During Discovery

Claude may ask clarifying questions. Here are ready responses:

If asked about testing approach:
```
Use pytest. Property-based tests with hypothesis would be nice for the math functions.
```

If asked about error handling approach:
```
Use Result types — return success/error values, not exceptions.
```

If asked about Use Case 1 vs 2:
```
Use Case 1 — this is regular software development.
```

If asked about any other details, use your judgment or say:
```
Use your best judgment based on the project description.
```

### Verification Checklist — Act 2

**ProjectBlueprint.md:**
- [ ] All `[BRACKET]` placeholders replaced with real data
- [ ] Project Overview section populated (idea, goals, success criteria)
- [ ] Technical Blueprint section populated (Python 3.11+, FP paradigm)
- [ ] Themes & Flows section populated with at least 2 themes
- [ ] Completion Path section populated with stages and milestones
- [ ] HTML comment block from template removed

**Database state:**
```bash
# Themes should exist
sqlite3 .aifp-project/project.db "SELECT name, purpose FROM themes;"

# Flows should exist
sqlite3 .aifp-project/project.db "SELECT name FROM flows;"

# Completion path should exist
sqlite3 .aifp-project/project.db "SELECT name, status FROM completion_path;"

# Milestones should exist
sqlite3 .aifp-project/project.db "SELECT name, status FROM milestones;"

# NO tasks should exist yet (tasks are incremental)
sqlite3 .aifp-project/project.db "SELECT COUNT(*) FROM tasks;"
# Expected: 0

# Evolution notes should be logged
sqlite3 .aifp-project/project.db "SELECT note_type, content FROM notes WHERE note_type='evolution' LIMIT 5;"

# Infrastructure should be populated
sqlite3 .aifp-project/project.db "SELECT type, value FROM infrastructure WHERE type='language';"
```

**Behavioral checks:**
- [ ] Claude asked about the project (did not assume everything)
- [ ] Claude identified this as Use Case 1 (regular software development)
- [ ] Claude created themes and flows (not just milestones)
- [ ] Claude did NOT create any tasks during discovery
- [ ] Claude populated the blueprint with real data
- [ ] Claude logged evolution notes for structural changes

---

## Act 3: First Milestone — Core Conversion Functions

### What Happens

After discovery, the directive flow is: `project_discovery` -> `aifp_status` -> `project_progression`. Claude should:

1. Open the first milestone
2. Create the first task for that milestone (with task items)
3. Begin writing code

### What You Say

If Claude presents the status and asks what to do next:
```
Let's start working on the first milestone.
```

If Claude proactively starts working (which is preferred behavior):
```
Looks good, continue.
```

### What Claude Should Do

1. **Create a task** under the first milestone (e.g., "Implement core conversion functions")

2. **Reserve file name(s)** via the reserve helpers — getting database IDs BEFORE writing code

3. **Reserve function name(s)** via the reserve helpers — getting function IDs

4. **Write FP-compliant code** with IDs embedded in names. Expected patterns:
   - Filename: something like `conversions_id_1.py` (ID will vary)
   - Function names: something like `celsius_to_fahrenheit_id_1()` (IDs will vary)
   - Pure functions (no classes, no mutations, no side effects)
   - Type hints on all parameters and return values
   - Frozen dataclasses for any data structures (if used)
   - Result types for fallible operations (validation)

5. **Finalize** the reserved file and function entries after writing

6. **Track everything in project.db** — files, functions, interactions

7. **Create a `src/` directory** in the project (or whatever was discussed during discovery)

### What to Look For in the Code

The code Claude writes should be FP-compliant:

```python
# GOOD — what you should see:
from typing import Final
from dataclasses import dataclass

ABSOLUTE_ZERO_C: Final[float] = -273.15

@dataclass(frozen=True)
class ConversionResult:
    value: float
    from_scale: str
    to_scale: str

def celsius_to_fahrenheit_id_N(celsius: float) -> float:
    """Pure: Convert Celsius to Fahrenheit."""
    return celsius * 9.0 / 5.0 + 32.0

# BAD — what you should NOT see:
class TemperatureConverter:      # No classes with methods
    def convert(self, temp):     # No self, no methods
        self.result = ...        # No mutation
```

### Verification Checklist — Act 3

**Files created:**
- [ ] `src/` directory exists
- [ ] At least one `.py` file exists in `src/` with an `_id_N` suffix in the filename
- [ ] Code is syntactically valid Python

**FP Compliance:**
- [ ] No classes with methods (frozen dataclasses OK)
- [ ] No mutations (no `self.x = ...`, no `list.append()`, no `dict[key] = ...`)
- [ ] All functions have type hints
- [ ] Pure functions (same inputs -> same outputs)
- [ ] No OOP patterns (no inheritance, no polymorphism)

**AIFP Workflow:**
- [ ] Claude reserved file name(s) before writing (check tool calls for `reserve_file`)
- [ ] Claude reserved function name(s) before writing (check for `reserve_function`)
- [ ] IDs are embedded in code names (filenames and/or function names have `_id_N`)
- [ ] Claude finalized the reservations after writing (check for `finalize_file`, `finalize_function`)
- [ ] Claude created a task with items before starting work

**Database state:**
```bash
# Task should exist now
sqlite3 .aifp-project/project.db "SELECT name, status FROM tasks;"

# Files should be tracked
sqlite3 .aifp-project/project.db "SELECT name, path, status FROM files;"

# Functions should be tracked
sqlite3 .aifp-project/project.db "SELECT name, purity_level, status FROM functions;"

# Interactions should be tracked (function dependencies)
sqlite3 .aifp-project/project.db "SELECT * FROM interactions LIMIT 5;"
```

**Exception rules verified:**
- [ ] `__init__.py` files (if any) do NOT have `_id_N` suffix
- [ ] Private functions (prefixed with `_`) are NOT reserved/tracked individually

---

## Act 4: Continue Development

### What You Say

After the first task is complete, Claude should either continue automatically or present the status. If it pauses:

```
Continue with the next task.
```

### What Should Happen

1. Claude marks the previous task as complete
2. If more work remains in the current milestone: creates the next task and continues
3. If the milestone is complete: marks it complete and opens the next milestone
4. The directive flow loops: `project_task_complete` -> (check milestone) -> `aifp_status` -> `project_progression` -> next task

### Mid-Project Status Check

At some point during development, ask:

```
What's the current project status?
```

Claude should answer from its existing context (NOT by calling aifp_status — its context shouldn't be stale yet). The response should include:
- Current milestone and its progress
- Active task
- Overall completion path progress
- What comes next

### Verification Checklist — Act 4

- [ ] Claude completed tasks and created new ones incrementally (not all at once)
- [ ] Claude marked milestones as complete when all tasks in them were done
- [ ] Claude opened the next milestone after completing the previous one
- [ ] Multiple files exist in `src/` covering the project scope
- [ ] All code follows FP conventions (spot-check a few functions)
- [ ] Status response was informative and accurate

**Database state:**
```bash
# Multiple tasks should exist with various statuses
sqlite3 .aifp-project/project.db "SELECT name, status FROM tasks;"

# Multiple files and functions tracked
sqlite3 .aifp-project/project.db "SELECT COUNT(*) FROM files;"
sqlite3 .aifp-project/project.db "SELECT COUNT(*) FROM functions;"

# Milestones progressing
sqlite3 .aifp-project/project.db "SELECT name, status FROM milestones;"
```

---

## Act 5: Validation & Formatting

### What You Say

If Claude pauses between milestones:

```
Continue.
```

### What Should Happen

Claude continues through the remaining milestones (validation functions, batch processing, formatting). The same patterns from Act 3-4 repeat:
- Reserve -> Write -> Finalize
- Track in database
- FP compliance
- Task/milestone progression

### Look For

- **Validation functions** that use Result types (not exceptions)
- **Batch conversion** using `map`/list comprehensions (not for loops with mutation)
- **Formatting functions** that are pure (take precision as parameter, not global config)

---

## Act 6: Testing (If Included in Milestones)

### What You Say

If Claude reaches a testing milestone:

```
Go ahead and write the tests.
```

### What Should Happen

Claude writes tests in `tests/` directory:
- Uses pytest
- Tests pure functions (easy to test — same inputs, same outputs)
- May include property-based tests with hypothesis
- Test files may or may not have `_id_N` suffixes (depends on whether Claude tracks test files)

### Verification

- [ ] `tests/` directory exists
- [ ] Test files exist and are valid Python
- [ ] Tests cover the core conversion functions
- [ ] Tests cover validation (edge cases like negative Kelvin)

---

## Act 7: Completion

### What Happens

When all milestones are complete, the flow is: `aifp_status` -> `project_completion_check`. Claude should:

1. Detect that all milestones are complete
2. Run the completion check
3. Verify all success criteria are met
4. Report the project as complete (or identify gaps)

### What You Say

If Claude doesn't automatically trigger completion:

```
I think we're done. Can you check if the project is complete?
```

### Verification Checklist — Act 7

```bash
# All milestones should be complete
sqlite3 .aifp-project/project.db "SELECT name, status FROM milestones;"
# Expected: all 'complete'

# All tasks should be complete
sqlite3 .aifp-project/project.db "SELECT name, status FROM tasks WHERE status != 'complete';"
# Expected: 0 rows

# Completion path stages should reflect progress
sqlite3 .aifp-project/project.db "SELECT name, status FROM completion_path;"

# Notes should have a rich history
sqlite3 .aifp-project/project.db "SELECT COUNT(*) FROM notes;"
```

---

## Act 8: Session End

### What You Say

```
End the session.
```

### What Should Happen

Claude calls `aifp_end` which:
1. Audits the session (verifies DB state matches filesystem)
2. Logs a session summary
3. Confirms it's safe to close

### Verification

- [ ] Claude called `aifp_end` (check tool calls)
- [ ] Claude provided a session summary
- [ ] No errors or warnings about untracked files

---

## Final Product Checklist

After completing all acts, verify the overall result:

### Project Structure

```
~/aifp-test-project/
├── src/
│   ├── [conversion_file]_id_N.py      # Core conversion functions
│   ├── [validation_file]_id_N.py      # Input validation (maybe)
│   ├── [formatting_file]_id_N.py      # Output formatting (maybe)
│   └── __init__.py                     # No _id_N suffix (exception rule)
├── tests/
│   ├── test_[something].py            # Test files
│   └── ...
├── .aifp-project/
│   ├── project.db                      # Full project state
│   ├── user_preferences.db             # Default preferences
│   └── ProjectBlueprint.md             # Fully populated blueprint
└── (possibly pyproject.toml or other config)
```

Notes:
- Exact filenames will vary (IDs are auto-incremented)
- Claude may organize files differently than listed above
- The important thing is that files HAVE `_id_N` suffixes (except exceptions)

### Code Quality

- [ ] ALL functions are pure (no side effects in business logic)
- [ ] NO classes with methods anywhere
- [ ] ALL data structures use frozen dataclasses (if any)
- [ ] Type hints on all function signatures
- [ ] Result types for operations that can fail
- [ ] No mutable global state
- [ ] Code is correct and would actually work

### Database Completeness

```bash
# Full audit
echo "=== Project ==="
sqlite3 .aifp-project/project.db "SELECT name, status FROM project;"

echo "=== Themes ==="
sqlite3 .aifp-project/project.db "SELECT name, purpose FROM themes;"

echo "=== Flows ==="
sqlite3 .aifp-project/project.db "SELECT name FROM flows;"

echo "=== Completion Path ==="
sqlite3 .aifp-project/project.db "SELECT name, status FROM completion_path;"

echo "=== Milestones ==="
sqlite3 .aifp-project/project.db "SELECT name, status FROM milestones;"

echo "=== Tasks ==="
sqlite3 .aifp-project/project.db "SELECT name, status FROM tasks;"

echo "=== Files ==="
sqlite3 .aifp-project/project.db "SELECT name, path, status FROM files;"

echo "=== Functions ==="
sqlite3 .aifp-project/project.db "SELECT name, purity_level FROM functions;"

echo "=== Notes ==="
sqlite3 .aifp-project/project.db "SELECT COUNT(*) as total_notes FROM notes;"
sqlite3 .aifp-project/project.db "SELECT note_type, COUNT(*) FROM notes GROUP BY note_type;"

echo "=== Infrastructure ==="
sqlite3 .aifp-project/project.db "SELECT type, value FROM infrastructure;"
```

Expected results:
- [ ] Project row exists with meaningful name and status
- [ ] At least 2 themes exist
- [ ] At least 1 flow exists
- [ ] Completion path has stages
- [ ] All milestones are complete (or nearly complete)
- [ ] All tasks are complete (or nearly complete)
- [ ] Files tracked match actual files in `src/`
- [ ] Functions tracked are real functions in the code
- [ ] Evolution notes exist (blueprint changes logged)
- [ ] Infrastructure shows Python 3.11+

### Blueprint Quality

Open `.aifp-project/ProjectBlueprint.md` and verify:
- [ ] No `[BRACKET]` placeholders remain
- [ ] Project Overview accurately describes the temperature converter
- [ ] Technical Blueprint shows Python 3.11+ and FP paradigm
- [ ] Themes and Flows match what's in the database
- [ ] Completion Path reflects the actual milestones
- [ ] Evolution History has at least one entry

---

## Troubleshooting

### Claude does not call aifp_run first

The system prompt must be properly loaded. Verify:
- **Claude Desktop**: Check Custom Instructions contains the full system prompt
- **Claude Code**: Check `CLAUDE.md` exists in the project root and contains the system prompt

### Claude does not detect the project directory

The MCP server resolves the project root from the working directory. Make sure:
- You are in the correct directory when starting Claude
- Claude Code: `pwd` shows the test project folder

### Claude writes OOP code

This indicates the FP baseline in the system prompt is not being followed. The system prompt explicitly states "No OOP — No classes with methods, no inheritance." If this happens consistently, the system prompt may not be loaded.

### Claude does not track files in the database

The reserve-finalize flow should happen automatically as part of `project_file_write`. If files are written but not tracked, check if Claude is following the directive flow or going off-script.

### Tools are not appearing

Run the manual verification:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | PYTHONPATH=/path/to/AIFP/src python3 -m aifp
```

You should receive a JSON response with server capabilities. Then test:
```bash
# In a separate test (server is stateful over a single stdio session)
# Use a script that sends initialize + tools/list in sequence
```

---

## Summary of Expected Directive Chain

The complete directive flow for this test, in order:

```
1. aifp_run(is_new_session=true)
2. aifp_status  ──  detects no .aifp-project/
3. aifp_init    ──  creates DBs, blueprint template
4. project_discovery  ──  interactive: blueprint, themes, flows, completion path, milestones
5. aifp_status  ──  detects discovery complete, progression needed
6. project_progression  ──  opens first milestone, creates first task
7. aifp_status  ──  has incomplete items
8. project_file_write  ──  reserve -> write FP code -> finalize -> update DB
9. project_task_complete  ──  task done
10. (repeat 6-9 for each task/milestone)
11. project_milestone_complete  ──  when all tasks in milestone done
12. (repeat 6-11 for each milestone)
13. project_completion_check  ──  all milestones done
14. project_archive  ──  (optional) archive completed project
15. aifp_end  ──  session audit and close
```

This is the happy path. Real sessions may include loops, status checks, and user-driven detours — all of which should route through `aifp_status` as the central hub.
