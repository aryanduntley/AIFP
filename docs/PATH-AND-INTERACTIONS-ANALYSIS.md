# Path Resolution & Interactions Analysis

**Date**: 2025-10-28
**Purpose**: Address path resolution concerns and verify directive interactions for 11 newly added directives

---

## 1. MD File Path Resolution Strategy

### Question: Is `"directives/fp_purity.md"` Sufficient?

**Answer**: ✅ **YES** - This is the correct and optimal approach.

### How Path Resolution Works in MCP Server

**JSON Stores Relative Paths**:
```json
{
  "name": "fp_purity",
  "md_file_path": "directives/fp_purity.md"
}
```

**MCP Server Has Base Directory Configuration**:
```python
# In MCP server initialization (Phase 1)
import os
from pathlib import Path

# Get package installation directory
PACKAGE_DIR = Path(__file__).parent  # src/aifp/
REFERENCE_DIR = PACKAGE_DIR / "reference"
DIRECTIVES_DIR = REFERENCE_DIR / "directives"
GUIDES_DIR = REFERENCE_DIR / "guides"

# When loading directive MD file
def load_directive_md(md_file_path: str) -> Result[str, str]:
    """Load directive MD file from package."""
    full_path = DIRECTIVES_DIR / md_file_path.replace("directives/", "")
    # full_path = /path/to/aifp/src/aifp/reference/directives/fp_purity.md

    if not full_path.exists():
        return Failure(f"Directive file not found: {md_file_path}")

    return Success(full_path.read_text())
```

### Why This Approach is Correct

**Benefits**:
1. ✅ **Portable**: Works regardless of where package is installed
2. ✅ **No Search Needed**: Direct path construction, O(1) operation
3. ✅ **Package-Relative**: Paths relative to package structure, not filesystem
4. ✅ **Standard Practice**: How Python packages handle resources (e.g., `importlib.resources`)

**MCP Server Package Structure** (after installation):
```
site-packages/aifp/
├── __init__.py
├── server.py
├── reference/
│   ├── directives/       ← Base directory for MD files
│   │   ├── fp_purity.md
│   │   ├── fp_api_design.md
│   │   └── ... (all 121 files)
│   └── guides/
│       ├── automation-projects.md
│       └── ...
├── helpers/
└── database/
```

**Resolution Example**:
```
JSON: "directives/fp_purity.md"
Base: /usr/local/lib/python3.11/site-packages/aifp/reference/directives/
Full: /usr/local/lib/python3.11/site-packages/aifp/reference/directives/fp_purity.md
```

### No AI Search Required

**AI Never Searches for Paths**:
- MCP server loads MD content from database path
- Returns content to AI as part of directive object
- AI sees: `{ name: "fp_purity", description: "...", content: "..." }`
- Path resolution happens once at server startup or on-demand

**Flow**:
```
AI → "Get fp_purity directive"
  ↓
MCP Server → Query aifp_core.db
  ↓
Database → Returns { name: "fp_purity", md_file_path: "directives/fp_purity.md" }
  ↓
MCP Server → Loads DIRECTIVES_DIR / "fp_purity.md"
  ↓
MCP Server → Returns full directive with content to AI
  ↓
AI → Receives complete directive (no file system access)
```

### Conclusion: ✅ Paths Are Correct

**Status**: No changes needed. Current path format is optimal.

---

## 2. Directive Interactions Review

### Newly Added Directives (11 total)

**FP Auxiliary** (4):
1. fp_test_purity
2. fp_api_design
3. fp_documentation
4. fp_naming_conventions

**Project** (7):
1. project_file_read
2. project_file_delete
3. project_task_create
4. project_task_update ✅ (already has interaction)
5. project_subtask_create
6. project_item_create
7. project_sidequest_create

### Current Interactions Status

**Total Interactions**: 70 entries in `directives-interactions.json`

**Already Present**:
- ✅ `project_task_update` - Has interaction with `git_merge_branch`

