# aifp.scripts References - Cleanup Analysis

**Date**: 2026-01-17
**Status**: Analysis Complete - Ready for Cleanup
**Total References**: 4 in active directives (all in `project_init`)

---

## Summary

Found **4 references** to `aifp.scripts.init_aifp_project` - all in `directives-project.json` in the `project_init` directive workflow.

**Status**: Non-existent module from pre-MCP planning (October 2025)
**Current Architecture**: Helper-based MCP system (orchestrators + sub-helpers)

---

## References in directives-project.json

All references are in the **`project_init` directive** workflow.

### Reference 1: Line 137 - Description
```json
"description": "Initializes a new AIFP project ... Wraps the standalone initialization script (aifp.scripts.init_aifp_project) helper functions to ensure consistent setup."
```
**Context**: Directive description mentions wrapping the standalone script
**Action**: Remove mention of `aifp.scripts`, replace with orchestrator reference
**Replace with**: "Coordinates project initialization through the `project_init` orchestrator helper."

---

### Reference 2: Line 246 - create_project_structure
```json
{
  "if": "source_directory_determined",
  "then": "create_project_structure",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {
      "target_path": "user_working_dir"
    },
    "create_folders": [
      ".aifp-project/",
      ".aifp-project/backups/"
    ],
    "note": "Uses standalone initialization script helper function"
  }
}
```

**Purpose**: Create `.aifp-project/` directory structure

**Current Reality**: Simple directory creation operation

**Decision**: **Execute directly in `project_init` orchestrator** (not a separate helper)
- Reason: One-time operation, simple os.makedirs call
- No reusability needed

**Replace with**:
```json
{
  "if": "source_directory_determined",
  "then": "create_project_structure",
  "details": {
    "action": "create_directories",
    "directories": [
      ".aifp-project/",
      ".aifp-project/backups/"
    ],
    "note": "project_init orchestrator creates directories directly (os.makedirs)"
  }
}
```

---

### Reference 3: Line 261 - generate_project_blueprint
```json
{
  "if": "structure_created",
  "then": "generate_project_blueprint",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {
      "aifp_dir": ".aifp-project/",
      "metadata": "from_prompts"
    },
    "template": "ProjectBlueprint_template.md",
    "output": ".aifp-project/ProjectBlueprint.md",
    "note": "Uses standalone initialization script helper function"
  }
}
```

**Purpose**: Generate ProjectBlueprint.md from template

**Current Reality**: Template-based file generation

**Decision**: **Create helper** `generate_blueprint_from_template()`
- Reason: Reusable for blueprint updates, complex template logic
- Used by: `project_init` orchestrator, blueprint update operations

**Replace with**:
```json
{
  "if": "structure_created",
  "then": "generate_project_blueprint",
  "details": {
    "helper": "generate_blueprint_from_template",
    "parameters": {
      "aifp_dir": ".aifp-project/",
      "metadata": "from_prompts"
    },
    "note": "Helper generates blueprint from template with project metadata"
  }
}
```

**New Helper Needed**:
```json
{
  "name": "generate_blueprint_from_template",
  "file_path": "helpers/project/blueprint.py",
  "parameters": [
    {
      "name": "aifp_dir",
      "type": "string",
      "required": true,
      "description": "Path to .aifp-project/ directory"
    },
    {
      "name": "project_name",
      "type": "string",
      "required": true,
      "description": "Project name"
    },
    {
      "name": "project_purpose",
      "type": "string",
      "required": true,
      "description": "Project purpose"
    },
    {
      "name": "goals",
      "type": "array",
      "required": true,
      "description": "Array of project goals"
    },
    {
      "name": "language",
      "type": "string",
      "required": false,
      "default": "Python",
      "description": "Primary programming language"
    }
  ],
  "purpose": "Generate ProjectBlueprint.md from template with project metadata",
  "error_handling": "Return error if template not found or file write fails",
  "is_tool": false,
  "is_sub_helper": true,
  "return_statements": [
    "Blueprint generated successfully at {path}",
    "Error: Template not found",
    "Error: Failed to write blueprint file"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "generate_blueprint",
      "sequence_order": 7,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Generate ProjectBlueprint.md during initialization"
    }
  ],
  "implementation_notes": [
    "Load template from: src/aifp/templates/ProjectBlueprint_template.md",
    "Replace placeholders: {{PROJECT_NAME}}, {{PURPOSE}}, {{GOALS}}, {{LANGUAGE}}",
    "Write to: {aifp_dir}/ProjectBlueprint.md",
    "Returns: {success: true, blueprint_path: '...'}",
    "Reusable for blueprint updates and regeneration"
  ]
}
```

