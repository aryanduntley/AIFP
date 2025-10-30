# aifp_run - Gateway Directive

**Type**: Orchestration
**Level**: 0 (Root)
**Parent**: None (entry point)
**Category**: Core System

---

## Purpose

`aifp_run` is the **gateway directive** and primary entry point for all AIFP operations. It acts as a router and reminder system, ensuring AI applies AIFP directives appropriately based on user intent. Every AIFP interaction begins with this directive.

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
    "directive_access": "Call get_all_directives() if needed. Call get_directive(name) for specific details.",
    "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
    "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
    "available_helpers": [
      "get_all_directives",
      "get_directive",
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

2. **What type of task is this?**
   - **Coding** → Apply FP directives
   - **Project Management** → Apply Project directives
   - **User Directives** → Apply User System directives
   - **Git Operations** → Apply Git directives
   - **Discussion** → No directives unless decision made

3. **Do I have directives in memory?**
   - **NO** → Call `get_all_directives()` to load 108 directives
   - **YES** → Use cached directives

4. **Which directives apply?**
   - Match user intent to directive keywords
   - Check confidence threshold (>0.7)
   - Execute matching directives

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
aifp_run recognizes: coding + project management
  ↓
AI applies:
  ├─ FP directives (fp_purity, fp_immutability, fp_no_oop)
  └─ project_file_write (tracks in project.db)
```

**Pattern 3: Project Initialization**
```
User: "Initialize AIFP for my project"
  ↓
aifp_run routes to: project_init
  ├─ Checks get_project_status()
  ├─ Creates .aifp-project/
  ├─ Initializes project.db
  └─ Creates ProjectBlueprint.md
```

---

## Examples

### Example 1: First Interaction

**User**: "Help me build a calculator"

**AI Processing**:
1. Calls `aifp_run("Help me build a calculator")`
2. Receives guidance
3. Evaluates: "Project management action"
4. Checks memory: "No directives loaded"
5. Calls `get_all_directives()` → caches 108 directives
6. Matches intent: `project_init` (confidence: 0.92)
7. Checks `get_project_status()` → Not initialized
8. Executes `project_init` workflow

**Result**: Project initialized with `.aifp-project/` structure

---

### Example 2: Continuation

**User**: "Continue"

**AI Processing**:
1. Calls `aifp_run("Continue")`
2. Receives guidance
3. Matches keyword: "continue" → Call `aifp_status` first
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
1. Calls `aifp_run("Write a function to calculate factorial")`
2. Receives guidance
3. Evaluates: "Coding task + project management"
4. Has directives in memory ✓
5. Applies FP directives:
   - `fp_purity` → Ensures no side effects
   - `fp_immutability` → No mutations
   - `fp_no_oop` → Function-only, no classes
6. Applies `project_file_write`:
   - Writes file
   - Updates project.db (files, functions, interactions)

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

### Case 3: Ambiguous Intent

**Input**: "Do something with the code"

**AI Processing**:
1. Calls `aifp_run("Do something with the code")`
2. Intent matching: Low confidence (<0.7)
3. AI prompts user: "What would you like me to do with the code? (write, refactor, review, test)"

---

### Case 4: Context Lost After Compression

**Situation**: Directives evicted from context

**Behavior**:
1. AI calls `aifp_run`
2. Checks memory: "No directives"
3. Calls `get_all_directives()` to refresh
4. Continues work with reloaded directives

---

## Related Directives

### Primary Relationships

- **`aifp_status`** - Called by `aifp_run` for continuation requests
- **`project_init`** - Routed to for project initialization
- **`project_file_write`** - Routed to for code writing
- **`project_task_decomposition`** - Routed to for task creation
- **`user_directive_parse`** - Routed to for user automation parsing

### Helper Functions Used

- `get_all_directives()` - Load all 108 directives
- `get_directive(name)` - Get specific directive details
- `get_project_status()` - Check if project initialized
- `get_project_context()` - Get full project context

---

## Database Operations

**Read Operations**:
- Queries `aifp_core.db` (via MCP server) for directive definitions
- Checks `project.db` (in user project) via `get_project_status()`
- Reads `config.json` for project-specific configuration

**Database Architecture**:
- **`aifp_core.db`**: Lives in MCP server installation directory, accessed via MCP tools
  - Contains all 122 core AIFP directive definitions
  - Read-only, immutable
  - Never copied to user projects
- **`project.db`**: Lives in user's `.aifp-project/` directory
  - Contains project-specific state (tasks, files, functions)
  - Mutable, updated by directives
- **`user_preferences.db`**: Lives in user's `.aifp-project/` directory
  - Contains user customizations and preferences
  - Mutable
- **`user_directives.db`**: (Optional, Use Case 2 only) Lives in user's `.aifp-project/` directory
  - Contains user-defined automation directives
  - Created on first directive parse

**Write Operations**:
- None directly (routing only)
- Routed directives perform writes

---

## FP Compliance

**Purity**: ✅ Pure function
- No side effects
- Returns guidance only
- All routing logic deterministic

**Immutability**: ✅ Immutable
- No state mutations
- Context passed explicitly
- Guidance structure frozen

**Side Effects**: ✅ Isolated
- Reads from databases (effect)
- Isolated in helper function calls

---

## Error Handling

### Low Confidence Intent

**Trigger**: Intent matching < 0.7

**Response**:
```json
{
  "success": true,
  "confidence": 0.6,
  "matched_directives": ["project_file_write", "project_evolution"],
  "user_prompt": "Unclear intent. Did you mean: (1) Write new file, (2) Update project architecture?"
}
```

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
2. **Status-first for continuation** - Use `aifp_status` for "continue", "resume", "status"
3. **Load directives once** - Cache in memory, refresh only if lost
4. **Trust guidance** - Follow the returned guidance structure
5. **Check confidence** - Only execute directives with confidence >0.7
6. **Fail gracefully** - Prompt user on ambiguity, don't guess

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
