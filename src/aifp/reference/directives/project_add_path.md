# Directive: project_add_path

**Type**: Project
**Level**: 2 (High-Level Coordination)
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Roadmap structure management

---

## Purpose

The `project_add_path` directive handles creation and modification of project roadmap structures in `project.db`. This directive serves as the **roadmap architect**, managing the hierarchical relationship between completion paths, milestones, and tasks to maintain project structure coherence.

Key responsibilities:
- **Create completion path stages** - Add new high-level stages to roadmap
- **Create milestones** - Add milestones within stages
- **Update roadmap structure** - Maintain order and relationships
- **Validate hierarchy** - Ensure proper parent-child relationships
- **Preserve order** - Manage order_index for sequential stages
- **Trigger blueprint updates** - Call `project_evolution` when roadmap changes

This is the **roadmap structure manager** - ensures coherent, well-ordered project paths.

---

## When to Apply

This directive applies when:
- **New project stages** - Adding major phases to completion path
- **Milestone creation** - Adding milestones within stages
- **Roadmap restructuring** - Reordering or reorganizing stages
- **Project evolution** - Adapting roadmap to changing goals
- **Called by other directives**:
  - `project_init` - Creates initial completion path structure
  - `project_task_decomposition` - May create new milestones for tasks
  - `project_evolution` - Updates roadmap when goals change
  - User directly - Manual roadmap management

---

## Workflow

### Trunk: modify_path

Determines what type of modification is needed to the roadmap.

**Steps**:
1. **Identify modification type** - New path stage, new milestone, or restructure
2. **Validate inputs** - Ensure names, descriptions, and order make sense
3. **Check existing structure** - Avoid duplicates, maintain consistency
4. **Execute modification** - Insert or update database records
5. **Trigger updates** - Call `project_evolution` if needed

### Branches

**Branch 1: If new_path_stage**
- **Then**: `insert_completion_path`
- **Details**: Create new stage in completion_path
  - Determine order_index (sequential)
  - Set status to 'pending'
  - Link to project_id
  - Create stage with name and description
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: New completion path stage created

**Branch 2: If new_milestone**
- **Then**: `insert_milestone`
- **Details**: Create new milestone within stage
  - Link to completion_path stage via completion_path_id
  - Set status to 'pending'
  - Set priority based on stage order
  - Create with name and description
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: New milestone created within stage

**Branch 3: If new_task_in_milestone**
- **Then**: `insert_task`
- **Details**: Create task within milestone
  - Link to milestone via milestone_id
  - Call `project_task_create` directive
  - Set priority and status
- **Result**: New task created (delegates to project_task_create)

**Branch 4: If new_subtask**
- **Then**: `insert_subtask`
- **Details**: Create subtask within task
  - Link to task via task_id
  - Call `project_subtask_create` directive
  - Set high priority and pause parent
- **Result**: New subtask created (delegates to project_subtask_create)

**Branch 5: If reorder_stages**
- **Then**: `update_order_indices`
- **Details**: Reorder completion path stages
  - Update order_index for multiple stages
  - Maintain sequential numbering (1, 2, 3, ...)
  - Preserve relationships
  - Call `project_evolution` to update blueprint
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Stages reordered, blueprint updated

**Branch 6: If path_or_milestone_created**
- **Then**: `trigger_blueprint_update`
- **Details**: Roadmap changed, update blueprint
  - Call `project_evolution` directive
  - Change type: 'completion_path_change'
  - Update Section 4 of ProjectBlueprint.md
  - Increment project version
- **Result**: Blueprint synchronized with new roadmap

**Branch 7: If validate_hierarchy**
- **Then**: `check_parent_child_relationships`
- **Details**: Ensure proper structure
  - Stages must belong to project
  - Milestones must belong to stages
  - Tasks must belong to milestones
  - No orphaned records
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Hierarchy validated, orphans flagged

**Branch 8: If duplicate_stage_name**
- **Then**: `warn_and_confirm`
- **Details**: Stage with similar name exists
  - Warn user about potential duplicate
  - Prompt: "Stage '[name]' already exists. Continue?"
  - User confirms or cancels
- **Result**: User decides to proceed or cancel

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: Invalid parent, duplicate name, ordering conflict

### Error Handling

**on_failure**: `rollback_and_prompt`
- If modification fails: Rollback database transaction
- Prompt user with specific error
- Common issues: Foreign key violation, duplicate name, invalid order

---

## Examples

### Example 1: Create New Completion Path Stage

**Parameters**:
- `project_id`: 1
- `name`: "Performance Optimization"
- `description`: "Profile and optimize critical paths"

**AI Execution**:
1. Validates inputs: ✓ All valid
2. Checks for duplicates: None found
3. Gets next order_index:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Creates stage:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Triggers blueprint update:
   - Calls `project_evolution`
   - Change type: 'completion_path_change'
   - Updates Section 4 of ProjectBlueprint.md
   - Increments project version
6. Returns:
   ```json
   {
     "stage_id": 5,
     "name": "Performance Optimization",
     "order_index": 5,
     "status": "pending"
   }
   ```

### Example 2: Create New Milestone

**Parameters**:
- `completion_path_id`: 2
- `name`: "Matrix Operations"
- `description`: "Core matrix calculation functions"
- `priority`: 2

**AI Execution**:
1. Validates stage exists:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Checks for duplicate milestones: None found
3. Creates milestone:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Logs creation:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Returns:
   ```json
   {
     "milestone_id": 8,
     "name": "Matrix Operations",
     "stage": "Core Development",
     "priority": 2,
     "status": "pending"
   }
   ```

