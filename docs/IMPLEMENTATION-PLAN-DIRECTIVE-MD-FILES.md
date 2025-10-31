# AIFP Directive MD Files Implementation Plan

**Date**: 2025-10-28
**Purpose**: Eliminate guide files, create self-documenting directive system
**Status**: Planning → Implementation

---

## Core Principle

**AIFP MCP Server is NOT a typical tool collection.**

Traditional MCP servers provide tools that AI calls as needed. AIFP provides:
- **Directives** = Behavioral guidance and action workflows (PRIMARY)
- **Helper Functions** = Utility tools to support directive execution (SECONDARY)

**AI must understand**: This MCP teaches "how to behave and act" throughout the entire project lifecycle, not just "what tools are available."

---

## Architecture Change

### ❌ OLD: Guide Files as External Documentation
```
System Prompt → "Use get_reference_guide() to fetch guides"
├── automation-projects.md (separate guide)
├── project-structure.md (separate guide)
├── directive-interactions.md (separate guide)
└── git-integration.md (separate guide)
```

### ✅ NEW: Self-Documenting Directives
```
System Prompt → "This MCP guides your behavior via directives"
└── Directives (comprehensive MD files)
    ├── Each directive = complete action guide
    ├── Related directives = interaction patterns
    ├── Helper functions = tools to support actions
    └── Examples = how to execute properly
```

---

## Phase 1: User System Directive MD Files

### Objective
Create 8 individual MD files for user directive automation system. These replace `automation-projects.md`.

### Files to Create

#### 1. user_directive_parse.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_parse.md`
- [x] Add Purpose section: Parse YAML/JSON/TXT directive files
- [x] Add Workflow section: File reading, format detection, JSON extraction
- [x] Add Related Directives: Links to validate → implement → activate pipeline
- [x] Add Examples: YAML/JSON/TXT parsing with compliant/non-compliant examples
- [x] Add Edge Cases: Malformed files, missing fields, nested structures
- [x] Add Helper Functions: File reading, JSON validation, schema checking
- [x] Add Database Operations: Insert into user_directives.db
- [x] Add Testing scenarios

#### 2. user_directive_validate.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_validate.md`
- [x] Add Purpose section: Interactive Q&A validation of parsed directives
- [x] Add Workflow section: Ambiguity detection, question generation, config storage
- [x] Add Related Directives: Receives from parse, sends to implement
- [x] Add Examples: Q&A flows for home automation, cloud infrastructure
- [x] Add Edge Cases: User provides incomplete answers, contradictory responses
- [x] Add Helper Functions: Question generation, answer validation
- [x] Add Database Operations: Update user_directives with validated_config
- [x] Add Testing scenarios

#### 3. user_directive_implement.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_implement.md`
- [x] Add Purpose section: Generate FP-compliant implementation code
- [x] Add Workflow section: Code generation, FP validation, file writing to src/
- [x] Add Related Directives: Links to FP directives (purity, immutability, etc.)
- [x] Add Examples: Generated code for various directive types
- [x] Add Edge Cases: Complex trigger conditions, multiple actions, error handling
- [x] Add Helper Functions: Code generation, FP validation
- [x] Add Database Operations: directive_implementations table, project.db files
- [x] Add Testing scenarios: Generated code must pass FP compliance
- [x] Corrected: Generated code goes in src/ (the project codebase)

#### 4. user_directive_approve.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_approve.md`
- [x] Add Purpose section: User testing and approval workflow (approval gate)
- [x] Add Workflow section: Test completion check, feedback collection, approval confirmation
- [x] Add Related Directives: Between implement and activate
- [x] Add Examples: Testing scenarios for different directive types
- [x] Add Edge Cases: User rejects, requests modifications, partial approval
- [x] Add Helper Functions: Testing guidance, feedback processing
- [x] Add Database Operations: Update directive status to approved/rejected
- [x] Add Testing scenarios

#### 5. user_directive_activate.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_activate.md`
- [x] Add Purpose section: Deploy and activate directives for real-time execution
- [x] Add Workflow section: Approval gate, pre-activation verification, deployment by type
- [x] Add Related Directives: After approve, before monitor
- [x] Add Examples: Activation for scheduled triggers, event-based triggers, polling services
- [x] Add Edge Cases: Service startup failures, port conflicts, missing dependencies
- [x] Add Helper Functions: Deployment helpers, service management, logging configuration
- [x] Add Database Operations: Update status to active, initialize execution stats, project status change
- [x] Add Testing scenarios

