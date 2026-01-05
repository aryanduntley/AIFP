# Settings Design and Integration Strategy

**Date**: 2026-01-04
**Purpose**: Define the dynamic settings architecture and integration approach for AIFP
**Status**: Design specification based on analysis of current system

---

## Vision: Dynamic, User-Driven Settings

**Core Principle**: Settings are NOT extensive static configurations for the MCP, but **dynamic preferences created as AI interacts with users**.

### Key Concepts

1. **User-Driven Creation**: Settings are created when users express preferences
2. **Directive-Specific**: Settings modify specific directive behavior
3. **Runtime Integration**: Settings are loaded before directive execution
4. **Getter Integration**: Settings provided alongside directives via getters

---

## 1. Current Architecture

### Database Tables

**user_preferences.db** contains three tables:

#### user_settings (Global)
```sql
CREATE TABLE user_settings (
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    scope TEXT DEFAULT 'project'
);
```

**Purpose**: Project-wide settings that affect multiple directives
**Examples**:
- `fp_strictness_level` - Global FP enforcement level
- `prefer_explicit_returns` - Code generation preference
- `suppress_warnings` - Warning suppression list

#### directive_preferences (Per-Directive)
```sql
CREATE TABLE directive_preferences (
    directive_name TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    description TEXT,
    UNIQUE(directive_name, preference_key)
);
```

**Purpose**: Atomic key-value overrides for specific directives
**Examples**:
- `project_file_write.always_add_docstrings = true`
- `project_task_decomposition.task_granularity = fine`
- `project_compliance_check.strict_mode = true`

#### tracking_settings (Feature Flags)
```sql
CREATE TABLE tracking_settings (
    feature_name TEXT NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT 0,
    description TEXT,
    estimated_token_overhead TEXT
);
```

**Purpose**: Opt-in tracking features (all disabled by default)
**Examples**:
- `fp_flow_tracking` - Track FP directive usage
- `ai_interaction_log` - Log corrections for learning

---

## 2. How Settings Are Created (Dynamic Workflow)

### Traditional Static Approach (WRONG)
```
❌ Developer pre-creates 92+ settings
❌ User never uses most of them
❌ Settings drift from actual directive implementations
❌ Unclear which settings are valid
```

### Dynamic User-Driven Approach (CORRECT)
```
✅ User expresses preference during interaction
✅ AI creates setting dynamically
✅ AI updates directive to check setting
✅ Setting is documented after creation
```

### Example Workflow

**Step 1: User Expresses Preference**
```
User: "Always add type hints when writing files"
```

**Step 2: AI Calls user_preferences_update**
```python
# AI identifies:
# - Intent: Modify file writing behavior
# - Target directive: project_file_write
# - Preference key: always_add_type_hints
# - Preference value: true

INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description)
VALUES ('project_file_write', 'always_add_type_hints', 'true', 'Always add type hints to function signatures');
```

**Step 3: AI Updates Directive Workflow (if needed)**
```json
{
  "directive": "project_file_write",
  "workflow": {
    "trunk": "prepare_file_write",
    "branches": [
      {
        "condition": "directive_preferences_exist",
        "action": "load_preferences",
        "apply": [
          "always_add_docstrings",
          "max_function_length",
          "prefer_guard_clauses",
          "always_add_type_hints"  // ← NEW preference added
        ]
      }
    ]
  }
}
```

**Step 4: AI Confirms to User**
```
AI: "✅ Preference saved: project_file_write
     Key: always_add_type_hints
     Value: true

     I'll now add type hints to all functions when writing files."
```

**Step 5: Setting is Documented**
```markdown
## always_add_type_hints

**Directive**: project_file_write
**Type**: Boolean
**Default**: false
**Description**: Add type hints to function signatures
**Created**: 2026-01-04 (user request)
```

---

## 3. When Settings Are Called

### Directive Execution Flow

```
1. AI receives user request
   ↓
2. AI determines which directive to execute
   ↓
3. BEFORE executing directive:
   - Check if directive has preferences
   - If yes: Call user_preferences_sync(directive_name)
   ↓
4. user_preferences_sync loads preferences:
   - Query: SELECT preference_key, preference_value
            FROM directive_preferences
            WHERE directive_name=? AND active=1
   ↓
5. Apply preferences to directive execution context
   ↓
6. Execute directive with modified behavior
   ↓
7. Return result
```

### user_preferences_sync Directive

**Purpose**: Load preferences before directive execution

**When Called**:
- Automatically before any "customizable" directive
- Manually by AI when exploring user preferences
- Never called for non-customizable directives (e.g., pure FP reference directives)

**What It Returns**:
```json
{
  "directive_name": "project_file_write",
  "preferences": {
    "always_add_docstrings": "true",
    "max_function_length": "50",
    "prefer_guard_clauses": "true",
    "code_style": "explicit",
    "indent_style": "spaces_2"
  },
  "global_settings": {
    "fp_strictness_level": {"level": "standard", "exceptions": []},
    "prefer_explicit_returns": "true"
  }
}
```