---

### Reference 4: Line 275 - initialize_databases
```json
{
  "if": "blueprint_generated",
  "then": "initialize_databases",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {
      "aifp_dir": ".aifp-project/",
      "project_metadata": "from_prompts"
    },
    "databases": [
      "project.db",
      "user_preferences.db"
    ],
    "schemas": [
      "project_db_schema.sql",
      "user_preferences_schema.sql"
    ],
    "note": "Uses standalone initialization script helper functions"
  }
}
```

**Purpose**: Initialize project.db and user_preferences.db with schemas and data

**Current Reality**: Database creation, schema execution, data population

**Decision**: **Execute directly in `project_init` orchestrator**
- Reason: One-time operation, sequential dependencies
- Operations: Load schema → execute SQL → insert metadata → execute standard_infrastructure.sql
- Better kept together for atomic initialization

**Replace with**:
```json
{
  "if": "blueprint_generated",
  "then": "initialize_databases",
  "details": {
    "action": "create_and_populate_databases",
    "databases": {
      "project.db": {
        "schema": "schemas/project.sql",
        "data": [
          "INSERT project metadata",
          "Execute initialization/standard_infrastructure.sql",
          "INSERT default completion_path"
        ]
      },
      "user_preferences.db": {
        "schema": "schemas/user_preferences.sql",
        "data": [
          "INSERT default tracking_settings"
        ]
      }
    },
    "note": "project_init orchestrator executes database initialization directly"
  }
}
```

**Operations in Orchestrator**:
1. Load `schemas/project.sql`
2. Create `project.db`
3. Execute schema SQL
4. INSERT project metadata (name, purpose, goals)
5. Execute `initialization/standard_infrastructure.sql` ⭐ **NEW FILE NEEDED**
6. INSERT default completion_path
7. Load `schemas/user_preferences.sql`
8. Create `user_preferences.db`
9. Execute schema SQL
10. INSERT default tracking_settings

---

### Reference 5: Line 295 - validate_initialization
```json
{
  "if": "databases_initialized",
  "then": "validate_initialization",
  "details": {
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {
      "aifp_dir": ".aifp-project/"
    },
    "checks": [
      "project.db exists and has metadata",
      "user_preferences.db has schema",
      "ProjectBlueprint.md exists",
      "all required tables created"
    ],
    "note": "Validates complete initialization using script function"
  }
}
```

**Purpose**: Validate that initialization completed successfully

**Current Reality**: Helper already exists!

**Decision**: **Use existing helper** `validate_initialization` (in helpers-orchestrators.json)

**Replace with**:
```json
{
  "if": "databases_initialized",
  "then": "validate_initialization",
  "details": {
    "helper": "validate_initialization",
    "parameters": {
      "aifp_dir": ".aifp-project/"
    },
    "note": "Validates directory structure, databases, tables, and blueprint file"
  }
}
```

**Helper exists**: ✅ Already in `helpers-orchestrators.json`

---

## New Helpers Needed

Based on aifp.scripts analysis, we need:

### 1. generate_blueprint_from_template()
- **Purpose**: Generate ProjectBlueprint.md from template
- **Location**: helpers/project/blueprint.py
- **Used by**: project_init orchestrator, blueprint updates
- **Specification**: See Reference 3 above

