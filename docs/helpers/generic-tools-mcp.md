# Generic Tools: MCP (aifp_core.db)

**Database**: aifp_core.db
**Purpose**: High-level orchestrator functions for directive and helper management
**Layer**: Layer 2 (MCP-Exposed Generic Tools)
**Total Tools**: 4 generic orchestrators

---

## Overview

These generic tools provide **single-call interfaces** for MCP operations - directive discovery, helper lookup, and system queries. They orchestrate multiple specific helpers (Layer 3) to provide intuitive high-level operations for AI and core system functions.

**All functions in this file have `is_tool: true`** (MCP-exposed)

---

## 1. find_directives()

**Purpose**: Intelligent directive discovery and matching. Single entry point for all directive lookup operations - by intent, keyword, category, or complex criteria.

**Signature**:
```python
def find_directives(
    query: str = None,        # Natural language query or keyword
    filters: dict = {},       # Structured filters
    match_mode: str = "intent",  # "intent", "keyword", "category", "exact"
    include_related: bool = False,  # Include related directives
    limit: int = 10           # Max results
) -> dict
```

**Parameters**:

### query (str)
Natural language user request or keyword:
- `"I want to create a new task"` (intent matching)
- `"resume work"` (keyword matching)
- `"matrix multiplication"` (content search)
- `"project_task_create"` (exact name)

### filters (dict)
Structured filtering:
```python
filters = {
    "type": "project",               # Directive type (fp, project, user, git)
    "category": "task_management",   # Category name
    "level": 3,                      # Execution level (1-4)
    "priority": "HIGH",              # Priority level
    "confidence_threshold": 0.7      # Min confidence for intent matching
}
```

### match_mode (str)
How to interpret query:
- `"intent"` (default) - Use AI intent matching with confidence scores
- `"keyword"` - Match against intent_keywords_json field
- `"category"` - Filter by category name
- `"exact"` - Exact name match
- `"fuzzy"` - Fuzzy name matching (typo tolerance)

### include_related (bool)
If true, includes related directives (depends_on, triggers, escalates_to)

### limit (int)
Maximum number of results to return

**Returns**:

### Intent Match Response
```json
{
  "query": "I want to create a task for implementing matrix operations",
  "match_mode": "intent",
  "matches": [
    {
      "directive": {
        "name": "project_task_create",
        "type": "project",
        "level": 3,
        "category": "task_management",
        "description": "Atomic task constructor for creating new independent tasks...",
        "priority": "HIGH"
      },
      "confidence": 0.95,
      "match_reasons": [
        "Intent keyword: 'create task'",
        "Category match: task_management",
        "Description relevance: high"
      ],
      "related_directives": {
        "depends_on": ["project_task_decomposition"],
        "triggers": ["project_item_create"],
        "alternatives": ["project_subtask_create"]
      }
    },
    {
      "directive": {
        "name": "project_task_decomposition",
        "type": "project",
        "level": 2,
        "category": "task_management",
        "description": "Breaks down user goals into tasks and subtasks...",
        "priority": "HIGH"
      },
      "confidence": 0.72,
      "match_reasons": [
        "Parent directive of top match",
        "Related to task creation workflow"
      ]
    }
  ],
  "total_matches": 2,
  "top_match": {
    "name": "project_task_create",
    "confidence": 0.95,
    "suggested_action": "Create task with milestone assignment"
  }
}
```

### Keyword Match Response
```json
{
  "query": "resume",
  "match_mode": "keyword",
  "matches": [
    {
      "directive": {
        "name": "project_auto_resume",
        "type": "project",
        "level": 3,
        "category": "recovery_automation",
        "description": "Detects unfinished tasks and resumes execution..."
      },
      "confidence": 1.0,
      "match_reasons": [
        "Intent keyword exact match: 'resume'"
      ]
    }
  ],
  "total_matches": 1
}
```

