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
- [ ] Delete `src/aifp/reference/guides/automation-projects.md` after absorption complete
- [ ] Update directive-md-mapping.csv to reflect new MD files
- [ ] Update user system directives to include MD files

---

## Phase 2: Absorb Guide Content Into Existing Directives

### 2.1 Project Structure Guide → Existing Directives

#### Enrich project_init.md
- [ ] Add comprehensive "Directory Structure Created" section
- [ ] Document `.aifp-project/` folder and all contents
- [ ] Explain purpose of each file (ProjectBlueprint.md, project.db, etc.)
- [ ] Add "Use Case 1 vs Use Case 2" initialization differences
- [ ] Document when user_directives.db is created

#### Enrich aifp_status.md
- [ ] Add "Files Read" section listing all files accessed
- [ ] Document ProjectBlueprint.md reading and parsing
- [ ] Explain database connections (project.db, user_preferences.db, user_directives.db)
- [ ] Add file location reference table

#### Enrich aifp_run.md
- [ ] Add architecture overview diagram/description
- [ ] Explain routing logic (coding vs project vs discussion)
- [ ] Document how it accesses aifp_core.db for directive definitions
- [ ] Add project structure context for routing decisions

#### Cleanup
- [ ] Delete `src/aifp/reference/guides/project-structure.md` after absorption complete

### 2.2 Git Integration Guide → Git Directive MD Files

#### Enrich git_init.md
- [ ] Add "Why FP + Git is Superior" section from guide
- [ ] Document multi-user collaboration philosophy
- [ ] Add .gitignore setup for AIFP projects
- [ ] Explain what gets tracked vs ignored
- [ ] Add integration with project_init

#### Enrich git_detect_external_changes.md
- [ ] Add detailed explanation of hash comparison
- [ ] Document sync with project.db
- [ ] Add workflow for handling external modifications
- [ ] Explain when this directive is triggered automatically

#### Enrich git_create_branch.md
- [ ] Add branch naming conventions: `aifp-{user}-{number}`
- [ ] Document multi-user workflow patterns
- [ ] Add examples: alice-001, ai-claude-001, bob-002
- [ ] Explain work_branches table tracking

#### Enrich git_detect_conflicts.md
- [ ] Add FP-powered conflict analysis explanation
- [ ] Document purity level comparison
- [ ] Explain test-based conflict resolution
- [ ] Add confidence scoring algorithm

#### Enrich git_merge_branch.md
- [ ] Add auto-resolution strategy details
- [ ] Document confidence threshold (>0.8)
- [ ] Explain "higher purity wins" rule
- [ ] Add merge history tracking

#### Enrich git_sync_state.md
- [ ] Add last_known_git_hash tracking details
- [ ] Document when sync occurs (commits, pulls)
- [ ] Explain out-of-sync detection triggers

#### Cleanup
- [ ] Delete `src/aifp/reference/guides/git-integration.md` after absorption complete

### 2.3 Directive Interactions Guide → Enhance All Directive MD Files

#### Task: Strengthen "Related Directives" Sections
- [ ] Review all 121 directive MD files
- [ ] For each directive, expand "Related Directives" section to include:
  - **Depends On**: Prerequisites that must run first
  - **Triggers After Completion**: What runs automatically after this
  - **Escalates To (on failure)**: Error handling flow
  - **Works With**: Collaborating directives during execution
  - **Called By**: Parent directives that invoke this one
- [ ] Add interaction examples showing the flow
- [ ] Cross-reference directives-interactions.json

#### Priority Order
1. [ ] Core system directives: aifp_run, aifp_status (CRITICAL)
2. [ ] Project Level 1-2 directives: init, file_write, task_decomposition (HIGH)
3. [ ] FP Core Level 1 directives: purity, immutability, no_oop (HIGH)
4. [ ] Git directives (6 files) (HIGH)
5. [ ] User system directives (9 files) (MEDIUM)
6. [ ] Remaining project directives (MEDIUM)
7. [ ] FP Auxiliary directives (LOW)

#### Cleanup
- [ ] Delete `src/aifp/reference/guides/directive-interactions.md` after absorption complete

---

## Phase 3: Helper Functions (Tools)

### Objective
Add helper functions needed to support directive execution. These are MCP tools but should be positioned as "utilities that directives use."

### New Helper Functions to Add

#### 3.1 Directive Interaction Queries
- [ ] `get_directive_interactions(directive_name: str) -> dict`
  - Returns: depends_on, triggers, escalates_to, calls relationships
  - Purpose: Help AI understand directive flow without reading entire JSON
  - Database: Query directives_interactions table in aifp_core.db

#### 3.2 Guide Content Retrieval (for MD files)
- [ ] `get_directive_content(directive_name: str) -> str`
  - Returns: Full markdown content of directive's MD file
  - Purpose: Load detailed directive guidance on-demand
  - Location: Read from `src/aifp/reference/directives/{name}.md`

