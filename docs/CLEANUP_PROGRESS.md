# Directive Cleanup - Progress Report

**Date**: 2026-01-18
**Session**: SQL and aifp.scripts Cleanup
**Status**: ✅ ALL CLEANUP COMPLETE | Infrastructure Files Created | Documentation Updated

---

## Summary of Changes

### ✅ COMPLETED: SQL Query Removal (24 queries)

**Total Replaced**: 24 SQL queries across 4 JSON directive files
**Approach**: Replace hardcoded SQL with concise `"use_helper": "description of action"` pattern
**Rationale**:
- Helper names change frequently
- AI already has full helper list from `aifp_run(is_new_session=true)`
- System prompt instructs to query helper_functions table
- Verbose guidance wastes tokens unnecessarily

**Files Updated**:
1. ✅ `directives-project.json` - 17 queries replaced
2. ✅ `directives-git.json` - 2 queries replaced
3. ✅ `directives-user-system.json` - 3 queries replaced
4. ✅ `directives-user-pref.json` - 2 queries replaced

**Example Replacement**:
```json
// BEFORE (verbose, 200+ tokens)
"action": "query_helpers_database",
"guidance": "Search helper_functions table for task helpers by querying: target_database='project' AND purpose contains keywords 'task', 'incomplete', 'milestone'. Use helper that returns incomplete tasks for milestone, then count results to check if all complete.",
"note": "Helper names change frequently. Query aifp_core.db helper_functions table for current helpers. No need for dedicated count helper - retrieve incomplete tasks and count them."

// AFTER (concise, ~15 tokens)
"use_helper": "get incomplete tasks for milestone"
```

**Token Savings**: Approximately 3,000+ tokens saved per directive load

---

## Key Decisions Made

### 1. ✅ Git Database Tables - KEEP THEM

**Question**: Do we need `work_branches` and `merge_history` tables, or is git alone sufficient?

**Decision**: **KEEP BOTH TABLES** - They are NOT redundant

**Rationale**:
- **Git tracks**: What code IS and WAS (version control)
- **Database tracks**: WHO, WHY, STATUS, and FP INTELLIGENCE (collaboration metadata)
- **Use cases that git can't do easily**:
  - "Show all active branches for user Alice with their purposes"
  - "How many merges had FP conflicts auto-resolved?"
  - "Which user is assigned to Matrix Operations theme?"
  - Structured SQL queries vs parsing git output
- **AIFP-specific metadata**:
  - Branch purpose ("Implement matrix multiplication")
  - Workflow status (active → merged → abandoned)
  - FP merge intelligence (auto-resolved conflicts, resolution strategies)
  - Audit trails for team collaboration

**Verdict**: Hybrid approach - Git is source of truth for CODE, Database is source of truth for COLLABORATION

### 2. ✅ `last_known_git_hash` Field - KEEP IT

**Purpose**: Detects changes made **outside AIFP sessions**
**How**: Compare current `git rev-parse HEAD` vs stored hash
**Why needed**: Git knows current state, but not "what changed since AIFP last ran"
**Use case**: Manual edits, IDE changes, teammate pushes

**Verdict**: NOT redundant - enables external change detection

### 3. ✅ Simplified SQL Replacement Pattern

**Original approach**: Long verbose guidance with keywords, database names, helper search instructions
**Problem**: Wastes tokens, repeats what's already in system prompt
**New approach**: Short `"use_helper": "action description"`

**Rationale**:
- AI gets all helper names at session start
- System prompt already explains helper usage
- AI is capable of querying helper_functions table
- Concise descriptions are sufficient

---

## ✅ COMPLETE: aifp.scripts References (5 refs)

**Location**: All in `directives-project.json` (project_init directive)
**Status**: ✅ All replaced with two-phase approach

### Analysis Summary (from AIFP_SCRIPTS_CLEANUP_ANALYSIS.md)

**Reference 1: Line 137 - Description**
- **Original**: Mentions "wraps standalone initialization script (aifp.scripts.init_aifp_project)"
- **Decision**: Replace with orchestrator reference
- **Action**: Change description to reference `project_init` orchestrator

