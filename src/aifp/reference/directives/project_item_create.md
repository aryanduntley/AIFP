# Directive: project_item_create

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_task_decomposition
**Priority**: MEDIUM - Atomic item creation for task breakdown

---

## Purpose

The `project_item_create` directive handles atomic creation of items in `project.db`. Items are the **smallest work units**, representing individual actionable steps within tasks. This directive serves as the **item constructor**, providing granular task tracking.

Key responsibilities:
- **Create item record** - Insert into `items` table
- **Link to task** - Associate with parent task
- **Set initial status** - Default to 'pending'
- **Optional references** - Link to files, functions, or other entities
- **Track completion** - Enable fine-grained progress monitoring
- **Auto-complete task** - Mark parent task complete when all items done
- **Validate parent** - Ensure task exists and is open

This is the **atomic item creator** - provides granular work breakdown within tasks.

---

## When to Apply

This directive applies when:
- **Breaking down tasks** - Decomposing tasks into specific steps
- **Tracking progress** - Monitoring completion at granular level
- **Action items** - Creating specific, actionable steps
- **Checklist creation** - Building task checklists
- **Called by other directives**:
  - `project_task_decomposition` - Creates items when decomposing tasks
  - `project_file_write` - Creates items for file generation
  - User directly - Manual item creation

**Items vs. Subtasks**:
- **Items**: Smaller, non-blocking, multiple can be active simultaneously
- **Subtasks**: Larger, block parent task, high priority
- **Items**: Track progress within task
- **Subtasks**: Refinement of task requiring dedicated focus

---

## Workflow

### Trunk: validate_inputs

Ensures all required fields are present and parent task is valid.

**Steps**:
1. **Validate item name** - Non-empty, descriptive
2. **Validate parent task** - Task exists and is open
3. **Validate references** - If linking to file/function, verify exists
4. **Check duplicates** - Warn if similar item exists

### Branches

**Branch 1: If inputs_valid**
- **Then**: `check_parent_task_exists`
- **Details**: Verify parent task is valid
  - Query `tasks` table for task_id
  - Check task status (must be pending, in_progress, or paused)
  - If task completed: Cannot add items
  - If task cancelled: Warn but allow (for planning)
- **Query**:
  ```sql
  SELECT id, name, status, milestone_id
  FROM tasks
  WHERE id = ? AND project_id = ?;
  ```
- **Result**: Parent task validated

**Branch 2: If parent_task_valid**
- **Then**: `check_duplicate_items`
- **Details**: Warn if similar item exists
  - Query `items` table for similar names
  - Use fuzzy matching
  - Prompt if duplicate found
- **Query**:
  ```sql
  SELECT name, status
  FROM items
  WHERE task_id = ? AND status != 'completed'
  ORDER BY order_index;
  ```
- **Result**: User confirms or cancels

**Branch 3: If no_duplicates_or_confirmed**
- **Then**: `create_item_record`
- **Details**: Insert new item into database
  - Generate item record
  - Default status: 'pending'
  - Calculate order_index (last + 1)
  - Set created_at, updated_at timestamps
  - Return generated item ID
- **SQL**:
  ```sql
  -- Get last order_index
  SELECT COALESCE(MAX(order_index), 0) + 1 as next_index
  FROM items WHERE task_id = ?;

  -- Create item
  INSERT INTO items (
    task_id,
    name,
    description,
    status,
    order_index,
    reference_table,
    reference_id,
    created_at,
    updated_at
  ) VALUES (?, ?, ?, 'pending', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

  -- Get generated ID
  SELECT last_insert_rowid() as item_id;
  ```
- **Result**: Item created, ID returned

**Branch 4: If item_created_and_reference_provided**
- **Then**: `link_to_reference`
- **Details**: Link item to file, function, or other entity
  - Set `reference_table` (e.g., 'files', 'functions')
  - Set `reference_id` (entity ID)
  - Enables tracking which items relate to which code
- **Example**:
  ```sql
  -- Link item to file
  UPDATE items
  SET reference_table = 'files', reference_id = 15
  WHERE id = ?;
  ```
- **Result**: Item linked to specific entity

**Branch 5: If all_items_completed_after_creation**
- **Then**: `check_task_completion`
- **Details**: Check if task should be marked complete
  - Query all items for task
  - If all items completed: Mark task complete
  - Else: Task remains in current status
- **Query**:
  ```sql
  SELECT COUNT(*) as incomplete_count
  FROM items
  WHERE task_id = ? AND status != 'completed';
  ```
- **SQL** (if count = 0):
  ```sql
  UPDATE tasks
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP
  WHERE id = ?;
  ```
- **Result**: Task auto-completed if all items done

**Branch 6: If item_created**
- **Then**: `log_item_creation`
- **Details**: Record item creation in notes
  - Log item name, parent task
  - Source: directive
  - Include item_id for reference