### 2. scan_for_oop_patterns()
- **Purpose**: Detect OOP patterns to abort initialization
- **Location**: helpers/project/validation.py
- **Used by**: project_init orchestrator (pre-init check)
- **Specification**:

```json
{
  "name": "scan_for_oop_patterns",
  "file_path": "helpers/project/validation.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "description": "Path to project root directory"
    },
    {
      "name": "threshold",
      "type": "integer",
      "required": false,
      "default": 3,
      "description": "Number of OOP patterns required to flag as OOP project"
    }
  ],
  "purpose": "Scan codebase for OOP patterns (classes, self, this) to determine if project is FP-compatible",
  "error_handling": "Return error if directory not accessible",
  "is_tool": false,
  "is_sub_helper": true,
  "return_statements": [
    "Returns: {oop_detected: false, patterns_found: 0} if FP-compatible",
    "Returns: {oop_detected: true, patterns_found: N, affected_files: [...]} if OOP detected",
    "Threshold default: 3+ patterns across multiple files"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "oop_scan",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Scan for OOP patterns before initialization - abort if detected"
    }
  ],
  "implementation_notes": [
    "Scan patterns by language:",
    "  Python: ['class .*\\(.*\\):', 'self\\.', '__init__', 'def .*\\(self']",
    "  JavaScript: ['class ', 'this\\.', 'extends ', 'constructor\\(']",
    "  TypeScript: ['class ', 'this\\.', 'extends ', 'implements ', 'interface ']",
    "Threshold: 3+ patterns across multiple files = OOP project",
    "Returns: {oop_detected: bool, patterns_found: int, affected_files: [...]}"
  ]
}
```

### 3. detect_primary_language()
- **Purpose**: Infer primary language from file extensions
- **Location**: helpers/project/analysis.py
- **Used by**: project_init orchestrator, AI post-init infrastructure population
- **Specification**:

```json
{
  "name": "detect_primary_language",
  "file_path": "helpers/project/analysis.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "description": "Path to project root directory"
    }
  ],
  "purpose": "Detect primary programming language by analyzing file extensions",
  "error_handling": "Return 'Unknown' if no code files found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns detected language: 'Python', 'JavaScript', 'Rust', 'Go', etc.",
    "Returns 'Unknown' if no code files or multiple languages tied"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "language_detection",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Detect language during init for infrastructure population"
    }
  ],
  "implementation_notes": [
    "Count file extensions: .py, .js, .ts, .rs, .go, .java, .cpp, etc.",
    "Return language with most files",
    "Return 'Unknown' if no clear majority",
    "Returns: {language: 'Python', confidence: 0.85, file_count: 42}"
  ]
}
```

### 4. detect_build_tool()
- **Purpose**: Detect build tool from config files
- **Location**: helpers/project/analysis.py
- **Used by**: AI post-init infrastructure population
- **Specification**:

```json
{
  "name": "detect_build_tool",
  "file_path": "helpers/project/analysis.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "description": "Path to project root directory"
    }
  ],
  "purpose": "Detect build tool by checking for config files (Cargo.toml, package.json, Makefile, etc.)",
  "error_handling": "Return 'Unknown' if no build config found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns detected build tool: 'cargo', 'npm', 'make', 'maven', 'gradle', etc.",
    "Returns 'Unknown' if no build config found"
  ],
  "target_database": "none",
  "used_by_directives": [],
  "implementation_notes": [
    "Check for files:",
    "  Cargo.toml → 'cargo'",
    "  package.json → 'npm' (check scripts for yarn/pnpm)",
    "  Makefile → 'make'",
    "  pom.xml → 'maven'",
    "  build.gradle → 'gradle'",
    "  go.mod → 'go'",
    "Returns: {build_tool: 'cargo', config_file: 'Cargo.toml'}"
  ]
}
```

