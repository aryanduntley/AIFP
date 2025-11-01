# Helper-Directive Integration Plan

**Problem**: 41 out of 50 helper functions are not referenced in directive workflows, so the AI won't know to call them.

**Solution**: Wire helpers into directive workflows systematically.

---

## Integration Required

### 1. Git Directives (ALL 10 helpers missing)

| Directive | Missing Helpers | Priority |
|-----------|----------------|----------|
| `git_init` | `get_current_commit_hash`, `sync_git_state` | HIGH |
| `git_sync_state` | `sync_git_state`, `get_current_branch`, `get_current_commit_hash`, `get_git_status` | HIGH |
| `git_detect_external_changes` | `detect_external_changes` | HIGH |
| `git_create_branch` | `create_user_branch`, `get_user_name_for_branch`, `get_current_branch` | HIGH |
| `git_detect_conflicts` | `detect_conflicts_before_merge` | HIGH |
| `git_merge_branch` | `merge_with_fp_intelligence`, `detect_conflicts_before_merge` | HIGH |
| `aifp_status` | `get_git_status`, `sync_git_state`, `list_active_branches` | MEDIUM |

---

### 2. User Directive System (ALL 10 helpers missing)

| Directive | Missing Helpers | Priority |
|-----------|----------------|----------|
| `user_directive_parse` | `parse_directive_file` | HIGH |
| `user_directive_validate` | `validate_user_directive` | HIGH |
| `user_directive_implement` | `generate_implementation_code`, `detect_dependencies`, `install_dependency` | HIGH |
| `user_directive_activate` | `activate_directive` | HIGH |
| `user_directive_monitor` | `monitor_directive_execution` | HIGH |
| `user_directive_status` | `get_user_directive_status` | HIGH |
| `user_directive_update` | `update_directive` | HIGH |
| `user_directive_deactivate` | `deactivate_directive` | HIGH |
| `aifp_status` | `get_user_directive_status` | MEDIUM |

---

### 3. User Preferences (ALL 4 helpers missing)

| Directive | Missing Helpers | Priority |
|-----------|----------------|----------|
| `user_preferences_set` | `set_directive_preference` | MEDIUM |
| `user_preferences_get` | `get_directive_preference` | MEDIUM |
| `tracking_toggle` | `toggle_tracking_feature`, `get_tracking_settings` | MEDIUM |
| All directives | `get_directive_preference` (for user overrides) | LOW |

---

### 4. Project Directives (12 helpers missing)

| Directive | Missing Helpers | Priority |
|-----------|----------------|----------|
| `aifp_status` | `get_status_tree`, `get_project_context`, `detect_and_init_project` | HIGH |
| `project_init` | `scan_existing_files`, `infer_architecture` | MEDIUM |
| `project_evolution` | `read_project_blueprint`, `update_project_blueprint_section` | MEDIUM |
| `project_blueprint_update` | `update_project_blueprint_section` | MEDIUM |
| `project_file_read` | (may need `get_project_files`) | LOW |
| `project_compliance_check` | `get_project_functions` (FP checking) | LOW |
| Task directives | (Already have `get_project_tasks`) | N/A |

---

### 5. MCP Helpers (6 out of 7 missing)

| Directive | Missing Helpers | Priority |
|-----------|----------------|----------|
| `aifp_run` | `get_all_directives`, `search_directives` | HIGH |
| `aifp_status` | `get_directive_interactions` (show workflow) | MEDIUM |
| (Future) `aifp_help` | `get_directive_content` (load MD docs) | LOW |
| Advanced usage | `query_mcp_db`, `query_project_db` | LOW |

---

## Implementation Strategy

### Phase 1: Critical Helpers (HIGH Priority)
Wire helpers that make directives actually functional:
1. **Git directives** - Without these, git operations can't work
2. **User Directive system** - Each directive needs its corresponding helper
3. **`aifp_status`** - Needs `get_status_tree`, `get_project_context`

### Phase 2: Enhancement Helpers (MEDIUM Priority)
Add helpers that improve functionality:
1. **User preferences** - Enable customization
2. **Project scanning** - Better initialization
3. **Blueprint management** - Evolution support

### Phase 3: Advanced Helpers (LOW Priority)
Add helpers for specialized use cases:
1. **FP compliance checking** - `get_project_functions`
2. **Advanced queries** - `query_mcp_db`, `query_project_db`
3. **Help system** - `get_directive_content`

---

## How to Wire Helpers into Directives

### Pattern 1: Explicit Helper Call

```json
{
  "if": "condition_met",
  "then": "action_description",
  "details": {
    "helper": "helper_function_name",
    "parameters": {
      "param1": "value1"
    }
  }
}
```

### Pattern 2: Multiple Helpers in Sequence

```json
{
  "if": "step_1_complete",
  "then": "step_2_action",
  "details": {
    "helper_1": "first_helper",
    "helper_2": "second_helper",
    "sequence": ["helper_1", "helper_2"]
  }
}
```

### Pattern 3: Sub-Helpers (Called by Other Helpers)

Some helpers call other helpers internally - these don't need directive references:
- `get_git_status` calls `get_current_branch`, `get_current_commit_hash`, `detect_external_changes`
- `merge_with_fp_intelligence` calls `detect_conflicts_before_merge`

**Rule**: Only add helper to directive if AI should call it directly, not if it's only called by other helpers.

---

## Next Steps

1. Review this plan
2. Decide: Update directives now OR wait until Phase 1 MCP implementation?
3. If updating now: Start with Git directives (most critical)
4. Create validation: Ensure every defined helper is either:
   - Referenced in a directive, OR
   - Marked as "sub-helper" (called by other helpers)

---

## Open Questions

1. Should `query_mcp_db` and `query_project_db` be exposed as fallback/advanced tools?
2. Do we need an `aifp_help` directive that uses `get_directive_content`?
3. Should preference helpers be automatically checked before every directive execution?
4. Are there any helpers that should be deprecated/removed?