- **SQL**:
  ```sql
  INSERT INTO notes (
    content,
    note_type,
    reference_table,
    reference_id,
    source,
    directive_name
  ) VALUES (
    'Item created: [name] (task: [task_name])',
    'item_creation',
    'items',
    ?,
    'directive',
    'project_item_create'
  );
  ```
- **Result**: Creation logged

**Branch 7: If bulk_create_requested**
- **Then**: `create_multiple_items`
- **Details**: Create multiple items at once
  - Parse list of item names
  - Create each in sequence
  - Assign consecutive order_index values
  - Return list of item IDs
- **Result**: Multiple items created efficiently

**Branch 8: If parent_task_completed**
- **Then**: `reject_creation`
- **Details**: Cannot add items to completed task
  - Error: "Task '[name]' is completed"
  - Suggestion: "Reopen task or create new task"
  - Abort item creation
- **Result**: Creation blocked

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: Invalid parent task, missing name

### Error Handling

**on_failure**: `rollback_and_prompt`
- If item creation fails: Rollback database transaction
- Prompt user with specific error
- Common issues: Database lock, constraint violation

---

## Examples

### Example 1: Create Single Item

**Parameters**:
- `task_id`: 42
- `name`: "Write multiply_matrices function"
- `description`: "Implement pure functional matrix multiplication"
- `reference_table`: "files"
- `reference_id`: 15

**AI Execution**:
1. Validates inputs: ✓ All valid
2. Checks parent task:
   - ID=42, name="Implement matrix operations", status="in_progress" ✓
3. Checks duplicates: None found
4. Gets next order_index: 1 (first item)
5. Creates item:
   ```sql
   INSERT INTO items (task_id, name, description, status, order_index, reference_table, reference_id, created_at, updated_at)
   VALUES (42, 'Write multiply_matrices function', 'Implement pure functional matrix multiplication', 'pending', 1, 'files', 15, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

   -- Returns item_id: 123
   ```
6. Logs creation:
   ```sql
   INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
   VALUES ('Item created: Write multiply_matrices function (task: Implement matrix operations)', 'item_creation', 'items', 123, 'directive', 'project_item_create');
   ```
7. Returns:
   ```json
   {
     "item_id": 123,
     "name": "Write multiply_matrices function",
     "task": "Implement matrix operations",
     "task_id": 42,
     "status": "pending",
     "order_index": 1,
     "reference": {"table": "files", "id": 15}
   }
   ```

### Example 2: Bulk Create Items (Checklist)

**Parameters**:
- `task_id`: 42
- `items`: [
    "Write multiply_matrices function",
    "Write validate_dimensions helper",
    "Add error handling",
    "Write unit tests"
  ]

**AI Execution**:
1. Validates parent task: ✓ Valid
2. Creates multiple items:
   ```sql
   INSERT INTO items (task_id, name, status, order_index, created_at, updated_at) VALUES
   (42, 'Write multiply_matrices function', 'pending', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
   (42, 'Write validate_dimensions helper', 'pending', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
   (42, 'Add error handling', 'pending', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
   (42, 'Write unit tests', 'pending', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
   ```
3. Returns list of item IDs: [123, 124, 125, 126]
4. Logs: "Created 4 items for task 42"
5. Returns:
   ```json
   {
     "items_created": 4,
     "item_ids": [123, 124, 125, 126],
     "task": "Implement matrix operations"
   }
   ```

### Example 3: Auto-Complete Task When Last Item Created Complete

**Context**: Task has 3 items, all completed. User creates 4th item and immediately marks it complete.

**AI Execution**:
1. Creates item (status='pending')
2. User marks item complete immediately
3. Checks all items:
   ```sql
   SELECT COUNT(*) FROM items WHERE task_id = 42 AND status != 'completed';
   -- Result: 0
   ```
4. All items complete → Mark task complete:
   ```sql
   UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 42;
   ```
5. Logs:
   ```
   Task 42 auto-completed: All 4 items finished
   ```

### Example 4: Item with File Reference

**Parameters**:
- `task_id`: 50
- `name`: "Refactor process_data function"
- `reference_table`: "functions"
- `reference_id`: 88

**AI Execution**:
1. Validates parent task: ✓ Valid
2. Validates function reference:
   ```sql
   SELECT id, name FROM functions WHERE id = 88;
   -- Returns: process_data
   ```
3. Creates item linked to function 88
4. Returns item_id with reference metadata
5. When item marked complete: Can trigger function metadata update

### Example 5: Completed Task Error

**Parameters**:
- `task_id`: 10
- `name`: "Add new feature"

**AI Execution**:
1. Checks parent task:
   - ID=10, name="Setup database", status="completed" ✗
2. Rejects creation:
   ```
   ❌ Cannot add item to completed task

   Task: "Setup database" (completed on 2025-10-25)
   Attempted item: "Add new feature"

   Suggestion: Create new task for this work
   ```
3. Prompts: "Create as new task instead?"
4. If yes: Calls `project_task_create`

### Example 6: Paused Task (Subtask Active)

**Parameters**:
- `task_id`: 15
- `name`: "Document API endpoints"