**Missing** (10 directives):
- ⚠️ `fp_test_purity`
- ⚠️ `fp_api_design`
- ⚠️ `fp_documentation`
- ⚠️ `fp_naming_conventions`
- ⚠️ `project_file_read`
- ⚠️ `project_file_delete`
- ⚠️ `project_task_create`
- ⚠️ `project_subtask_create`
- ⚠️ `project_item_create`
- ⚠️ `project_sidequest_create`

### Required Interactions Analysis

Let me analyze which of these 10 directives **need** interaction entries:

#### FP Directives (4)

**1. fp_test_purity**
- **Nature**: Code quality / testing enforcement
- **Interactions Needed**: YES
- **Rationale**: Should be triggered by `project_compliance_check` when analyzing tests
```json
{
  "source": "project_compliance_check",
  "target": "fp_test_purity",
  "relation_type": "fp_reference",
  "description": "Compliance check uses fp_test_purity to validate test code purity"
}
```

**2. fp_api_design**
- **Nature**: Code quality / API design
- **Interactions Needed**: YES
- **Rationale**: Should be referenced by `project_compliance_check` and `project_file_write` for public API files
```json
{
  "source": "project_compliance_check",
  "target": "fp_api_design",
  "relation_type": "fp_reference",
  "description": "Compliance check uses fp_api_design for public API validation"
}
```

**3. fp_documentation**
- **Nature**: Code quality / documentation enforcement
- **Interactions Needed**: YES
- **Rationale**: Should be triggered after `project_file_write` to ensure docs
```json
{
  "source": "project_file_write",
  "target": "fp_documentation",
  "relation_type": "fp_reference",
  "description": "File write triggers fp_documentation to ensure proper code documentation"
}
```

**4. fp_naming_conventions**
- **Nature**: Code quality / naming standards
- **Interactions Needed**: YES
- **Rationale**: Core compliance directive, referenced by `project_compliance_check` and `project_file_write`
```json
{
  "source": "project_compliance_check",
  "target": "fp_naming_conventions",
  "relation_type": "fp_reference",
  "description": "Compliance check uses fp_naming_conventions to validate naming standards"
},
{
  "source": "project_file_write",
  "target": "fp_naming_conventions",
  "relation_type": "fp_reference",
  "description": "File write uses fp_naming_conventions to validate function/variable names"
}
```

#### Project Directives (6)

**5. project_file_read**
- **Nature**: Utility / context loading
- **Interactions Needed**: YES
- **Rationale**: Dependency for many directives that need file context
```json
{
  "source": "project_compliance_check",
  "target": "project_file_read",
  "relation_type": "depends_on",
  "description": "Compliance check depends on project_file_read to load file context"
},
{
  "source": "project_file_write",
  "target": "project_file_read",
  "relation_type": "depends_on",
  "description": "File write may depend on project_file_read to check existing code"
}
```

**6. project_file_delete**
- **Nature**: File operation / cleanup
- **Interactions Needed**: YES
- **Rationale**: Should update database after deletion, may trigger dependency checks
```json
{
  "source": "project_file_delete",
  "target": "project_update_db",
  "relation_type": "triggers",
  "description": "File delete triggers DB update to remove file records and orphaned functions"
},
{
  "source": "project_file_delete",
  "target": "project_dependency_sync",
  "relation_type": "triggers",
  "description": "File delete triggers dependency sync to check for broken dependencies"
}
```

**7. project_task_create**
- **Nature**: Atomic task creation
- **Interactions Needed**: YES
- **Rationale**: Core task management, triggered by `project_task_decomposition`
```json
{
  "source": "project_task_decomposition",
  "target": "project_task_create",
  "relation_type": "triggers",
  "description": "Task decomposition triggers project_task_create for individual task creation"
},
{
  "source": "project_task_create",
  "target": "project_update_db",
  "relation_type": "triggers",
  "description": "Task creation triggers DB update to insert task record"
}
```