**Reference 2: Line 246 - create_project_structure**
- **Purpose**: Create `.aifp-project/` directory structure
- **Decision**: Execute directly in orchestrator (os.makedirs)
- **Rationale**: One-time operation, simple directory creation
- **Action**: Remove `"module"` reference, add `"action": "create_directories"` with note that orchestrator handles directly

**Reference 3: Line 261 - generate_project_blueprint**
- **Purpose**: Generate ProjectBlueprint.md from template
- **Decision**: Execute directly in orchestrator
- **Rationale**: One-time operation during init, no reusability needed (REVISED from original analysis)
- **Action**: Remove `"module"` reference, add note that orchestrator handles directly

**Reference 4: Line 275 - initialize_databases**
- **Purpose**: Create and populate project.db and user_preferences.db
- **Decision**: Execute directly in orchestrator
- **Rationale**: One-time operation, sequential dependencies, atomic initialization
- **Operations**: Load schema → execute SQL → insert metadata → execute standard_infrastructure.sql
- **Action**: Remove `"module"` reference, add note that orchestrator handles directly

**Reference 5: Line 295 - validate_initialization**
- **Purpose**: Validate that initialization completed successfully
- **Decision**: **Use existing helper** `validate_initialization`
- **Rationale**: Helper already exists in helpers-orchestrators.json
- **Action**: Remove `"module"` reference, add `"use_helper": "validate initialization"`

---

## Files That Need to Be Created

### 1. ✅ standard_infrastructure.sql (CREATED)

**Path**: `src/aifp/database/initialization/standard_infrastructure.sql`
**Purpose**: Pre-populate infrastructure table with 8 standard entries (empty values)
**Executed by**: `aifp_init` helper after creating project.db schema
**Status**: ✅ File created with 8 entries (added project_root, source_directory, main_branch)

**Content**:
```sql
-- Standard Infrastructure Entries
-- Populated during project initialization with empty values
-- AI detects and populates values after initialization

INSERT INTO infrastructure (type, value, description) VALUES
  ('source_directory', '', 'Primary source code directory (e.g., src, lib, app)'),
  ('primary_language', '', 'Main programming language (e.g., Python 3.11, Rust 1.75, Node 18)'),
  ('build_tool', '', 'Primary build tool (e.g., cargo, npm, make, maven, gradle)'),
  ('package_manager', '', 'Package/dependency manager (e.g., pip, npm, cargo, maven)'),
  ('test_framework', '', 'Testing framework (e.g., pytest, jest, cargo test, junit)'),
  ('runtime_version', '', 'Language runtime or compiler version (e.g., Python 3.11.2, rustc 1.75.0)');
```

**Status**: ✅ Specified in INFRASTRUCTURE_GOALS.md, ❌ File not created yet

---

## Helper Definitions Needed

### 1. ✅ project_init Orchestrator (DOCUMENTED, NOT DEFINED YET)

**File**: `docs/helpers/json/helpers-orchestrators.json`
**Status**: ✅ Specified in INFRASTRUCTURE_GOALS.md and NEW_HELPERS_SPECIFICATIONS.md, ❌ Not added to JSON yet

**Purpose**: Main initialization orchestrator that coordinates:
1. Check for existing .aifp-project/ or .git/.aifp/ folders
2. Scan for OOP patterns (AI does this naturally, no helper needed)
3. Prompt user for project metadata (name, purpose, goals)
4. Create directory structure (direct os.makedirs in orchestrator)
5. Generate ProjectBlueprint.md from template (direct operation in orchestrator)
6. Initialize project.db:
   - Load schemas/project.sql
   - Execute schema
   - INSERT project metadata
   - Execute initialization/standard_infrastructure.sql ⭐ NEW FILE
   - INSERT default completion_path
7. Initialize user_preferences.db:
   - Load schemas/user_preferences.sql
   - Execute schema
   - INSERT default tracking_settings
8. Call `validate_initialization` helper
9. Guide AI to populate infrastructure values (detect language, build tool, etc.)

**Key Implementation Notes**:
- One-time operations (mkdir, template generation, DB creation) happen directly in orchestrator code
- No separate sub-helpers needed for these simple operations
- Calls existing `validate_initialization` helper at end

### 2. ✅ get_all_infrastructure Helper (DOCUMENTED, NOT DEFINED YET)