**Context**: Task paused due to active subtask

**AI Execution**:
1. Checks parent task:
   - ID=15, status="paused" (subtask active)
2. Prompts:
   ```
   ⚠️  Task is paused (subtask active)

   Task: Implement authentication (paused)
   Active subtask: Add email verification

   Add item "Document API endpoints"?
   - Item will be pending until task resumes
   - Subtask must complete first
   ```
3. User confirms: "Yes"
4. Creates item with status='pending'
5. Item will become actionable when task resumes

---

## Integration with Other Directives

### Called By:
- `project_task_decomposition` - Creates items when decomposing tasks
- `project_file_write` - Links files to items
- User directly - Manual item creation

### Calls:
- `project_task_update` - Auto-completes task when all items done
- `project_file_read` - Validates file references

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Create item
INSERT INTO items (
  task_id,
  name,
  description,
  status,
  order_index,
  reference_table,
  reference_id,
  created_at,
  updated_at
) VALUES (?, ?, ?, 'pending', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Get item ID
SELECT last_insert_rowid() as item_id;

-- Auto-complete task if all items done
UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP
WHERE id = ? AND (SELECT COUNT(*) FROM items WHERE task_id = ? AND status != 'completed') = 0;

-- Log creation
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
VALUES (?, 'item_creation', 'items', ?, 'directive', 'project_item_create');
```

---

## Roadblocks and Resolutions

### Roadblock 1: parent_task_not_found
**Issue**: Specified parent task doesn't exist
**Resolution**: List available open tasks, prompt user to select

### Roadblock 2: parent_task_completed
**Issue**: Cannot add items to completed task
**Resolution**: Offer to create new task instead

### Roadblock 3: duplicate_item
**Issue**: Similar item already exists
**Resolution**: Warn user, show similar item, confirm intent

### Roadblock 4: invalid_reference
**Issue**: Referenced entity (file/function) doesn't exist
**Resolution**: Skip reference or prompt user to correct

### Roadblock 5: database_constraint_violation
**Issue**: Item creation violates database constraints
**Resolution**: Rollback, report specific constraint, prompt user

---

## Input Parameters

**Required**:
- `task_id` (int) - Parent task ID
- `name` (str) - Item name (non-empty, action-oriented)

**Optional**:
- `description` (str, default: "") - Detailed item description
- `reference_table` (str, default: null) - Entity type (files, functions, etc.)
- `reference_id` (int, default: null) - Entity ID
- `order_index` (int, default: auto) - Position in task checklist

**Bulk Create**:
- `items` (list[str]) - List of item names for bulk creation

**Returns**:
```json
{
  "item_id": 123,
  "name": "Item name",
  "task": "Task name",
  "task_id": 42,
  "status": "pending",
  "order_index": 1,
  "reference": {"table": "files", "id": 15}
}
```

---

## Intent Keywords

- "create item"
- "add item"
- "add checklist"
- "break down"
- "add step"

**Confidence Threshold**: 0.6

---

## Related Directives

- `project_task_decomposition` - Decides when to create items
- `project_task_create` - Creates parent tasks
- `project_subtask_create` - Creates larger subtasks
- `project_task_update` - Auto-completes task when items done
- `project_file_write` - Links items to generated files

---

## Item Best Practices

**Good Item Names** (Action-oriented):
- "Write multiply_matrices function"
- "Add error handling for edge cases"
- "Write unit tests for validation"
- "Document API endpoints"
- "Refactor process_data for clarity"

**Bad Item Names** (Vague):
- "Fix bug"
- "Update code"
- "Do thing"
- "TODO"

**Item Scope**:
- Single, specific action
- 15-60 minutes of work typically
- Clear completion criteria
- Atomic (cannot be subdivided)

---

## Item Status Lifecycle

```
pending → in_progress → completed
   ↓                       ↑
   └─────→ cancelled ←─────┘
```

**Valid Transitions**:
- pending → in_progress
- in_progress → completed
- pending → cancelled
- in_progress → cancelled

**Invalid Transitions**:
- completed → any (items cannot be reopened)

---

## Validation Rules

**Item Name**:
- Non-empty
- Max 200 characters
- Action-oriented (starts with verb)
- Specific and clear

**Parent Task**:
- Must exist in database
- Can be any status (even paused/cancelled for planning)
- Completed tasks discouraged but allowed

**Reference**:
- If provided, must be valid entity
- reference_table: 'files', 'functions', 'types', etc.
- reference_id: Must exist in referenced table

---

## Notes

- **Items are lightweight** - No parent task blocking
- **Multiple active items OK** - Unlike subtasks
- **Auto-complete tasks** - When all items done
- **Link to entities** - Track which items relate to which code
- **Order matters** - order_index controls display sequence
- **Bulk creation supported** - Efficient checklist creation
- **Return item ID** - Enable immediate tracking
- **Log all creations** - Audit trail in `notes` table
- **Atomic operation** - Single transaction, rollback on failure
