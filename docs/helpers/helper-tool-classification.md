# Helper Function Tool Classification

**Purpose**: Defines which helpers are exposed as MCP tools (`is_tool: true`) vs internal helpers (`is_tool: false`)

**Last Updated**: 2025-11-05

---

## Classification Strategy

### is_tool: true (MCP-Exposed Tools)
**Criteria**:
- Generic orchestrator functions (Layer 2)
- Primary interfaces AI calls directly
- High-level operations with significant value
- Commonly used entry points

**Typical Count**: ~20-30% of total helpers

### is_tool: false (Internal Helpers)
**Criteria**:
- Specific CRUD operations
- Called primarily by generic tools or directives
- Internal utilities and sub-helpers
- Low-level operations

**Typical Count**: ~70-80% of total helpers

---

## Project Database (project.db)

**Total Helpers**: 79
**is_tool=true**: 15
**is_tool=false**: 64

### is_tool: TRUE (15)

#### Generic Tools (5)
1. `get_current_progress()` - Status query orchestrator
2. `update_project_state()` - Update orchestrator
3. `batch_update_progress()` - Batch update orchestrator
4. `query_project_state()` - Query orchestrator
5. `get_work_context()` - Resume context (critical)

#### Primary Interfaces (10)
6. `get_project_metadata()` - Project overview
7. `get_completion_path()` - Roadmap status
8. `get_task_by_id()` - Task lookup
9. `get_tasks_by_status()` - Task filtering
10. `create_task()` - Task creation
11. `update_task_status()` - Task updates
12. `link_task_to_flows()` - Flow linking
13. `get_all_flows()` - Flow listing
14. `get_project_summary()` - Summary stats
15. `get_project_metrics()` - Analytics

### is_tool: FALSE (64)

**All other helpers including**:
- Specific getters: `get_project_name()`, `get_project_version()`, etc.
- Sub-helpers: `validate_flow_ids()`, `infer_action()`, `check_blueprint_sync()`
- Secondary operations: `add_flow_to_task()`, `remove_flow_from_task()`
- Detailed queries: `get_functions_by_file()`, `get_files_in_theme()`
- Internal utilities: All helpers in `internal/` directory

---

## MCP Database (aifp_core.db)

**Total Helpers**: 55
**is_tool=true**: 12
**is_tool=false**: 43

### is_tool: TRUE (12)

#### Generic Tools (4)
1. `find_directives()` - Directive discovery
2. `find_helpers()` - Helper discovery
3. `get_system_context()` - System state
4. `query_mcp_relationships()` - Relationship queries

#### Primary Interfaces (8)
5. `get_all_directives()` - Directive listing
6. `get_directive()` - Directive lookup
7. `search_directives()` - Directive search
8. `find_directive_by_intent()` - Intent matching
9. `get_directive_interactions()` - Relationships
10. `get_directive_md_content()` - Full documentation
11. `get_all_helpers()` - Helper listing
12. `query_mcp_db()` - Direct queries

### is_tool: FALSE (43)

**All other helpers including**:
- Internal lookups: Helper relationship traversal
- Specific queries: Category filters, type filters
- Validation helpers
- Cache management
- Schema utilities

---

## User Preferences Database (user_preferences.db)

**Total Helpers**: 39
**is_tool=true**: 8
**is_tool=false**: 31

### is_tool: TRUE (8)

1. `get_all_preferences()` - List all preferences
2. `get_preference()` - Get single preference
3. `set_preference()` - Update preference
4. `get_active_preferences()` - Active prefs only
5. `get_directive_preferences()` - Directive-specific prefs
6. `set_directive_preference()` - Update directive pref
7. `export_preferences()` - Backup
8. `import_preferences()` - Restore

### is_tool: FALSE (31)

**All other helpers including**:
- Specific getters by category
- Validation helpers
- Default value management
- Internal preference logic
- Preference history tracking

---

## User Directives Database (user_directives.db)

**Total Helpers**: 32
**is_tool=true**: 7
**is_tool=false**: 25

### is_tool: TRUE (7)

1. `get_all_user_directives()` - List user directives
2. `get_user_directive()` - Get single directive
3. `create_user_directive()` - Create new
4. `update_user_directive_status()` - Status updates
5. `get_user_directive_implementations()` - Implementation status
6. `sync_user_directive()` - Sync with source files
7. `test_user_directive()` - Test execution

### is_tool: FALSE (25)

**All other helpers including**:
- Parsing helpers
- Validation helpers
- Implementation detail tracking
- Internal sync logic
- History tracking

---

## Summary Across All Databases

| Database | Total Helpers | is_tool=true | is_tool=false | % Tools |
|----------|---------------|--------------|---------------|---------|
| **project.db** | 79 | 15 | 64 | 19% |
| **aifp_core.db** | 55 | 12 | 43 | 22% |
| **user_preferences.db** | 39 | 8 | 31 | 21% |
| **user_directives.db** | 32 | 7 | 25 | 22% |
| **TOTAL** | **205** | **42** | **163** | **20%** |

**Key Insight**: ~20% of helpers are MCP-exposed tools, ~80% are internal helpers

---

## Decision Guidelines

### When is_tool should be TRUE:
- ✅ Generic orchestrator (Layer 2)
- ✅ Primary entry point for common operations
- ✅ AI calls directly for status/updates
- ✅ High-level abstraction with clear value
- ✅ Reduces multiple calls to single call

### When is_tool should be FALSE:
- ✅ Specific CRUD operation
- ✅ Called primarily by other helpers
- ✅ Internal utility or sub-helper
- ✅ Low-level operation
- ✅ Validation or formatting helper
- ✅ Granular detail retrieval

---

## Implementation Notes

### helpers_parsed.json Structure
```json
{
  "name": "get_current_progress",
  "is_tool": true,
  "is_sub_helper": false,
  ...
}
```

```json
{
  "name": "validate_flow_ids",
  "is_tool": false,
  "is_sub_helper": true,
  ...
}
```

### MCP Server Registration
Only helpers with `is_tool: true` are registered as MCP tools. Internal helpers are available to Python code but not exposed via MCP.

---

## Future Considerations

### Promoting Internal Helpers to Tools
If usage patterns show AI frequently needs direct access to an internal helper:
1. Evaluate if it should be promoted to `is_tool: true`
2. Update classification
3. Re-register with MCP server
4. Update documentation

### Creating New Generic Tools
When patterns emerge of AI repeatedly calling multiple helpers:
1. Create new generic tool that orchestrates them
2. Mark as `is_tool: true`
3. Document in generic-tools-{database}.md
4. Update classification

---

**End of Classification Guide**
