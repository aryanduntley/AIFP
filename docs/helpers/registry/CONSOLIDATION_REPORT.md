# Helper Registry Consolidation Report

**Date**: 2025-11-29 (Updated after verification)
**Purpose**: Analysis of 7 documentation files for incorporation into JSON registries
**Current Registry Status**: 347 helpers across 12 JSON files (8 orchestrators added)

---

## Executive Summary

**Files Reviewed**: 7
**Orchestrators Added**: ✅ 8 (4 MCP + 4 Project, plus get_work_context moved)
**helpers_parsed.json Verification**: ✅ Complete - See VERIFICATION_REPORT.md
**Directive-Helper Mappings**: ⏸️ Deferred (to be done with directive work)
**Documentation Files**: 5 kept as reference

**Completed Actions**:
1. ✅ **ADDED**: 8 orchestrator tools (Layer 2) to 2 new registry files
2. ✅ **VERIFIED**: helpers_parsed.json (49 helpers) - most exist with better names/organization
3. ⏸️ **DEFERRED**: Directive-helper mappings (62) - will use registry data for parser later
4. ✅ **DOCUMENTED**: Kept 5 architecture/spec files as reference
5. ✅ **READY TO ARCHIVE**: helpers_parsed.json after final user review

**Pending User Review**:
- 11 helpers from helpers_parsed.json not in info-helpers-*.txt (evaluate for addition)

---

## File-by-File Analysis

### 1. docs/directives-json/helpers_parsed.json

**Content**: 49 helpers with detailed specifications (older subset from helper-functions-reference.md v1.0)
**Status**: ✅ **VERIFICATION COMPLETE** - See VERIFICATION_REPORT.md for details

**Verification Summary**:
- **Total helpers**: 49
- **Exact name matches**: 12 (mostly git helpers)
- **Semantic matches**: ~37 (exist with different/better names in registries)
- **Not in info-helpers-*.txt**: 11 (require user evaluation)

**Key Findings**:
1. ✅ Current registries have **better organization** than helpers_parsed.json
2. ✅ Registries use more specific naming (e.g., `get_directives` vs generic `get_all_directives`)
3. ✅ Modern Layer 2 orchestrators subsume many generic helpers
4. ✅ 347 helpers in registries vs 49 in helpers_parsed.json (7x more comprehensive)

**11 Helpers NOT in info-helpers-*.txt (Require User Review)**:

These were in old helper-functions-reference.md but never in your source txt files:

**Project Initialization (7) - 🔍 EVALUATE FOR ADDITION**:
- create_project_blueprint
- read_project_blueprint
- update_project_blueprint_section
- initialize_project_db
- initialize_user_preferences_db
- create_project_directory
- validate_initialization

**Project Analysis (3) - 🔍 EVALUATE FOR ADDITION**:
- detect_and_init_project
- scan_existing_files
- infer_architecture

**MCP Query (1) - ❌ NOT NEEDED**:
- query_mcp_db (AI can do direct read-only queries; helper is redundant)

**Action**: User to review and evaluate 10 project helpers for potential addition (next session)

---

### 2. docs/directives-json/directive-helper-interactions.json

**Content**: 62 directive-helper mappings showing which directives use which helpers
**Status**: ⏸️ **DEFERRED** - Will be done with directive work

**Decision**:
- Current registries already have `used_by_directives` field
- Mappings in this file may be outdated compared to registry data
- When directives work begins, we'll use registry data to generate the directive_helpers table
- Parser will be rewritten to use registry as source of truth

**Action**: Keep this file for reference, but don't merge into registries now

---

### 3. docs/helpers/generic-tools-mcp.md

**Content**: 4 generic orchestrator tools (Layer 2) for MCP operations
**Status**: ✅ **ADDED TO REGISTRY**

**Actions Completed**:
1. ✅ Created `helpers_registry_mcp_orchestrators.json` with 4 tools:
   - find_directives: Intelligent directive discovery and matching
   - find_helpers: Helper function discovery
   - get_system_context: Complete AIFP system state
   - query_mcp_relationships: Relationship queries
2. ✅ All tools set to is_tool=true (MCP-exposed)
3. ✅ Updated HELPER_REGISTRY_STATUS.md
4. ✅ Keeping this file as Layer 2 architecture documentation

---

### 4. docs/helpers/generic-tools-project.md

**Content**: 5 generic orchestrator tools (Layer 2) for project operations
**Status**: ✅ **ADDED TO REGISTRY**

**Actions Completed**:
1. ✅ Created `helpers_registry_project_orchestrators.json` with 5 tools:
   - get_current_progress: Status queries with flexible scope/detail
   - update_project_state: Common state updates (task lifecycle, flows, files)
   - batch_update_progress: Atomic multi-item updates
   - query_project_state: Flexible SQL-like queries
   - get_work_context: Complete work resumption context (moved from workflow getters)