#### 3.3 User Directive Helpers
- [ ] `parse_user_directive_file(file_path: str) -> Result[dict, str]`
  - Purpose: Parse YAML/JSON/TXT directive files
  - Used by: user_directive_parse

- [ ] `validate_directive_config(directive_dict: dict) -> Result[dict, list[str]]`
  - Purpose: Detect ambiguities and generate validation questions
  - Used by: user_directive_validate

- [ ] `generate_directive_code(directive_config: dict) -> Result[str, str]`
  - Purpose: Generate FP-compliant implementation code
  - Used by: user_directive_implement

- [ ] `get_user_directive_status(directive_name: str = None) -> dict`
  - Purpose: Get status of user directives (all or specific)
  - Used by: user_directive_status, aifp_status

#### 3.4 Git Integration Helpers (if not already present)
- [ ] `get_git_status() -> dict`
  - Returns: Current branch, uncommitted changes, last commit hash
  - Used by: git_detect_external_changes, git_sync_state

- [ ] `detect_merge_conflicts(branch_name: str) -> dict`
  - Returns: Conflict analysis with FP metrics
  - Used by: git_detect_conflicts

### Update Helper Functions Reference
- [ ] Add new helpers to `docs/helper-functions-reference.md`
- [ ] Document parameters, return types, usage
- [ ] Link to directives that use each helper

---

## Phase 4: System Prompt Overhaul

### Objective
**Make it CRYSTAL CLEAR** that AIFP MCP is fundamentally different from typical MCP servers.

### Key Messages to Convey

#### 4.1 Core Identity Statement
- [ ] Add prominent section: "What AIFP MCP Is (And Isn't)"
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
- [ ] Restructure system prompt to emphasize directive flow
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
- [ ] Delete entire "REFERENCE GUIDES" section from system prompt
- [ ] Remove `get_reference_guide()` tool mentions
- [ ] Remove guide access instructions

#### 4.4 Simplify Available Functions Section
- [ ] Restructure as "Helper Functions (Supporting Tools)"
- [ ] Group by purpose, not by database
- [ ] Add note: "These helpers support directive execution"
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
- [ ] Create new section explaining behavior guidance
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
- [ ] Remove guide token costs (+50 tokens)
- [ ] Update with directive-first approach
- [ ] Note that comprehensive directive MD files are loaded on-demand

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
- [ ] `docs/blueprints/blueprint_system_prompt.md`
- [ ] `sys-prompt/aifp_system_prompt.txt`

---

## Phase 5: Documentation Updates

### 5.1 Update Directive Documentation Status
- [ ] Update `docs/directive-documentation-status.md`
  - Mark 9 user system directives as "MD files created"
  - Mark guide files as "absorbed into directives"
  - Update totals and status

### 5.2 Update CSV Mapping
- [ ] Update `docs/directive-md-mapping.csv`
  - Add rows for 9 user system directive MD files
  - Update paths for enriched directive files
  - Mark guide files as deprecated

### 5.3 Update README
- [ ] Remove references to guide files in documentation section
- [ ] Update "Reference Documents" section
- [ ] Emphasize directive self-documentation

### 5.4 Update Helper Functions Reference
- [ ] Add new helper functions (Phase 3)
- [ ] Update "Used By" sections to reference directives
- [ ] Remove any guide references

---

## Phase 6: Testing & Validation

### 6.1 Directive MD File Completeness
- [ ] Verify all 121 directives have MD files
- [ ] Check each MD file has all required sections:
  - [ ] Purpose
  - [ ] When to Apply
  - [ ] Workflow (trunk → branches → fallback)
  - [ ] Examples (compliant vs non-compliant)
  - [ ] Edge Cases
  - [ ] Related Directives
  - [ ] Helper Functions Used
  - [ ] Database Operations
  - [ ] Testing scenarios

### 6.2 Cross-Reference Validation
- [ ] Verify "Related Directives" sections match directives-interactions.json
- [ ] Check helper function references match helper-functions-reference.md
- [ ] Validate database operation descriptions match schema files

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
- [ ] Add 9 new directive entries for user system directives
- [ ] Add md_file_path for each: `directives/user_directive_*.md`
- [ ] Update directives-interactions.json with user directive pipeline
- [ ] Add new helper function entries

### 7.2 Sync Script Updates
- [ ] Update `docs/sync-directives.py` to handle new MD files
- [ ] Add validation for MD file existence
- [ ] Add check for guide file removal

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

## Notes

- This implementation eliminates redundancy between guides and directives
- Results in a more maintainable, self-documenting directive system
- Makes AIFP's unique purpose (behavior guidance) crystal clear to AI
- Positions helper functions correctly as supporting utilities, not primary tools
- Maintains all knowledge within the directive system itself

**Key Principle**: If AI needs to know it, a directive should tell it.