### Category Filter Response
```json
{
  "query": null,
  "match_mode": "category",
  "filters": {"category": "fp_purity"},
  "matches": [
    {
      "directive": {
        "name": "fp_purity_check",
        "type": "fp",
        "level": 3,
        "category": "fp_purity",
        "description": "Validates function purity..."
      }
    },
    {
      "directive": {
        "name": "fp_side_effects_detect",
        "type": "fp",
        "level": 3,
        "category": "fp_purity",
        "description": "Identifies side effects in functions..."
      }
    }
  ],
  "total_matches": 2
}
```

**Internally Calls**:
- `find_directive_by_intent(query, threshold)` (if match_mode="intent")
- `search_directives(keyword, category, type)` (if match_mode="keyword")
- `get_directive(name)` (if match_mode="exact")
- `get_directive_interactions(name)` (if include_related=true)
- Intent matching algorithm (semantic similarity)

**Used By**:
- `aifp_run` directive (PRIMARY - user intent resolution)
- AI query: "what directive should I use?"
- Directive discovery UI
- Workflow planning

**Error Handling**:
- Returns empty matches list if no results
- Logs failed queries
- Suggests alternative search terms

**is_tool**: `true`

---

## 2. find_helpers()

**Purpose**: Intelligent helper function discovery. Find helpers by purpose, database, category, or usage pattern.

**Signature**:
```python
def find_helpers(
    query: str = None,        # Natural language query or keyword
    filters: dict = {},       # Structured filters
    include_examples: bool = False,  # Include usage examples
    group_by: str = None,     # Group results by field
    limit: int = 20           # Max results
) -> dict
```

**Parameters**:

### query (str)
Natural language query or keyword:
- `"get current task status"` (intent matching)
- `"link task to flows"` (keyword matching)
- `"matrix checksum"` (content search)

### filters (dict)
Structured filtering:
```python
filters = {
    "database": "project",           # Which database (project, mcp, preferences, user_directives)
    "is_tool": True,                 # Only MCP-exposed tools
    "used_by": "project_auto_resume", # Used by specific directive
    "category": "task_management",   # Functional category
    "file_path": "flow_context_tools.py"  # Specific file
}
```

### include_examples (bool)
If true, includes code examples and usage patterns

### group_by (str)
Group results by: `"database"`, `"category"`, `"file"`, `"is_tool"`

### limit (int)
Maximum results per group (if grouped) or total

**Returns**:

### Query Match Response
```json
{
  "query": "get task with flows and files",
  "matches": [
    {
      "helper": {
        "name": "get_work_context",
        "file_path": "src/aifp/helpers/project/tools/flow_context_tools.py",
        "database": "project",
        "purpose": "Get complete context for resuming work. Single call retrieves task + flows + files + functions + interactions.",
        "is_tool": true,
        "used_by": ["project_auto_resume", "aifp_status"]
      },
      "relevance": 0.95,
      "match_reasons": [
        "Purpose keyword match: 'task', 'flows', 'files'",
        "Returns comprehensive work context"
      ],
      "example": {
        "signature": "get_work_context(work_item_type: str, work_item_id: int)",
        "usage": "context = get_work_context('task', 5)",
        "returns": "Complete task context with flows, files, and functions"
      }
    },
    {
      "helper": {
        "name": "get_flows_for_task",
        "file_path": "src/aifp/helpers/project/tools/flow_context_tools.py",
        "database": "project",
        "purpose": "Get all flows associated with task.",
        "is_tool": true,
        "used_by": ["project_auto_resume", "aifp_status"]
      },
      "relevance": 0.82,
      "match_reasons": [
        "Purpose keyword match: 'task', 'flows'",
        "Specific to flow retrieval"
      ]
    }
  ],
  "total_matches": 2,
  "suggestion": "Use get_work_context() for comprehensive context, or get_flows_for_task() for flows only"
}
```

