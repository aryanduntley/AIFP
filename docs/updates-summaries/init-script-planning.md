# AIFP Project Initialization Script - Planning Document

**Date**: 2025-10-25
**Status**: Documented in Phase 1 Implementation Plan
**Priority**: High - Foundational for pre-MCP setup

---

## Purpose

Create a **standalone Python initialization script** that allows AI assistants and developers to bootstrap new AIFP projects correctly BEFORE the full MCP server is ready.

### Why This Matters

1. **Pre-MCP Development**: Enables project setup during MCP server development
2. **AI Guidance**: Ensures AI sets up the `.aifp-project/` folder structure correctly
3. **Consistency**: Standardized initialization prevents setup errors
4. **Testing**: Facilitates rapid project creation for testing and development

---

## What's Been Documented

### Added to Phase 1 Plan (phase-1-mcp-server-bootstrap.md)

**Milestone 1.1: Task #5** - Complete specification for standalone initialization script

**Location**: `src/aifp/scripts/init_aifp_project.py`

**Functions to Implement**:
```python
# CLI interface
- CLI interface with argparse (name, purpose, goals, language)

# Core initialization functions (all return Result types)
- create_project_directory(target_path: Path) -> Result[Path, str]
- initialize_project_db(aifp_dir: Path, project_metadata: dict) -> Result[Path, str]
- initialize_user_preferences_db(aifp_dir: Path) -> Result[Path, str]
- create_project_blueprint(aifp_dir: Path, metadata: dict) -> Result[Path, str]
- validate_initialization(aifp_dir: Path) -> Result[bool, str]
```

**What Gets Created**:
```
.aifp-project/
├── project.db                 # Populated with project metadata
├── user_preferences.db        # Schema only (empty tables)
├── ProjectBlueprint.md        # Template with customization note
└── .gitkeep                   # For Git tracking
```

**CLI Usage Examples**:
```bash
# Basic initialization
python -m aifp.scripts.init_aifp_project --name "MyProject" --purpose "Build a web app"

# With full details
python -m aifp.scripts.init_aifp_project \
  --name "MatrixCalc" \
  --purpose "Functional matrix calculator" \
  --goals "Pure FP,No OOP,90% test coverage" \
  --language "Python"

# Initialize in specific directory
python -m aifp.scripts.init_aifp_project \
  --name "MyProject" \
  --purpose "..." \
  --directory ~/projects/myproject
```

**Exit Codes**:
- `0` - Success (project initialized)
- `1` - Error (directory exists, invalid args, database error)

---

## ProjectBlueprint.md Template

The script will create this template:

```markdown
# {Project Name} - Project Blueprint

**Note**: This blueprint is auto-generated. Please customize it by discussing the project
architecture, goals, and structure with your AI assistant. The AI will help fill in:
- Technical architecture decisions
- Project themes and flows
- Completion path milestones
- Infrastructure requirements

Run 'aifp_run update blueprint' with your AI to collaboratively build this document.
```

---

## Testing Requirements

**Test file**: `tests/unit/scripts/test_init_aifp_project.py`

**Test cases documented**:
- ✅ `test_creates_directory_structure` - Verifies .aifp-project/ creation
- ✅ `test_initializes_project_db_with_metadata` - Checks project.db setup
- ✅ `test_initializes_user_preferences_db` - Validates user_preferences.db schema
- ✅ `test_creates_project_blueprint_template` - Ensures blueprint file created
- ✅ `test_validates_initialization_success` - Full validation check
- ✅ `test_handles_existing_directory_error` - Error handling for existing projects
- ✅ `test_cli_argument_parsing` - CLI interface validation
- ✅ `test_full_initialization_workflow` - End-to-end integration test

---

## FP Compliance

The script follows AIFP principles:

1. **Pure Functions**: Logic separated from effects
2. **Result Types**: All fallible operations return `Result[T, str]`
3. **Immutable Data**: Project metadata as frozen dataclasses
4. **Effect Isolation**: Database writes isolated in effect functions
5. **Explicit Parameters**: No hidden state or global variables

---

## Success Criteria Updated

### Phase 1 Completion Now Includes:

- ✅ Standalone initialization script (`init_aifp_project.py`) implemented and tested
- ✅ Pre-MCP project initialization working (AI can bootstrap new projects correctly)

### Week 1 Deliverable Now Includes:

- ✅ Standalone initialization script working
- ✅ AI can bootstrap new AIFP projects correctly using the script

### Immediate Actions Updated:

Added tasks:
- [ ] Implement standalone initialization script: `init_aifp_project.py`
- [ ] Test initialization script with multiple scenarios

---

## Integration with MCP Server

### Development Phase (Pre-MCP)

