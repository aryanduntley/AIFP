# aifp_run - Gateway Directive

**Type**: Orchestration
**Level**: 0 (Root)
**Parent**: None (entry point)
**Category**: Core System

---

## Purpose

`aifp_run` is the **gateway directive** and primary entry point for all AIFP operations. It acts as a reminder system that returns guidance to AI on every interaction, ensuring AI stays aligned with AIFP directives. AI receives the guidance and makes its own decisions about which directives to apply. Every AIFP interaction begins with this directive.

---

## When to Use

**Automatic Execution** (Default):
- AI automatically calls `aifp_run` before every response when AIFP MCP server is installed
- User does NOT need to type "aifp run" explicitly
- Only skip if user explicitly says "do not use aifp"

**Manual Invocation**:
```bash
aifp run "Initialize project for calculator"
aifp run "Write multiply function"
aifp run "Check project status"
```

---

## Workflow

### Trunk: `evaluate_and_route`

**Step 1: Return Guidance**

`aifp_run` does NOT execute tasks directly. It returns guidance to AI:

```json
{
  "success": true,
  "message": "AIFP MCP available",
  "guidance": {
    "directive_access": "Directive names cached from is_new_session bundle. Call get_directive(name) for specific details.",
    "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
    "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
    "available_helpers": [
      "get_directive",
      "search_directives",
      "get_project_context",
      "get_project_status"
    ]
  }
}
```

**Step 2: AI Decision Flow**

After receiving guidance, AI evaluates:

1. **Is this a continuation request?**
   - Keywords: "continue", "status", "resume", "where were we", "what's next"
   - **YES** → Call `aifp_status` first for context
   - **NO** → Proceed to step 2

2. **Check project type (Use Case 1 vs Use Case 2)**
   - Query: `SELECT user_directives_status FROM project WHERE id = 1`
   - **NULL** → Use Case 1 (regular software development)
   - **'in_progress', 'active', 'disabled'** → Use Case 2 (automation project)

3. **What type of task is this?**
   - **Coding** → Write FP-compliant code (consult FP directives only if uncertain)
   - **Project Management** → Execute Project directives
   - **User Directives** (Use Case 2) → Execute User System directives
   - **Git Operations** → Execute Git directives
   - **Discussion** → No directives unless decision made

4. **Do I have directive names?**
   - **NO** → Already provided in is_new_session bundle (directive names only)
   - **YES** → Use cached directive names
   - **Need details?** → Query specific directive by name

5. **Which directives to execute?**
   - AI evaluates user request and project context
   - AI decides which project/user/git directives to execute
   - For coding: Write FP code naturally, query FP directives only if uncertain about implementation

---

## Interactions with Other Directives

### Hierarchical Routing

```
aifp_run (Level 0)
  ├─ Routes to aifp_status (Level 1)           [Continuation requests]
  ├─ Routes to project_init (Level 1)          [Initialization]
  ├─ Routes to project_file_write (Level 2)    [Code writing]
  ├─ Routes to project_task_decomposition (L1) [Task creation]
  ├─ Routes to fp_purity, fp_immutability      [FP compliance]
  └─ Routes to user_directive_parse (Level 2)  [User automations]
```

### Common Routing Patterns

**Pattern 1: Continuation Request**
```
User: "Continue"
  ↓
aifp_run → aifp_status
  ├─ Calls get_project_context()
  ├─ Queries project.db for open tasks
  ├─ Reads ProjectBlueprint.md
  └─ Returns status report with recommendations
```

**Pattern 2: Coding Task**
```
User: "Write multiply function"
  ↓
aifp_run returns: guidance
  ↓
AI evaluates: coding + project management
  ↓
AI writes FP-compliant code naturally (pure, immutable, no OOP)
  ↓
AI executes: project_file_write
  └─ Writes file + calls helpers to update project.db
```

**Pattern 3: Project Initialization**
```
User: "Initialize AIFP for my project"
  ↓
aifp_run routes to: project_init
  ├─ Checks get_project_status()
  ├─ Creates .aifp-project/
  ├─ Initializes project.db
  ├─ Sets user_directives_status (NULL for Use Case 1, 'in_progress' for Use Case 2)
  └─ Creates ProjectBlueprint.md
```

**Pattern 4: User Directive Automation (Use Case 2)**
```
User: "Parse my directive file at /path/to/directives.yaml"
  ↓
aifp_run checks: project.user_directives_status
  ├─ If NULL → Set to 'in_progress' (first directive)
  └─ Routes to: user_directive_parse
      ↓
  user_directive_parse → validate → implement → approve → activate
  ↓
  When activated: project.user_directives_status = 'active'
```

---

## Examples

### Example 1: First Interaction

**User**: "Help me build a calculator"

**AI Processing**:
1. Calls `aifp_run(is_new_session=True)` → Receives bundled startup data
   - Status: No project initialized
   - Settings: Default preferences
   - FP directive index: Names grouped by category
   - Guidance: Common starting point is `project_init`
2. Evaluates user request: "Project initialization needed"
3. Decides to execute `project_init` workflow
4. Executes `project_init` directive

**Result**: Project initialized with `.aifp-project/` structure

---

### Example 2: Continuation

**User**: "Continue"

