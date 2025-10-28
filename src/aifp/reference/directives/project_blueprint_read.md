# Directive: project_blueprint_read

**Type**: Project
**Level**: 2
**Parent Directive**: aifp_status
**Priority**: HIGH - Critical for project context

---

## Purpose

The `project_blueprint_read` directive reads and parses the `ProjectBlueprint.md` file into structured data that can be used by other directives and the AI assistant. This directive is essential for understanding the current project state, goals, architecture, themes, flows, and completion paths.

The ProjectBlueprint.md serves as the **single source of truth** for:
- Project overview (name, purpose, goals, status)
- Technical blueprint (language, runtime, architecture, dependencies)
- Project themes and flows (organizational structure)
- Completion path stages and milestones
- Evolution history (version tracking and pivots)
- User settings system configuration
- Custom directive system (if enabled)

This directive provides critical context for:
- **`aifp_status`** - Displaying comprehensive project status
- **`project_task_decomposition`** - Aligning tasks with project goals
- **`project_evolution`** - Understanding project changes over time
- **`project_blueprint_update`** - Knowing current structure before updates
- **AI assistant** - Understanding project context for all operations

When the blueprint file is missing or corrupted, this directive falls back to querying the project database to reconstruct as much context as possible.

---

## When to Apply

This directive applies when:
- **Called by `aifp_status`** - Need project context for status reporting
- **Called by `project_task_decomposition`** - Need goals/themes for task creation
- **Session continuation** - AI needs project context to resume work
- **Project evolution tracking** - Understanding current state before changes
- **User asks "what's the project?"** - Providing project overview
- **Blueprint verification** - Checking sync between blueprint and database

---

## Workflow

### Trunk: read_blueprint_file

Attempts to read ProjectBlueprint.md from `.aifp-project/` directory.

**Steps**:
1. **Locate blueprint file** - Check `.aifp-project/ProjectBlueprint.md` exists
2. **Read file contents** - Load markdown file into memory
3. **Verify checksum** - Compare with `project.blueprint_checksum` in database
4. **Route to parsing or fallback** - Based on file status

### Branches

**Branch 1: If blueprint_exists**
- **Then**: `parse_markdown_sections`
- **Details**: Parse all standard sections of ProjectBlueprint.md
  - **Section 1**: Project Overview (name, idea, goals, success criteria)
  - **Section 2**: Technical Blueprint (language, runtime, architecture, infrastructure)
  - **Section 3**: Project Themes & Flows (organizational structure)
  - **Section 4**: Completion Path (stages, milestones, current progress)
  - **Section 5**: Evolution History (version changes, pivots)
  - **Section 6**: User Settings System (if present)
  - **Section 7**: User Custom Directives System (if enabled)
- **Result**: Returns structured data object with all sections

**Branch 2: If blueprint_missing**
- **Then**: `check_database_fallback`
- **Details**: Reconstruct project context from database
  - Query `project` table for metadata (name, purpose, goals, status, version)
  - Query `infrastructure` table for technical details
  - Query `themes` and `flows` tables for organizational structure
  - Query `completion_path` and `milestones` for roadmap
  - Warn user that blueprint file is missing
- **Result**: Returns database-reconstructed project context

**Branch 3: If database_fallback_success**
- **Then**: `return_db_data`
- **Details**: Return reconstructed data with warning
  - Include all available database data
  - Warn: "Blueprint missing, using database data"
  - Suggest regenerating blueprint with `project_blueprint_update`
- **Result**: Structured data from database

**Branch 4: If parse_complete**
- **Then**: `return_structured_data`
- **Details**: Return parsed blueprint with metadata
  - Include all section data
  - Include blueprint checksum for validation
  - Compare checksum with `project.blueprint_checksum` in DB
  - Flag checksum mismatch if detected (blueprint/DB desync)
- **Result**: Complete structured project context

**Fallback**: `prompt_user`
- **Details**: Blueprint not found and database empty
  - Alert: "No project context available"
  - Ask: "Initialize new project or provide existing ProjectBlueprint.md?"
  - Suggest calling `project_init`
- **Result**: User guidance requested

---

## Examples

### ✅ Compliant Usage

