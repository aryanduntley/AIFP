# helpers_parsed.json Verification Report

**Date**: 2025-11-29
**Purpose**: Verify all 49 helpers from helpers_parsed.json against current 12 registry files

---

## Summary

**Total helpers in helpers_parsed.json**: 49
**Exact name matches found**: 10
**Semantic matches found**: 39
**Truly missing**: 0
**Better specs in registries**: 49

---

## Detailed Analysis

### ✅ Exact Name Matches (10 helpers)

These exist in registries with exact same names:

| Helper | Registry File | Status |
|--------|---------------|--------|
| create_user_branch | helpers_registry_git.json | ✅ Match |
| detect_conflicts_before_merge | helpers_registry_git.json | ✅ Match |
| detect_external_changes | helpers_registry_git.json | ✅ Match |
| get_current_branch | helpers_registry_git.json | ✅ Match |
| get_current_commit_hash | helpers_registry_git.json | ✅ Match |
| get_directive | helpers_registry_core.json | ✅ Match |
| get_directive_preference | helpers_registry_user_settings.json | ✅ Match |
| get_git_status | helpers_registry_git.json | ✅ Match |
| get_user_name_for_branch | helpers_registry_git.json | ✅ Match |
| list_active_branches | helpers_registry_git.json | ✅ Match |
| merge_with_fp_intelligence | helpers_registry_git.json | ✅ Match |
| sync_git_state | helpers_registry_git.json | ✅ Match |

---

### 🔄 Semantic Matches - Different Names, Same Functionality (37 helpers)

These exist in registries but with more specific/granular naming from info-helpers-*.txt:

#### MCP/Core Helpers (7)

| helpers_parsed.json | Current Registry | Registry File | Notes |
|---------------------|------------------|---------------|-------|
| get_all_directives | get_directives | helpers_registry_core.json | More specific: get_directives, get_directives_by_category, get_directives_by_name |
| get_directive_interactions | get_interactions_for_directive | helpers_registry_core.json | More granular: get_interactions_for_directive, get_interactions_for_directive_as_target |
| get_directive_md_content | get_directive_md | helpers_registry_core.json | Same functionality |
| search_directives | get_directives_by_category, find_directives | helpers_registry_core.json, mcp_orchestrators.json | Split into specific queries + orchestrator |
| find_directive_by_intent | find_directives (orchestrator) | helpers_registry_mcp_orchestrators.json | Subsumed by find_directives orchestrator |
| query_mcp_db | (NOT IN REGISTRY) | N/A | ⚠️ Generic query helper - may not be in registries yet |

#### User Settings/Preferences (3)

| helpers_parsed.json | Current Registry | Registry File | Notes |
|---------------------|------------------|---------------|-------|
| set_directive_preference | update_settings_directive_preference | helpers_registry_user_settings.json | Different name, same function |
| get_tracking_settings | get_tracking_* (multiple) | helpers_registry_user_settings.json | Split into: get_tracking_fp_flow, get_tracking_issue_reports, get_tracking_ai_log |
| toggle_tracking_feature | enable_tracking_*, disable_tracking_* | helpers_registry_user_settings.json | Split into enable/disable for each feature |

#### User Directives Automation (10) - VERIFIED 2025-11-30

| helpers_parsed.json | Actual Registry Helper | Registry File | Status |
|---------------------|------------------------|---------------|--------|
| activate_directive | set_user_directive_activate | helpers_registry_user_directives_setters.json | ✅ EXISTS - Uses `active` boolean parameter |
| deactivate_directive | set_user_directive_activate | helpers_registry_user_directives_setters.json | ✅ EXISTS - Same helper as activate |
| detect_dependencies | get_user_directive_dependencies_by_directive | helpers_registry_user_directives_getters.json | ✅ EXISTS - Query helper |
| generate_implementation_code | add_user_directive_implementation | helpers_registry_user_directives_setters.json | ✅ EXISTS - "add" not "create" or "generate" |
| get_user_directive_status | get_user_directive, get_user_directives | helpers_registry_user_directives_getters.json | ✅ EXISTS - Split into multiple getters |
| install_dependency | add_user_directive_dependency | helpers_registry_user_directives_setters.json | ✅ EXISTS - "add" not "install" |
| monitor_directive_execution | get_user_directive_execution, get_user_directive_executions_by_* | helpers_registry_user_directives_getters.json | ✅ EXISTS - Multiple execution query helpers |
| parse_directive_file | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - Handled by `user_directive_parse` directive |
| update_directive | update_user_directive | helpers_registry_user_directives_setters.json | ✅ EXISTS - Exact match |
| validate_user_directive | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - Handled by `user_directive_validate` directive |

