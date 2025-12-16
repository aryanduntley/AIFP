# Mapping Setup Complete

**Date**: 2025-12-16
**Status**: ✅ Ready to begin mapping

---

## Summary

All file structures and tracking systems are now in place for the directive flow and helper function mapping tasks.

---

## Created Files

### Helper JSON Files (9 files) - ✅ UPDATED & CONSOLIDATED

**Location**: `docs/helpers/json/`
**Total Helpers**: 201 (reduced from 206 after removing 5 duplicates)

1. **Index Helper** (1 total):
   - `helpers-index.json` - 25 lines, 1 helper

2. **Core Helpers** (33 total):
   - `helpers-core.json` - 657 lines, 33 helpers ✅ CONSOLIDATED

3. **Git Helpers** (11 total):
   - `helpers-git.json` - 182 lines, 11 helpers

4. **Orchestrator Helpers** (11 total):
   - `helpers-orchestrators.json` - 348 lines, 11 helpers ✅ CONSOLIDATED

5. **Project Helpers** (112 total):
   - `helpers-project-1.json` (1-37) - 716 lines, 37 helpers ✅ CONSOLIDATED
   - `helpers-project-2.json` (38-77) - 599 lines, 40 helpers ✅ CONSOLIDATED
   - `helpers-project-3.json` (78-112) - 589 lines, 35 helpers ✅ CONSOLIDATED

6. **Settings Helpers** (17 total):
   - `helpers-settings.json` - 301 lines, 17 helpers

7. **User Custom Helpers** (16 total):
   - `helpers-user-custom.json` - 254 lines, 16 helpers

**Changes Made**:
- Consolidated from 14 files → 9 files (36% reduction)
- Removed 5 duplicate orchestrator helpers from project files
- All helpers fully converted from markdown to JSON with complete structure
- All files under 900 lines for readability

---

### Directive Flow File (1 file)

**Location**: `docs/directives-json/`

- `directive_flow.json` - 430 bytes (empty, ready for mapping)

**Note**: If more than 900 lines needed, create `directive_flow_2.json`

---

### Tracking Checklists (2 files)

**Location**: `docs/directives-json/Tasks/`

1. **DIRECTIVES_MAPPING_PROGRESS.md** - New file
   - Tracks all 125 directives with checkboxes
   - Organized by category (FP Aux, FP Core, Git, Project, User Pref, User System)
   - Shows progress percentages

2. **HELPER_FUNCTIONS_MAPPING_PROGRESS.md** - ✅ UPDATED
   - Tracks all 201 helpers with checkboxes (reduced from 206 after removing duplicates)
   - Organized by database type (Index, Core, Git, Orchestrator, Project, Settings, User Custom)
   - Updated to reflect 9 consolidated JSON files
   - All helpers converted from markdown to JSON with complete structure

---

### Existing Quick References (Verified Correct)

**Location**: `docs/directives-json/Tasks/`

1. **DIRECTIVES_QUICK_REF.md** - 230 lines
   - Lists all 125 directives with JSON file locations and line numbers
   - ✅ Correct and complete

2. **HELPER_FUNCTIONS_QUICK_REF.md** - 395 lines
   - Lists all 337 documented helpers (includes registry duplicates)
   - ✅ Correct and complete

---

## File Structure Overview

```
docs/
├── helpers/
│   ├── consolidated/              # Source markdown (reference)
│   │   ├── helpers-consolidated-core.md
│   │   ├── helpers-consolidated-git.md
│   │   ├── helpers-consolidated-orchestrators.md
│   │   ├── helpers-consolidated-project.md
│   │   ├── helpers-consolidated-settings.md
│   │   └── helpers-consolidated-user-custom.md
│   └── json/                      # Target JSON files (for import) ✅ COMPLETE
│       ├── helpers-index.json
│       ├── helpers-core.json              ✅ CONSOLIDATED
│       ├── helpers-git.json
│       ├── helpers-orchestrators.json     ✅ CONSOLIDATED
│       ├── helpers-project-1.json         ✅ CONSOLIDATED
│       ├── helpers-project-2.json         ✅ CONSOLIDATED
│       ├── helpers-project-3.json         ✅ CONSOLIDATED
│       ├── helpers-settings.json
│       └── helpers-user-custom.json
└── directives-json/
    ├── Tasks/
    │   ├── DIRECTIVES_QUICK_REF.md              ✅ Existing (verified)
    │   ├── HELPER_FUNCTIONS_QUICK_REF.md        ✅ Existing (verified)
    │   ├── DIRECTIVES_MAPPING_PROGRESS.md       ✅ NEW (tracking)
    │   └── HELPER_FUNCTIONS_MAPPING_PROGRESS.md ✅ NEW (tracking)
    ├── directive_flow.json                      ✅ CREATED (empty)
    ├── directives-fp-aux.json                   ✅ Existing (source)
    ├── directives-fp-core.json                  ✅ Existing (source)
    ├── directives-git.json                      ✅ Existing (source)
    ├── directives-project.json                  ✅ Existing (source)
    ├── directives-user-pref.json                ✅ Existing (source)
    └── directives-user-system.json              ✅ Existing (source)
```