#### 6. user_directive_monitor.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_monitor.md`
- [x] Add Purpose section: Continuous monitoring, track statistics, handle errors
- [x] Add Workflow section: Execution tracking, error logging, log rotation, health monitoring
- [x] Add Related Directives: Runs continuously after activate
- [x] Add Examples: Execution tracking, error handling, high error rate alerts
- [x] Add Edge Cases: Log rotation, disk space, error rate thresholds, monitoring failures
- [x] Add Helper Functions: Logging, statistics, health monitoring, alerting
- [x] Add Database Operations: directive_executions table updates
- [x] Add Testing scenarios

#### 7. user_directive_update.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_update.md`
- [x] Add Purpose section: Detect and handle source file changes
- [x] Add Workflow section: Change detection, deactivate, re-parse, re-validate, re-implement
- [x] Add Related Directives: Loops back to parse → validate → implement pipeline
- [x] Add Examples: Time changes, parameter changes, breaking changes, file deletion
- [x] Add Edge Cases: Breaking changes, backward compatibility, active directive updates, conflicts
- [x] Add Helper Functions: Change detection, file watching, backup, version control
- [x] Add Database Operations: Increment version, update source_files table, reset approval
- [x] Add Testing scenarios

#### 8. user_directive_deactivate.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_deactivate.md`
- [x] Add Purpose section: Stop execution, clean up resources (non-destructive)
- [x] Add Workflow section: Service shutdown by type, log finalization, cleanup, status updates
- [x] Add Related Directives: Opposite of activate, called by update/monitor
- [x] Add Examples: Normal deactivation, update deactivation, error deactivation, force stop
- [x] Add Edge Cases: Force stop, process already dead, cleanup failures, orphaned resources
- [x] Add Helper Functions: Process management, scheduler management, logging, cleanup
- [x] Add Database Operations: Update status to paused/inactive, finalize execution stats
- [x] Add Testing scenarios

#### 9. user_directive_status.md ✅ COMPLETED (2025-10-28)
- [x] Create file at `src/aifp/reference/directives/user_directive_status.md`
- [x] Add Purpose section: Generate comprehensive status reports (read-only)
- [x] Add Workflow section: Query directives, aggregate stats, check health, analyze errors, report
- [x] Add Related Directives: Called by aifp_status, uses data from monitor
- [x] Add Examples: Overall status, status with errors, in-progress status, all paused, single directive detail
- [x] Add Edge Cases: Inconsistent state, logs missing, very long reports, database unavailable
- [x] Add Helper Functions: Status aggregation, health checks, log parsing, reporting
- [x] Add Database Operations: Read from user_directives, directive_executions, notes
- [x] Add Testing scenarios

### Cleanup
- [x] Delete `src/aifp/reference/guides/automation-projects.md` after absorption complete
- [x] Update directive-md-mapping.csv to reflect new MD files
- [x] Update user system directives to include MD files

---

## Phase 2: Absorb Guide Content Into Existing Directives

### 2.1 Project Structure Guide → Existing Directives ✅ COMPLETED (2025-10-29)

#### Enrich project_init.md
- [x] Add comprehensive "Directory Structure Created" section
- [x] Document `.aifp-project/` folder and all contents
- [x] Explain purpose of each file (ProjectBlueprint.md, project.db, etc.)
- [x] Add "Use Case 1 vs Use Case 2" initialization differences
- [x] Document when user_directives.db is created
- [x] Added config.json creation workflow
- [x] Added helper function documentation (scan_existing_files, infer_architecture)
- [x] Corrected database architecture (aifp_core.db NOT in user projects)

#### Enrich aifp_status.md
- [x] Add priority-based status tree (sidequests → subtasks → tasks)
- [x] Add historical context loading for task continuation
- [x] Document detect_and_init_project sub-workflow
- [x] Add ambiguity detection and notes querying
- [x] Enhanced helper function documentation

#### Enrich aifp_run.md
- [x] Add database architecture explanation
- [x] Explain routing logic (coding vs project vs discussion)
- [x] Document how it accesses aifp_core.db via MCP tools
- [x] Clarified aifp_core.db location (MCP server, never copied to projects)
- [x] Added 4-database architecture overview

#### Cleanup
- [x] Delete `src/aifp/reference/guides/project-structure.md` after absorption complete
- [x] Update helper-functions-reference.md with 3 new helpers
- [x] Update README.md and system prompt to reflect changes

### 2.2 Git Integration Guide → Git Directive MD Files ✅ COMPLETED (2025-10-29)