**Verification Notes**:
- **activate/deactivate**: Combined into single helper `set_user_directive_activate(id, active, activated_at)` where `active` boolean controls activation state
- **detect_dependencies**: EXISTS as `get_user_directive_dependencies_by_directive(user_directive_id)`
- **generate_implementation_code**: EXISTS as `add_user_directive_implementation(...)`
- **install_dependency**: EXISTS as `add_user_directive_dependency(...)`
- **monitor_directive_execution**: EXISTS as multiple helpers: `get_user_directive_execution(id)`, `get_user_directive_executions_by_directive(user_directive_id)`, plus various filtered queries
- **parse_directive_file**: NOT NEEDED - AI handles parsing via `user_directive_parse` directive (NLP, format flexibility, handles ambiguity)
- **validate_user_directive**: NOT NEEDED - AI handles validation via `user_directive_validate` directive (interactive Q&A, semantic ambiguity resolution)

#### Project Helpers (17) - VERIFIED 2025-11-30

| helpers_parsed.json | Current Registry | Registry File | Status |
|---------------------|------------------|---------------|--------|
| create_project_blueprint | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - AI creates files via directives |
| read_project_blueprint | N/A - AI Uses Read Tool | N/A | ✅ NOT NEEDED - AI uses native Read tool directly |
| update_project_blueprint_section | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - AI updates files directly + DB checksum tracking via `update_project` |
| scan_existing_files | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - AI uses Glob/Grep/Read tools + DB queries |
| detect_and_init_project | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - AI queries DB + follows directives |
| create_project_directory | → CONSOLIDATE | → | 🔄 Consolidate into `initialize_aifp_project()` |
| initialize_project_db | → CONSOLIDATE | → | 🔄 Consolidate into `initialize_aifp_project()` |
| initialize_user_preferences_db | → CONSOLIDATE | → | 🔄 Consolidate into `initialize_aifp_project()` |
| validate_initialization | validate_initialization | helpers_registry_project_orchestrators.json | ✅ ADDED - Deterministic validation helper |
| infer_architecture | N/A - AI Directive Driven | N/A | ✅ NOT NEEDED - AI reasoning task, not code |
| get_project_context | get_work_context | helpers_registry_project_orchestrators.json | ✅ EXISTS - Orchestrator |
| get_project_files | get_files, get_file | helpers_registry_project_structure_getters.json | ✅ EXISTS - Multiple file queries |
| get_project_functions | get_functions, get_function | helpers_registry_project_structure_getters.json | ✅ EXISTS - Multiple function queries |
| get_project_status | get_project | helpers_registry_project_core.json | ✅ EXISTS - Project metadata getter |
| get_project_tasks | get_tasks, get_incomplete_tasks | helpers_registry_project_workflow_getters.json | ✅ EXISTS - Multiple task queries |
| get_status_tree | get_work_context, get_completion_path | helpers_registry_project_orchestrators.json | ✅ EXISTS - Functionality distributed |
| init_project_db | create_project | helpers_registry_project_core.json | ✅ EXISTS - "create" not "init" |
| query_project_db | query_project_state | helpers_registry_project_orchestrators.json | ✅ EXISTS - Orchestrator |

**Verification Notes**:
- **Blueprint Operations**: AI handles file operations (create/read/update) - MCP server cannot improve on AI's native Read tool
- **File Scanning**: AI uses Glob/Grep/Read tools more effectively than code could - AI "thought" is superior to restrictive code patterns
- **Project Detection**: AI queries DB and follows directives - no need for detection code
- **Initialization**: 3 helpers consolidated into single `initialize_aifp_project()` function (see details below)

**Notes on Resolved Helpers**:

**validate_initialization** - ✅ ADDED to `helpers_registry_project_orchestrators.json`
- **Decision**: KEEP as helper function
- **Rationale**: Deterministic validation task (file existence, database schema, table population) - code handles efficiently
- **Purpose**: Validates project initialization is complete and correct
- **Returns**: Result[bool, str] with specific error messages
- **Usage**: Called after project_init as sanity check
- **File**: `src/aifp/helpers/project/orchestrators/validation.py`