### Grouped Response (group_by="database")
```json
{
  "query": "get current status",
  "grouped_by": "database",
  "groups": {
    "project": {
      "count": 5,
      "helpers": [
        {"name": "get_current_progress", "purpose": "Single entry point for all status queries", "is_tool": true},
        {"name": "get_project_metadata", "purpose": "Get project overview and metadata", "is_tool": false},
        {"name": "get_task_by_id", "purpose": "Get single task by ID", "is_tool": false}
      ]
    },
    "preferences": {
      "count": 2,
      "helpers": [
        {"name": "get_all_preferences", "purpose": "Get all user preferences", "is_tool": true},
        {"name": "get_preference", "purpose": "Get single preference value", "is_tool": false}
      ]
    }
  },
  "total_matches": 7
}
```

### Filtered Response (is_tool=true only)
```json
{
  "query": null,
  "filters": {"database": "project", "is_tool": true},
  "matches": [
    {"name": "get_current_progress", "purpose": "Status queries", "is_tool": true},
    {"name": "update_project_state", "purpose": "Common updates", "is_tool": true},
    {"name": "batch_update_progress", "purpose": "Multi-item updates", "is_tool": true},
    {"name": "query_project_state", "purpose": "Complex queries", "is_tool": true},
    {"name": "get_work_context", "purpose": "Resume context", "is_tool": true}
  ],
  "total_matches": 5
}
```

**Internally Calls**:
- Queries `helpers` table in aifp_core.db
- Semantic matching on purpose field
- Keyword matching on name and purpose
- Filters by is_tool, database, etc.

**Used By**:
- AI: "what helper should I use?"
- Directive developers
- Helper documentation generation
- Code completion/suggestions

**Error Handling**:
- Returns empty matches if no results
- Suggests alternative search terms
- Logs search queries for improvement

**is_tool**: `true`

---

## 3. get_system_context()

**Purpose**: Get complete AIFP system state and configuration. Single call for session initialization, debugging, and status reporting.

**Signature**:
```python
def get_system_context(
    include_directives: bool = True,
    include_helpers: bool = True,
    include_preferences: bool = True,
    include_project: bool = True,
    summary_only: bool = False  # Just counts, not full data
) -> dict
```

**Parameters**:

### include_directives (bool)
Include directive counts and categories

### include_helpers (bool)
Include helper counts and categories

### include_preferences (bool)
Include user preferences summary

### include_project (bool)
Include active project info

### summary_only (bool)
Return counts only (fast) or full details (comprehensive)

**Returns**:

### Full Context Response
```json
{
  "aifp_version": "1.0.0",
  "databases": {
    "aifp_core": {
      "path": ".aifp/aifp_core.db",
      "size_mb": 2.3,
      "last_updated": "2025-11-05T14:00:00",
      "status": "healthy"
    },
    "project": {
      "path": ".aifp-project/project.db",
      "size_mb": 1.1,
      "last_updated": "2025-11-05T15:00:00",
      "status": "healthy"
    },
    "user_preferences": {
      "path": ".aifp/user_preferences.db",
      "size_mb": 0.2,
      "last_updated": "2025-11-01T10:00:00",
      "status": "healthy"
    },
    "user_directives": {
      "path": ".aifp/user_directives.db",
      "size_mb": 0.5,
      "last_updated": "2025-10-28T12:00:00",
      "status": "healthy"
    }
  },
  "directives": {
    "total": 89,
    "by_type": {
      "fp": 35,
      "project": 32,
      "user": 15,
      "git": 7
    },
    "by_level": {
      "1": 5,
      "2": 15,
      "3": 55,
      "4": 14
    },
    "categories": [
      "fp_purity", "fp_adt", "task_management", "recovery_automation", "git_integration"
    ]
  },
  "helpers": {
    "total": 195,
    "tools_exposed": 25,
    "by_database": {
      "project": 79,
      "mcp": 55,
      "preferences": 39,
      "user_directives": 32
    }
  },
  "active_project": {
    "name": "MatrixCalculator",
    "status": "active",
    "version": 3,
    "progress": 0.35,
    "current_work": "Task: Implement matrix operations (in_progress)"
  },
  "user_preferences": {
    "helper_function_logging": true,
    "fp_strict_mode": false,
    "auto_resume": false,
    "default_language": "Python"
  },
  "system_health": {
    "all_databases_accessible": true,
    "schema_versions_match": true,
    "no_corruption_detected": true,
    "last_health_check": "2025-11-05T15:00:00"
  }
}
```

