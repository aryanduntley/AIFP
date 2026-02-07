# Directive: project_evolution

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_completion_check
**Priority**: HIGH - Captures project pivots and architectural changes

---

## Purpose

The `project_evolution` directive handles versioning and pivot tracking for evolving project goals, architecture, and structure. This directive serves as the **project change manager**, ensuring that when project-wide changes occur, they are properly documented, versioned, and synchronized between `ProjectBlueprint.md` and `project.db`.

Key responsibilities:
- **Track architectural changes** - Language, runtime, infrastructure updates
- **Capture goal pivots** - Purpose, success criteria, and goal modifications
- **Update themes and flows** - Organizational structure changes
- **Manage completion path evolution** - Roadmap adjustments
- **Version management** - Increment `project.version` on significant changes
- **Blueprint synchronization** - Update `ProjectBlueprint.md` sections accordingly
- **Evolution history** - Log all changes in Section 5 of blueprint
- **Backup before changes** - Preserve previous state in `.aifp-project/backups/`

This is the **project change auditor** - all significant project-wide modifications flow through here.

---

## When to Apply

This directive applies when:
- **Architecture changes** - Language, runtime, framework, or infrastructure modifications
- **Goals change** - Project purpose, success criteria, or goals updated
- **Themes/flows change** - Organizational structure evolves
- **Completion path changes** - Roadmap restructured or milestones added
- **Infrastructure changes** - Package dependencies, build tools, testing framework updates
- **Project pivots** - Major direction changes requiring version increment
- **Called by other directives**:
  - `project_theme_flow_mapping` - When themes or flows are added/modified
  - `project_init` - Initial project setup creates version 1
  - `project_add_path` - When completion path is restructured

---

## Workflow

### Trunk: detect_project_wide_change

Identifies the type of project-wide change and routes to appropriate handler.

**Steps**:
1. **Analyze change request** - Determine which aspect of project changed
2. **Identify blueprint section** - Map change to ProjectBlueprint.md section
3. **Backup current blueprint** - Preserve state before modification
4. **Update database** - Modify relevant `project.db` tables
5. **Update blueprint section** - Modify corresponding ProjectBlueprint.md section
6. **Increment version** - Update `project.version` if significant
7. **Add evolution history** - Log change in Section 5

### Branches

**Branch 1: If architecture_change**
- **Then**: `update_blueprint_section_2`
- **Details**: Technical Blueprint changes
  - Section: "2. Technical Blueprint"
  - Database tables: `project.version`, `infrastructure`
  - Examples:
    - Language change: Python → Rust
    - Runtime change: Node.js 16 → Node.js 20
    - Framework change: Flask → FastAPI
  - Actions:
    - Backup current blueprint
    - Increment `project.version`
    - Update `infrastructure` table
    - Update Section 2 of blueprint
    - Add evolution history entry
- **Result**: Architecture change documented and versioned

**Branch 2: If goals_change**
- **Then**: `update_blueprint_section_1`
- **Details**: Project Overview changes
  - Section: "1. Project Overview"
  - Database tables: `project.goals_json`, `project.version`
  - Examples:
    - Purpose change: "Calculator library" → "Scientific computing platform"
    - Goals change: Add GPU acceleration requirement
    - Success criteria change: Test coverage 80% → 95%
  - Actions:
    - Backup current blueprint
    - Increment `project.version`
    - Update `project.goals_json`
    - Update Section 1 of blueprint
    - Add evolution history entry
- **Result**: Goals pivot documented and versioned

**Branch 3: If themes_or_flows_change**
- **Then**: `update_blueprint_section_3`
- **Details**: Project Themes & Flows changes
  - Section: "3. Project Themes & Flows"
  - Database tables: `themes`, `flows`, `project.version`
  - Examples:
    - New theme added: "Authentication"
    - Flow restructured: Split "User Management" into "Auth" + "Profiles"
    - Theme renamed: "Database Operations" → "Data Access Layer"
  - Actions:
    - Backup current blueprint
    - Increment `project.version`
    - Update `themes` and `flows` tables
    - Update Section 3 of blueprint
    - Add evolution history entry
  - **Triggered by**: `project_theme_flow_mapping` directive
- **Result**: Themes/flows evolution documented and versioned

**Branch 4: If completion_path_change**
- **Then**: `update_blueprint_section_4`
- **Details**: Completion Path changes
  - Section: "4. Completion Path"
  - Database tables: `completion_path`, `milestones`, `project.version`
  - Examples:
    - New stage added: "Performance Optimization"
    - Milestone restructured: Merge "Testing" into "Core Development"
    - Stage reordered: Move "Documentation" before "Testing"
  - Actions:
    - Backup current blueprint
    - Increment `project.version`
    - Update `completion_path` and `milestones` tables
    - Update Section 4 of blueprint
    - Add evolution history entry
- **Result**: Roadmap evolution documented and versioned