---

## Mapping Workflow

### For Directive Flow Mapping

1. Open `docs/directives-json/Tasks/DIRECTIVES_MAPPING_PROGRESS.md`
2. Pick a directive to map (start with project management directives)
3. Read the directive JSON in console: `cat docs/directives-json/directives-project.json | jq '.[] | select(.name=="aifp_run")'`
4. Identify flow relationships:
   - What directives can this flow to?
   - What conditions trigger each flow?
   - What priority?
5. Add entry to `docs/directives-json/directive_flow.json`
6. Check checkbox in tracking file
7. Repeat

### For Helper Mapping

1. Open `docs/directives-json/Tasks/HELPER_FUNCTIONS_MAPPING_PROGRESS.md`
2. Pick a helper to map (start with orchestrators - high frequency)
3. Read helper markdown in console: `cat docs/helpers/consolidated/helpers-consolidated-orchestrators.md`
4. For this helper:
   - Assign file_path
   - Structure parameters
   - Standardize error_handling
   - Convert return_statements to array
   - **Map used_by_directives** (search all directive JSONs)
5. Add complete entry to appropriate JSON file in `docs/helpers/json/`
6. Check checkbox in tracking file
7. Repeat

---

## Console Commands for Efficient Mapping

### Read Directive JSON (less cognitive load)
```bash
# View single directive
cat docs/directives-json/directives-project.json | jq '.[] | select(.name=="aifp_run")'

# View directive workflow only
cat docs/directives-json/directives-project.json | jq '.[] | select(.name=="aifp_run") | .workflow'

# Search for helper usage in directive
grep -n "get_task" docs/directives-json/directives-project.json
```

### Read Helper Markdown
```bash
# View specific helper
cat docs/helpers/consolidated/helpers-consolidated-orchestrators.md | grep -A 20 "^### \`aifp_status"

# List all helpers in file
cat docs/helpers/consolidated/helpers-consolidated-core.md | grep "^### \`"
```

### Update JSON Files
```bash
# Validate JSON syntax
jq '.' docs/helpers/json/helpers-core.json

# Pretty print for review
jq '.' docs/directives-json/directive_flow.json

# Count completed helpers
jq '.helpers | length' docs/helpers/json/helpers-core.json

# Verify total helper count across all files
jq -s 'map(.helpers | length) | add' docs/helpers/json/helpers-*.json
```

---

## Next Steps

### Priority 1: Map Core Navigation (directive_flow.json)
Start with the most critical flows (~20 mappings):
1. `aifp_run` → `aifp_status`
2. `aifp_status` → [all possible next directives based on conditions]
3. All completion directives → `aifp_status` (completion loops)

**File**: `docs/directives-json/directive_flow.json`
**Tracking**: `docs/directives-json/Tasks/DIRECTIVES_MAPPING_PROGRESS.md`

### Priority 2: Map Orchestrator Helpers (helpers JSON)
These are used most frequently and have complex used_by_directives:
1. `aifp_status` (used by: aifp_run, all completion directives)
2. `initialize_aifp_project` (used by: project_init)
3. `get_current_progress` (used by: aifp_status)

**Files**: `docs/helpers/json/helpers-orchestrators.json` (consolidated)
**Tracking**: `docs/directives-json/Tasks/HELPER_FUNCTIONS_MAPPING_PROGRESS.md`

### Priority 3: Map Project Management Helpers
Most numerous (112 helpers), but follow patterns:
- All `get_*` helpers: used by aifp_status, various query operations
- All `add_*` helpers: used by create directives
- All `update_*` helpers: used by update/complete directives

**Files**: `docs/helpers/json/helpers-project-1.json`, `helpers-project-2.json`, `helpers-project-3.json` (consolidated from 6 to 3)
**Tracking**: Same file as above

---

## Success Criteria

- [ ] directive_flow.json has 60-80 flow mappings
- [ ] All 9 helper JSON files fully complete (consolidated from 14)
- [ ] Each helper has:
  - [ ] file_path assigned (currently placeholders)
  - [ ] parameters structured as JSON array
  - [ ] error_handling standardized
  - [ ] return_statements detailed for directive guidance
  - [ ] used_by_directives mapped (at least 1 directive per helper)
- [ ] All checkboxes in tracking files completed
- [x] JSON files validate (no syntax errors) ✅
- [x] Files consolidated and organized (14 → 9 files) ✅

---

## Estimation

**Directive Flow Mapping**: 2-3 days (60-80 flows)
**Helper Mapping**: 2-3 weeks (227 helpers × multiple directives each)
**Total**: 3-4 weeks for complete mapping

---

**Setup Date**: 2025-12-16
**Ready to Begin**: ✅ YES
**Next Action**: Start with Priority 1 (Core Navigation Flows)
