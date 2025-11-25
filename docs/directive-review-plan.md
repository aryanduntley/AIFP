# Directive Review Plan
**Date**: 2025-11-24
**Purpose**: Systematic review of all directives to reflect schema changes and minimize helper references

---

## Schema Changes Impacting Directives

### Critical Changes Requiring Directive Updates

#### 1. Reservation System (project.db)
- **New Fields**: `is_reserved` on files, functions, types
- **New Workflow**: Reserve → Implement → Finalize with ID embedding
- **Impacted Directives**:
  - All FP directives that create functions
  - `project_file_management` - file operations
  - `fp_adt` - type creation
  - Any directive that modifies files/functions/types

**Required Updates**:
- Add reservation step before creation
- Embed IDs: `# AIFP:FILE:10`, `# AIFP:FUNC:42`, `# AIFP:TYPE:7`
- Add finalization step after implementation
- Update error handling for reservation conflicts

#### 2. Unique Function Names (project.db)
- **Change**: `functions.name` is now UNIQUE
- **Impact**: No function overloading allowed (FP flat namespace)
- **Impacted Directives**:
  - All FP directives that create functions
  - Function naming guidance directives

**Required Updates**:
- Enforce descriptive, unique names (e.g., `process_user()` not `process()`)
- Check for existing function names before creation
- Update naming conventions in guidance
- Error handling for duplicate name attempts

#### 3. types_functions Junction Table (project.db)
- **Removed**: `types.linked_function_id`
- **Added**: `types_functions` table with role field
- **Role Values**: 'factory', 'transformer', 'operator', 'pattern_matcher', 'accessor', 'validator', 'combinator'
- **Impacted Directives**:
  - `fp_adt` - type creation
  - Any directive creating ADTs or type-related functions

**Required Updates**:
- Use types_functions table for type-function relationships
- Remove references to linked_function_id
- Specify role when linking types to functions
- Use FP terminology (factory, not constructor)

#### 4. New Fields Added (project.db)
- **files.name** (separate from path)
- **functions.returns** (JSON return value description)
- **types.file_id** (track which file defines type)

**Required Updates**:
- Populate file_name when creating files
- Add returns description when creating functions
- Set file_id when creating types

#### 5. Removed project_id Fields (project.db)
- **Removed from**: infrastructure, files, types, themes, flows, completion_path
- **Impact**: No longer pass project_id to helpers

**Required Updates**:
- Remove project_id parameters from helper calls
- Update workflow details that reference project_id

#### 6. Priority Field Standardization (project.db)
- **Change**: tasks.priority from INTEGER to TEXT
- **Values**: 'low', 'medium', 'high', 'critical'
- **Impacted Directives**: All task management directives

**Required Updates**:
- Use TEXT values instead of integers
- Update priority documentation
- Consistent priority levels across all task-related directives

#### 7. CHECK Constraints (all databases)
- **Impact**: All status/priority/select fields now have enforced values
- **Impacted**: All directives that set status, priority, or similar fields

**Required Updates**:
- Ensure directives only use valid values from CHECK constraints
- Document allowed values in directive guidance
- Error handling for invalid values

---

## Directive Files to Review

### 1. directives-project.json (HIGHEST PRIORITY)
**Size**: ~92KB
**Estimated Directives**: ~15-20
**Schema Changes**: Reservation system, priority fields, removed project_id

**Key Directives to Check**:
- `project_init` - Database initialization
- `project_file_management` - File operations (needs reservation)
- Task management directives - Priority field changes
- Status/context directives - Removed project_id

### 2. directives-fp-core.json
**Size**: ~37KB
**Estimated Directives**: ~30-40
**Schema Changes**: Unique function names, returns field

**Key Directives to Check**:
- Function creation directives - Unique names, reservation, returns field
- `fp_purity` and related - Should enforce unique naming
- `fp_chaining` - Function composition with unique names

### 3. directives-fp-aux.json
**Size**: ~45KB
**Estimated Directives**: ~40-50
**Schema Changes**: types_functions junction, unique function names

**Key Directives to Check**:
- `fp_adt` - types_functions table, file_id, reservation
- Type-related directives - Use new junction table
- FP terminology enforcement - No OOP concepts

### 4. directives-git.json
**Size**: ~15KB
**Estimated Directives**: ~10-15
**Schema Changes**: Minimal (mostly isolated from project.db changes)

**Key Directives to Check**:
- Verify no reliance on removed fields
- Check if any git directives interact with project database

### 5. directives-user-pref.json
**Size**: ~13KB
**Estimated Directives**: ~8-12
**Schema Changes**: directive_context → directive_name, CHECK constraints