### Summary Only Response
```json
{
  "aifp_version": "1.0.0",
  "directives_count": 89,
  "helpers_count": 195,
  "active_project": "MatrixCalculator",
  "databases_healthy": true,
  "system_ready": true
}
```

**Internally Calls**:
- `count_directives_by_type()`
- `count_helpers_by_database()`
- `get_project_metadata()` (if include_project=true)
- `get_all_preferences()` (if include_preferences=true)
- Database health checks
- Schema version checks

**Used By**:
- Session initialization
- `aifp_status` directive
- System diagnostics
- Debugging and troubleshooting
- Health monitoring

**Error Handling**:
- Returns partial data if some databases inaccessible
- Flags unhealthy databases in response
- Never fails completely

**Performance**:
- Summary mode: <50ms
- Full context: <200ms

**is_tool**: `true`

---

## 4. query_mcp_relationships()

**Purpose**: Query directive and helper relationships. Understand dependencies, interactions, and workflow patterns.

**Signature**:
```python
def query_mcp_relationships(
    entity_type: str,         # "directive" or "helper"
    entity_name: str,         # Name of entity
    relationship_type: str = "all",  # Which relationships to query
    depth: int = 1,           # Relationship depth (1-3)
    include_descriptions: bool = True  # Include entity descriptions
) -> dict
```

**Parameters**:

### entity_type (str)
- `"directive"` - Query directive relationships
- `"helper"` - Query helper relationships

### entity_name (str)
Name of directive or helper (e.g., "project_task_create", "get_work_context")

### relationship_type (str)
Which relationships to include:

**For Directives**:
- `"all"` (default) - All relationships
- `"depends_on"` - Directives this depends on
- `"triggers"` - Directives this triggers
- `"escalates_to"` - Escalation path
- `"cross_links"` - Related directives
- `"uses_helpers"` - Helpers used by this directive

**For Helpers**:
- `"all"` (default) - All relationships
- `"used_by"` - Which directives use this helper
- `"calls"` - Other helpers this calls
- `"called_by"` - Helpers that call this

### depth (int)
How deep to traverse relationships:
- `1` - Direct relationships only
- `2` - Relationships of relationships
- `3` - Three levels deep

### include_descriptions (bool)
Include full descriptions of related entities

**Returns**:

### Directive Relationships Response
```json
{
  "entity_type": "directive",
  "entity_name": "project_task_create",
  "relationships": {
    "depends_on": [
      {
        "name": "project_task_decomposition",
        "type": "project",
        "description": "Breaks down user goals into tasks...",
        "relationship": "Parent directive that calls project_task_create"
      }
    ],
    "triggers": [
      {
        "name": "project_item_create",
        "type": "project",
        "description": "Creates items for tasks...",
        "relationship": "Called after task creation to add items"
      }
    ],
    "escalates_to": [
      {
        "name": "project_user_referral",
        "type": "project",
        "description": "Prompts user when input needed...",
        "relationship": "Called when validation fails"
      }
    ],
    "uses_helpers": [
      {
        "name": "create_task",
        "file_path": "src/aifp/helpers/project/tools/task_tools.py",
        "purpose": "Create new task in database",
        "is_tool": false
      },
      {
        "name": "link_task_to_flows",
        "file_path": "src/aifp/helpers/project/tools/flow_context_tools.py",
        "purpose": "Associate task with flows",
        "is_tool": true
      },
      {
        "name": "validate_flow_ids",
        "file_path": "src/aifp/helpers/project/internal/validation.py",
        "purpose": "Validate flow IDs exist",
        "is_tool": false
      }
    ],
    "cross_links": [
      {
        "name": "project_subtask_create",
        "type": "project",
        "description": "Creates subtasks under tasks...",
        "relationship": "Alternative for hierarchical task breakdown"
      }
    ]
  },
  "depth": 1,
  "total_relationships": 6
}
```