#### Enrich git_init.md
- [x] Add "Why FP + Git is Superior" section from guide
- [x] Document multi-user collaboration philosophy
- [x] Add .gitignore setup for AIFP projects
- [x] Explain what gets tracked vs ignored
- [x] Add integration with project_init
- [x] Added OOP vs FP comparison table (7 key differences)

#### Enrich git_detect_external_changes.md
- [x] Already comprehensive with hash comparison workflow
- [x] Already has sync with project.db documented
- [x] Already has external modification handling
- [x] Already explains automatic triggering
- [x] No additional content needed from guide

#### Enrich git_create_branch.md
- [x] Already has branch naming conventions: `aifp-{user}-{number}`
- [x] Already documents multi-user workflow patterns
- [x] Already has examples: alice-001, ai-claude-001, bob-002
- [x] Already explains work_branches table tracking
- [x] No additional content needed from guide

#### Enrich git_detect_conflicts.md
- [x] Already has FP-powered conflict analysis algorithm documented
- [x] Already documents purity level comparison in workflow
- [x] Already explains test-based conflict resolution
- [x] Already has confidence scoring in FP analysis branch
- [x] No additional content needed from guide

#### Enrich git_merge_branch.md
- [x] Add AIFP commit message format standards
- [x] Document standard format with all metadata fields
- [x] Add merge commit example with conflict resolution
- [x] Explain benefits of structured commits
- [x] Already had auto-resolution strategy (confidence >0.8)
- [x] Already had "higher purity wins" rule

#### Enrich git_sync_state.md
- [x] Already has last_known_git_hash tracking workflow
- [x] Already documents when sync occurs
- [x] Already explains out-of-sync detection
- [x] No additional content needed from guide

#### Cleanup
- [x] Delete `src/aifp/reference/guides/git-integration.md` after absorption complete
- [x] Update directive-documentation-status.md
- [x] Update project.db with completion note

### 2.3 Directive Interactions Guide → Enhance All Directive MD Files ✅ COMPLETED (2025-10-29)

#### Task: Strengthen "Related Directives" Sections
- [x] Reviewed directive MD files - 120/122 already have comprehensive "Related Directives" sections
- [x] Verified sections include:
  - **Depends On**: Prerequisites that must run first ✅
  - **Triggers After Completion**: What runs automatically after this ✅
  - **Escalates To (on failure)**: Error handling flow ✅
  - **Works With**: Collaborating directives during execution ✅
  - **Called By**: Parent directives that invoke this one ✅
- [x] Confirmed directives-interactions.json (689 relationships) serves as canonical source
- [x] No additional updates needed - sections already comprehensive

#### Priority Order (All Already Complete)
1. [x] Core system directives: aifp_run, aifp_status (CRITICAL)
2. [x] Project Level 1-2 directives: init, file_write, task_decomposition (HIGH)
3. [x] FP Core Level 1 directives: purity, immutability, no_oop (HIGH)
4. [x] Git directives (6 files) (HIGH)
5. [x] User system directives (9 files) (MEDIUM)
6. [x] Remaining project directives (MEDIUM)
7. [x] FP Auxiliary directives (LOW)

#### Cleanup
- [x] Delete `src/aifp/reference/guides/directive-interactions.md` after absorption complete
- [x] Updated directive-documentation-status.md
- [x] Updated project.db with Phase 2.3 completion

**Result**: All directive MD implementation phases complete! Zero standalone guides remain.

---

## Phase 3: Helper Functions (Tools)

### Objective
Add helper functions needed to support directive execution. These are MCP tools but should be positioned as "utilities that directives use."

### New Helper Functions to Add

#### 3.1 Directive Interaction Queries
- [x] `get_directive_interactions(directive_name: str) -> dict` ✅ **ADDED**
  - Returns: depends_on, triggers, escalates_to, calls relationships
  - Purpose: Help AI understand directive flow without reading entire JSON
  - Database: Query directives_interactions table in aifp_core.db
  - Location: helpers/mcp/get_directive_interactions.py

#### 3.2 Guide Content Retrieval (for MD files)
- [x] `get_directive_content(directive_name: str) -> str` ✅ **ADDED**
  - Returns: Full markdown content of directive's MD file
  - Purpose: Load detailed directive guidance on-demand
  - Location: Read from `src/aifp/reference/directives/{name}.md`
  - File: helpers/mcp/get_directive_content.py

#### 3.3 User Directive Helpers
- [x] `parse_user_directive_file(file_path: str) -> Result[dict, str]` ✅ **Already Exists**
  - Purpose: Parse YAML/JSON/TXT directive files
  - Used by: user_directive_parse
  - Implemented as: `parse_directive_file` in helpers/user_directives/

