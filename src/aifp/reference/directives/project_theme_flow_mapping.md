# Directive: project_theme_flow_mapping

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_file_write
**Priority**: MEDIUM - Theme and flow organization

---

## Purpose

The `project_theme_flow_mapping` directive infers or assigns theme and flow groupings for files based on metadata, updating linking tables in `project.db`. This directive serves as the **organizational coordinator**, maintaining thematic and procedural structure across the codebase.

Key responsibilities:
- **Infer themes from metadata** - Extract theme from AIFP_METADATA or file path
- **Assign flows** - Determine procedural flow associations
- **Create new themes/flows** - Add if not existing
- **Update linking tables** - Maintain file_flows and flow_themes relationships
- **Trigger blueprint updates** - Call `project_evolution` when themes/flows change
- **Support roadmap visualization** - Enable theme-based project views

This is the **theme/flow organizer** - ensures files are properly categorized for project understanding.

---

## When to Apply

This directive applies when:
- **New file created** - Assign theme and flow to new files
- **File metadata updated** - Re-assign based on new AIFP_METADATA
- **Theme/flow inference** - Auto-detect from file path or purpose
- **Manual assignment** - User explicitly assigns themes/flows
- **Called by other directives**:
  - `project_file_write` - Assigns themes/flows to new files
  - `project_update_db` - Updates mappings when files change
  - User directly - Manual theme/flow management

---

## Workflow

### Trunk: infer_metadata

Attempts to determine theme and flow from file metadata.

**Steps**:
1. **Read AIFP_METADATA** - Extract theme/flow from file header
2. **Parse file path** - Infer from directory structure (e.g., `src/auth/` → "Authentication")
3. **Analyze function purposes** - Infer from function descriptions
4. **Check existing mappings** - See if similar files have themes/flows
5. **Prompt user if uncertain** - Ask for clarification if confidence low

### Branches

**Branch 1: If metadata_present**
- **Then**: `extract_theme_and_flow`
- **Details**: Read theme and flow from AIFP_METADATA
  - Parse AIFP_METADATA JSON in file header
  - Extract `theme` field (e.g., "Authentication")
  - Extract `flow` field (e.g., "Login Flow")
  - High confidence (> 0.9) if explicitly specified
- **Example Metadata**:
  ```python
  # AIFP_METADATA: {
  #   "function_names": ["hash_password", "validate_token"],
  #   "theme": "Authentication",
  #   "flow": "Security Flow",
  #   ...
  # }
  ```
- **Result**: Theme and flow extracted from metadata

**Branch 2: If no_metadata_infer_from_path**
- **Then**: `infer_from_file_path`
- **Details**: Deduce theme from directory structure
  - Parse file path segments
  - Map common patterns:
    - `src/auth/` → "Authentication"
    - `src/database/` → "Database Operations"
    - `src/api/` → "API Layer"
    - `src/utils/` → "Utilities"
  - Medium confidence (0.5 - 0.7)
- **Result**: Theme inferred from path, prompt for flow

**Branch 3: If theme_or_flow_inferred**
- **Then**: `check_if_exists_in_db`
- **Details**: Verify theme/flow exist in database
  - Query `themes` table for matching name
  - Query `flows` table for matching name
  - If exists: Use existing ID
  - If not exists: Create new theme/flow
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Theme/flow IDs obtained or created

**Branch 4: If theme_exists**
- **Then**: `link_to_existing_theme`
- **Details**: Use existing theme
  - Get theme_id from themes table
  - Use for file_flows linking
- **Result**: Existing theme reused

**Branch 5: If theme_not_exists**
- **Then**: `create_new_theme`
- **Details**: Add new theme to database
  - Insert into `themes` table
  - Infer description from name
  - Trigger `project_evolution` (themes changed)
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: New theme created, evolution triggered

**Branch 6: If flow_not_exists**
- **Then**: `create_new_flow`
- **Details**: Add new flow to database
  - Insert into `flows` table
  - Infer description from name
  - Trigger `project_evolution` (flows changed)
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: New flow created, evolution triggered

**Branch 7: If theme_and_flow_obtained**
- **Then**: `update_file_flows_table`
- **Details**: Link file to flow
  - Insert into `file_flows` table (file_id, flow_id)
  - Update if already exists
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: File linked to flow