### Helper Relationships Response
```json
{
  "entity_type": "helper",
  "entity_name": "get_work_context",
  "relationships": {
    "used_by": [
      {
        "name": "project_auto_resume",
        "type": "project",
        "level": 3,
        "description": "Detects unfinished tasks and resumes...",
        "usage": "Primary function for retrieving resume context"
      },
      {
        "name": "aifp_status",
        "type": "core",
        "level": 2,
        "description": "Displays project status...",
        "usage": "Used when detail_level='detailed'"
      }
    ],
    "calls": [
      {
        "name": "get_flows_for_task",
        "purpose": "Get flows associated with task",
        "is_tool": true
      },
      {
        "name": "get_recent_files_for_task",
        "purpose": "Get files in task's flows",
        "is_tool": true
      },
      {
        "name": "get_recent_functions_for_task",
        "purpose": "Get functions in task's files",
        "is_tool": true
      },
      {
        "name": "infer_action",
        "purpose": "Determine if file/function created or modified",
        "is_tool": false
      }
    ]
  },
  "depth": 1,
  "total_relationships": 6
}
```

### Depth 2 Response (Relationships of Relationships)
```json
{
  "entity_type": "directive",
  "entity_name": "project_auto_resume",
  "relationships": {
    "depends_on": [
      {
        "name": "aifp_run",
        "depth": 1,
        "description": "Gateway directive...",
        "sub_relationships": {
          "depends_on": [
            {"name": "aifp_status", "depth": 2}
          ]
        }
      }
    ],
    "uses_helpers": [
      {
        "name": "get_work_context",
        "depth": 1,
        "sub_relationships": {
          "calls": [
            {"name": "get_flows_for_task", "depth": 2},
            {"name": "get_recent_files_for_task", "depth": 2}
          ]
        }
      }
    ]
  },
  "depth": 2,
  "total_relationships": 5
}
```

**Internally Calls**:
- `get_directive_interactions(directive_name)` (for directives)
- `get_helper_relationships(helper_name)` (for helpers)
- Recursive queries for depth > 1
- Description lookup for related entities

**Used By**:
- Workflow visualization
- Dependency analysis
- Documentation generation
- Debugging directive chains
- Understanding system architecture

**Error Handling**:
- Returns empty relationships if entity not found
- Warns about circular dependencies (depth limit)
- Logs relationship queries

**Performance**:
- Depth 1: <50ms
- Depth 2: <150ms
- Depth 3: <300ms (limit to prevent excessive traversal)

**is_tool**: `true`

---

## Generic Tools Summary

| Tool | Primary Use Case | Typical Response Time |
|------|------------------|----------------------|
| `find_directives()` | Directive discovery and intent matching | 50-200ms |
| `find_helpers()` | Helper function discovery | 30-100ms |
| `get_system_context()` | System state and health | 50-200ms |
| `query_mcp_relationships()` | Dependency and workflow analysis | 50-300ms |

**Total Generic Tools**: 4
**Total Specific Helpers Available**: 55 MCP helpers

---

## Implementation Notes

### Intent Matching Algorithm
`find_directives()` uses semantic similarity:
1. Tokenize user query
2. Compare against directive descriptions and intent keywords
3. Score matches using TF-IDF or embedding similarity
4. Filter by confidence threshold
5. Rank by relevance

### Caching Strategy
- System context cached for 30 seconds (fast repeated queries)
- Directive/helper lists cached until schema changes
- Relationship graphs cached per entity

### Performance Optimization
- Lazy loading of descriptions (only if requested)
- Batch queries for relationships at depth > 1
- Index all foreign keys for fast JOINs

---

**End of MCP Generic Tools Specification**