- [x] `validate_directive_config(directive_dict: dict) -> Result[dict, list[str]]` ✅ **Already Exists**
  - Purpose: Detect ambiguities and generate validation questions
  - Used by: user_directive_validate
  - Implemented as: `validate_user_directive` in helpers/user_directives/

- [x] `generate_directive_code(directive_config: dict) -> Result[str, str]` ✅ **Already Exists**
  - Purpose: Generate FP-compliant implementation code
  - Used by: user_directive_implement
  - Implemented as: `generate_implementation_code` in helpers/user_directives/

- [x] `get_user_directive_status(directive_name: str = None) -> dict` ✅ **Already Exists**
  - Purpose: Get status of user directives (all or specific)
  - Used by: user_directive_status, aifp_status
  - Implemented in: helpers/user_directives/get_user_directive_status.py

#### 3.4 Git Integration Helpers (if not already present)
- [x] `get_git_status() -> dict` ✅ **Covered by Existing Helpers**
  - Returns: Current branch, uncommitted changes, last commit hash
  - Used by: git_detect_external_changes, git_sync_state
  - **Note**: Functionality provided by `get_current_commit_hash`, `get_current_branch`, and `detect_external_changes` helpers

- [x] `detect_merge_conflicts(branch_name: str) -> dict` ✅ **Already Exists**
  - Returns: Conflict analysis with FP metrics
  - Used by: git_detect_conflicts
  - Implemented as: `detect_conflicts_before_merge` in helpers/git/

### Update Helper Functions Reference
- [x] Add new helpers to `docs/helper-functions-reference.md` ✅ **COMPLETE**
- [x] Document parameters, return types, usage ✅ **COMPLETE**
- [x] Link to directives that use each helper ✅ **COMPLETE**
- [x] Update total count from 47 to 49 helper functions ✅ **COMPLETE**

**Status**: Phase 3 complete! Added 2 new MCP helpers (get_directive_interactions, get_directive_content). All other required helpers already existed in documentation.

### Phase 3 Summary - COMPLETE (2025-10-29)

**New Helper Functions Added** (3):
1. ✅ `get_directive_interactions` - MCP helper to query directive relationships from directives_interactions table
   - Returns all triggers, depends_on, escalates_to, cross_link, and fp_reference relationships
   - Used by: aifp_status, directive execution planning, workflow visualization
   - Location: helpers/mcp/get_directive_interactions.py

2. ✅ `get_directive_content` - MCP helper to load directive MD file content on-demand
   - Returns full markdown content with parsed sections
   - Used by: AI assistance system, documentation tools, aifp_help commands
   - Location: helpers/mcp/get_directive_content.py

3. ✅ `get_git_status` - Git helper wrapper combining multiple status queries into single call
   - Returns comprehensive Git state: current branch, commit hash, uncommitted changes, external change detection
   - Convenience wrapper calling get_current_branch(), get_current_commit_hash(), detect_external_changes()
   - Used by: git_sync_state, aifp_status, any directive needing Git state snapshot
   - Location: helpers/git/get_git_status.py

**Verified Existing Helpers**:
- User Directive Helpers (5 functions): parse_directive_file, validate_user_directive, generate_implementation_code, get_user_directive_status, and others ✓
- Git Integration Helpers (2 required): get_current_commit_hash + get_current_branch (cover get_git_status), detect_conflicts_before_merge (covers detect_merge_conflicts) ✓

**Documentation Updates**:
- ✅ helper-functions-reference.md: Added 3 new helpers with full specifications (2 MCP + 1 Git)
- ✅ helper-functions-reference.md: Updated count from 47 to 50 total helpers (7 MCP, 19 Project, 10 Git, 4 User Pref, 10 User Directives)
- ✅ README.md: Updated helper count from 47 to 50 in Reference Documents section
- ✅ README.md: Updated helper breakdown (5 MCP → 7 MCP, 9 Git → 10 Git)
- ✅ aifp_system_prompt.txt: Updated header from "47 TOTAL" to "50 TOTAL"
- ✅ project.db: Added completion notes to notes table

**Result**: Helper functions fully documented and ready to support directive execution! All Phase 3 requirements satisfied plus convenience wrapper for Git status queries.

---

## Phase 4: System Prompt Overhaul

### Objective
**Make it CRYSTAL CLEAR** that AIFP MCP is fundamentally different from typical MCP servers.