**8. project_subtask_create**
- **Nature**: Atomic subtask creation
- **Interactions Needed**: YES
- **Rationale**: Triggered by `project_task_decomposition` for task refinement
```json
{
  "source": "project_task_decomposition",
  "target": "project_subtask_create",
  "relation_type": "triggers",
  "description": "Task decomposition triggers project_subtask_create for task refinement"
},
{
  "source": "project_subtask_create",
  "target": "project_task_update",
  "relation_type": "triggers",
  "description": "Subtask creation triggers task update to pause parent task"
}
```

**9. project_item_create**
- **Nature**: Atomic item creation (checklist)
- **Interactions Needed**: YES
- **Rationale**: Triggered by `project_task_decomposition` for granular tracking
```json
{
  "source": "project_task_decomposition",
  "target": "project_item_create",
  "relation_type": "triggers",
  "description": "Task decomposition triggers project_item_create for checklist items"
}
```

**10. project_sidequest_create**
- **Nature**: Exploratory work tracking
- **Interactions Needed**: YES
- **Rationale**: Triggered by user request or task blocker, pauses active task
```json
{
  "source": "project_task_decomposition",
  "target": "project_sidequest_create",
  "relation_type": "triggers",
  "description": "Task decomposition triggers project_sidequest_create for exploratory work"
},
{
  "source": "project_sidequest_create",
  "target": "project_task_update",
  "relation_type": "triggers",
  "description": "Sidequest creation triggers task update to pause related task"
}
```

### Summary: Interactions Required

| Directive | Needs Interactions | Count | Priority |
|-----------|-------------------|-------|----------|
| fp_test_purity | ✅ Yes | 1 | Medium |
| fp_api_design | ✅ Yes | 1 | Medium |
| fp_documentation | ✅ Yes | 1 | Medium |
| fp_naming_conventions | ✅ Yes | 2 | High |
| project_file_read | ✅ Yes | 2 | High |
| project_file_delete | ✅ Yes | 2 | High |
| project_task_create | ✅ Yes | 2 | High |
| project_subtask_create | ✅ Yes | 2 | High |
| project_item_create | ✅ Yes | 1 | Medium |
| project_sidequest_create | ✅ Yes | 2 | Medium |
| **TOTAL** | **10 directives** | **16 new interactions** | |

---

## 3. Recommended Actions

### Priority 1: Add Missing Interactions (HIGH)

**Action**: Add 16 new interaction entries to `directives-interactions.json`

**Impact**:
- Ensures directive system functions correctly
- Enables automatic directive triggering
- Critical for proper workflow execution

**Effort**: 30 minutes (16 entries)

### Priority 2: Update Verification Report (MEDIUM)

**Action**: Add "Post-Verification Updates" section noting fixes applied

**Impact**: Prevents future confusion about resolved issues

**Effort**: 5 minutes

### Priority 3: Update Project Database (MEDIUM)

**Action**: Log today's work in project.db

**Impact**: Maintains development tracking consistency

**Effort**: 5 minutes

---

## 4. Blueprint Review

### docs/blueprints/blueprint_interactions.md

**Status**: Need to review if this blueprint needs updating

**Question**: Does this blueprint document the interaction patterns we're adding?

**Recommendation**: Review blueprint after adding interactions to ensure consistency

---

## 5. Next Steps Summary

**Before Running sync-directives.py**:

1. ✅ **Paths** - No action needed (already correct)
2. ⚠️ **Add 16 interactions** to `directives-interactions.json`
3. ⚠️ **Update VERIFICATION-REPORT.md** with "Fixes Applied" section
4. ⚠️ **Review blueprint_interactions.md** for consistency
5. ⚠️ **Update project.db** with completion notes

**After Completing Above**:
6. ✅ Run `python docs/sync-directives.py` to populate database
7. ✅ Verify 70 + 16 = 86 interactions loaded
8. ✅ Begin Phase 1 implementation

---

**Analysis Complete**: 2025-10-28
**Conclusion**: Paths are correct. Need to add 16 directive interactions before database population.
