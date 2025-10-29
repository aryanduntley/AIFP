# Reference Guides Workflow Analysis

**Date**: 2025-10-28
**Question**: When are guides needed? Should they be a tool or directives?

---

## Guide Usage Analysis

### 1. automation-projects.md
**Purpose**: Complete guide for custom directive automation (Use Case 2)

**When Needed**:
- User says: "I want to automate my home" / "manage AWS infrastructure" / "create custom directives"
- During: `user_directive_parse` execution
- During: `user_directive_validate` execution
- Frequency: **Occasional** - Only for Use Case 2 projects (~20% of users)

**Workflow Integration Point**:
```
User: "Help me automate my smart home"
  ↓
AI recognizes: Use Case 2 (automation project)
  ↓
AI needs: automation-projects.md to explain workflow
  ↓
AI guides user through: Parse → Validate → Implement → Activate
```

**Is this an action or information?** → **Information** (explains process)

---

### 2. project-structure.md
**Purpose**: .aifp-project/ folder structure and ProjectBlueprint.md specification

**When Needed**:
- User asks: "What's in .aifp-project?" / "Explain project.db" / "What is ProjectBlueprint.md?"
- After: `project_init` (user wants to understand what was created)
- During: Debugging database issues
- Frequency: **Occasional** - Early project setup or troubleshooting

**Workflow Integration Point**:
```
AI executes: project_init
  ↓
User asks: "What did you just create?"
  ↓
AI needs: project-structure.md to explain
  ↓
AI explains: Databases, blueprint file, schema
```

**Is this an action or information?** → **Information** (explains structure)

---

### 3. directive-interactions.md
**Purpose**: How directives, databases, and MCP server interact

**When Needed**:
- User asks: "How does the directive system work?" / "Why did that happen?" / "How do directives interact?"
- During: Advanced usage or debugging
- Frequency: **Rare** - Advanced users or troubleshooting (~5% of interactions)

**Workflow Integration Point**:
```
User: "Why did project_file_write trigger project_update_db?"
  ↓
AI needs: directive-interactions.md to explain
  ↓
AI explains: Interaction types, triggers, workflows
```

**Is this an action or information?** → **Information** (explains system)

---

### 4. git-integration.md
**Purpose**: Multi-user collaboration with FP-powered conflict resolution

**When Needed**:
- User says: "Set up Git collaboration" / "How do I handle conflicts?"
- Before: `git_init` (user wants to understand the system)
- During: `git_detect_conflicts` (user needs conflict resolution guidance)
- Frequency: **Occasional** - Multi-user projects (~30% of users)

**Workflow Integration Point**:
```
User: "How does AIFP handle Git conflicts?"
  ↓
AI needs: git-integration.md to explain FP-powered resolution
  ↓
AI explains: Purity analysis, auto-merge, work branches
```

**Is this an action or information?** → **Information** (explains Git system)

---

## Frequency Summary

| Guide | Frequency | User Type | Workflow Stage |
|-------|-----------|-----------|----------------|
| automation-projects.md | Occasional | Use Case 2 users | Setup phase |
| project-structure.md | Occasional | All users | Early/Debug |
| directive-interactions.md | Rare | Advanced users | Troubleshoot |
| git-integration.md | Occasional | Multi-user teams | Git setup |

**Pattern**: All guides are **on-demand information**, not proactive workflow actions.

---

## Tool vs Directive Analysis

### Option 1: MCP Tool `get_reference_guide(guide_name)`

**Pros**:
- ✅ Simple, clean, direct
- ✅ Standard MCP pattern for information retrieval
- ✅ Minimal overhead (20 lines of code)
- ✅ Clear purpose: "get information"
- ✅ Similar to existing `get_directive()` helper
- ✅ Can be called by AI when user asks questions

**Cons**:
- ⚠️ Not integrated with directive system
- ⚠️ No workflow, roadblocks, or intent matching
- ⚠️ Just a utility, not part of the architecture

**Implementation**:
```python
# src/aifp/helpers/mcp/get_reference_guide.py

from pathlib import Path
from returns.result import Result, Success, Failure

GUIDES_DIR = Path(__file__).parent.parent / "reference" / "guides"

AVAILABLE_GUIDES = {
    "automation-projects": "automation-projects.md",
    "project-structure": "project-structure.md",
    "directive-interactions": "directive-interactions.md",
    "git-integration": "git-integration.md"
}

def get_reference_guide(guide_name: str) -> Result[str, str]:
    """
    Get reference guide content.

    Args:
        guide_name: Guide name (e.g., "automation-projects", "project-structure")

    Returns:
        Success with guide content or Failure with error message
    """
    if guide_name not in AVAILABLE_GUIDES:
        available = ", ".join(AVAILABLE_GUIDES.keys())
        return Failure(f"Guide '{guide_name}' not found. Available: {available}")

    guide_file = AVAILABLE_GUIDES[guide_name]
    guide_path = GUIDES_DIR / guide_file

    if not guide_path.exists():
        return Failure(f"Guide file not found: {guide_path}")

    try:
        content = guide_path.read_text(encoding='utf-8')
        return Success(content)
    except Exception as e:
        return Failure(f"Error reading guide: {str(e)}")

# MCP tool wrapper
def tool_get_reference_guide(guide_name: str) -> str:
    """
    MCP tool: Get reference guide content.

    Available guides:
    - automation-projects: User directive automation guide
    - project-structure: Project folder and database structure
    - directive-interactions: How directives work together
    - git-integration: Multi-user Git collaboration guide
    """
    return get_reference_guide(guide_name).unwrap_or(
        f"Error: Could not load guide '{guide_name}'"
    )
```