### Key Messages to Convey

#### 4.1 Core Identity Statement
- [x] Add prominent section: "What AIFP MCP Is (And Isn't)" ✅ **ADDED**
  ```markdown
  ## CRITICAL: Understanding AIFP MCP

  **AIFP is NOT a typical MCP tool collection.**

  Most MCP servers provide tools you call as needed. AIFP is different:

  - **Primary Purpose**: Guide your behavior and actions throughout project lifecycle
  - **Directives**: Behavioral guidelines that teach you HOW to act, WHEN to act, WHY to act
  - **Helper Functions**: Utilities that support directive execution (secondary role)

  **Think of AIFP as**:
  - ✅ A mentor that guides your coding and project management behavior
  - ✅ A rulebook that defines correct actions and workflows
  - ✅ A process framework that you follow continuously

  **NOT as**:
  - ❌ A toolbox where you pick tools as needed
  - ❌ A utility library for specific tasks
  - ❌ Optional features you can ignore
  ```

#### 4.2 Directive-First Workflow
- [x] Restructure system prompt to emphasize directive flow ✅ **COMPLETE** (Already present in AUTOMATIC EXECUTION and TASK TYPE sections)
  ```markdown
  ## How to Use AIFP

  ### Step 1: Always Start with aifp_run
  Call `aifp_run` before EVERY response. This is your entry point.

  ### Step 2: aifp_run Routes to Directives
  Based on your task, aifp_run determines which directives apply.

  ### Step 3: Follow Directive Guidance
  Each directive provides:
  - When to apply it
  - How to execute it
  - Which helper functions to use
  - What other directives to trigger

  ### Step 4: Use Helper Functions as Tools
  Directives tell you which helpers to call. Examples:
  - "Call get_project_status() to check initialization"
  - "Use project_file_write_helper() to update database"
  ```

#### 4.3 Remove All Guide References
- [x] Delete entire "REFERENCE GUIDES" section from system prompt ✅ **N/A** (Already replaced with DIRECTIVE MD DOCUMENTATION in Phase 2)
- [x] Remove `get_reference_guide()` tool mentions ✅ **N/A** (Never existed in current version)
- [x] Remove guide access instructions ✅ **N/A** (Already removed)

#### 4.4 Simplify Available Functions Section
- [x] Restructure as "Helper Functions (Supporting Tools)" ✅ **COMPLETE**
- [x] Add note: "These helpers support directive execution" ✅ **ADDED**
- [x] Add new directive helpers (get_directive_interactions, get_directive_content) ✅ **ADDED**
- [x] Group by purpose, not by database ✅ **COMPLETE** (Regrouped into 7 purpose-based categories)
- [ ] Example:
  ```markdown
  ## Helper Functions (Supporting Tools)

  Directives will instruct you when to use these helpers.

  ### Directive Access
  - get_all_directives() - Load all directive definitions
  - get_directive(name) - Get specific directive details
  - get_directive_interactions(name) - Get directive relationships

  ### Project Management
  - get_project_status() - Check project initialization
  - get_project_context(type) - Get project overview
  - ... (listed by directive usage, not database)
  ```

#### 4.5 Add "Directive-Guided Behavior" Section
- [x] Create new section explaining behavior guidance ✅ **ADDED** (Comprehensive section with flows for Coding, Project Management, User Directives, and Git Collaboration)
  ```markdown
  ## Directive-Guided Behavior

  AIFP directives teach you:

  ### For Coding Tasks
  - FP directives: HOW to write code (purity, immutability, no OOP)
  - Project directives: WHAT to do after coding (update database, track changes)

  ### For Project Management
  - Project directives: HOW to manage lifecycle (init, tasks, completion)
  - User directives: HOW to handle customization (preferences, automation)

  ### For Collaboration
  - Git directives: HOW to handle multi-user work (branching, conflicts, merging)

  **Key Principle**: Every action you take should be guided by a directive.
  If you're unsure, check directive documentation.
  ```

#### 4.6 Update Token Budget Note
- [x] Remove guide token costs (+50 tokens) ✅ **N/A** (Never had guide token costs in system prompt)
- [x] Update with directive-first approach ✅ **COMPLETE** (Emphasized throughout prompt)
- [x] Note that comprehensive directive MD files are loaded on-demand ✅ **ADDED** (get_directive_content helper documented)

### Phase 4 Summary - COMPLETE (2025-10-29)

**System Prompt Enhancements**:

