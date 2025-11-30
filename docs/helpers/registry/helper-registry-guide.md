# Helper Registry Guide

**Purpose:** Design decisions, philosophy, and standards for the helper registry system

---

## Key Design Decisions

### 1. File Structure - Split by Database
**Decision**: Split helpers into separate files by database instead of one monolithic file

**Why**: Easier to manage, clearer organization, better for future maintenance

**Structure**:
- `helpers_registry_core.json` - MCP database (aifp_core.db)
- `helpers_registry_user_settings.json` - User preferences database (user_preferences.db)
- `helpers_registry_user_directives_getters.json` - User directives READ operations
- `helpers_registry_user_directives_setters.json` - User directives WRITE operations
- `helpers_registry_project_core.json` - Project table operations
- `helpers_registry_project_structure_getters.json` - Code structure READ
- `helpers_registry_project_structure_setters.json` - Code structure WRITE
- `helpers_registry_project_workflow_getters.json` - Workflow READ
- `helpers_registry_project_workflow_setters.json` - Workflow WRITE
- `helpers_registry_git.json` - Git integration operations

### 2. Getters/Setters Split Strategy
**Decision**: Split large registries (>70 helpers) by operation type

**Why**: Keeps files manageable, logical separation between read and write operations

**When to split**:
- User directives: 78 helpers → getters (45) + setters (33)
- Project structure: 76 helpers → getters (38) + setters (38)
- Project workflow: 91 helpers → getters (54) + setters (37)

**When NOT to split**:
- Small registries (<20 helpers): Keep unified (project_core: 5, git: 10)
- Medium registries (20-50 helpers): Evaluate case-by-case

### 3. Return Statements Purpose
**Original Misunderstanding**: Initially designed as type definitions/schema

**Correct Purpose**: AI behavioral guidance - what to check/do NEXT after calling helper

**Content**:
- Conditional logic suggestions
- Directive chaining recommendations
- Validation checks to perform
- Helper chaining guidance
- FP flow reminders
- User interaction expectations

**Format**: Array of simple strings (flexible, no predefined keys needed)

**Examples**:
- "If initialized=false, escalate to project_init directive"
- "Verify flows are added for this file in file_flows table if necessary"
- "Check is_required flag - required helpers must be called"
- "Follow chain of severity: sidequests → subtasks → tasks"

### 4. Metadata Standards
**Removed fields**: `sources` - these are production files for DB import, not dev docs

**Required fields**:
- `version`: Semantic versioning (1.0.0)
- `last_updated`: YYYY-MM-DD format
- `description`: Clear, concise registry purpose
- `database`: Full database name (e.g., "project.db")
- `target_database`: Database name without extension (e.g., "project")
- `total_helpers`: Exact count for verification
- `schema_version`: Schema compatibility version
- `notes`: Additional context or warnings

**Database naming**: Always use full names: `aifp_core.db`, `project.db`, `user_preferences.db`, `user_directives.db`

### 5. Helper Function Classification
**`is_tool`**: Boolean - MCP-exposed tools (primary entry points for AI)
- True = AI can call directly via MCP
- False = Not exposed via MCP

**`is_sub_helper`**: Boolean - Internal utilities called by other helpers
- True = AI shouldn't call directly (internal implementation detail)
- False = AI can call when needed

**Regular helpers**: Neither tool nor sub-helper
- AI can call when appropriate
- Often called through directive workflows

### 6. Source of Truth Hierarchy
1. **Primary**: JSON registry files (production-ready, complete)
2. **Secondary**: `info-helpers-*.txt` files (human-readable documentation)
3. **Tertiary**: Other docs (to be consolidated/archived)

---

## Database-Specific Guidelines

### User Directives Special Nature
**Philosophy**: AI has freedom to write custom SQL queries for user_directives.db

**Why**: User directives are dynamic, user-defined automation. Helpers are guides, not constraints.

**Implications**:
- Helpers provide convenience, not restrictions
- AI encouraged to write custom queries if helpers don't satisfy needs
- Emphasize this flexibility in return_statements
- User directives flow: user file → AI parsing & clarification → validated directives → implementation → activation

**Example return statement**: "AI is encouraged to write custom queries if helpers don't satisfy needs. User directives database is designed for flexibility."

### Project Database Organization
**Structure table** (infrastructure, files, functions, types, interactions):
- Code-level tracking
- File checksums and validation
- Function purity analysis
- Type definitions
- Cross-function dependencies