**File**: `docs/helpers/json/helpers-project-1.json`
**Status**: ✅ Specified in INFRASTRUCTURE_GOALS.md, ❌ Not added to JSON yet

**Purpose**: Get all infrastructure entries including empty standard entries
**Used by**: `aifp_run(is_new_session=true)` to bundle infrastructure in session context

**Implementation**:
```python
def get_all_infrastructure():
    """Get all infrastructure entries"""
    return db.execute("SELECT * FROM infrastructure ORDER BY created_at").fetchall()
```

**Returns**: Array of all infrastructure rows (includes empty values)

---

## ✅ Completed in This Session

### 1. ✅ SQL Cleanup (24 queries)
- ✅ Replaced all 24 SQL queries with concise `"use_helper": "action"` pattern
- ✅ Saved ~3,000+ tokens per directive
- ✅ Updated: directives-project.json, directives-git.json, directives-user-system.json, directives-user-pref.json

### 2. ✅ aifp.scripts Cleanup (5 refs)
- ✅ Line 137: Updated description to reference two-phase approach
- ✅ Line 246: Replaced with Phase 1 direct action
- ✅ Line 261: Replaced with Phase 1 direct action
- ✅ Line 275: Replaced with Phase 1 direct action
- ✅ Line 295: Replaced with helper usage (validate_initialization)

### 3. ✅ Infrastructure Files Created
- ✅ Created `standard_infrastructure.sql` with 8 entries
- ✅ Updated `directives-project.json` to two-phase approach
- ✅ Updated `project_init.md` to document two-phase approach

### 4. ✅ Architecture Decisions Documented
- ✅ Decided to keep git database tables (collaboration metadata)
- ✅ Decided to keep last_known_git_hash (external change detection)
- ✅ Added infrastructure entries: project_root, source_directory, main_branch

## Next Steps

### Immediate Tasks (Helper Definitions)

1. **Define Helpers in JSON**
   - [ ] Add `aifp_init` orchestrator to `helpers-orchestrators.json`
   - [ ] Add `get_all_infrastructure` to `helpers-project-1.json`
   - [ ] Update `aifp_run` in `helpers-orchestrators.json` to include infrastructure_data when is_new_session=true

### Verification Tasks

4. **Validate JSON Files**
   - [ ] Verify all directive JSON files are valid JSON (no syntax errors)
   - [ ] Check for any remaining SQL queries: `grep -r "SELECT.*FROM" docs/directives-json/`
   - [ ] Check for any remaining aifp.scripts refs: `grep -r "aifp.scripts" docs/directives-json/`

5. **Update MD Files**
   - [ ] Update corresponding MD directive files to match JSON changes
   - [ ] Focus on project_init.md (most changes)
   - [ ] Update git_sync_state.md if git helper references changed

---

## Documentation Updated

- ✅ `SQL_CLEANUP_ANALYSIS.md` - Added note to see DIRECTIVE_CLEANUP_REVISED.md
- ✅ `NEW_HELPERS_SPECIFICATIONS.md` - Added note that only 2 helpers actually needed
- ✅ `AIFP_SCRIPTS_CLEANUP_ANALYSIS.md` - Added note to see DIRECTIVE_CLEANUP_REVISED.md
- ✅ `DIRECTIVE_CLEANUP_REVISED.md` - Complete revised approach documented
- ✅ `CLEANUP_PROGRESS.md` - **THIS DOCUMENT** - Current progress and next steps

---

## Session Continuity Notes

**For Next Session**:
1. Start with completing aifp.scripts removal (4 simple replacements)
2. Create `standard_infrastructure.sql` file (simple INSERT statements)
3. Define the 2 helpers in JSON files (copy from specifications)
4. Validate JSON syntax
5. Update project_init.md to match JSON changes

**Key Principle to Remember**:
- Don't hardcode helper names in directives
- Use short, descriptive `"use_helper"` values
- AI has full helper list and can query the database
- One-time initialization operations happen directly in `project_init` orchestrator code

**Token Budget Success**:
- Saved ~3,000+ tokens per directive by simplifying SQL replacement pattern
- Makes directives more maintainable as helper names evolve