**System Prompt Update**:
```markdown
=== HELPER FUNCTIONS (45 TOTAL) ===

MCP Database (aifp_core.db - read-only):
- get_all_directives(): Get all 121 directives
- get_directive(name): Get specific directive
- get_reference_guide(guide_name): Get reference documentation
  Available guides: automation-projects, project-structure,
  directive-interactions, git-integration
- search_directives(keyword, category, type): Filter search
...
```

**Token Cost**: ~50 tokens added to system prompt

---

### Option 2: Create Reference Directives

**Pros**:
- ✅ Fits AIFP architecture (everything is a directive)
- ✅ Can have workflows, intent matching, roadblocks
- ✅ Integrated with directive system
- ✅ Can trigger other directives if needed
- ✅ Searchable via `find_directive_by_intent()`

**Cons**:
- ❌ Overkill for simple information retrieval
- ❌ Adds 4 directive entries to database (noise)
- ❌ Requires JSON definitions, workflows, interactions
- ❌ More complex than needed
- ❌ Directives are for "actions", these are "information"

**Implementation**:
Would need 4 new directives in `directives-user-system.json` or new category:

```json
{
  "name": "reference_automation_projects",
  "type": "reference",
  "description": "Provide comprehensive guide for user directive automation",
  "md_file_path": "guides/automation-projects.md",
  "workflow": {
    "trunk": "load_guide_content",
    "branches": [
      {
        "if": "guide_found",
        "then": "return_content"
      },
      {
        "fallback": "return_error"
      }
    ]
  },
  "intent_keywords_json": [
    "automation guide",
    "custom directives",
    "how to automate",
    "user directives guide"
  ],
  "confidence_threshold": 0.7
}
```

**Repeat for all 4 guides** → 4 new directive entries + interactions

**Token Cost**: ~200 tokens (4 new directives in system prompt list)

---

## Comparison

| Aspect | MCP Tool | Directives |
|--------|----------|------------|
| **Complexity** | Low | High |
| **Lines of Code** | ~30 | ~200 (JSON + interactions) |
| **Tokens** | +50 | +200 |
| **Purpose Fit** | ✅ Information retrieval | ⚠️ Information as action |
| **Architecture** | Standard helper | Fits AIFP model |
| **Searchability** | By name only | By intent matching |
| **Maintenance** | Simple | Complex |
| **Overkill?** | No | Yes |

---

## Recommendation: MCP Tool (Option 1)

### Rationale

**1. Guides Are Information, Not Actions**
- Directives are for **actions**: write file, create task, check compliance
- Guides are **reference material**: explain how things work
- Using directives for docs is architectural mismatch

**2. Simplicity Wins**
- 30 lines of code vs 200
- Standard MCP pattern (like existing helpers)
- Easy to maintain and test

**3. Efficient Token Usage**
- Tool approach: +50 tokens
- Directive approach: +200 tokens
- User wants minimal system prompt

**4. Clear Purpose**
- `get_reference_guide("automation-projects")` → obvious
- `reference_automation_projects` directive → confusing purpose

**5. Precedent in Helper Functions**
- `get_directive()` exists (information retrieval)
- `get_project_context()` exists (information retrieval)
- `get_reference_guide()` follows same pattern

### When AI Uses It

**Workflow**:
```
User: "How do I set up home automation with AIFP?"
  ↓
AI recognizes: Needs automation-projects guide
  ↓
AI calls: get_reference_guide("automation-projects")
  ↓
AI receives: Full guide content
  ↓
AI summarizes: Key steps for user
```

**Frequency**: On-demand when user asks guide-related questions

**No Continual Reads**: Content loaded only when user asks, then cached in context

---

## Implementation Plan

### Phase 1: Add Tool

**File**: `src/aifp/helpers/mcp/get_reference_guide.py`

**Steps**:
1. Create helper function (30 lines)
2. Add to MCP tool list
3. Update system prompt (+50 tokens)
4. Test with all 4 guides

**Effort**: 30 minutes

**System Prompt Addition** (replace lines 327-336):
```markdown
=== REFERENCE GUIDES ===

Use get_reference_guide(guide_name) to fetch guide content when users ask about:
- "automation-projects": User directive automation workflow
- "project-structure": .aifp-project/ folder and database structure
- "directive-interactions": How directives work together
- "git-integration": Multi-user Git collaboration

Call this tool when users need detailed explanations about these topics.
```

---

## Alternative: Hybrid Approach

**If we want best of both worlds**:

### Keep guides as information tools
### Add "explain" directives for common workflows

Example:
```json
{
  "name": "project_explain_structure",
  "type": "project",
  "description": "Explain project structure and databases to user",
  "workflow": {
    "trunk": "check_project_initialized",
    "branches": [
      {
        "if": "project_exists",
        "then": "load_structure_guide"
      },
      {
        "if": "explain_requested",
        "then": "return_explanation"
      }
    ]
  }
}
```

**But**: This adds complexity without clear benefit. User can just ask "explain X" and AI uses the tool.

---

## Conclusion

### Recommended: Simple MCP Tool

**Reasons**:
1. ✅ Guides are information, not actions
2. ✅ Simple, maintainable, clear purpose
3. ✅ Minimal tokens (+50 vs +200)
4. ✅ Standard MCP helper pattern
5. ✅ On-demand access (no continual reads)

**Implementation**: Add `get_reference_guide()` helper in Phase 1

**Alternative Rejected**: Directives approach is architectural mismatch and adds unnecessary complexity

---

**Analysis Complete**: 2025-10-28
**Recommendation**: Implement simple MCP tool for guide access