**Branch 5: If infrastructure_change**
- **Then**: `update_blueprint_section_2_infrastructure`
- **Details**: Key Infrastructure changes
  - Section: "2. Technical Blueprint - Key Infrastructure"
  - Database tables: `infrastructure`, `project.version`
  - Examples:
    - Add dependency: `pandas` for data processing
    - Change build tool: `setuptools` → `poetry`
    - Update testing framework: `unittest` → `pytest + hypothesis`
  - Actions:
    - Backup current blueprint
    - Increment `project.version`
    - Update `infrastructure` table
    - Update "Key Infrastructure" subsection
    - Add evolution history entry
- **Result**: Infrastructure change documented and versioned

**Branch 6: If pivot_detected**
- **Then**: `increment_version`
- **Details**: Major project direction change
  - Significant purpose or goal shift
  - Update `project.version` (major increment)
  - Update `project.goals_json`
  - Update Section 1 of blueprint
  - Add detailed evolution history entry
- **Result**: Major pivot documented with version bump

**Branch 7: If path_affected**
- **Then**: `update_completion_path`
- **Details**: Pivot affects roadmap
  - Update `completion_path` table
  - Restructure milestones if needed
  - Log note about path changes
  - Update Section 4 of blueprint
- **Result**: Roadmap adjusted to reflect pivot

**Branch 8: If blueprint_updated**
- **Then**: `add_evolution_history`
- **Details**: Record change in evolution history
  - Section: "5. Evolution History"
  - Format:
    ```markdown
    ### Version X - YYYY-MM-DD
    - **Change**: [description]
    - **Rationale**: [why this change was made]
    ```
  - Log change details
  - Show new version number
- **Result**: Evolution history updated with audit trail

**Branch 9: Parallel execution**
- **Then**: `backup_blueprint_to_aifp_backups` AND `log_evolution_to_notes`
- **Details**: Execute simultaneously
  - **Parallel 1**: Backup to `.aifp-project/backups/ProjectBlueprint.md.v{version}`
  - **Parallel 2**: Log to `notes` table:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Backup created and change logged

**Fallback**: `prompt_user`
- Present detected changes and ask for confirmation
- Log to `notes` for future reference

### Error Handling

**on_failure**: `prompt_user`
- If blueprint update fails, restore from backup
- If database update fails, rollback transaction
- Prompt user to resolve issue manually

---

## Examples

### Example 1: Architecture Change - Language Switch

**User**: "Migrate from Python to Rust for performance"

**AI Execution**:
1. Detects: Architecture change (language)
2. Backs up blueprint to `.aifp-project/backups/ProjectBlueprint.md.v1`
3. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
4. Updates infrastructure:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Updates Section 2 of `ProjectBlueprint.md`:
   ```markdown
   ### Language & Runtime
   - **Primary Language**: Rust 1.75+
   - **Runtime/Framework**: Tokio async runtime
   ```
6. Adds evolution history to Section 5:
   ```markdown
   ### Version 2 - 2025-10-27
   - **Change**: Migrated from Python to Rust for performance-critical components
   - **Rationale**: Benchmarks showed 10x performance improvement in matrix operations. Rust's memory safety aligns with AIFP principles.
   ```
7. Logs to notes:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 2: Goals Change - Scope Expansion

**User**: "Add machine learning capabilities to project goals"

**AI Execution**:
1. Detects: Goals change (scope expansion)
2. Backs up blueprint
3. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
4. Updates goals:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
5. Updates Section 1 of blueprint:
   ```markdown
   ### Goals
   - Pure functional implementation (no OOP, no mutations)
   - Comprehensive test coverage (>90%)
   - Machine learning integration for predictive analytics
   ```
6. Adds evolution history:
   ```markdown
   ### Version 3 - 2025-10-27
   - **Change**: Expanded goals to include machine learning capabilities
   - **Rationale**: User demand for predictive analytics features. ML models fit well with FP paradigm (pure transformations).
   ```

### Example 3: Themes/Flows Change

**User**: "Split Authentication theme into separate Auth and Authorization themes"

**AI Execution**:
1. Triggered by: `project_theme_flow_mapping` directive
2. Detects: Themes change (restructuring)
3. Backs up blueprint
4. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
5. Updates themes table:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
6. Updates Section 3 of blueprint:
   ```markdown
   ### Themes

   1. **Authentication**
      - Purpose: User identity verification
      - Files: src/aifp/auth/

   2. **Authorization**
      - Purpose: Role-based access control and permissions
      - Files: src/aifp/permissions/
   ```
7. Adds evolution history:
   ```markdown
   ### Version 4 - 2025-10-27
   - **Change**: Split Authentication theme into Auth and Authorization
   - **Rationale**: Separation of concerns - identity verification vs. access control. Improves modularity and testability.
   ```

### Example 4: Completion Path Change

**User**: "Add 'Performance Optimization' stage after Core Development"

**AI Execution**:
1. Detects: Completion path change (new stage)
2. Backs up blueprint
3. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
4. Updates completion_path:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Updates Section 4 of blueprint:
   ```markdown
   ### Stage 3: Performance Optimization (Weeks 5-6)

   **Status**: pending

   **Key Milestones**:
   - Profile CPU and memory usage
   - Optimize hot paths
   - Benchmark improvements
   ```
