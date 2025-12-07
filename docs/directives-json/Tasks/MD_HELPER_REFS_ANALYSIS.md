# Directive Markdown Files - Helper References Analysis

**Date Created**: 2025-12-07
**Purpose**: Document all helper references in directive MD files for careful manual review and cleanup
**Status**: Analysis Complete

---

## Executive Summary

**Files Scanned**: 125 directive markdown files
**Files with Issues**: 94 (75%)
**Total Issues Found**: 105

**Issue Breakdown**:
- Links to `helper-functions-reference.md`: 71 (REMOVE - outdated doc)
- "## Helper Functions" section headers: 23 (REVIEW & UPDATE)
- Hardcoded module paths `src/aifp/helpers/*.py`: 4 (REMOVE - implementation detail)
- Helper call instructions: 4 (VERIFY helpers exist)
- Helper function lists: 3 (REVIEW - may be outdated)

---

## Key Architectural Changes Affecting MD Files

### 1. Helper Registry Complete
- 349+ helpers now documented in `docs/helpers/registry/*.json`
- Organized by database and function type (12 registry files)
- Many consolidations and removals (see `docs/helpers/registry/CONSOLIDATION_REPORT.md`)

### 2. Database-Driven Helper Relationships
- Helper-directive relationships in `directive_helpers` junction table
- Directive JSON files cleaned (no more hardcoded helper refs)
- AI queries database at runtime, NOT docs

### 3. Helper Function Changes
**Consolidated**:
- `create_project_directory`, `initialize_project_db`, `initialize_user_preferences_db` → `initialize_aifp_project()`

**Removed** (AI directive-driven):
- `create_project_blueprint` - AI uses Write tool
- `read_project_blueprint` - AI uses Read tool
- `parse_directive_file` - AI handles via `user_directive_parse` directive
- `validate_user_directive` - AI handles via `user_directive_validate` directive
- `scan_existing_files` - AI uses Glob/Grep/Read tools

**Added**:
- `validate_initialization()` - Post-init validation
- 8 orchestrators for MCP and project operations

### 4. Outdated Reference Document
- `docs/helper-functions-reference.md` - Superseded by helper registry
- All links to this doc should be removed or updated

---

## Recommended Approach for Each Issue Type

### Issue Type 1: Links to helper-functions-reference.md (71 instances)

**Current Pattern**:
```markdown
- [Helper Functions Reference](../../../docs/helper-functions-reference.md#section)
```

**Recommendation**: REMOVE these links entirely

**Replacement** (if section needs helper guidance):
```markdown
## Helper Functions

This directive's helper functions are stored in `aifp_core.db`.

Query at runtime:
\```python
# Get helpers for this directive
get_helpers_for_directive(directive_id, include_helpers_data=true)
\```

See `helper_functions` and `directive_helpers` tables for complete mapping.
```

**Action**: Safe to remove - these are just reference links at end of files

---

### Issue Type 2: Helper Function Section Headers (23 instances)

**Current Pattern**:
```markdown
## Helper Functions

- `get_project_status()` - Check if project initialized
- `init_project_db()` - Initialize project database
```

**Problem**: Hardcoded lists may be outdated after helper consolidations

**Recommendation**: REVIEW EACH - Replace with database query guidance

**Replacement Template**:
```markdown
## Helper Functions

This directive's associated helpers are dynamically mapped in `aifp_core.db`.

**Query at runtime**:
\```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
# Returns: directive_helpers data + full helper_functions data
\```

**Database tables**:
- `helper_functions` - All helper definitions
- `directive_helpers` - Junction table mapping directives to helpers
- `directives` - Directive metadata

**Example query**:
\```sql
SELECT hf.name, hf.purpose, hf.parameters
FROM directive_helpers dh
JOIN helper_functions hf ON dh.helper_function_id = hf.id
JOIN directives d ON dh.directive_id = d.id
WHERE d.name = 'this_directive_name'
ORDER BY dh.sequence_order;
\```
```

**Action**: Need careful review - some may have important context

---

### Issue Type 3: Hardcoded Module Paths (4 instances)

**Example** (from `aifp_help.md`):
```markdown
**Helper Function**:
- **Name**: `get_directive_content`
- **Module**: `src/aifp/helpers/mcp.py`  ← REMOVE THIS LINE
- **Parameters**: `directive_name` (string)
- **Returns**: Full markdown documentation as string
- **Error**: Returns None if MD file not found
```

**Problem**:
1. Exposes implementation details (module paths)
2. May be incorrect after code reorganization
3. Not relevant to AI using the helper (calls via database/MCP)

**Recommendation**: REMOVE module path lines, KEEP other specification details

**Revised**:
```markdown
**Helper Function**:
- **Name**: `get_directive_content`
- **Parameters**: `directive_name` (string)
- **Returns**: Full markdown documentation as string
- **Error**: Returns None if MD file not found
- **Query database for complete specification**
```

**Action**: Manual removal - preserve surrounding context

**Files Affected**:
1. `aifp_help.md` (4 instances)

---

### Issue Type 4: Helper Call Instructions (4 instances)

**Examples**:
```markdown
2. **Find matching directive** - Use `find_directive_by_intent` helper for intelligent matching
```

```markdown
- Call `project_blueprint_read` helper
```

**Recommendation**: VERIFY these helpers still exist with same names