---

## project_init Orchestrator - Complete Definition

Based on aifp.scripts analysis, here's the complete `project_init` orchestrator specification:

```json
{
  "name": "project_init",
  "file_path": "helpers/orchestrators/orchestrators.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "description": "Path to project root directory"
    },
    {
      "name": "project_name",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project name (NULL = infer from directory)"
    },
    {
      "name": "project_purpose",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project purpose (NULL = prompt user)"
    },
    {
      "name": "goals",
      "type": "array",
      "required": false,
      "default": [],
      "description": "Array of project goals"
    }
  ],
  "purpose": "Complete project initialization orchestrator. Coordinates OOP scan, directory creation, database setup, blueprint generation, and state DB initialization. Ensures project only initialized once.",
  "error_handling": "Return detailed error if: already initialized, OOP detected, directory permissions denied, database creation failed. Clean up partial initialization on error.",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Project initialized successfully",
    "Created: .aifp-project/project.db, user_preferences.db, ProjectBlueprint.md, {source}/.state/",
    "Standard infrastructure entries created with empty values (6 entries)",
    "AI MUST now populate infrastructure values:",
    "  1. Call detect_primary_language(), detect_build_tool() for detection",
    "  2. Prompt user for confirmation or missing values",
    "  3. Update via: update_project_entry('infrastructure', id, {'value': '...'})",
    "Call get_all_infrastructure() to retrieve entries with IDs for updating"
  ],
  "target_database": "orchestrator",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "main_orchestrator",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "project_init directive calls project_init orchestrator for complete initialization"
    }
  ],
  "implementation_notes": [
    "ORCHESTRATOR - coordinates initialization, calls sub-helpers, executes direct operations",
    "",
    "Step 1: Check if already initialized",
    "  - Check for .aifp-project/ directory existence",
    "  - If exists and has project.db → return error: 'Already initialized'",
    "",
    "Step 2: Scan for OOP patterns",
    "  - Call: scan_for_oop_patterns(project_root, threshold=3)",
    "  - If OOP detected → abort with detailed error message",
    "",
    "Step 3: Gather project info",
    "  - Prompt user if parameters not provided",
    "  - Detect language: detect_primary_language(project_root)",
    "",
    "Step 3.5: Determine source directory",
    "  - Scan for existing: src/, lib/, app/, pkg/",
    "  - Use language conventions if not found",
    "  - Prompt user if ambiguous",
    "  - Call: add_source_directory(project_db_path, source_dir)",
    "",
    "Step 4: Create directory structure (DIRECT)",
    "  - os.makedirs('.aifp-project/', exist_ok=True)",
    "  - os.makedirs('.aifp-project/backups/', exist_ok=True)",
    "",
    "Step 5: Initialize project.db (DIRECT)",
    "  - Load schema: load_sql_file('schemas/project.sql')",
    "  - Create DB: sqlite3.connect('.aifp-project/project.db')",
    "  - Execute schema SQL",
    "  - INSERT project metadata (name, purpose, goals, status='active', version=1)",
    "  - Execute: load_sql_file('initialization/standard_infrastructure.sql')",
    "  - INSERT default completion_path (Setup, Development, Testing, Finalization)",
    "",
    "Step 6: Initialize user_preferences.db (DIRECT)",
    "  - Load schema: load_sql_file('schemas/user_preferences.sql')",
    "  - Create DB: sqlite3.connect('.aifp-project/user_preferences.db')",
    "  - Execute schema SQL",
    "  - INSERT default tracking_settings (all disabled)",
    "",
    "Step 7: Generate ProjectBlueprint.md",
    "  - Call: generate_blueprint_from_template(aifp_dir, name, purpose, goals, language)",
    "",
    "Step 8: Create .gitkeep files (DIRECT)",
    "  - Write '.aifp-project/.gitkeep'",
    "",
    "Step 9.5: Initialize state database",
    "  - Call: initialize_state_database(project_root, source_dir, language)",
    "  - Creates: {source}/.state/runtime.db, README.md, state_operations.{ext}",
    "",
    "Step 10: Validate initialization",
    "  - Call: validate_initialization(aifp_dir)",
    "  - Checks: directories exist, databases have tables, blueprint exists",
    "",
    "Step 11: Return success with guidance",
    "  - Returns: {success: true, project_name, files_created[], next_steps[]}",
    "  - Guidance for AI: populate infrastructure values using detection helpers",
    "",
    "ERROR HANDLING:",
    "  - If any step fails: clean up partial initialization",
    "  - Remove created directories/files on error",
    "  - Return detailed error with step that failed"
  ]
}
```