**Key Directives to Check**:
- Update any references to directive_context field
- Verify scope values match CHECK constraints

### 6. directives-user-system.json
**Size**: ~34KB
**Estimated Directives**: ~15-20
**Schema Changes**: Various user_directives.db updates

**Key Directives to Check**:
- User directive creation/validation pipeline
- action_type CHECK constraint values

### 7. directives-interactions.json
**Size**: ~30KB
**Purpose**: Directive relationships and dependencies

**Key Review**:
- Verify interaction types still valid
- Check for references to deprecated fields

---

## Helper Reference Minimization Guidelines

### Current State (PROBLEM)
```json
{
  "then": "create_project_structure",
  "details": {
    "helper": "create_project_directory",
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {...},
    "available_helpers": [
      "get_all_directives",
      "get_directive",
      "search_directives",
      ...
    ]
  }
}
```

**Issues**:
- Helpers scattered throughout directive workflow details
- Must update directive JSON when helpers change
- Duplicate information (also in directive_helpers table)
- Maintenance burden

### Target State (SOLUTION)
```json
{
  "then": "create_project_structure",
  "details": {
    "action": "Create .aifp-project/ directory structure",
    "validation": "Verify directories exist and are writable",
    "next_step": "initialize_databases"
  }
}
```

**Benefits**:
- Directives describe WHAT to do, not HOW (implementation details)
- Helper mappings centralized in directive_helpers table
- Easy to update helpers without touching directive JSON
- Cleaner, more maintainable directives

### Guidelines for Directive JSON Content

**INCLUDE (Directive Logic)**:
- Workflow steps (what needs to happen)
- Branching conditions (if/then logic)
- Validation requirements
- Error handling strategies
- User prompts and messages
- Database field values to set
- Status transitions

**MINIMIZE (Implementation Details)**:
- Specific helper function names (use directive_helpers table instead)
- Module/file paths (internal implementation detail)
- Helper parameter details (helpers know their own parameters)
- Lists of "available helpers" (redundant with directive_helpers table)

**EXCEPTION - When to Include Helper References**:
- When helper is the entire purpose of directive step (e.g., "call get_all_directives()")
- When specific helper parameters override defaults
- When directive provides user-facing tool access (MCP tools)

### Refactoring Approach

**Before** (Too Specific):
```json
{
  "then": "create_file_record",
  "details": {
    "helper": "add_file",
    "parameters": {
      "path": "src/calculator.py",
      "language": "python"
    }
  }
}
```

**After** (Directive-Focused):
```json
{
  "then": "create_file_record",
  "details": {
    "action": "Register new file in project database",
    "file_path": "src/calculator.py",
    "language": "python",
    "set_reserved": true
  }
}
```
*Helper mapping in directive-helper-interactions.json handles the implementation*

---

## REFINED Systematic Review Process (5 at a Time)

**Critical Finding**: sync-directives.py does NOT use `available_helpers` arrays
**Action**: Remove all `available_helpers`, replace SQL queries with helper calls

### Workflow Per Batch (5 Directives)

#### Step 1: Extract Batch (5 min)
```bash
jq '.[0:5]' directives-project.json > batch-01-project.json
```

#### Step 2: Analyze Batch (10 min)
- List directive names
- Check for SQL queries
- Check for available_helpers arrays
- Check for project_id references
- Identify file/function/type creation (reservation needed)

#### Step 3: Fix All Issues (30-40 min)
For each directive in batch:
1. **Remove** `available_helpers` arrays (not used)
2. **Replace** SQL queries with helper function calls
3. **Remove** `project_id` references
4. **Update** helper names to current helpers
5. **Verify** priority/status values
6. **Add** reservation workflow (if creates files/functions/types)
7. **Remove** `linked_function_id` (if type directive)
8. **Verify** FP terminology (no OOP)

#### Step 4: Validate Batch (5 min)
```bash
jq '.' batch-01-project.json > /dev/null  # Check JSON syntax
git diff batch-01-project.json             # Review changes
```

#### Step 5: Review MD Files (15-20 min)
After every 5 directives, review corresponding .md files:
1. Open each .md in src/aifp/reference/directives/
2. Update to match JSON changes
3. Fix examples
4. Document new workflows

#### Step 6: Commit Batch
- Mark batch complete in master checklist
- Prepare for next batch

**Time Per Batch**: ~1-1.5 hours
**Total Batches for directives-project.json**: 8 batches (37 directives)

---

### Detailed Per-Directive Checklist