```bash
# Developers and AI use standalone script
python -m aifp.scripts.init_aifp_project --name "NewProject" --purpose "..."
```

### Production Phase (With MCP)

```python
# AI calls project_init directive through MCP
# project_init directive wraps the standalone script functions
await mcp_client.call_tool("project_init", {
    "name": "NewProject",
    "purpose": "...",
    "goals": [...]
})
```

**Relationship**: The `project_init` directive ✅ **WRAPS** the standalone script's helper functions:

**Directive workflow explicitly references** (see `directives-project.json`):
- ✅ `create_project_directory()` - Called in "create_project_structure" step
- ✅ `create_project_blueprint()` - Called in "generate_project_blueprint" step
- ✅ `initialize_project_db()` - Called in "initialize_databases" step
- ✅ `initialize_user_preferences_db()` - Called in "initialize_databases" step
- ✅ `validate_initialization()` - Called in "validate_initialization" step

**Module reference**: `aifp.scripts.init_aifp_project`

This ensures:
- ✅ **Consistent initialization** whether used standalone or through MCP
- ✅ **Single source of truth** for initialization logic
- ✅ **Code reuse** - directive and script share the same helper functions
- ✅ **Testability** - test helpers once, both paths work

The script remains useful for:
- Development and testing
- Manual project creation
- Pre-MCP bootstrapping
- Direct CLI usage

---

## Files Updated

1. **phase-1-mcp-server-bootstrap.md**
   - Added Task #5 and Task #6 to Milestone 1.1
   - Added explicit MCP integration section (project_init wraps these helpers)
   - Updated Success Criteria
   - Updated Immediate Actions
   - Updated Week 1 Deliverable

2. **overview-all-phases.md**
   - Added to Phase 1 Key Deliverables
   - Updated Success Criteria with pre-MCP initialization

3. **directives-project.json** ✅ NEW
   - Updated project_init directive description to mention wrapper
   - Updated workflow steps to explicitly reference helper functions:
     * create_project_directory (module: aifp.scripts.init_aifp_project)
     * create_project_blueprint (module: aifp.scripts.init_aifp_project)
     * initialize_project_db (module: aifp.scripts.init_aifp_project)
     * initialize_user_preferences_db (module: aifp.scripts.init_aifp_project)
     * validate_initialization (module: aifp.scripts.init_aifp_project)
   - Added notes in workflow details explaining helper usage

---

## Implementation Timeline

**Week 1 of Phase 1**:
- Task priority: After schema files are in place, before first helper function
- Estimated effort: 4-8 hours (implementation + tests)
- Dependencies: Database schemas must be copied to `src/aifp/database/schemas/`

**Sequence**:
```
1. Copy database schemas ✓
2. Implement init_aifp_project.py ← YOU ARE HERE (documented, ready to implement)
3. Test initialization script
4. Implement get_all_directives() helper
5. Continue with other helpers
```

---

## Key Benefits

1. **Immediate Value**: Usable before full MCP server is ready
2. **Development Aid**: Rapid project creation for testing
3. **AI Enablement**: Ensures correct .aifp-project/ structure
4. **Consistency**: Standardized initialization across all projects
5. **Foundation**: Serves as basis for `project_init` directive later

---

## Future Enhancements (Post-Phase 1)

Potential additions after initial implementation:

- **Templates**: Support for language-specific project templates
- **Interactive Mode**: Guided setup with prompts
- **Git Integration**: Optionally initialize Git repository
- **Validation**: Check for required tools (Python, dependencies)
- **Configuration**: Load defaults from user config file
- **Dry Run**: Preview what will be created without creating

---

## Status: Ready for Implementation

✅ **Fully documented** in Phase 1 implementation plan
✅ **Specifications complete** - all functions, tests, and usage defined
✅ **Success criteria updated** - clear definition of done
✅ **Timeline established** - Week 1 of Phase 1

**Next step**: When Phase 1 coding begins, implement according to this specification.

---

## Questions Addressed

**Q**: Do we have this planned in the implementation files?
**A**: ✅ **Yes, now fully documented** in:
- `phase-1-mcp-server-bootstrap.md` (detailed specification)
- `overview-all-phases.md` (high-level deliverable)

**Q**: Is this for pre-MCP setup?
**A**: ✅ **Yes, explicitly designed** for pre-MCP project initialization, ensuring AI can bootstrap projects correctly before the full MCP server is ready.

**Q**: Should we ensure complete setup on init?
**A**: ✅ **Yes, the script creates**:
- Complete `.aifp-project/` directory structure
- Fully initialized `project.db` with metadata
- Schema-ready `user_preferences.db`
- Template `ProjectBlueprint.md` with customization note
- Validation to ensure everything is properly set up

---

**Status**: Documentation complete, ready for Phase 1 implementation. ✅