**Branch 8: If flow_obtained**
- **Then**: `update_flow_themes_table`
- **Details**: Link flow to theme
  - Insert into `flow_themes` table (flow_id, theme_id)
  - Update if already exists
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Flow linked to theme

**Branch 9: If theme_or_flow_created**
- **Then**: `call_project_evolution`
- **Details**: Update ProjectBlueprint.md
  - Trigger: `project_evolution` directive
  - Change type: 'themes_or_flows_change'
  - Update Section 3 of blueprint
  - Increment project version
- **Result**: Blueprint synchronized with new themes/flows

**Branch 10: If confidence_low**
- **Then**: `prompt_user`
- **Details**: Ask user for theme/flow assignment
  - Present file info (path, functions)
  - Show existing themes and flows
  - Prompt: "Assign theme and flow for [file]:"
  - User selects or creates new
- **Result**: User provides theme/flow

**Branch 11: If no_metadata_and_path_generic**
- **Then**: `assign_default_theme`
- **Details**: Use default "Uncategorized" theme
  - Theme: "Uncategorized"
  - Flow: "General"
  - Prompt user to categorize later
- **Result**: File has default categorization

**Fallback**: `prompt_user`
- Present file details and ask for theme/flow
- Log to `notes` for future learning

### Error Handling

**on_failure**: `rollback_and_prompt`
- If mapping fails: Rollback database transaction
- Prompt user with specific error
- Common issues: Database constraint violation, invalid theme/flow names

---

## Examples

### Example 1: File with Explicit Metadata

**File**: `src/auth/login.py`
```python
# AIFP_METADATA: {
#   "function_names": ["hash_password", "validate_credentials"],
#   "theme": "Authentication",
#   "flow": "Login Flow",
#   ...
# }
```

**AI Execution**:
1. Reads AIFP_METADATA: Theme="Authentication", Flow="Login Flow"
2. Checks if theme exists:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
3. Checks if flow exists:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Links file to flow:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Links flow to theme:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
6. No evolution needed (theme/flow already exist)
7. Logs mapping:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 2: Infer from Path, Create New Theme

**File**: `src/payment/processor.py` (no AIFP_METADATA)

**AI Execution**:
1. No metadata found → Infer from path
2. Parses path: `/src/payment/` → Theme="Payment Processing"
3. Checks if theme exists:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Creates new theme:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Triggers `project_evolution`:
   - Change type: 'themes_or_flows_change'
   - Updates Section 3 of ProjectBlueprint.md
   - Adds evolution history
6. Prompts for flow: "Assign flow for payment/processor.py:"
7. User provides: "Transaction Flow"
8. Creates new flow:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
9. Links file to flow and flow to theme
10. Logs mapping and evolution

### Example 3: Low Confidence, Prompt User

**File**: `src/utils/helpers.py` (generic name, no metadata)

**AI Execution**:
1. No metadata found
2. Path inference: `/src/utils/` → Generic, low confidence
3. Prompts user:
   ```
   Unable to infer theme/flow for: src/utils/helpers.py

   Functions: format_date, parse_json, log_error

   Existing themes:
   1. Authentication
   2. Database Operations
   3. API Layer
   4. Payment Processing

   Assign theme (or create new):
   ```
4. User selects: "4" (create new) → "Utility Functions"
5. Creates theme "Utility Functions"
6. Prompts for flow:
   ```
   Existing flows:
   1. Login Flow
   2. Data Access Flow
   3. Request Handling
   4. Transaction Flow

   Assign flow (or create new):
   ```
7. User creates: "Helper Functions Flow"
8. Links file, triggers evolution

### Example 4: Update Existing Mapping

**File**: `src/auth/login.py` (already mapped, metadata changed)

**Old Metadata**: Theme="Authentication", Flow="Login Flow"
**New Metadata**: Theme="Security", Flow="Identity Verification"

**AI Execution**:
1. Reads new metadata: Theme="Security", Flow="Identity Verification"
2. Checks if theme exists:
   - "Security" not found
   - Creates new theme
3. Checks if flow exists:
   - "Identity Verification" not found
   - Creates new flow
4. Updates file_flows mapping:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Updates flow_themes mapping:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
6. Triggers `project_evolution` (new theme and flow created)
7. Logs remapping:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 5: Multiple Files Same Theme

**Files**:
- `src/auth/login.py`
- `src/auth/register.py`
- `src/auth/reset_password.py`