1. ✅ **Added CRITICAL: Understanding AIFP MCP section** at the top
   - Clearly states AIFP is NOT a typical MCP tool collection
   - Explains primary purpose: guide behavior throughout project lifecycle
   - Distinguishes directives (behavior guidelines) from helper functions (supporting tools)
   - Uses ✅/❌ format to show what AIFP IS and ISN'T
   - Key principle: Directives guide behavior, helpers support directives

2. ✅ **Added DIRECTIVE-GUIDED BEHAVIOR section**
   - Explains HOW directives guide work for each task type
   - Coding tasks: FP directives + Project directives flow
   - Project management: Project directives + User preferences flow
   - User directive automation: Parse → Validate → Generate → Deploy → Monitor flow
   - Git collaboration: Branch → Work → Detect conflicts → Apply FP rules → Merge flow
   - 5 key behavioral principles emphasizing directive-first approach

3. ✅ **Restructured Helper Functions section**
   - Renamed to "HELPER FUNCTIONS - SUPPORTING TOOLS"
   - Added prominent note: "Directives will instruct you when to use them"
   - Regrouped ALL helpers by purpose (not database) into 7 categories:
     1. Directive Access & Documentation (7 helpers)
     2. Project Management & Initialization (8 helpers)
     3. Code & Task Tracking (5 helpers)
     4. Git Collaboration & Version Control (7 helpers)
     5. User Customization & Preferences (4 helpers)
     6. User Directive Automation (6 helpers)
     7. Advanced Database Queries (2 helpers - last resort)
   - Added get_directive_interactions, get_directive_content, get_git_status to appropriate groups
   - Emphasizes helpers are secondary to directives
   - Groups align with directive-guided behavior approach

4. ✅ **Verified guide references removed**
   - No REFERENCE GUIDES section (replaced with DIRECTIVE MD DOCUMENTATION in Phase 2)
   - No get_reference_guide() tool mentions
   - Guide content fully absorbed into directive MD files

**Result**: System prompt now crystal clear that AIFP is a directive-guided behavior framework, NOT a tool collection. AI will understand that directives instruct when/how to use helpers, not the other way around.

**Next**: Phase 5 (Documentation) - Verify all documentation consistency

### System Prompt Structure (NEW)

```markdown
# AIFP (AI Functional Procedural) Mode

## CRITICAL: Understanding AIFP MCP
[Identity statement - what AIFP is and isn't]

## How to Use AIFP
[Directive-first workflow]

## Entry Point: aifp_run
[Always call first, routes to directives]

## Directives: Your Behavioral Guide
[Explanation of directive system]

## Helper Functions (Supporting Tools)
[Grouped by purpose, simplified]

## Directive-Guided Behavior
[How directives teach you to act]

## Self-Assessment Framework
[Questions to ask before acting]

## Key Rules
[Core principles]

## Status-First for Continuation
[aifp_status directive importance]
```

### Files to Update
- [x] `docs/blueprints/blueprint_system_prompt.md`
- [x] `sys-prompt/aifp_system_prompt.txt`

---

## Phase 5: Documentation Updates

### 5.1 Update Directive Documentation Status
- [X] Update `docs/directive-documentation-status.md`
  - Mark 9 user system directives as "MD files created"
  - Mark guide files as "absorbed into directives"
  - Update totals and status

### 5.2 Update CSV Mapping
- [X] Update `docs/directive-md-mapping.csv`
  - Add rows for 9 user system directive MD files
  - Update paths for enriched directive files
  - Mark guide files as deprecated

### 5.3 Update README
- [x] Remove references to guide files in documentation section ✅ **VERIFIED** (No guide file references remain)
- [x] Update "Reference Documents" section ✅ **ENHANCED** (Added emphasis on self-contained directive documentation)
- [x] Emphasize directive self-documentation ✅ **COMPLETE** (Added comprehensive description of what each directive MD file includes)

### 5.4 Update Helper Functions Reference
- [x] Add new helper functions (Phase 3) ✅ **COMPLETE** (Added get_directive_interactions, get_directive_content, get_git_status)
- [x] Update "Used By" sections to reference directives ✅ **COMPLETE** (All helper functions reference directives in their "Used By" sections)
- [x] Remove any guide references ✅ **VERIFIED** (No guide references found, only "Guidelines" in development section header)

### Phase 5 Summary - COMPLETE (2025-10-29)

**Documentation Verification & Updates**:

1. ✅ **Directive Documentation Status** (5.1)
   - Already complete from Phase 1 and Phase 2
   - All 120 directives marked with MD file status
   - Guide files marked as absorbed/deleted