#### 1. Remove available_helpers
```json
// REMOVE THIS:
"available_helpers": [
  "get_all_directives",
  "get_directive",
  ...
]
```
**Reason**: sync-directives.py doesn't read it. directive-helper-interactions.json populates directive_helpers table.

#### 2. Replace SQL Queries with Helpers
```json
// BEFORE (BAD):
"query": "SELECT type, value FROM infrastructure WHERE project_id = ?"

// AFTER (GOOD):
"action": "get_infrastructure",
"helper": "get_infrastructure_items"  // Reference in directive-helper-interactions.json
```

**Why**:
- AI shouldn't formulate custom queries
- Helpers are faster, safer, validated
- Easier to maintain

#### 3. Remove project_id
```json
// BEFORE:
"query": "... WHERE project_id = ?"

// AFTER:
"query": "..."  // No project_id needed (1 project per database)
```

#### 4. Add Reservation System (if creates files/functions/types)
```json
"workflow": {
  "trunk": "reserve_then_create",
  "branches": [
    {
      "then": "reserve_function_name",
      "details": {
        "helper": "reserve_function",
        "returns_function_id": true
      }
    },
    {
      "then": "implement_with_id",
      "details": {
        "embed_id": "# AIFP:FUNC:42",
        "write_code": true
      }
    },
    {
      "then": "finalize_reservation",
      "details": {
        "helper": "finalize_function",
        "set_is_reserved": false
      }
    }
  ]
}
```

---

### Phase 4: New Directive Creation (Separate Task)

Create new directives (not in existing files):
1. **reserve_file** - Reserve file name with ID return
2. **reserve_function** - Reserve function name with ID return
3. **reserve_type** - Reserve type name with ID return
4. **finalize_reservation** - Mark reservations as finalized
5. **verify_ids** - Check code IDs match database
6. **repair_ids** - Fix ID mismatches

**Output**: New directive JSON + MD files

---

### Phase 5: Final Merge & Validation

After all batches complete:
```bash
# Merge all batches back
jq -s 'add' batch-*-project.json > directives-project-updated.json

# Verify count
jq '. | length' directives-project-updated.json  # Should be 37

# Replace original
mv directives-project.json directives-project-backup.json
mv directives-project-updated.json directives-project.json
```

---

## Checklist for Each Directive

### Schema Compliance
- [ ] No references to `project_id` (if project directive)
- [ ] No references to `linked_function_id` (if type directive)
- [ ] Priority values use TEXT not INTEGER
- [ ] All status values match CHECK constraints
- [ ] New fields included where applicable (file_name, returns, file_id)
- [ ] Unique function name enforcement (if creates functions)
- [ ] FP terminology only (no OOP: constructor, method, class)

### Reservation System (if applicable)
- [ ] Reserve step before creation
- [ ] ID embedding in code comments
- [ ] Finalize step after implementation
- [ ] Error handling for reservation conflicts
- [ ] is_reserved field management

### Helper References
- [ ] Embedded helper calls minimized
- [ ] Implementation details removed
- [ ] Mappings added to directive-helper-interactions.json
- [ ] Workflow focuses on WHAT not HOW
- [ ] User-facing tools clearly documented

### Documentation
- [ ] Corresponding .md file updated
- [ ] Workflow examples current
- [ ] New fields documented
- [ ] Error scenarios covered
- [ ] Next steps clearly stated

---

## Review Priority Order

### High Priority (Week 1)
1. **directives-project.json** - Most schema changes, reservation system
2. **directives-fp-core.json** - Function creation, unique names
3. **directives-fp-aux.json** - ADT creation, types_functions

### Medium Priority (Week 2)
4. **New directives** - reserve/finalize/verify system
5. **directive-helper-interactions.json** - Update mappings
6. **directives-user-pref.json** - directive_context rename

### Lower Priority (Week 3)
7. **directives-git.json** - Minimal changes expected
8. **directives-user-system.json** - Verify user directive pipeline
9. **directives-interactions.json** - Update relationships

---

## Success Criteria

Directives are ready for database sync when:
1. ✅ All schema changes reflected in directive workflows
2. ✅ No references to removed fields
3. ✅ All new required fields documented
4. ✅ Reservation workflow integrated where needed
5. ✅ Helper references minimized (implementation in table)
6. ✅ CHECK constraint values documented
7. ✅ FP terminology enforced (no OOP)
8. ✅ Unique function name enforcement added
9. ✅ .md files synchronized with JSON changes
10. ✅ directive-helper-interactions.json updated

**Final Step**: Run sync-directives.py to populate database

---

**Last Updated**: 2025-11-24