---

## 4. Integration with Directive Getters

### Current Problem

**Without Settings Integration**:
```
AI: get_directive('project_file_write')
→ Returns: Directive definition only
→ AI must separately query preferences
→ Two calls required
```

### Proposed Solution

**With Settings Integration** (preferences passed automatically):

#### Option 1: Getter Returns Settings
```python
def get_directive(directive_name: str, include_preferences: bool = True):
    """Get directive with optional preferences"""
    directive = query_directive(directive_name)

    if include_preferences:
        preferences = query_preferences(directive_name)
        global_settings = query_global_settings()

        directive['preferences'] = preferences
        directive['global_settings'] = global_settings

    return directive
```

**Result**:
```json
{
  "directive": {
    "name": "project_file_write",
    "workflow": {...}
  },
  "preferences": {
    "always_add_docstrings": "true",
    "max_function_length": "50"
  },
  "global_settings": {
    "fp_strictness_level": {"level": "standard", "exceptions": []}
  }
}
```

#### Option 2: Separate Preference Getter (Current Approach)
```python
# Step 1: Get directive
directive = get_directive('project_file_write')

# Step 2: Get preferences (via user_preferences_sync)
preferences = user_preferences_sync('project_file_write')

# Step 3: AI applies preferences manually
```

**Recommendation**: Keep Option 2 (current approach) because:
- Settings are optional (not all executions need them)
- Explicit preference loading is clearer
- Separates concerns (directive definition vs. user customization)

---

## 5. How Directives Should Check Settings

### Pattern: Conditional Preference Loading

**Directive Workflow Structure**:
```json
{
  "directive": "project_file_write",
  "trunk": "prepare_file_write",
  "branches": [
    {
      "condition": "directive_preferences_exist",
      "query": "SELECT COUNT(*) FROM directive_preferences WHERE directive_name='project_file_write' AND active=1",
      "if_true": {
        "action": "load_preferences",
        "helper": "user_preferences_sync",
        "apply": "modify_behavior"
      },
      "if_false": {
        "action": "use_defaults"
      }
    },
    {
      "action": "write_file"
    }
  ]
}
```

### Example: project_file_write

**Without Preferences** (Default Behavior):
```python
def write_file(path, content):
    # Default: No docstrings, no style rules
    return write_to_filesystem(path, content)
```

**With Preferences** (Modified Behavior):
```python
def write_file(path, content, preferences):
    # Apply preferences
    if preferences.get('always_add_docstrings') == 'true':
        content = add_docstrings(content)

    if preferences.get('max_function_length'):
        content = validate_function_length(content, preferences['max_function_length'])

    if preferences.get('prefer_guard_clauses') == 'true':
        content = convert_to_guard_clauses(content)

    # Apply code style
    if preferences.get('code_style'):
        content = apply_code_style(content, preferences['code_style'])

    return write_to_filesystem(path, content)
```

---

## 6. Settings Integration Points

### Where Settings Should Be Queried

**For Each Directive Category**:

#### Project Management Directives
- **project_file_write** → Load before writing
- **project_task_decomposition** → Load before creating tasks
- **project_compliance_check** → Load before checking + load `fp_strictness_level`
- **aifp_status** → Load display preferences (if implemented)

#### User Preference Directives
- **user_preferences_sync** → Loads all preferences for target directive
- **user_preferences_update** → Creates/updates preferences
- **user_preferences_learn** → Requires `ai_interaction_log` tracking enabled
- **tracking_toggle** → Modifies `tracking_settings` table

#### FP Directives (Reference Only)
- **NO settings integration** - These are reference documentation, not executed
- AI consults them for guidance, but they don't execute with preferences

#### Git Directives
- **git_detect_external_changes** → Could load display preferences (if implemented)
- **git_detect_conflicts** → Could load resolution preferences (if implemented)
- **git_merge_branch** → Could load merge strategy preferences (if implemented)

---

## 7. Implementation Checklist

### Phase 1: Core Settings (18 existing)
- [x] Database schema supports settings
- [x] `user_preferences_sync` directive exists
- [x] `user_preferences_update` directive exists
- [x] Settings documented in directive workflows
- [ ] All customizable directives check for preferences
- [ ] AI system prompt includes settings guidance

### Phase 2: Dynamic Creation
- [ ] Document dynamic creation workflow
- [ ] Add examples of creating new settings
- [ ] Update system prompt with creation guidelines
- [ ] Test setting creation for new preferences

### Phase 3: Getter Integration
- [ ] Decide: Include preferences in get_directive() or keep separate?
- [ ] Document preference query pattern for AI
- [ ] Ensure all directive getters support preference loading
- [ ] Test preference propagation