### Example 3: Reorder Stages

**Parameters**:
- `reorder_map`: {
    3: 2,  // Move stage 3 to position 2
    2: 3   // Move stage 2 to position 3
  }

**AI Execution**:
1. Validates all stages exist
2. Checks for order conflicts: None
3. Updates order indices in transaction:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Triggers blueprint update:
   - Calls `project_evolution`
   - Updates Section 4 with new order
5. Logs reordering:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
6. Returns: "Stages reordered successfully"

### Example 4: Duplicate Stage Name Warning

**Parameters**:
- `name`: "Core Development"
- `description`: "Build core features"

**Context**: Stage "Core Development" already exists

**AI Execution**:
1. Checks for duplicates:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Warns user:
   ```
   ⚠️  Stage with similar name already exists

   Existing stage: "Core Development" (in_progress)
   New stage: "Core Development"

   This appears to be a duplicate.

   Options:
   1. Cancel (recommended)
   2. Create with different name
   3. Create anyway
   ```
3. User chooses: "2" (Different name)
4. Prompts: "Enter new name:"
5. User provides: "Core Features Expansion"
6. Creates with new name

### Example 5: Create Task Within Milestone (Delegation)

**Parameters**:
- `milestone_id`: 8
- `task_name`: "Implement matrix multiplication"
- `task_description`: "Create pure functional matrix mult"

**AI Execution**:
1. Validates milestone exists: ✓
2. Delegates to `project_task_create`:
   ```python
   project_task_create(
       milestone_id=8,
       name="Implement matrix multiplication",
       description="Create pure functional matrix mult",
       priority=2
   )
   ```
3. Returns task_id from `project_task_create`

### Example 6: Orphaned Milestone Detection

**Background**: User deleted completion_path stage but milestones remain

**AI Execution**:
1. Runs hierarchy validation:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Warns user:
   ```
   ⚠️  Orphaned milestone detected

   Milestone: "Orphaned Tests" (id=12)
   Missing parent stage

   Options:
   1. Link to existing stage
   2. Delete milestone
   3. Leave as-is (not recommended)
   ```
3. User chooses: "1" (Link to stage)
4. Lists available stages
5. User selects stage
6. Updates milestone:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Integration with Other Directives

### Called By:
- `project_init` - Creates initial roadmap structure
- `project_task_decomposition` - May create milestones
- `project_evolution` - Updates roadmap when goals change
- User directly - Manual roadmap management

### Calls:
- `project_evolution` - Updates blueprint when roadmap changes
- `project_task_create` - Delegates task creation
- `project_subtask_create` - Delegates subtask creation

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: path_misaligned
**Issue**: New stage doesn't fit logically in roadmap sequence
**Resolution**: Prompt user for roadmap alignment, suggest appropriate position

### Roadblock 2: duplicate_entry
**Issue**: Stage or milestone with same name exists
**Resolution**: Verify uniqueness, warn user, suggest alternative name

### Roadblock 3: invalid_order
**Issue**: Order indices become inconsistent
**Resolution**: Recalculate all order indices sequentially (1, 2, 3, ...)

### Roadblock 4: orphaned_records
**Issue**: Child records exist without valid parents
**Resolution**: Detect orphans, offer to link or delete

### Roadblock 5: foreign_key_violation
**Issue**: Attempting to create child without valid parent
**Resolution**: Validate parent exists first, prompt user to create parent

---

## Intent Keywords

- "add path"
- "create stage"
- "update roadmap"
- "add milestone"
- "reorder stages"
- "restructure roadmap"

**Confidence Threshold**: 0.6

---

## Related Directives

- `project_init` - Creates initial roadmap structure
- `project_evolution` - Updates blueprint when roadmap changes
- `project_task_create` - Creates tasks within milestones
- `project_task_decomposition` - Decides when to create milestones
- `project_refactor_path` - Major roadmap restructuring

---

## Roadmap Hierarchy

```
Project
  └── Completion Path (Stages)
      └── Milestones
          └── Tasks
              ├── Subtasks
              └── Items
```

**Relationships**:
- **1 Project** : **N Completion Path Stages**
- **1 Stage** : **N Milestones**
- **1 Milestone** : **N Tasks**
- **1 Task** : **N Subtasks** + **N Items**

---

## Input Parameters

**For New Stage**:
- `project_id` (int) - Project this stage belongs to
- `name` (str) - Stage name (e.g., "Core Development")
- `description` (str) - Stage description
- `order_index` (int, optional) - Position (auto if not specified)

**For New Milestone**:
- `completion_path_id` (int) - Parent stage ID
- `name` (str) - Milestone name (e.g., "Matrix Operations")
- `description` (str) - Milestone description
- `priority` (int, 1-5) - Milestone priority

**For Reorder**:
- `reorder_map` (dict) - Mapping of stage_id to new order_index

---

## Notes

- **Maintain sequential order** - order_index should be 1, 2, 3, ... (no gaps)
- **Trigger blueprint updates** - Call `project_evolution` when roadmap changes
- **Validate hierarchy** - Ensure no orphaned records
- **Check duplicates** - Warn about similar names
- **Delegate task creation** - Use `project_task_create` for tasks
- **Log all modifications** - Audit trail in `notes` table
- **Transactional updates** - Rollback on failure
- **Support restructuring** - Enable major roadmap changes via reordering