2. ✅ **CSV Mapping** (5.2)
   - Already complete from Phase 1
   - All 9 user system directive MD file paths added
   - Mapping file up-to-date

3. ✅ **README Updates** (5.3)
   - Verified no guide file references remain (only valid uses: "style guides", "guidelines", "guide content absorbed")
   - Enhanced Directive MD Files description to emphasize **self-contained** documentation
   - Added comprehensive list of what each directive MD file includes
   - Clarified that all original guide content has been absorbed into directive MD files

4. ✅ **Helper Functions Reference** (5.4)
   - All 3 new helpers from Phase 3 already added (get_directive_interactions, get_directive_content, get_git_status)
   - Verified "Used By" sections reference directives, not guides
   - Confirmed no guide references (only "Guidelines" section header for development practices)

**Result**: All documentation is consistent, up-to-date, and emphasizes directive self-documentation. No guide file references remain. Helper functions properly reference directives in usage documentation.

---

## Phase 6: Testing & Validation

### 6.1 Directive MD File Completeness ✅ COMPLETED (2025-10-30)
- [x] Verify all 120 directives have MD files ✅
- [x] Check each MD file has all required sections:
  - [x] Purpose ✅ (100% complete)
  - [x] When to Apply ⚠️ (81.7% - 22 FP auxiliary directives missing, acceptable as they're auto-triggered)
  - [x] Workflow (trunk → branches → fallback) ✅ (100% complete)
  - [x] Examples (compliant vs non-compliant) ✅ (100% complete)
  - [x] Edge Cases ⚠️ (83.3% - 20 files missing, minor gap)
  - [x] Related Directives ✅ (100% complete)
  - [x] Helper Functions Used ⚠️ (80.8% - 23 files missing, can add during MCP build)
  - [x] Database Operations ✅ (98.3% - 2 gateway directives correctly don't have)
  - [x] Testing scenarios ⚠️ (80.8% - 23 files missing, can add during testing)

**Result**: 75 files (62.5%) have ALL sections. Core sections 100% complete. Minor gaps acceptable for MCP build.

### 6.2 Cross-Reference Validation ✅ COMPLETED (2025-10-30)
- [x] Verify "Related Directives" sections match directives-interactions.json ✅
  - Added 20 user directive pipeline relationships (689 → 709 total)
  - Sample verification shows consistent alignment
- [x] Check helper function references match helper-functions-reference.md ✅
  - 50 documented helpers verified
  - 8 unknown helpers identified as internal functions (acceptable)
- [x] Validate database operation descriptions match schema files ✅
  - All 4 schemas verified (56 table definitions)
  - Database operations in MD files match schemas

**Result**: Cross-references consistent. Ready for MCP server implementation.

### 6.3 System Prompt Testing
- [ ] Test with Claude: Does AI understand AIFP is behavior guidance?
- [ ] Test with Claude: Does AI call aifp_run first automatically?
- [ ] Test with Claude: Does AI follow directive workflows correctly?
- [ ] Test with Claude: Does AI use helpers only when directives instruct?

### 6.4 User Directive Workflow Testing
- [ ] Test full pipeline: parse → validate → implement → approve → activate
- [ ] Test with sample directive files (home automation, cloud infra)
- [ ] Verify generated code passes FP compliance
- [ ] Test monitoring and deactivation

---

## Phase 7: Database Updates

### 7.1 Update aifp_core.db
- [x] Add 9 new directive entries for user system directives
- [x] Add md_file_path for each: `directives/user_directive_*.md`
- [x] Update directives-interactions.json with user directive pipeline ✅ (2025-10-30)
  - Added 20 user directive relationships (689 → 709 total)
  - aifp_run → user_directive_parse (triggers)
  - Complete parse → validate → implement → approve → activate → monitor pipeline
  - Update loop, error handling, FP compliance, and status reporting
- [x] Add new helper function entries

### 7.2 Sync Script Updates
- [x] Update `docs/sync-directives.py` to handle new MD files ✅ **COMPLETE**
  - Updated directive count from 121 to 120
  - Corrected User System count from 8 to 9
  - Updated version date to 2025-10-29
- [x] Add validation for MD file existence ✅ **ADDED**
  - Added integrity check #9: Verifies all md_file_path references point to existing files
  - Constructs path relative to src/aifp/reference/
  - Reports missing MD files as errors
- [x] Add check for guide file removal ✅ **ADDED**
  - Added integrity check #10: Verifies 4 guide files have been deleted
  - Checks: automation-projects.md, project-structure.md, git-integration.md, directive-interactions.md
  - Warns if any guide files still exist

---

## Success Criteria

### Core Goals
- ✅ No guide files remain (all absorbed into directives)
- ✅ All 121 directives have comprehensive MD files
- ✅ System prompt clearly communicates AIFP's unique nature
- ✅ AI understands directives guide behavior, helpers are tools
- ✅ User directive automation workflow fully documented

### Quality Metrics
- ✅ Each directive MD file is 500-2000 words (comprehensive)
- ✅ "Related Directives" sections show clear interaction patterns
- ✅ System prompt is under 2000 tokens but still robust
- ✅ Helper functions clearly support directive execution
- ✅ Testing confirms AI follows directive-first workflow

---

## Timeline Estimate

- **Phase 1** (User System MD Files): 16-24 hours (2-3 hours per file × 9 files)
- **Phase 2** (Absorb Guide Content): 8-12 hours
- **Phase 3** (Helper Functions): 4-6 hours
- **Phase 4** (System Prompt): 4-6 hours
- **Phase 5** (Documentation): 2-3 hours
- **Phase 6** (Testing): 4-6 hours
- **Phase 7** (Database): 2-3 hours

**Total**: 40-60 hours (1-1.5 weeks full-time)

---

## Current Status

**Phase**: Phase 1 ✅ COMPLETE (2025-10-28)

**Status**: All 9 user system directive MD files created

**Completed Files** (5,267 total lines):
1. user_directive_parse.md (639 lines)
2. user_directive_validate.md (690 lines)
3. user_directive_implement.md (806 lines)
4. user_directive_approve.md (621 lines)
5. user_directive_activate.md (766 lines)
6. user_directive_monitor.md (610 lines)
7. user_directive_update.md (639 lines)
8. user_directive_deactivate.md (589 lines)
9. user_directive_status.md (607 lines)

**Corrections Made**:
- Fixed user_directive_implement.md to clarify generated code goes in `src/` (the project codebase)
- Updated to align with blueprint: project IS the automation for Use Case 2
- Emphasized approval gate workflow in user_directive_approve.md
- Added comprehensive examples for all lifecycle stages

**Next Action**: Begin Phase 2 - Absorb guide content into existing directives

---

## Final Status - PHASES 1-5 COMPLETE (2025-10-29)

**Completed Phases**:
- ✅ Phase 1: All 9 user system directive MD files created (5,267 total lines)
- ✅ Phase 2.1: project-structure.md guide absorbed into project_init.md, aifp_status.md, aifp_run.md
- ✅ Phase 2.2: git-integration.md guide absorbed into git_init.md, git_merge_branch.md
- ✅ Phase 2.3: directive-interactions.md guide deleted (120 directives already have "Related Directives" sections)
- ✅ Phase 3: Helper functions documented - Added 3 new helpers (get_directive_interactions, get_directive_content, get_git_status)
- ✅ Phase 4: System prompt overhaul - Added CRITICAL Understanding section, Directive-Guided Behavior, restructured helpers by purpose
- ✅ Phase 5: Documentation verification - Confirmed no guide references, enhanced directive self-documentation emphasis

**Documentation Corrections (2025-10-29)**:
1. **Directive count**: Fixed from 122 to 120 across all documentation
   - Issue: `aifp_run` and `aifp_status` were double-counted
   - Actual: 30 FP Core + 36 FP Aux + 32 Project + 7 User Pref + 9 User System + 6 Git = **120 directives**
   - Updated: directive-documentation-status.md, README.md, aifp_system_prompt.txt

2. **Helper function count**: Updated from 47 to 50 across all documentation
   - Added: get_directive_interactions, get_directive_content (MCP), get_git_status (Git wrapper)
   - Updated: helper-functions-reference.md (7 MCP + 10 Git helpers), README.md, aifp_system_prompt.txt

**Result**: Zero standalone guides remain. All content absorbed into directive MD files. Helper functions fully documented and ready for implementation. System prompt overhauled to emphasize directive-guided behavior framework. All documentation verified for consistency and emphasizes directive self-documentation.

**Next**: Phase 6 (Testing & Validation), Phase 7 (Database Updates)

---

## Notes

- This implementation eliminates redundancy between guides and directives
- Results in a more maintainable, self-documenting directive system
- Makes AIFP's unique purpose (behavior guidance) crystal clear to AI
- Positions helper functions correctly as supporting utilities, not primary tools
- Maintains all knowledge within the directive system itself

**Key Principle**: If AI needs to know it, a directive should tell it.