### Phase 4: Validation & Cleanup
- [ ] Remove unused settings from COMPREHENSIVE_SETTINGS_SPEC.md
- [ ] Audit directive workflows for missing preference checks
- [ ] Validate all 18 settings are actually used
- [ ] Document setting lifecycle (create → use → deprecate)

---

## 8. Guidelines for Creating New Settings

### When to Create a Setting

**DO create a setting when**:
- ✅ User expresses a preference: "Always do X"
- ✅ Setting modifies existing directive behavior
- ✅ Preference is reusable across sessions
- ✅ Setting provides value (not micro-management)

**DON'T create a setting when**:
- ❌ Trying to override locked database schema values
- ❌ Preference is one-time only
- ❌ Directive doesn't check for the setting
- ❌ Setting is too granular (micro-optimization)

### Setting Naming Convention

**Format**: `{category}_{action}_{detail}`

**Examples**:
- ✅ `always_add_docstrings` - Clear, boolean
- ✅ `max_function_length` - Clear, numeric
- ✅ `task_granularity` - Clear, enum
- ❌ `preference_for_code_style` - Redundant "preference"
- ❌ `setting_1` - Not descriptive

### Setting Types

**Boolean** (true/false):
- Store as string: `'true'` or `'false'`
- Example: `always_add_docstrings = 'true'`

**Numeric** (integer/float):
- Store as string: `'50'` or `'0.8'`
- Example: `max_function_length = '50'`

**Enum** (predefined options):
- Store as string: `'fine'`, `'medium'`, `'coarse'`
- Example: `task_granularity = 'fine'`

**JSON** (complex):
- Store as JSON string: `'{"level": "standard", "exceptions": []}'`
- Example: `fp_strictness_level = '{"level": "standard"}'`

---

## 9. Example: Adding a New Setting

### Scenario: User wants AI to always add error handling

**Step 1: User Request**
```
User: "Always add comprehensive error handling when writing functions"
```

**Step 2: AI Analysis**
```
AI thinks:
- This is a file writing preference
- Target directive: project_file_write
- Preference key: always_add_error_handling
- Preference value: true
- Type: Boolean
```

**Step 3: AI Creates Setting**
```sql
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, active, description)
VALUES (
  'project_file_write',
  'always_add_error_handling',
  'true',
  1,
  'Add comprehensive error handling to all functions'
);
```

**Step 4: AI Updates Directive Workflow** (if needed)
```json
{
  "directive": "project_file_write",
  "workflow": {
    "branches": [
      {
        "condition": "directive_preferences_exist",
        "apply": [
          "always_add_docstrings",
          "max_function_length",
          "always_add_error_handling"  // ← NEW
        ]
      }
    ]
  }
}
```

**Step 5: AI Implements Logic**
```python
def write_file_with_preferences(path, content, preferences):
    if preferences.get('always_add_error_handling') == 'true':
        # Wrap function bodies with try/Result type handling
        content = add_comprehensive_error_handling(content)

    # Continue with other preferences...
```

**Step 6: AI Confirms**
```
AI: "✅ Preference saved: project_file_write.always_add_error_handling = true

     I'll now add comprehensive error handling to all functions when writing files.
     This includes try/Result type wrappers and explicit error returns."
```

**Step 7: Document**
```markdown
## always_add_error_handling

**Preference Key**: `always_add_error_handling`
**Directive**: `project_file_write`
**Type**: Boolean
**Default**: false
**Description**: Add comprehensive error handling to all functions
**Created**: 2026-01-04 (user request)
**Usage**: Wraps function bodies with Result type handling
```

---

## 10. Summary: Key Takeaways

### Design Principles

1. **Dynamic, not Static**: Settings created on-demand, not pre-defined
2. **User-Driven**: Settings reflect user preferences, not developer assumptions
3. **Directive-Specific**: Settings modify specific directive behavior
4. **Integrated at Runtime**: Settings loaded before directive execution
5. **Documented After Creation**: Settings documented after they exist and work

### Integration Points

1. **Creation**: `user_preferences_update` creates settings dynamically
2. **Loading**: `user_preferences_sync` loads settings before directive execution
3. **Application**: Directives check for preferences and modify behavior
4. **Getters**: Settings optionally included in directive getters
5. **Documentation**: Settings documented in reference files

### Current Status

- ✅ 18 valid settings identified
- ✅ Database schema supports settings
- ✅ Core preference directives exist
- ⚠️ 74+ unused settings in spec (need cleanup)
- ⚠️ Not all directives check for preferences (need implementation)
- ⚠️ Dynamic creation workflow not documented (this document addresses it)

---

**Document Status**: ✅ Complete
**Last Updated**: 2026-01-04
**Next Steps**:
1. Cleanup COMPREHENSIVE_SETTINGS_SPEC.md (remove unused settings)
2. Update system prompt with dynamic creation guidance
3. Audit directives for missing preference checks