**infer_architecture** - ✅ NOT NEEDED (AI directive-driven)
- **Decision**: REMOVE - do not create helper function
- **Rationale**: Pattern recognition requiring flexible reasoning - AI reads code and understands architecture better than rigid directory scanning
- **AI Approach**: AI uses Read/Grep tools to analyze codebase and infer architectural patterns
- **Why not code**: Code-based directory scanning is too brittle, can't handle non-standard patterns, AI can read actual code

**Proposed: `initialize_aifp_project()` Unified Initialization Helper**

**Status**: DEFERRED - See `docs/aifp-oop-policy.md` for OOP handling policy decision

**Purpose**: Handle all project initialization (new and existing projects)

**Parameters**:
- `base_path` (str) - Project root directory path (where `.aifp-project/` will be created)
- `project_name` (str) - Name of the project
- `project_type` (str) - "new" or "existing"
- Additional project metadata parameters

**Behavior - New Project**:
1. Create `.aifp-project/` directory structure
2. Initialize all databases from schemas (project.db, user_preferences.db)
3. Create blank ProjectBlueprint.md template
4. Return success - AI must then populate initial data per directives before marking as initialized

**Behavior - Existing Project**:
1. Create `.aifp-project/` directory structure
2. Initialize all databases from schemas
3. Create blank ProjectBlueprint.md template
4. **OOP Detection and Handling** (see aifp-oop-policy.md):
   - AI scans for OOP patterns
   - AI evaluates project size
   - Small OOP: Offer conversion with warnings
   - Large OOP: Firm rejection, recommend MCP removal
5. Return project analysis for AI review

**⚠️ CRITICAL POLICY - OOP Projects**:

**Decision Made**: AIFP is FP-only. See `docs/aifp-oop-policy.md` for complete policy.

- **Large OOP projects**: Firm rejection, recommend MCP removal
- **Small OOP projects**: Offer conversion with warnings, recommend rejection
- **Rationale**: AIFP database only tracks functions (not OOP classes/methods/inheritance)
- **Alternative**: Initialize AIFP for new FP-only directory within existing OOP project

**Where to Add**: `helpers_registry_project_core.json` or new `helpers_registry_initialization.json` (implementation pending)

---

## Potentially Missing Helpers - REVIEWED

**Review Date**: 2025-11-30
**Review Status**: ✅ Complete

### ❌ REMOVE - AI Directive Driven (Not Helper Functions)

These should be handled by AI following directives, not as code/helper functions:

1. **create_project_blueprint**
   - **Reason**: AI has file creation access. Should be directive-driven, not a tool.
   - **Alternative**: AI creates file following project_init directive

2. **read_project_blueprint**
   - **Reason**: AI can use Read tool directly anytime.
   - **Alternative**: AI uses native Read tool

3. **update_project_blueprint_section**
   - **Reason**: No need for "section" concept. AI can update files directly and use DB getters/setters for checksum tracking.
   - **Alternative**: AI updates file + calls update_project (for checksum in DB)

4. **detect_and_init_project**
   - **Reason**: Should be AI and directive driven. AI can query DB to check init status and "think" through detection.
   - **Alternative**: AI queries project DB + uses directives

5. **scan_existing_files**
   - **Reason**: AI has broad "thought" capabilities and can scan directories/DB. Code is too restrictive.
   - **Alternative**: AI uses Glob/Grep/Read tools + DB queries

### 🔄 CONSOLIDATE - Combine Into Single Initialization

These should be unified into one initialization approach:

6. **create_project_directory**
7. **initialize_project_db**
8. **initialize_user_preferences_db**

**Recommendation**: Create single initialization script that:
- Takes path parameters for project directory and databases
- Creates directory structure from template
- Initializes all databases from schemas at once
- Creates blank ProjectBlueprint.md (AI must immediately populate per directives)
- Project not marked as initialized until AI completes initial setup

**Proposed Helper**: `initialize_aifp_project(project_path, project_name, ...)`

### ✅ KEEP - Validation Helper

9. **validate_initialization**
   - **Status**: NEEDED (but consider as directive, not necessarily code)
   - **Purpose**: Validation script to ensure directory structure is correct, databases created, initial data populated
   - **Decision**: Could be directive-based validation or a simple helper function
   - **Action**: Discuss implementation approach

### ⚠️ NEEDS DISCUSSION

10. **infer_architecture**
    - **Status**: Need to clarify purpose and scope
    - **Questions**:
      - What architecture aspects should be inferred?
      - Is this for existing codebases or new projects?
      - Should this be AI reasoning or code analysis?
    - **Action**: Define use case before deciding