**Reading Blueprint for Status Report:**
```python
# Called by aifp_status directive
blueprint_data = project_blueprint_read(project_root="/path/to/project")

# Returns structured data
{
    "project_overview": {
        "name": "AIFP MCP Server",
        "version": "1.0",
        "status": "Active (In Development)",
        "purpose": "Build MCP server for AI-driven FP enforcement",
        "goals": [
            "Pure functional implementation",
            "Meta-circular development",
            "Comprehensive test coverage"
        ]
    },
    "technical_blueprint": {
        "language": "Python 3.11+",
        "runtime": "MCP Python SDK",
        "architecture": "Functional Procedural (AIFP)",
        "key_infrastructure": ["SQLite3", "returns", "toolz", "dataclasses"]
    },
    "themes": [
        {"name": "Database Operations", "description": "..."},
        {"name": "Helper Functions", "description": "..."}
    ],
    "completion_path": [
        {"stage": "Foundation", "status": "in_progress", "milestones": [...]}
    ],
    "checksum": "a1b2c3d4...",
    "checksum_match": true
}
```

---

**Fallback to Database (Blueprint Missing):**
```python
# Blueprint file not found
blueprint_data = project_blueprint_read(project_root="/path/to/project")

# Returns database reconstruction
{
    "source": "database_fallback",
    "warning": "Blueprint missing, using database data",
    "project_overview": {
        "name": "AIFP MCP Server",
        "purpose": "Build MCP server...",
        "status": "active"
    },
    "technical_blueprint": {
        "infrastructure": [
            {"type": "language", "value": "Python 3.11"},
            {"type": "package", "value": "returns"}
        ]
    },
    "suggest_action": "Regenerate blueprint with project_blueprint_update"
}
```

---

### ❌ Non-Compliant Usage

**Not Handling Missing Blueprint:**
```python
# ❌ Assumes blueprint always exists
with open(".aifp-project/ProjectBlueprint.md") as f:
    content = f.read()
# Crashes if file missing
```

**Why Non-Compliant**:
- No fallback to database
- No error handling
- Crashes instead of gracefully degrading

---

**Ignoring Checksum Mismatch:**
```python
# ❌ Reads blueprint without verification
blueprint_data = parse_blueprint(".aifp-project/ProjectBlueprint.md")
# Doesn't check if blueprint matches database
```

**Why Non-Compliant**:
- Blueprint could be out of sync with database
- Changes made directly to blueprint not reflected in DB
- Could lead to inconsistent project state

---

## Edge Cases

### Edge Case 1: Blueprint Corrupted

**Issue**: Blueprint file exists but is malformed (invalid markdown, missing sections)

**Handling**:
- Attempt to parse sections individually
- Use available sections, skip corrupted ones
- Fill missing sections from database
- Warn user about corruption
- Suggest regenerating blueprint

```python
# Partial parse with fallback
result = {
    "section_1": parsed_section_1,  # Successfully parsed
    "section_2": None,  # Corrupted, skipped
    "section_3": db_themes,  # Fallback to database
    "warnings": ["Section 2 corrupted, using database fallback"],
    "suggest_action": "Regenerate blueprint"
}
```

---

### Edge Case 2: Checksum Mismatch

**Issue**: Blueprint file modified outside of AIFP (manual edits)

**Handling**:
- Calculate current checksum
- Compare with `project.blueprint_checksum`
- If mismatch: warn about desync
- Parse blueprint anyway (user edits take precedence)
- Update database checksum

```python
# Checksum mismatch detected
result = {
    "blueprint_data": {...},
    "checksum_mismatch": True,
    "warning": "Blueprint modified outside AIFP - potential DB desync",
    "action": "Updating project.blueprint_checksum",
    "suggest": "Run project_compliance_check to verify consistency"
}
```

---

### Edge Case 3: Empty Database and Missing Blueprint

**Issue**: Both blueprint and database are empty/missing

**Handling**:
- Detect empty state
- Prompt user to initialize project
- Suggest calling `project_init`
- Do not attempt reconstruction

```python
# No project context available
result = {
    "error": "No project context available",
    "blueprint_exists": False,
    "database_empty": True,
    "suggestion": "Call project_init to initialize AIFP project",
    "action_required": True
}
```