6. Adds evolution history:
   ```markdown
   ### Version 5 - 2025-10-27
   - **Change**: Added 'Performance Optimization' stage to completion path
   - **Rationale**: Profiling revealed bottlenecks in matrix operations. Dedicated optimization stage ensures performance targets met.
   ```

### Example 5: Infrastructure Change

**User**: "Switch from unittest to pytest with hypothesis for property-based testing"

**AI Execution**:
1. Detects: Infrastructure change (testing framework)
2. Backs up blueprint
3. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
4. Updates infrastructure:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Updates Section 2 - Key Infrastructure:
   ```markdown
   ### Key Infrastructure
   - **Testing**: pytest + hypothesis for property-based testing
   ```
6. Adds evolution history:
   ```markdown
   ### Version 6 - 2025-10-27
   - **Change**: Switched from unittest to pytest + hypothesis
   - **Rationale**: Property-based testing better validates FP purity. Hypothesis auto-generates test cases for edge conditions.
   ```

### Example 6: Major Pivot

**User**: "Change project from 'Calculator library' to 'Scientific computing platform'"

**AI Execution**:
1. Detects: Major pivot (purpose change)
2. Prompts user: "This is a significant change. Confirm pivot?"
3. User confirms
4. Backs up blueprint
5. Major version increment:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
6. Updates goals:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
7. Updates completion path (major restructuring)
8. Updates blueprint Section 1:
   ```markdown
   ## 1. Project Overview

   ### Idea
   Build a GPU-accelerated scientific computing platform for high-performance numerical analysis.

   ### Goals
   - GPU-accelerated linear algebra operations
   - Distributed computing support for large datasets
   - Scientific visualization and plotting
   ```
9. Adds detailed evolution history:
   ```markdown
   ### Version 10 - 2025-10-27 (MAJOR PIVOT)
   - **Change**: Pivoted from calculator library to scientific computing platform
   - **Rationale**: User research revealed demand for GPU acceleration and distributed computing. Calculator features remain but expanded significantly. This represents a major scope increase and architectural shift.
   ```

---

## Integration with Other Directives

### Called By:
- `project_theme_flow_mapping` - When themes/flows change
- `project_init` - Creates version 1
- `project_add_path` - When completion path restructured

### Calls:
- `project_blueprint_update` - Updates specific blueprint sections
- `project_update_db` - Syncs all database changes
- `project_backup_restore` - Creates backups before changes

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

**Filesystem**:
```bash
# Backup blueprint
cp .aifp-project/ProjectBlueprint.md .aifp-project/backups/ProjectBlueprint.md.v{version}

# Update blueprint
# (Modify specific sections in-place)
```

---

## Roadblocks and Resolutions

### Roadblock 1: pivot_ambiguity
**Issue**: Unclear if change constitutes a pivot or minor adjustment
**Resolution**: Prompt user for new purpose and goals, confirm version increment

### Roadblock 2: version_conflict
**Issue**: Version number mismatch between project table and completion_path
**Resolution**: Reconcile by querying `project.version` as source of truth, update completion_path

### Roadblock 3: blueprint_missing
**Issue**: ProjectBlueprint.md file not found
**Resolution**: Generate new blueprint from current database state using `project_blueprint_read`

### Roadblock 4: blueprint_update_failed
**Issue**: Unable to write to ProjectBlueprint.md
**Resolution**: Backup current state, restore from backup, prompt user for manual update

### Roadblock 5: backup_failed
**Issue**: Cannot create backup before modification
**Resolution**: Abort evolution update, prompt user to resolve file permissions

---

## Intent Keywords

- "pivot"
- "evolve"
- "update goals"
- "project change"
- "change architecture"
- "update infrastructure"
- "modify roadmap"
- "restructure"

**Confidence Threshold**: 0.6

---

## Related Directives

- `project_blueprint_update` - Updates blueprint sections
- `project_theme_flow_mapping` - Triggers evolution on theme/flow changes
- `project_update_db` - Syncs database changes
- `project_backup_restore` - Creates backups
- `project_init` - Creates initial version
- `project_completion_check` - Uses version for progress tracking

---

## Blueprint Section Mapping

| Change Type | Blueprint Section | Database Tables |
|-------------|-------------------|-----------------|
| Architecture | Section 2: Technical Blueprint | `infrastructure`, `project.version` |
| Goals | Section 1: Project Overview | `project.goals_json`, `project.purpose` |
| Themes/Flows | Section 3: Themes & Flows | `themes`, `flows` |
| Completion Path | Section 4: Completion Path | `completion_path`, `milestones` |
| Infrastructure | Section 2: Key Infrastructure | `infrastructure` |
| All Changes | Section 5: Evolution History | `notes` (evolution type) |

---

## Notes

- **Always backup before modification** - Preserve previous state
- **Version increments are permanent** - Cannot decrement version
- **Evolution history is append-only** - Never delete history entries
- **Blueprint and DB must stay in sync** - Update both atomically
- **Log all changes to notes table** - Audit trail for transparency
- **Major pivots get major version bumps** - Use versioning to signal significance