**Workflow table** (tasks, themes, flows, milestones, notes):
- Project management
- Progress tracking
- Organization and categorization
- Completion path management

**Core table** (project):
- Single entry per database
- High-level project metadata
- Git synchronization fields
- Blueprint tracking

**Git integration**: Cross-cutting concern supporting multi-user collaboration

### Core Database (aifp_core.db)
**Nature**: Read-only for AI

**Purpose**: Central registry of directives, helpers, and their relationships

**Never modified**: AI queries but never writes to aifp_core.db

---

## File Organization Standards

### File Naming Convention
Pattern: `helpers_registry_{database}_{category}_{operation}.json`

**Examples**:
- `helpers_registry_core.json` (no category needed - single file)
- `helpers_registry_user_settings.json` (no category needed - single file)
- `helpers_registry_project_core.json` (category = core, no operation split)
- `helpers_registry_project_structure_getters.json` (category = structure, operation = getters)
- `helpers_registry_git.json` (category = git, no operation split)

### File Splitting Strategy
**Guideline**: If any registry file exceeds ~1500 lines or ~70 helpers:

1. **First try**: Split by operation type (getters/setters)
   - Separate read operations from write operations
   - Most intuitive split for developers

2. **If still too large**: Split by table/category
   - Group related helpers together
   - Example: tasks_helpers, files_helpers

3. **Last resort**: Number the splits (1, 2, 3, etc.)
   - Use when no logical categorization exists
   - Keep clear naming: `helpers_registry_{database}_{category}_{number}.json`

### Directory Structure
```
docs/helpers/registry/
├── helpers_registry_core.json
├── helpers_registry_user_settings.json
├── helpers_registry_user_directives_getters.json
├── helpers_registry_user_directives_setters.json
├── helpers_registry_project_core.json
├── helpers_registry_project_structure_getters.json
├── helpers_registry_project_structure_setters.json
├── helpers_registry_project_workflow_getters.json
├── helpers_registry_project_workflow_setters.json
├── helpers_registry_git.json
├── HELPER_REGISTRY_STATUS.md
└── helper-registry-guide.md (this file)
```

---

## Schema Standards

### Helper Entry Schema
Every helper must include:

**Required fields**:
- `name`: Function name (exact match to implementation)
- `file_path`: Path to implementation file
- `database`: Which database this helper operates on
- `target_database`: CHECK constraint value for aifp_core.db
- `purpose`: Detailed description of what this helper does
- `parameters`: Array of parameter objects
- `return_statements`: Array of AI behavioral guidance
- `error_handling`: How errors are handled
- `is_tool`: Boolean - exposed via MCP
- `is_sub_helper`: Boolean - internal utility

**Optional fields**:
- `used_by_directives`: Array of directive names
- `calls_helpers`: Array of helper names this function calls

### Parameter Object Schema
```json
{
  "name": "parameter_name",
  "type": "str|int|bool|float|dict|list",
  "required": true|false,
  "default": null|value,
  "description": "Parameter purpose (optional)",
  "values": ["enum", "values"] // optional for enums
}
```

---

## Quality Standards

### Completeness Checklist
For each helper entry:
- ✅ Name matches implementation
- ✅ Purpose is clear and detailed
- ✅ All parameters documented
- ✅ Return statements provide AI guidance
- ✅ Error handling specified
- ✅ Classification correct (is_tool, is_sub_helper)
- ✅ Used by directives listed (if known)
- ✅ Calls helpers listed (if applicable)

### Return Statements Quality
**Good return statements**:
- Provide next-step guidance
- Mention related helpers/directives
- Highlight validation needs
- Warn about edge cases
- Suggest conditional logic

**Poor return statements**:
- Just describe return type
- Duplicate purpose field
- Too vague or generic
- No actionable guidance

---

## Version Control

### Schema Version
Current: `1.0`

**When to increment**:
- Major changes to required fields
- Breaking changes to structure
- New mandatory fields added

### File Version
Current: `1.0.0`

**When to increment**:
- Major (1.x.x): Breaking schema changes
- Minor (x.1.x): New helpers added
- Patch (x.x.1): Bug fixes, clarifications

---

## Import Readiness

These registries are designed for direct import into `aifp_core.db` helper_functions table.

**Import script requirements**:
1. Validate JSON schema
2. Check for duplicate helper names
3. Verify file_path references
4. Validate database references
5. Insert into helper_functions table
6. Update directive_helpers junction table

**Ready for production**: Yes, after file consolidation review completes

---

**Last Updated**: 2025-11-29
**Status**: Complete and ready for database import after file review