**AI Processing**:
1. Calls `aifp_run()` → Receives lightweight guidance
2. Evaluates user request: "continue" = continuation request
3. Follows guidance: Call `aifp_status` first for context
4. `aifp_status` returns:
   - Current focus: "Implementing matrix operations"
   - Open tasks: "Multiply matrix function incomplete"
   - Last work: "Created add_matrices() in src/matrix.py"
5. AI resumes work on multiply_matrices()

**Result**: Contextual continuation with historical awareness

---

### Example 3: Coding Task

**User**: "Write a function to calculate factorial"

**AI Processing**:
1. Calls `aifp_run()` → Receives lightweight guidance
2. Evaluates user request: "Coding task + project management"
3. Writes FP-compliant factorial function:
   - Pure function (no side effects)
   - Immutable data (no mutations)
   - No OOP (function only, no classes)
4. Executes `project_file_write` directive:
   - Writes file to disk
   - Calls helpers to update project.db (files, functions, interactions)

**Result**: FP-compliant function written and tracked

---

## Edge Cases

### Case 1: User Explicitly Disables AIFP

**Input**: "Do not use aifp for this task"

**Behavior**:
- AI skips `aifp_run` call
- No directives applied
- Normal conversation mode

---

### Case 2: MCP Server Not Available

**Behavior**:
- AI attempts `aifp_run` call
- Call fails (MCP not installed)
- AI informs user: "AIFP MCP server not available. Install with: pip install aifp-mcp-server"

---

### Case 3: Ambiguous Request

**Input**: "Do something with the code"

**AI Processing**:
1. Calls `aifp_run()` → Receives guidance
2. Evaluates user request: Ambiguous, unclear action
3. AI prompts user: "What would you like me to do with the code? (write, refactor, review, test)"

---

### Case 4: Context Lost After Compression

**Situation**: Directive names evicted from context

**Behavior**:
1. AI calls `aifp_run(is_new_session=True)`
2. Receives fresh bundle with directive names
3. Continues work with refreshed context

---

## Related Directives

### Primary Relationships

- **`aifp_status`** - Called by `aifp_run` for continuation requests
- **`project_init`** - Routed to for project initialization
- **`project_file_write`** - Routed to for code writing
- **`project_task_decomposition`** - Routed to for task creation
- **`user_directive_parse`** - Routed to for user automation parsing

### Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Read Operations**:
- Queries `aifp_core.db` (via MCP server) for directive names and definitions
- Checks `project.db` (in user project) via helpers
- Reads `config.json` for project-specific configuration

**Database Architecture**:
- **`aifp_core.db`**: Lives in MCP server installation directory, accessed via MCP tools
  - Contains all 122 core AIFP directive definitions
  - Read-only, immutable
  - Never copied to user projects
  - Queried via helpers for directive names/details
- **`project.db`**: Lives in user's `.aifp-project/` directory
  - Contains project-specific state (tasks, files, functions)
  - Mutable, updated via helper functions during directive execution
- **`user_preferences.db`**: Lives in user's `.aifp-project/` directory
  - Contains user customizations and preferences
  - Mutable, updated via helper functions
- **`user_directives.db`**: (Optional, Use Case 2 only) Lives in user's `.aifp-project/` directory
  - Contains user-defined automation directives
  - Created on first directive parse

**Write Operations**:
- None directly (routing only)
- Routed directives perform writes

---

## FP Compliance

**Note**: This section describes the aifp_run helper function implementation, NOT how AI should code. AI writes FP-compliant code naturally without consulting directives for every line.

**Purity**: ✅ Pure function
- Returns guidance structure only
- No side effects in function logic
- Deterministic output given same inputs

**Immutability**: ✅ Immutable
- No state mutations within function
- Returns frozen data structures
- Context passed explicitly

**Side Effects**: ✅ Isolated
- Database reads isolated in helper calls
- File system reads isolated in helper calls
- All effects occur in dedicated helper functions

---

## Error Handling

### Ambiguous User Request

**Trigger**: User request is unclear or ambiguous

**AI Behavior**:
- AI receives standard guidance from aifp_run
- AI cannot determine appropriate action
- AI asks user for clarification
- No special error response from aifp_run itself

### MCP Server Unavailable

**Trigger**: MCP tool call fails

**Response**:
```json
{
  "success": false,
  "error": "MCP server not available",
  "installation_hint": "pip install aifp-mcp-server"
}
```

---

## Best Practices

1. **Always call first** - Every AIFP interaction starts with `aifp_run`
2. **Use is_new_session wisely** - `true` for first interaction, `false` for continuation
3. **Status-first for continuation** - Call `aifp_status` for "continue", "resume", "status"
4. **Directive names cached** - Provided in is_new_session bundle, query details when needed
5. **Trust guidance** - Follow the returned guidance structure
6. **AI decides** - Guidance informs, AI makes final decision on which directives to execute
7. **FP is baseline** - Write FP code naturally, consult FP directives only when uncertain
8. **Ask on ambiguity** - Prompt user for clarification when request is unclear

---

## Version History

- **v1.0** (2025-10-22): Initial gateway directive with routing logic
- **v1.1** (2025-10-23): Added `aifp_status` integration for continuation
- **v1.2** (2025-10-26): Added two use case support (regular dev vs automation)

---

## Notes

- This directive is **NOT an executor** - it's a gateway and reminder
- Actual work happens in routed directives
- AI maintains responsibility for directive selection
- `aifp_run` ensures AI never forgets to apply AIFP standards
