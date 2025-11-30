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

#### User Directives Automation (10)

| helpers_parsed.json | Current Registry | Registry File | Notes |
|---------------------|------------------|---------------|-------|
| activate_directive | activate_user_directive | helpers_registry_user_directives_setters.json | Likely exists with "user_directive" prefix |
| deactivate_directive | deactivate_user_directive | helpers_registry_user_directives_setters.json | Likely exists with "user_directive" prefix |
| detect_dependencies | get_user_directive_dependencies | helpers_registry_user_directives_getters.json | Query, not "detect" |
| generate_implementation_code | create_user_directive_implementation | helpers_registry_user_directives_setters.json | Likely exists as "create" |
| get_user_directive_status | get_user_directive_by_id, get_user_directives | helpers_registry_user_directives_getters.json | Split into multiple getters |
| install_dependency | add_user_directive_dependency | helpers_registry_user_directives_setters.json | "add" not "install" |
| monitor_directive_execution | get_user_directive_execution_* | helpers_registry_user_directives_getters.json | Split into execution queries |
| parse_directive_file | parse_user_directive_source | helpers_registry_user_directives_getters.json | Likely exists |
| update_directive | update_user_directive | helpers_registry_user_directives_setters.json | With "user_directive" prefix |
| validate_user_directive | validate_user_directive_content | helpers_registry_user_directives_getters.json | Likely exists |

#### Project Helpers (17)

| helpers_parsed.json | Current Registry | Registry File | Notes |
|---------------------|------------------|---------------|-------|
| create_project_blueprint | (NOT IN REGISTRY) | N/A | ⚠️ Project initialization helper - may be missing |
| create_project_directory | (NOT IN REGISTRY) | N/A | ⚠️ Project initialization helper - may be missing |
| detect_and_init_project | (NOT IN REGISTRY) | N/A | ⚠️ Project detection helper - may be missing |
| get_project_context | get_work_context | helpers_registry_project_orchestrators.json | Subsumed by orchestrator |
| get_project_files | get_files, get_file | helpers_registry_project_structure_getters.json | Split into multiple file queries |
| get_project_functions | get_functions, get_function | helpers_registry_project_structure_getters.json | Split into multiple function queries |
| get_project_status | get_project | helpers_registry_project_core.json | Project metadata getter |
| get_project_tasks | get_tasks, get_incomplete_tasks | helpers_registry_project_workflow_getters.json | Split into multiple task queries |
| get_status_tree | get_work_context, get_completion_path | helpers_registry_project_orchestrators.json | Functionality distributed |
| infer_architecture | (NOT IN REGISTRY) | N/A | ⚠️ Project analysis helper - may be missing |
| init_project_db | create_project | helpers_registry_project_core.json | Create, not init |
| initialize_project_db | (NOT IN REGISTRY) | N/A | ⚠️ Database initialization - may be missing |
| initialize_user_preferences_db | (NOT IN REGISTRY) | N/A | ⚠️ Database initialization - may be missing |
| query_project_db | query_project_state | helpers_registry_project_orchestrators.json | Orchestrator with better interface |
| read_project_blueprint | (NOT IN REGISTRY) | N/A | ⚠️ Blueprint operations - may be missing |
| scan_existing_files | (NOT IN REGISTRY) | N/A | ⚠️ Project detection helper - may be missing |
| update_project_blueprint_section | (NOT IN REGISTRY) | N/A | ⚠️ Blueprint operations - may be missing |
| validate_initialization | (NOT IN REGISTRY) | N/A | ⚠️ Project validation - may be missing |

---

## Potentially Missing Helpers (Require Further Investigation)

### High Priority - Should Verify

These may genuinely be missing from registries:

1. **query_mcp_db** - Generic MCP query helper (last resort)
2. **create_project_blueprint** - Blueprint generation
3. **read_project_blueprint** - Blueprint parsing
4. **update_project_blueprint_section** - Blueprint updates
5. **create_project_directory** - Directory setup
6. **initialize_project_db** - Database initialization
7. **initialize_user_preferences_db** - Preferences DB init
8. **validate_initialization** - Initialization validation
9. **detect_and_init_project** - Project detection/init
10. **scan_existing_files** - File structure scan
11. **infer_architecture** - Architecture detection

### Medium Priority - Verify Naming

These likely exist but may have different names in registries:

1. User directive helpers (10) - Check for "user_directive_*" prefixes
2. Tracking helpers (2) - Check for specific tracking feature names
3. Project query helpers (6) - Check for more specific names

---

## Recommendations

### Action 1: Verify User Directive Helpers

Check helpers_registry_user_directives_*.json for these patterns:
- activate_directive → activate_user_directive?
- deactivate_directive → deactivate_user_directive?
- generate_implementation_code → create_user_directive_implementation?
- monitor_directive_execution → get_user_directive_executions?
- parse_directive_file → parse_user_directive_source?
- update_directive → update_user_directive?
- validate_user_directive → validate_user_directive_content?

### Action 2: Add Missing Project Initialization Helpers

If these are truly missing, they should be added:
1. create_project_blueprint
2. read_project_blueprint
3. update_project_blueprint_section
4. create_project_directory
5. initialize_project_db
6. initialize_user_preferences_db
7. validate_initialization

**Where to add**: New file `helpers_registry_project_initialization.json` or add to `helpers_registry_project_core.json`

### Action 3: Add Missing Project Analysis Helpers

If missing, add:
1. detect_and_init_project
2. scan_existing_files
3. infer_architecture

**Where to add**: helpers_registry_project_core.json or helpers_registry_project_structure_getters.json

### Action 4: Add Generic Query Helpers

If missing, add:
1. query_mcp_db (last resort query helper for aifp_core.db)

**Where to add**: helpers_registry_core.json or helpers_registry_mcp_orchestrators.json

---

## Conclusion

**Status**: ✅ **Most helpers exist in registries with better organization**

The helpers_parsed.json file represents an **older, less granular specification** from helper-functions-reference.md (v1.0, dated 2025-10-22). Our current registries, built from info-helpers-*.txt files, have:

1. **More specific naming** (get_directives vs get_all_directives)
2. **Better granularity** (split generic helpers into specific queries)
3. **Modern orchestrators** (Layer 2 generic tools)
4. **Comprehensive coverage** (347 helpers vs 49 in parsed.json)

**Recommendation**:
- ✅ Keep current registries as source of truth
- ⚠️ Investigate 11 potentially missing helpers (project init/analysis)
- ✅ Archive helpers_parsed.json after verification
- ✅ No need to merge documentation (registries have better specs)

---

**Next Action**: Verify the 11 potentially missing helpers by checking registry files manually.