**Action Required**:
1. Check helper registry: Does `find_directive_by_intent` exist?
2. Check helper registry: Does `project_blueprint_read` exist?
3. If renamed/removed, update or remove instruction
4. If exists, keep instruction (it's workflow guidance)

**Files to Review**:
1. `user_preferences_update.md` - `find_directive_by_intent`
2. `project_blueprint_update.md` - `project_blueprint_read`
3. `user_directive_parse.md` - `parse_natural_language_directive`

---

### Issue Type 5: Helper Function Lists (3 instances)

**Example** (from `fp_chaining.md`):
```markdown
- `generate_pipe_function() -> str` - Generate pipe helper code
- `generate_compose_function() -> str` - Generate compose helper code
```

**Recommendation**: VERIFY these exist in helper registry

**Action**:
1. Search helper registry for these function names
2. If don't exist: Remove or mark as "planned"
3. If exist: Keep but note they're queried from database

**Files to Review**:
1. `fp_chaining.md` - `generate_pipe_function`, `generate_compose_function`
2. `project_update_db.md` - Transaction helpers

---

## Files Requiring Broader Review

Based on major changes to helpers and directives, these files likely need comprehensive review:

### High Priority (Helper changes affect these)

1. **`project_init.md`**
   - References: `create_project_blueprint()` (REMOVED - AI directive-driven)
   - References: `get_project_status()` (may be renamed)
   - Helper consolidations affect this directive heavily

2. **`user_directive_parse.md`**
   - References: `parse_directive_file` (REMOVED - AI handles via directive)
   - Entire workflow may need update

3. **`user_directive_validate.md`**
   - References: `validate_user_directive` (REMOVED - AI handles interactively)
   - Validation is now Q&A based, not a helper

4. **`aifp_help.md`**
   - 5 issues found
   - Core system directive - should be accurate
   - Module paths need removal

5. **`user_preferences_update.md`**
   - References `find_directive_by_intent` - verify exists
   - 3 issues found

### Medium Priority

Files with multiple helper reference issues that may need context review:
- `fp_chaining.md` (3 issues)
- `fp_optionals.md` (2 issues)
- `project_update_db.md` (2 issues)

---

## Verification Needed - Do These Helpers Exist?

These specific helper names appear in MD files and should be verified against helper registry:

**From workflow instructions**:
- `find_directive_by_intent`
- `project_blueprint_read`
- `parse_natural_language_directive`
- `get_directive_content`
- `get_project_status`
- `init_project_db`

**From function lists**:
- `generate_pipe_function`
- `generate_compose_function`
- `begin_transaction`
- `commit_transaction`
- `rollback_transaction`
- `query_project_db`

**Action**: Cross-reference with `docs/helpers/registry/*.json` files

---

## Recommended Cleanup Phases

### Phase 1: Safe Removals (Low Risk)
1. Remove all 71 links to `helper-functions-reference.md`
2. Remove 4 hardcoded module paths (preserve surrounding context)
3. Estimate: 1-2 hours

### Phase 2: Helper Name Verification (Medium Risk)
1. Verify all helper names mentioned in workflow instructions
2. Update names if changed, remove if deleted
3. Cross-reference with helper registry
4. Estimate: 2-3 hours

### Phase 3: Section Replacements (Higher Risk)
1. Review 23 "## Helper Functions" sections
2. Decide: Replace with DB guidance OR keep if has unique context
3. Update with database query templates
4. Estimate: 3-4 hours

### Phase 4: Comprehensive Review (Highest Priority)
1. Review 5 high-priority files end-to-end
2. Verify workflows align with current helper architecture
3. Update examples and code snippets
4. Estimate: 4-6 hours

---

## Standard Replacement Templates

### Template 1: Replace Helper Section (Minimal)
```markdown
## Helper Functions

This directive's helpers are stored in `directive_helpers` table.

Query at runtime:
\```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
\```
```

### Template 2: Replace Helper Section (Detailed)
```markdown
## Helper Functions

**Database-Driven**: This directive's helper functions are dynamically queried from `aifp_core.db`.

**Query helpers for this directive**:
\```python
# Get all helpers with full specifications
helpers = get_helpers_for_directive(directive_id, include_helpers_data=true)

# Returns:
# - Helper names, parameters, return types
# - Execution context and sequence order
# - Purpose and error handling
\```

**Database schema**:
- `helper_functions` - Helper definitions (name, purpose, parameters, file_path)
- `directive_helpers` - Many-to-many mapping (directive_id, helper_function_id, sequence_order)
- `directives` - Directive metadata

Query database for current helper list rather than relying on hardcoded documentation.
```

### Template 3: Remove Module Path
```markdown
<!-- BEFORE -->
**Helper Function**:
- **Name**: `function_name`
- **Module**: `src/aifp/helpers/module.py`  ← REMOVE
- **Parameters**: ...

<!-- AFTER -->
**Helper Function**:
- **Name**: `function_name`
- **Parameters**: ...
- **Query database for complete specification**
```

---

## Next Steps

1. ✅ Analysis complete - document generated
2. ⏳ Verify helper names against registry (use grep/search)
3. ⏳ Phase 1: Safe removals (links and module paths)
4. ⏳ Phase 2: Helper name verification
5. ⏳ Phase 3: Section replacements
6. ⏳ Phase 4: Comprehensive review of high-priority files

---

## Related Documentation

- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - Helper changes
- `docs/helpers/registry/CURRENT_STATUS.md` - Helper registry status
- `docs/directives-json/Tasks/DIRECTIVE_CLEANUP_TASK.md` - Overall cleanup task
- `docs/directives-json/Tasks/md_helper_refs_scan_report.json` - Detailed scan results

---

**Last Updated**: 2025-12-07
**Status**: Analysis complete, awaiting manual cleanup execution