**AI Execution**:
1. Processes login.py: Creates "Authentication" theme, "Login Flow"
2. Processes register.py: Reuses "Authentication" theme, creates "Registration Flow"
3. Processes reset_password.py: Reuses "Authentication" theme, creates "Password Reset Flow"
4. All three flows linked to "Authentication" theme
5. Single evolution trigger after all three processed
6. Section 3 updated with:
   ```markdown
   ### Themes

   1. **Authentication**
      - Purpose: User identity and access management
      - Flows: Login Flow, Registration Flow, Password Reset Flow
      - Files: src/auth/login.py, src/auth/register.py, src/auth/reset_password.py
   ```

---

## Integration with Other Directives

### Called By:
- `project_file_write` - Assigns themes/flows to new files
- `project_update_db` - Updates mappings when files change
- User directly - Manual theme/flow management

### Calls:
- `project_evolution` - Updates blueprint when themes/flows change
- `project_file_read` - Reads AIFP_METADATA from files

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: ambiguous_mapping
**Issue**: Cannot confidently infer theme or flow
**Resolution**: Prompt user to specify, show existing themes/flows for selection

### Roadblock 2: missing_metadata
**Issue**: File lacks AIFP_METADATA and path is generic
**Resolution**: Assign default "Uncategorized" theme, prompt user to categorize later

### Roadblock 3: blueprint_update_failed
**Issue**: Cannot update ProjectBlueprint.md after theme/flow creation
**Resolution**: Continue with DB update, log warning about blueprint desync

### Roadblock 4: conflicting_themes
**Issue**: File metadata specifies theme that conflicts with path inference
**Resolution**: Trust metadata over path inference, log discrepancy

---

## Intent Keywords

- "map theme"
- "assign flow"
- "categorize file"
- "organize themes"
- "link to flow"

**Confidence Threshold**: 0.5

---

## Related Directives

- `project_file_write` - Creates files that need theme/flow mapping
- `project_evolution` - Updates blueprint when themes/flows change
- `project_file_read` - Reads metadata for inference
- `project_update_db` - Syncs mappings

---

## Inference Patterns

### Path-to-Theme Mapping

| Path Pattern | Inferred Theme | Confidence |
|--------------|----------------|------------|
| `src/auth/` | Authentication | 0.8 |
| `src/database/` | Database Operations | 0.8 |
| `src/api/` | API Layer | 0.7 |
| `src/payment/` | Payment Processing | 0.8 |
| `src/utils/` | Utilities | 0.5 |
| `src/tests/` | Testing | 0.9 |
| `src/core/` | Core System | 0.6 |

### Function-to-Flow Mapping

| Function Keywords | Inferred Flow | Confidence |
|-------------------|---------------|------------|
| login, authenticate | Login Flow | 0.8 |
| register, signup | Registration Flow | 0.8 |
| validate, verify | Validation Flow | 0.7 |
| process, execute | Processing Flow | 0.6 |
| fetch, retrieve | Data Retrieval | 0.7 |
| save, persist | Data Storage | 0.7 |

---

## Blueprint Section 3 Format

When themes/flows are created or updated, Section 3 is formatted as:

```markdown
## 3. Project Themes & Flows

### Themes

1. **Authentication**
   - Purpose: User identity verification and access management
   - Files: src/aifp/auth/
   - Flows: Login Flow, Registration Flow, Password Reset Flow

2. **Database Operations**
   - Purpose: Data persistence and retrieval
   - Files: src/aifp/database/
   - Flows: Query Builder Flow, Migration Flow, Connection Pool Flow

### Flows

1. **Login Flow**
   - Steps: Credential validation → Session creation → Access grant
   - Related Theme: Authentication
   - Files: src/aifp/auth/login.py, src/aifp/auth/session.py

2. **Data Retrieval Flow**
   - Steps: Query construction → Execution → Result parsing
   - Related Theme: Database Operations
   - Files: src/aifp/database/query.py, src/aifp/database/results.py
```

---

## Notes

- **Metadata takes precedence** over path inference
- **Create themes/flows as needed** - Don't restrict to predefined list
- **Trigger evolution on creation** - Keep blueprint in sync
- **Support multiple flows per theme** - One theme can have many flows
- **Enable visualization** - Themes/flows support roadmap and dependency graphs
- **Log all mappings** - Audit trail for theme/flow assignments
- **Confidence scoring** - Use to decide when to prompt user
- **Reuse existing themes/flows** - Avoid duplicates with similar names
