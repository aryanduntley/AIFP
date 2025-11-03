# Additional User Directives Database Helpers (user_directives.db)

**Purpose**: Tools for managing custom user-defined automation directives (Use Case 2: Custom Directive Automation).

**Philosophy**: Enable AI to parse user directive files, generate FP-compliant implementation code, and manage real-time execution of automation workflows.

**Database**: `user_directives.db` (per-project, mutable, located in `.aifp-project/`, **only exists in automation projects**)

**Use Case**: Automation projects where users write directive definitions (YAML/JSON/TXT) and AI generates implementation code for real-time execution (home automation, cloud infrastructure, scheduled tasks, etc.)

**Status**: 🔵 Proposed (Not Yet Implemented)

---

## Table of Contents

1. [Directive Management Tools](#directive-management-tools)
2. [Execution Tracking Tools](#execution-tracking-tools)
3. [Dependency Management Tools](#dependency-management-tools)
4. [Implementation Management Tools](#implementation-management-tools)
5. [Logging Configuration Tools](#logging-configuration-tools)
6. [Analytics & Monitoring Tools](#analytics--monitoring-tools)

---

## Directive Management Tools

**Table**: `user_directives` - Parsed directive definitions

**Note**: 10 existing user directive helpers in user_directives.py (all internal, not tools)

### Getters

#### `get_directive_by_id(directive_id: int)`
**Purpose**: Get complete user directive details.

**Returns**:
```json
{
  "id": 1,
  "name": "turn_on_lights",
  "source_file": "directives/lights.yaml",
  "directive_type": "trigger",
  "trigger": "time: 18:00",
  "action": "http_request: POST /api/lights/on",
  "configuration_json": {...},
  "status": "active",
  "approved": true,
  "created_at": "2025-10-15T08:00:00"
}
```

---

#### `get_directive_by_name(name: str)`
**Purpose**: Get directive by name.

**Returns**: Directive object or `{"found": false}`

---

#### `get_directives_by_status(status: str)`
**Purpose**: Filter directives by status.

**Parameters**:
- `status` (str): "draft", "validated", "implemented", "active", "paused", "error", "archived"

**Returns**: List of directive objects

**Use Case**: Show active directives, troubleshoot errors

---

#### `get_directives_by_type(directive_type: str)`
**Purpose**: Filter directives by type.

**Parameters**:
- `directive_type` (str): "trigger", "schedule", "api", "conditional", "sequence"

**Returns**: List of directive objects

**Use Case**: Group directives by automation type

---

#### `get_active_directives()`
**Purpose**: Get all active (running) directives.

**Returns**: List of active directive objects

**Use Case**: `user_directive_status` directive, monitoring

**Note**: Similar to existing `get_user_directive_status()` but focused on directives table

---

#### `get_directives_from_file(source_file: str)`
**Purpose**: Get all directives parsed from specific source file.

**Returns**: List of directive objects

**Use Case**: Track which directives came from which file

---

### Setters

#### `update_directive_status(directive_id: int, status: str)`
**Purpose**: Update directive status.

**Parameters**:
- `status` (str): "draft", "validated", "implemented", "active", "paused", "error", "archived"

**Returns**: `{"success": true, "previous_status": "...", "new_status": "active"}`

**Use Case**: Lifecycle management (`user_directive_activate`, `user_directive_deactivate`)

---

#### `update_directive_config(directive_id: int, configuration_json: dict)`
**Purpose**: Update directive configuration after re-validation.

**Returns**: `{"success": true, "updated_fields": [...]}`

**Use Case**: `user_directive_update` directive

---

#### `set_directive_approval(directive_id: int, approved: bool)`
**Purpose**: Mark directive as approved for execution.

**Returns**: `{"success": true, "approved": true}`

**Use Case**: `user_directive_approve` directive (user confirmation)

---

#### `archive_directive(directive_id: int)`
**Purpose**: Archive directive (soft delete).

**Returns**: `{"success": true, "archived_date": "2025-11-02"}`

**Use Case**: Cleanup, disable without losing history

---

## Execution Tracking Tools

**Table**: `directive_executions` - Runtime execution statistics

### Getters

#### `get_execution_stats(directive_id: int)`
**Purpose**: Get execution statistics for directive.

**Returns**:
```json
{
  "directive_id": 1,
  "directive_name": "turn_on_lights",
  "total_executions": 45,
  "successful_executions": 42,
  "failed_executions": 3,
  "last_execution": "2025-11-02T10:00:00",
  "last_status": "success",
  "average_duration_ms": 235.5,
  "success_rate": 0.93
}
```

**Use Case**: Monitoring, reliability metrics

---

#### `get_recent_executions(directive_id: int = None, limit: int = 50)`
**Purpose**: Get recent execution history.

**Parameters**:
- `directive_id` (int, optional): Filter by directive
- `limit` (int): Number of records

**Returns**: List of execution records (summary only, detailed logs in files)

---

#### `get_failed_executions(directive_id: int = None, since_date: str = None)`
**Purpose**: Get failed executions for debugging.

**Parameters**:
- `directive_id` (int, optional): Filter by directive
- `since_date` (str, optional): ISO date string

**Returns**: List of failed execution records

**Use Case**: Troubleshooting, error analysis

---

#### `get_execution_trends(days: int = 7)`
**Purpose**: Get execution trends over time.

**Returns**:
```json
{
  "period": "7 days",
  "daily_stats": [
    {
      "date": "2025-11-02",
      "total_executions": 45,
      "success_rate": 0.96,
      "average_duration_ms": 230
    }
  ],
  "trending_up": true,
  "most_active_directive": "turn_on_lights"
}
```

**Use Case**: Performance monitoring, capacity planning

---

### Setters

#### `record_execution(directive_id: int, status: str, duration_ms: int = None, error_message: str = None)`
**Purpose**: Log directive execution (summary only).

**Parameters**:
- `status` (str): "success", "failure", "timeout"
- `duration_ms` (int, optional): Execution time
- `error_message` (str, optional): Error summary

**Returns**: `{"success": true, "execution_id": 1}`

**Note**: Detailed logs go to files, database stores summary statistics only

**Use Case**: Runtime execution tracking

---

## Dependency Management Tools

**Table**: `directive_dependencies` - Required packages, APIs, services

### Getters

#### `get_dependencies(directive_id: int = None)`
**Purpose**: Get all dependencies, optionally filtered by directive.

**Returns**:
```json
{
  "dependencies": [
    {
      "id": 1,
      "directive_id": 1,
      "dependency_type": "python_package",
      "name": "requests",
      "version": "2.31.0",
      "is_installed": true,
      "required_by": ["turn_on_lights", "check_status"]
    }
  ],
  "count": 5
}
```

---

#### `get_missing_dependencies()`
**Purpose**: Get dependencies that need installation.

**Returns**: List of dependency objects where `is_installed = false`

**Use Case**: Pre-flight checks before activation

---

#### `get_dependencies_by_type(dependency_type: str)`
**Purpose**: Filter dependencies by type.

**Parameters**:
- `dependency_type` (str): "python_package", "system_package", "api_key", "environment_var", "service"

**Returns**: List of dependency objects

---

### Setters

#### `add_dependency(directive_id: int, dependency_type: str, name: str, version: str = None)`
**Purpose**: Register new dependency.

**Returns**: `{"success": true, "dependency_id": 1}`

**Use Case**: `detect_dependencies()` helper finds required packages

**Note**: Existing helper in user_directives.py

---

#### `mark_dependency_installed(dependency_id: int)`
**Purpose**: Mark dependency as installed.

**Returns**: `{"success": true, "dependency": "requests", "version": "2.31.0"}`

**Use Case**: After `install_dependency()` succeeds

**Note**: Existing helper in user_directives.py

---

## Implementation Management Tools

**Table**: `directive_implementations` - Generated code tracking

### Getters

#### `get_implementation(directive_id: int)`
**Purpose**: Get generated code location and status.

**Returns**:
```json
{
  "id": 1,
  "directive_id": 1,
  "implementation_file": "src/automations/lights_controller.py",
  "entry_point": "execute_turn_on_lights",
  "generated_at": "2025-10-15T08:30:00",
  "last_modified": "2025-10-16T10:00:00",
  "status": "deployed",
  "test_file": "tests/test_lights_controller.py",
  "test_status": "passing"
}
```

**Use Case**: Track generated code files

---

#### `get_implementations_by_status(status: str)`
**Purpose**: Filter implementations by deployment status.

**Parameters**:
- `status` (str): "draft", "validated", "deployed", "failed"

**Returns**: List of implementation objects

---

#### `get_failing_tests()`
**Purpose**: Get implementations with failing tests.

**Returns**: List of implementation objects where `test_status != "passing"`

**Use Case**: Quality checks, CI/CD

---

### Setters

#### `register_implementation(directive_id: int, implementation_file: str, entry_point: str, test_file: str = None)`
**Purpose**: Register generated code.

**Returns**: `{"success": true, "implementation_id": 1}`

**Use Case**: After `generate_implementation_code()` creates files

**Note**: Existing helper in user_directives.py

---

#### `update_implementation_status(implementation_id: int, status: str)`
**Purpose**: Update deployment status.

**Returns**: `{"success": true}`

**Use Case**: Lifecycle tracking

---

#### `update_test_status(implementation_id: int, test_status: str)`
**Purpose**: Update test results.

**Parameters**:
- `test_status` (str): "passing", "failing", "pending", "skipped"

**Returns**: `{"success": true}`

**Use Case**: CI/CD integration

---

## Logging Configuration Tools

**Table**: `logging_config` - Log rotation and retention settings

### Getters

#### `get_logging_config(log_type: str = None)`
**Purpose**: Get logging configuration.

**Parameters**:
- `log_type` (str, optional): "execution", "error", "lifecycle"

**Returns**:
```json
{
  "configs": [
    {
      "id": 1,
      "log_type": "execution",
      "retention_days": 30,
      "rotation_size_mb": 50,
      "log_directory": ".aifp-project/logs/execution/",
      "enabled": true
    }
  ]
}
```

**Use Case**: Log management, disk space monitoring

---

#### `get_log_retention_policy()`
**Purpose**: Get all retention policies.

**Returns**: Dict of log types with retention settings

---

### Setters

#### `update_logging_config(log_type: str, retention_days: int = None, rotation_size_mb: int = None)`
**Purpose**: Update log configuration.

**Returns**: `{"success": true}`

**Use Case**: Adjust log retention based on disk space

---

#### `toggle_logging(log_type: str, enabled: bool)`
**Purpose**: Enable/disable specific log type.

**Returns**: `{"success": true, "log_type": "execution", "enabled": false}`

**Use Case**: Pause logging temporarily

---

## Analytics & Monitoring Tools

**Purpose**: Cross-table analytics and health monitoring

### Analytics

#### `get_directive_health_summary()`
**Purpose**: Get overall health of user directive system.

**Returns**:
```json
{
  "total_directives": 15,
  "active_directives": 12,
  "paused_directives": 2,
  "error_directives": 1,
  "overall_success_rate": 0.94,
  "total_executions_24h": 287,
  "failing_directives": [
    {"name": "...", "error_count": 3, "last_error": "..."}
  ],
  "missing_dependencies": 0,
  "failing_tests": 0
}
```

**Use Case**: `user_directive_status` directive, dashboard

**Note**: More comprehensive than existing `get_user_directive_status()`

---

#### `get_execution_summary(days: int = 7)`
**Purpose**: Execution statistics over time period.

**Returns**:
```json
{
  "period": "7 days",
  "total_executions": 1234,
  "success_rate": 0.96,
  "average_duration_ms": 245,
  "most_executed": [
    {"directive": "turn_on_lights", "count": 456},
    {"directive": "check_temperature", "count": 321}
  ],
  "most_failures": [
    {"directive": "api_call_service", "failure_count": 15}
  ]
}
```

**Use Case**: Performance reporting, capacity planning

---

#### `get_dependency_report()`
**Purpose**: Summary of all dependencies and their status.

**Returns**:
```json
{
  "total_dependencies": 12,
  "installed": 10,
  "missing": 2,
  "by_type": {
    "python_package": 8,
    "api_key": 3,
    "environment_var": 1
  },
  "missing_list": [
    {"name": "twilio", "required_by": ["send_sms"]},
    {"name": "API_KEY_WEATHER", "required_by": ["check_weather"]}
  ]
}
```

**Use Case**: Pre-flight checks, setup validation

---

### Monitoring

#### `get_error_directives()`
**Purpose**: Get directives in error state with details.

**Returns**:
```json
{
  "error_directives": [
    {
      "id": 5,
      "name": "api_call_service",
      "status": "error",
      "error_count_24h": 8,
      "last_error": "Connection timeout",
      "last_execution": "2025-11-02T09:45:00"
    }
  ],
  "count": 1
}
```

**Use Case**: Monitoring, alerting

---

#### `get_stale_directives(days: int = 7)`
**Purpose**: Get directives that haven't executed recently.

**Parameters**:
- `days` (int): Threshold for staleness

**Returns**: List of directives with no recent executions

**Use Case**: Identify inactive/forgotten directives

---

## Implementation Notes

### Module Organization

**Directory Structure**:
```
src/aifp/helpers/user_directives/
├── tools/                          # is_tool=true (MCP-exposed)
│   ├── directive_mgmt_tools.py     # ~8 functions
│   ├── execution_tools.py          # ~5 functions
│   ├── dependency_tools.py         # ~5 functions
│   ├── implementation_tools.py     # ~5 functions
│   ├── logging_tools.py            # ~4 functions
│   └── analytics_tools.py          # ~5 functions
└── internal/                       # is_tool=false (used by directives)
    ├── parsing.py                  # parse_directive_file
    ├── validation.py               # validate_user_directive
    ├── code_generation.py          # generate_implementation_code
    ├── dependency_detection.py     # detect_dependencies
    ├── installation.py             # install_dependency
    ├── activation.py               # activate_directive
    ├── monitoring.py               # monitor_directive_execution
    └── updates.py                  # update_directive
```

**Current User Directive Helpers**: 10 functions (all internal)
**Proposed User Directive Tools**: ~32 functions (from this document)
**Total User Directive Tools After Additions**: ~42 tools (32 new + 10 existing remain internal)

**Breakdown**:
- Directive Management: 8 functions (6 getters + 4 setters)
- Execution Tracking: 5 functions (4 getters + 1 setter)
- Dependency Management: 5 functions (3 getters + 2 setters)
- Implementation Management: 5 functions (3 getters + 2 setters)
- Logging Configuration: 4 functions (2 getters + 2 setters)
- Analytics & Monitoring: 5 functions (analytics/health)

### Naming Conventions

- **Directive queries**: `get_directive_by_id()`, `get_directives_by_status()`
- **Execution tracking**: `record_execution()`, `get_execution_stats()`
- **Dependencies**: `add_dependency()`, `mark_dependency_installed()`
- **Health checks**: `get_directive_health_summary()`, `get_error_directives()`

### Return Types

All functions return:
- **Single entity**: Object dict or `{"found": false}`
- **Multiple entities**: List of dicts (empty list if none)
- **Setters**: `{"success": true/false, ...details}`
- **Analytics**: Dict with metrics and insights

### Error Handling

- Never raise exceptions
- Return empty structures or `{"found": false}`
- Log warnings for invalid parameters
- Validate directive_id foreign keys

### File-Based Logging

**Important**: Detailed execution logs go to files, NOT database:
- `.aifp-project/logs/execution/` - Execution logs (30-day retention)
- `.aifp-project/logs/errors/` - Error logs (90-day retention)
- `.aifp-project/logs/lifecycle/` - Lifecycle events (180-day retention)

Database stores summary statistics only (execution counts, success rates, timestamps).

---

## Priority Implementation Order

### Phase 1: Critical (Core Automation Support)
**Essential for User Directive Workflow**
1. `get_directive_by_id()` - Directive operations
2. `get_directives_by_status()` - Status filtering
3. `update_directive_status()` - Lifecycle management
4. `get_active_directives()` - Active automation list
5. `get_execution_stats()` - Monitoring
6. `record_execution()` - Execution tracking
7. `get_missing_dependencies()` - Pre-flight checks
8. `get_directive_health_summary()` - Status overview

### Phase 2: Important (Reliability & Monitoring)
**Error Handling & Analytics**
9. `get_failed_executions()` - Troubleshooting
10. `get_error_directives()` - Alert system
11. `get_dependency_report()` - Setup validation
12. `get_implementation()` - Code tracking
13. `get_execution_trends()` - Performance analysis
14. `update_test_status()` - CI/CD integration

### Phase 3: Advanced (Management & Optimization)
**Configuration & Analytics**
15. `get_logging_config()` - Log management
16. `get_execution_summary()` - Reporting
17. `get_stale_directives()` - Maintenance
18. All remaining helpers

---

## Existing Helpers (Already in helpers_parsed.json)

**Current User Directive Helpers** (10 functions - all internal):

1. `parse_directive_file()` - Parse user directive files
2. `validate_user_directive()` - Interactive Q&A validation
3. `generate_implementation_code()` - Generate FP-compliant code
4. `detect_dependencies()` - Find required packages
5. `install_dependency()` - Install with user confirmation
6. `activate_directive()` - Deploy and start execution
7. `monitor_directive_execution()` - Track execution stats
8. `get_user_directive_status()` - Build status report
9. `update_directive()` - Handle directive updates
10. `deactivate_directive()` - Stop execution gracefully

**Note**: All existing helpers should remain internal (is_tool=false) - they are workflow orchestrators used by directives, not direct data access tools.

---

## Integration with Other Databases

### With project.db (Project Helpers)
- Generated implementation code tracked in project.db (files, functions)
- Project status includes `user_directives_status` field
- Completion path includes directive implementation stages

### With user_preferences.db (Preferences Helpers)
- User preferences for directive behavior (if needed)
- Tracking settings for execution logging

### With aifp_core.db (MCP Helpers)
- User system directives loaded from aifp_core.db
- Directive execution follows AIFP directive system

---

## Discussion Questions

1. **Log storage**: Should logs be in database or files? (Current: files for detail, DB for stats)
2. **Execution limits**: Should directives have rate limiting/throttling?
3. **Approval workflow**: Should all directives require manual approval before first execution?
4. **Dependency versioning**: Should dependencies track semantic version ranges?
5. **Rollback support**: Should implementations support rollback to previous versions?
6. **Multi-tenancy**: Should one automation project support multiple user directive sets?

---

## Use Case Context

**Use Case 2: Custom Directive Automation**

This database only exists when users enable custom directive automation. Projects using this are **dedicated automation projects** where:
- User writes directive definitions (YAML/JSON/TXT)
- AI generates FP-compliant implementation code in `src/`
- Code executes continuously via background services
- Real-time execution engine handles triggers, schedules, APIs

**Examples**:
- Home automation (lights, thermostats, security)
- Cloud infrastructure orchestration (AWS, GCP, Azure)
- Scheduled task automation (backups, reports, cleanup)
- API workflow automation (webhooks, data pipelines)
- IoT device management

**Not for**: Regular software development projects (those use only project.db)

---

**Next Steps**:
1. Review all four helper documents
2. Update project database with preparation notes
3. Prioritize helpers for implementation
4. Add approved helpers to `helpers_parsed.json` with new folder structure
5. Re-run `sync-directives.py`

---

**Status**: 🔵 Proposed - Awaiting Review
**Created**: 2025-11-02
**Author**: AIFP Development Team
