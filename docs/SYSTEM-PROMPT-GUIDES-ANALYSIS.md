# System Prompt Guide References Analysis

**Date**: 2025-10-28
**Issue**: System prompt references guides but mechanism unclear
**Concern**: Will this cause continual file reads? Are paths usable?

---

## Current System Prompt Text

**Lines 327-336** in `sys-prompt/aifp_system_prompt.txt`:

```
=== REFERENCE GUIDES ===

The following guides ship with the AIFP MCP package in src/aifp/reference/guides/ and are available for reference:

1. **automation-projects.md** - Complete guide for custom directive automation (Use Case 2)
2. **project-structure.md** - .aifp-project/ folder structure and ProjectBlueprint.md specification
3. **directive-interactions.md** - How directives, databases, and MCP server interact
4. **git-integration.md** - Multi-user collaboration with FP-powered conflict resolution

Refer to these guides when users ask about automation projects, project structure, directive workflows, or Git collaboration.
```

---

## Analysis: Current State

### What This Actually Does

**Intent**: Inform AI that guides exist for user reference
**Reality**: No mechanism for AI to access guide content

### The Problem

**Issue 1: No Access Mechanism**
- System prompt says guides are "available for reference"
- But no MCP tool exists to read them
- AI cannot actually access the content

**Issue 2: Ambiguous Instruction**
- "Refer to these guides when users ask" - but how?
- Does AI tell user to read the guide?
- Does AI try to read it (can't - no tool)?
- Does AI just know the content (not in prompt)?

**Issue 3: Path Reference Without Base**
- Path: `src/aifp/reference/guides/automation-projects.md`
- No base directory specified
- AI has no file system access anyway
- MCP server would need to provide the content

---

## How AI File Access Actually Works

### AI Cannot Read Files Directly

**Reality Check**:
1. AI receives system prompt (text)
2. AI can only use tools provided by MCP server
3. No direct filesystem access
4. Must use MCP tools for any file operations

### Current MCP Helper Functions (from system prompt)

**MCP Database Helpers** (5):
```
- get_all_directives()
- get_directive(name)
- search_directives(keyword, category, type)
- find_directive_by_intent(user_request, threshold)
- query_mcp_db(sql)
```

**Project Database Helpers** (16):
```
- get_project_context(type)
- get_project_status()
- get_project_files(language)
- ... (13 more)
```

**Git Helpers** (9)
**User Preferences Helpers** (4)
**User Directives Helpers** (10)

**Guide/Reference Helpers**: ❌ NONE

### The Gap

**What's Missing**: No `get_reference_guide(name)` or similar tool

---

## Will This Cause Continual Reads?

### Answer: ❌ NO - Because No Reads Are Possible

**Current Behavior**:
1. AI sees system prompt text
2. AI knows guides "exist" (conceptually)
3. When user asks about guides:
   - AI can describe what the guide covers (from system prompt description)
   - AI **cannot** read actual guide content
   - AI **cannot** provide specific details from guides

**No File Reads Occur Because**:
- No tool exists to read guides
- System prompt is static text (read once at startup)
- AI has no mechanism to trigger file reads

---

## Are Paths Correct?

### Path Analysis

**Given Path**: `src/aifp/reference/guides/automation-projects.md`

**Issues**:
1. ❌ **Relative path with no base directory**
2. ❌ **Not usable by AI** (no tool to resolve it)
3. ✅ **Correct for package structure** (if tool existed)

**If a tool existed**, proper resolution would be:
```python
# In MCP server
PACKAGE_DIR = Path(__file__).parent  # src/aifp/
GUIDES_DIR = PACKAGE_DIR / "reference" / "guides"

def get_reference_guide(guide_name: str) -> Result[str, str]:
    """Read reference guide content."""
    guide_path = GUIDES_DIR / f"{guide_name}.md"

    if not guide_path.exists():
        return Failure(f"Guide not found: {guide_name}")

    return Success(guide_path.read_text())
```

**But this tool doesn't exist in current design.**

---

## Can Paths Be Immediately Ascertained?

### Answer: ⚠️ NOT APPLICABLE - No Access Method

**The Real Question**: How should guides be accessed?

Three options:

### Option A: Embed in System Prompt (Current Implied Approach)

**Pros**:
- ✅ Always available to AI
- ✅ No tool needed
- ✅ No runtime file reads

**Cons**:
- ❌ Increases system prompt tokens significantly
- ❌ 4 guides × ~2000 tokens each = ~8000 tokens
- ❌ Wastes tokens if guides not needed
- ❌ Cannot be updated without changing prompt

**Status**: ❌ Not actually done (guides not embedded)

### Option B: Create MCP Tool to Fetch Guides

**Pros**:
- ✅ On-demand access (efficient)
- ✅ Can update guides without changing prompt
- ✅ Clear mechanism for AI to use

**Cons**:
- ⚠️ Requires implementing new tool
- ⚠️ Adds complexity
- ⚠️ File reads when guides accessed (but only when needed)

**Implementation**:
```python
# New MCP tool
def tool_get_reference_guide(guide_name: str) -> str:
    """
    Get reference guide content.

    Available guides:
    - automation-projects
    - project-structure
    - directive-interactions
    - git-integration
    """
    return get_reference_guide(guide_name).unwrap_or(
        f"Guide '{guide_name}' not found"
    )
```

**Status**: ❌ Not implemented

### Option C: Reference Only (Informational)

**Pros**:
- ✅ Simple
- ✅ No tokens or tools needed
- ✅ AI knows guides exist for user reference

**Cons**:
- ⚠️ AI cannot provide guide details
- ⚠️ Can only tell user "see guide X for info"
- ⚠️ Less helpful for complex questions

**Current Status**: ✅ This is what we have (unintentionally?)

---

## Recommended Solution

### Strategy: Hybrid Approach

**1. Keep Reference Section (Informational)**
```
=== REFERENCE GUIDES ===

The following guides are available in the AIFP documentation:
- automation-projects.md
- project-structure.md
- directive-interactions.md
- git-integration.md

When users ask about these topics, explain that detailed guides are available
in the AIFP MCP server documentation at src/aifp/reference/guides/.
```

**2. Add Key Information to System Prompt**

Instead of full guides, add **essential facts** directly:

```
=== PROJECT STRUCTURE ===

.aifp-project/ structure:
- project.db: Project metadata, tasks, files
- user_preferences.db: User customizations
- user_directives.db: Domain-specific automation (optional)
- ProjectBlueprint.md: Human-readable project overview

ProjectBlueprint.md sections:
1. Overview (purpose, goals, status)
2. Completion Path (milestones, tasks)
3. Infrastructure (languages, packages)
4. Files & Functions (code inventory)
5. Themes & Flows (AI-generated groupings)
```

**3. Optional: Add Tool for Detailed Questions**

Only if users frequently need guide details:
```python
def tool_get_reference_guide(guide_name: str) -> str:
    """Fetch detailed reference guide content."""
    # Implementation as shown in Option B
```

---

## Impact Assessment

### Current Implementation

| Aspect | Status | Impact |
|--------|--------|--------|
| **Continual Reads** | ❌ No | No reads occur (no tool exists) |
| **Path Correctness** | ⚠️ Relative | Correct format, but not usable |
| **Path Ascertainment** | ❌ N/A | No mechanism to resolve paths |
| **AI Functionality** | ⚠️ Limited | AI knows guides exist, can't access |
| **User Experience** | ⚠️ Incomplete | AI can't provide guide details |

### Impact of Current State

**Low Severity Issues**:
- AI can describe guide purpose (from prompt text)
- AI can tell users where guides are
- Works for basic "what's available?" questions

**Medium Severity Gap**:
- AI cannot answer detailed questions from guides
- Cannot provide specific sections or examples
- Must tell user to "read the guide" (less helpful)

**Not Broken, But Incomplete**

---

## Recommendations

### Priority 1: Clarify System Prompt (IMMEDIATE)

**Update Lines 327-336** to be clear about what AI can/cannot do:

```markdown
=== REFERENCE GUIDES ===

Reference guides are included in AIFP documentation at src/aifp/reference/guides/:

1. **automation-projects.md** - User directive automation (Use Case 2)
   - Parsing YAML/JSON/TXT directive files
   - Interactive validation workflow
   - Generating FP-compliant implementation code
   - Real-time execution via background services

2. **project-structure.md** - .aifp-project/ folder structure
   - project.db: Metadata, tasks, files, themes, flows
   - user_preferences.db: Directive customizations
   - ProjectBlueprint.md: Human-readable overview
   - Database schema and helper functions

3. **directive-interactions.md** - Directive system workflows
   - How directives trigger each other
   - Database interaction patterns
   - FP compliance enforcement flow

4. **git-integration.md** - Multi-user collaboration
   - FP-powered conflict resolution
   - Work branch management
   - Purity-based auto-merge

When users ask about these topics, reference the appropriate guide and
explain the key concepts summarized above.
```

**Rationale**:
- AI has key information inline (no tool needed)
- Can answer common questions
- Guides remain available for deep-dive reading
- No file access issues

### Priority 2: Add Essential Content (PHASE 1)

**During Phase 1 implementation**, add condensed guide content to system prompt:
- Key schemas
- Common workflows
- Essential patterns

**Token Budget**: ~2000-3000 tokens for essentials

### Priority 3: Consider Tool (PHASE 2+)

**If users frequently need guide details**, add tool in Phase 2:
- `get_reference_guide(guide_name)` helper
- Returns full guide content on demand
- Listed in available tools section

---

## Conclusion

### Current State: ⚠️ Informational Only

**What Works**:
- ✅ AI knows guides exist
- ✅ Can direct users to them
- ✅ No unwanted file reads

**What Doesn't Work**:
- ❌ AI cannot access guide content
- ❌ Cannot answer detailed guide questions
- ❌ Paths not actually usable

### Fix Priority: MEDIUM

**Not broken, but should clarify**:
1. Update system prompt to summarize key guide info
2. Make clear what AI can/cannot do
3. Consider tool in future phase if needed

### Action Items

- [ ] Update system prompt guide section (Priority 1)
- [ ] Add condensed essential info to prompt (Phase 1)
- [ ] Evaluate need for guide tool (Phase 2 decision)

---

**Analysis Complete**: 2025-10-28
**Conclusion**: No continual reads occur. System prompt should be clarified to either embed key info or add a tool.