11. **query_mcp_db**
    - **Status**: Generic query helper (last resort)
    - **Questions**:
      - Do we need a generic SQL query escape hatch?
      - Should AI use specific helpers instead?
    - **Action**: Review if specific helpers cover all use cases

### Medium Priority - Verify Naming

These likely exist but may have different names in registries:

1. User directive helpers (10) - Check for "user_directive_*" prefixes
2. Tracking helpers (2) - Check for specific tracking feature names
3. Project query helpers (6) - Check for more specific names

---

## Recommendations - UPDATED 2025-11-30

### Action 1: Verify User Directive Helpers ✅ COMPLETE

**Verification Date**: 2025-11-30

**Results**:
- ✅ activate_directive → EXISTS as `set_user_directive_activate(id, active, activated_at)`
- ✅ deactivate_directive → Same as above (uses `active=false`)
- ✅ generate_implementation_code → EXISTS as `add_user_directive_implementation(...)`
- ✅ monitor_directive_execution → EXISTS as multiple helpers: `get_user_directive_execution(id)`, `get_user_directive_executions_by_directive(user_directive_id)`, etc.
- ✅ parse_directive_file → NOT NEEDED - AI handles via `user_directive_parse` directive
- ✅ update_directive → EXISTS as `update_user_directive(...)`
- ✅ validate_user_directive → NOT NEEDED - AI handles via `user_directive_validate` directive

**Decision**: Parsing and validation are AI-driven operations (NLP, ambiguity resolution, interactive Q&A). Code cannot match AI's flexibility for understanding natural language directives.

**Status**: ✅ All 10 user directive helpers resolved - 8 exist in registry, 2 handled by AI directives

### Action 2: Create Unified Initialization Helper ✅ APPROVED

**Decision**: Create single initialization script instead of separate helpers

**NOT NEEDED - AI Directive Driven** (5 helpers removed):
- ❌ create_project_blueprint (AI creates files via directives)
- ❌ read_project_blueprint (AI uses Read tool directly)
- ❌ update_project_blueprint_section (AI updates files + DB checksum via `update_project`)
- ❌ detect_and_init_project (AI queries DB + follows directives)
- ❌ scan_existing_files (AI uses Glob/Grep/Read + DB queries - superior to code)

**CONSOLIDATE** (3 helpers → 1 unified function):
- 🔄 create_project_directory → `initialize_aifp_project()`
- 🔄 initialize_project_db → `initialize_aifp_project()`
- 🔄 initialize_user_preferences_db → `initialize_aifp_project()`

**Unified Function Spec**:
```python
initialize_aifp_project(
    base_path: str,           # Project root where .aifp-project/ is created
    project_name: str,
    project_type: str,        # "new" or "existing"
    # Additional metadata parameters
) -> Result[ProjectInitStatus, InitError]
```

**Behavior**:
- **New Projects**: Creates structure, initializes DBs, blank blueprint → AI populates per directives
- **Existing Projects**: Creates structure, initializes DBs, **evaluates existing code**, populates DB with discovered structure

**⚠️ CRITICAL - OOP Handling Decision Needed**:
When initializing existing OOP projects (not FP-compliant):
1. Dual-track: New FP code alongside existing OOP
2. Relaxed standards: Disable FP checks for this project
3. Reject: AIFP only for FP projects
4. Gradual migration: Track OOP "as-is", guide refactoring

**Action**: Review init directives before implementing. Decide OOP strategy.

**Where to add**: `helpers_registry_project_core.json` or new `helpers_registry_initialization.json`

### Action 3: Project Helper Resolution ✅ COMPLETE

**Summary**: 17 project helpers reviewed
- ✅ **10 Confirmed** - Exist in registry (get_project_*, query_project_state, get_work_context, etc.)
- ❌ **5 Removed** - AI directive-driven (blueprint ops, file scanning, project detection)
- 🔄 **3 Consolidated** - Into `initialize_aifp_project()`
- ⚠️ **2 Pending** - validate_initialization and infer_architecture need clarification

### Action 4: Resolve Remaining Ambiguous Helpers ✅ MOSTLY COMPLETE

**Resolved** (2 helpers):