2. ✅ Moved get_work_context from workflow getters to orchestrators
3. ✅ Set is_tool=true for get_work_context (was false)
4. ✅ Updated HELPER_REGISTRY_STATUS.md (workflow getters 54→53)
5. ✅ Keeping this file as Layer 2 architecture documentation

---


### 5. docs/helpers/helper-architecture.md

**Content**: Three-tier helper function architecture description (Layers 1-4)
**Status**: ✅ **KEEPING AS REFERENCE**

**Action**: Keep as architecture documentation - provides essential design philosophy

---

### 6. docs/helpers/helper-tool-classification.md

**Content**: Classification guide for is_tool field (which helpers are MCP-exposed)
**Status**: ✅ **KEEPING AS REFERENCE**

**Action**: Keep as reference guide for future helper design decisions

---

### 7. docs/helpers/helper-functions-reference.md

**Content**: Old reference doc listing 50 helpers (v1.0, dated 2025-10-22)
**Status**: ⏸️ **ARCHIVE AFTER USER REVIEW**

**Action**: Archive to `docs/helpers/archive/` after user reviews 10 potentially missing helpers

---

## Summary of Completed Work

### ✅ Registry Files Created (2 new)

1. **helpers_registry_mcp_orchestrators.json** (4 tools)
   - find_directives
   - find_helpers
   - get_system_context
   - query_mcp_relationships

2. **helpers_registry_project_orchestrators.json** (5 tools)
   - get_current_progress
   - update_project_state
   - batch_update_progress
   - query_project_state
   - get_work_context (moved from workflow getters)

### ✅ Registry Files Modified (2 updated)

1. **helpers_registry_project_workflow_getters.json**
   - Removed get_work_context (moved to orchestrators)
   - Updated total_helpers: 54 → 53

2. **HELPER_REGISTRY_STATUS.md**
   - Added MCP orchestrators section
   - Added Project orchestrators section
   - Updated totals: 339 → 347 helpers
   - Updated database breakdowns

### ✅ Verification Completed

- helpers_parsed.json (49 helpers) verified against registries
- VERIFICATION_REPORT.md created with detailed findings
- 12 exact matches, ~37 semantic matches found
- 10 helpers flagged for user evaluation

### ⏸️ Deferred Work

- Directive-helper mappings (62) - will use registry for parser later
- Not merging directive-helper-interactions.json into registries now

---

## Files Requiring User Review (Next Session)

### 10 Project Helpers from helpers_parsed.json

These exist in helper-functions-reference.md but NOT in info-helpers-*.txt:

**Project Initialization (7)**:
1. create_project_blueprint
2. read_project_blueprint
3. update_project_blueprint_section
4. initialize_project_db
5. initialize_user_preferences_db
6. create_project_directory
7. validate_initialization

**Project Analysis (3)**:
8. detect_and_init_project
9. scan_existing_files
10. infer_architecture

**User Questions for Next Session**:
1. Are these helpers needed/useful for orchestrators?
2. Were they intentionally omitted from info-helpers files?
3. Should any be added to:
   - helpers_registry_project_core.json (initialization)?
   - helpers_registry_project_orchestrators.json (if Layer 2)?
   - helpers_registry_project_structure_getters.json (analysis)?

---

## Final Registry State

**Total Registry Files**: 12 (10 original + 2 orchestrators)
**Total Helpers**: 347 (339 + 8 orchestrators)

**Breakdown by Database**:
- aifp_core.db: 40 (36 + 4 orchestrators)
- user_preferences.db: 43
- user_directives.db: 78
- project.db: 186 (182 + 4 orchestrators + moved get_work_context)

**Documentation Files Kept**: 5
- helper-architecture.md
- helper-tool-classification.md
- generic-tools-mcp.md
- generic-tools-project.md
- directive-helper-interactions.json

**Files Ready for Archive/Removal**:
- helpers_parsed.json (after user reviews 10 helpers)
- helper-functions-reference.md (after user reviews 10 helpers)

---

## Recommendations for Next Session

1. **User reviews 10 project helpers** listed above
2. **Decide which (if any) to add** to registries
3. **Archive obsolete files** (helpers_parsed.json, helper-functions-reference.md)
4. **Begin directive registry work** (if helpers are complete)
5. **Create database import script** (when all helpers finalized)

---

**Status**: ✅ Helper registry consolidation complete pending user review of 10 helpers
**Next Action**: User evaluation of project init/analysis helpers
**Updated**: 2025-11-29