---

### Edge Case 4: User Directives Section Present

**Issue**: Blueprint has Section 7 (User Custom Directives System)

**Handling**:
- Parse section 7 if present
- Check `project.user_directives_status` in database
- Include user directive context in result
- Flag if status doesn't match blueprint content

```python
# Blueprint with user directives
result = {
    "blueprint_data": {...},
    "user_directives": {
        "enabled": True,
        "status": "active",
        "use_case": "Custom Directive Automation",
        "directive_files": ["directives/lights.yaml", "directives/security.yaml"]
    },
    "db_status": "active",  # Matches blueprint
    "sync_status": "ok"
}
```

---

## Related Directives

- **Called By**:
  - `aifp_status` - Primary caller for status reporting
  - `project_task_decomposition` - Needs project goals/themes
  - `project_evolution` - Tracks changes over time
  - `project_blueprint_update` - Reads before updating
- **Calls**:
  - Database helpers: `query_project_db()`, `get_project_status()`
- **Related**:
  - `project_blueprint_update` - Updates blueprint sections
  - `project_init` - Creates initial blueprint
  - `project_evolution` - Modifies blueprint for pivots

---

## Helper Functions Used

- `read_file(path: str) -> Result[str, str]` - Reads blueprint file
- `parse_markdown_sections(content: str) -> dict` - Parses markdown into structured data
- `calculate_checksum(content: str) -> str` - Computes file checksum (MD5/SHA256)
- `query_project_db(project_root: str) -> dict` - Queries database for fallback data
- `get_project_metadata() -> dict` - Gets project table data
- `get_themes_and_flows() -> dict` - Gets themes/flows from database
- `get_completion_path() -> list` - Gets roadmap stages/milestones

---

## Database Operations

This directive reads from the following tables:

- **`project`**: Reads name, purpose, goals, status, version, blueprint_checksum
- **`infrastructure`**: Reads technical stack details
- **`themes`**: Reads project themes
- **`flows`**: Reads project flows
- **`completion_path`**: Reads roadmap stages
- **`milestones`**: Reads stage milestones

**Note**: This directive is **read-only** - it does not modify the database.

---

## Testing

How to verify this directive is working:

1. **Read existing blueprint** → Returns complete structured data
   ```python
   result = project_blueprint_read("/path/to/project")
   assert result["project_overview"]["name"] == "AIFP MCP Server"
   assert "checksum" in result
   ```

2. **Missing blueprint** → Falls back to database
   ```python
   # Remove blueprint file temporarily
   result = project_blueprint_read("/path/to/project")
   assert result["source"] == "database_fallback"
   assert "warning" in result
   ```

3. **Checksum verification** → Detects modifications
   ```python
   # Modify blueprint manually
   result = project_blueprint_read("/path/to/project")
   assert result["checksum_mismatch"] == True
   ```

---

## Common Mistakes

- ❌ **Not handling missing blueprint** - Always have database fallback
- ❌ **Ignoring checksum mismatch** - Checksums detect blueprint/DB desync
- ❌ **Assuming all sections present** - Blueprints may have optional sections
- ❌ **Not validating section format** - Blueprint could be hand-edited incorrectly
- ❌ **Caching stale data** - Always read fresh on each call

---

## Roadblocks and Resolutions

### Roadblock 1: blueprint_corrupted
**Issue**: Blueprint file is malformed or partially readable
**Resolution**: Attempt to parse sections individually, use database fallback for missing sections

### Roadblock 2: markdown_parse_error
**Issue**: Markdown parsing fails completely
**Resolution**: Use database data and offer to regenerate blueprint with `project_blueprint_update`

### Roadblock 3: checksum_mismatch
**Issue**: Blueprint checksum doesn't match database record
**Resolution**: Warn user about potential blueprint/DB desync, suggest compliance check

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#project-helpers)
- [Blueprint: Project Structure](../../../docs/blueprints/blueprint_aifp_project_structure.md)
- [JSON Definition](../../../docs/directives-json/directives-project.json)
- [ProjectBlueprint.md Example](../../../.aifp/ProjectBlueprint.md)

---

*Part of AIFP v1.0 - Critical Project directive for blueprint management*