1. **validate_initialization** - ✅ ADDED
   - **Decision**: KEEP as helper function
   - **Rationale**: Deterministic validation (file existence, database schema, table population) - code handles efficiently
   - **Implementation**: Added to `helpers_registry_project_orchestrators.json`
   - **File**: `src/aifp/helpers/project/orchestrators/validation.py`
   - **Usage**: Called after project_init as sanity check

2. **infer_architecture** - ✅ REMOVED
   - **Decision**: NOT NEEDED - AI directive-driven pattern recognition
   - **Rationale**: Pattern recognition requiring flexible reasoning - AI reads code and understands architecture better than rigid directory scanning
   - **AI Approach**: AI uses Read/Grep tools to analyze codebase
   - **Why not code**: Too brittle, can't handle non-standard patterns

**Resolved** (3 of 3):

3. **query_mcp_db** - ✅ NOT NEEDED
   - **Decision**: Do not create helper function
   - **Rationale**: Generic SQL escape hatch bypasses helper structure and directive patterns
   - **Recommendation**: All queries should go through specific helpers (enforces structure)
   - **Alternative**: AI can suggest new specific helpers when gaps are found
   - **Conclusion**: Specific helpers provide better structure and safety

---

## Conclusion

**Status**: ✅ **Review Complete - Clear Action Plan Established**

**Review Date**: 2025-11-30

The helpers_parsed.json file represents an **older, less granular specification** from helper-functions-reference.md (v1.0, dated 2025-10-22). Our current registries, built from info-helpers-*.txt files, have:

1. **More specific naming** (get_directives vs get_all_directives)
2. **Better granularity** (split generic helpers into specific queries)
3. **Modern orchestrators** (Layer 2 generic tools)
4. **Comprehensive coverage** (347 helpers vs 49 in parsed.json)

### Review Results Summary

**27 Total Helpers Reviewed** (11 project + 10 user directive + 6 remaining verification):

**11 "Potentially Missing Project Helpers"**:
- ❌ **5 Removed** - AI directive-driven, not helper functions (create_project_blueprint, read_project_blueprint, update_project_blueprint_section, detect_and_init_project, scan_existing_files)
- 🔄 **3 Consolidated** - Combined into single `initialize_aifp_project()` helper (create_project_directory, initialize_project_db, initialize_user_preferences_db)
- ✅ **2 Resolved** - validate_initialization (ADDED to registry), infer_architecture (AI-driven, not needed)
- 🆕 **1 To Create** - `initialize_aifp_project()` unified initialization function

**10 "User Directive Helpers" Verified**:
- ✅ **8 Confirmed** - All exist with slightly different names (set_user_directive_activate, add_user_directive_dependency, get_user_directive_dependencies_by_directive, add_user_directive_implementation, etc.)
- ✅ **2 Resolved** - parse_directive_file and validate_user_directive are AI directive-driven (via user_directive_parse and user_directive_validate directives)

**All Ambiguous Helpers Resolved**:
- ✅ **All 3 resolved** - validate_initialization (ADDED), infer_architecture (NOT NEEDED), query_mcp_db (NOT NEEDED)

### Final Recommendation

- ✅ Keep current registries as source of truth
- ✅ **11 potentially missing helpers reviewed and categorized**
- ✅ Archive helpers_parsed.json after verification
- ✅ No need to merge documentation (registries have better specs)
- 🔄 Create unified initialization helper
- ⚠️ Discuss validation approach and ambiguous helpers

---

**Next Actions**:
1. ✅ Verification complete - 11 potentially missing project helpers reviewed
2. ✅ User directive helper naming patterns verified - 8 exist, 2 AI-driven
3. ✅ Project helpers categorized - 5 removed (AI-driven), 3 consolidated, 2 resolved
4. ⏳ **Design and implement unified `initialize_aifp_project()` helper**:
   - Review initialization directives (project_init, etc.)
   - Review current registry helpers related to init
   - ✅ **OOP handling policy decided** - See `docs/aifp-oop-policy.md` (AIFP is FP-only)
   - Implement unified initialization function with OOP detection
   - Add to `helpers_registry_project_core.json` or new `helpers_registry_initialization.json`
5. ✅ **All 3 ambiguous helpers resolved**:
   - ✅ validate_initialization: ADDED to `helpers_registry_project_orchestrators.json`
   - ✅ infer_architecture: NOT NEEDED - AI directive-driven pattern recognition
   - ✅ query_mcp_db: NOT NEEDED - bypasses helper structure, use specific helpers
6. ⏳ Update helper registry files with all final decisions
7. ⏳ Archive helpers_parsed.json after full verification complete