---

## Replacement Summary

### directives-project.json Changes

**Line 137** - Description:
- ❌ Remove: "Wraps the standalone initialization script (aifp.scripts.init_aifp_project)"
- ✅ Replace: "Coordinates project initialization through the `project_init` orchestrator helper"

**Line 246** - create_project_structure:
- ❌ Remove: `"module": "aifp.scripts.init_aifp_project"`
- ✅ Replace: `"action": "create_directories"` (executed in orchestrator)

**Line 261** - generate_project_blueprint:
- ❌ Remove: `"module": "aifp.scripts.init_aifp_project"`
- ✅ Replace: `"helper": "generate_blueprint_from_template"`
- 📝 New helper needed

**Line 275** - initialize_databases:
- ❌ Remove: `"module": "aifp.scripts.init_aifp_project"`
- ✅ Replace: `"action": "create_and_populate_databases"` (executed in orchestrator)

**Line 295** - validate_initialization:
- ❌ Remove: `"module": "aifp.scripts.init_aifp_project"`
- ✅ Replace: `"helper": "validate_initialization"` (already exists!)

---

## Planning Documents to Update/Archive

### Archive (Mark as Outdated)
- `docs/updates-summaries/init-script-planning.md` - Pre-MCP planning
- `docs/implementation-plans/phase-1-mcp-server-bootstrap.md` - Sections referencing aifp.scripts

### Update
- `docs/helpers/DIRECTIVE_NAMES_REFERENCE.md` - Remove aifp.scripts references
- `docs/COMPLETE/helpers/helper-functions-reference.md` - Update with new helpers
- `docs/directive-review-plan.md` - Update with current architecture

---

## Action Items

### Phase 1: Define New Helpers (Documentation)
- [ ] Define `project_init` orchestrator (complete specification above)
- [ ] Define `generate_blueprint_from_template()` helper
- [ ] Define `scan_for_oop_patterns()` helper
- [ ] Define `detect_primary_language()` helper
- [ ] Define `detect_build_tool()` helper

### Phase 2: Update directives-project.json
- [ ] Line 137: Update description (remove aifp.scripts mention)
- [ ] Line 246: Replace module with action (create_directories)
- [ ] Line 261: Replace module with helper (generate_blueprint_from_template)
- [ ] Line 275: Replace module with action (create_and_populate_databases)
- [ ] Line 295: Replace module with helper (validate_initialization - existing!)

### Phase 3: Verify MD Files
- [ ] Check project_init.md for consistency with JSON changes
- [ ] Remove code examples that reference aifp.scripts
- [ ] Add orchestrator workflow description

### Phase 4: Archive Planning Docs
- [ ] Mark init-script-planning.md as "Outdated - Pre-MCP Planning"
- [ ] Update phase-1-mcp-server-bootstrap.md sections
- [ ] Update directive-review-plan.md with current architecture

---

## Next Steps

1. ✅ Review this analysis document
2. Create helper definition document (combine with SQL cleanup helpers)
3. Update directives-project.json (lines 137, 246, 261, 275, 295)
4. Update project_init.md for consistency
5. Create new helper definitions in helpers JSON files
6. Test initialization workflow with new architecture
