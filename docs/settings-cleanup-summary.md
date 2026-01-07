# Settings Cleanup Summary and Next Steps

**Date**: 2026-01-04
**Status**: ✅ Phase 1 Complete - Cleanup and Baseline Established

---

## What Changed

### Files Deleted
- ❌ **docs/COMPREHENSIVE_SETTINGS_SPEC.md** - Removed (92+ settings, mostly invalid/unused)

### Files Updated
- ✅ **docs/settings-specification.json** - Complete rewrite (v3.0)
  - **Before**: 92+ settings (speculative, unused)
  - **After**: 18 settings (validated, actually used in directives)

### Files Created
- ✅ **docs/settings-analysis-report.md** - Detailed analysis of valid vs invalid settings
- ✅ **docs/settings-directive-reference.md** - Complete reference with file locations
- ✅ **docs/settings-design-integration.md** - Design specification and integration strategy

---

## Why This Changed

### Original Problem
1. **Too many settings** - 92+ settings were documented, most never used
2. **Speculative design** - Settings created "in case they might be useful"
3. **Drift from reality** - Settings didn't match actual directive implementations
4. **Invalid settings** - Some tried to override locked schema values (e.g., `task_granularity_default`)
5. **Unclear validity** - No way to know which settings were real vs made-up

### Core Issues Identified
1. **74+ unused settings** - Documented but never referenced in directive workflows
2. **Schema conflicts** - Settings trying to change database-locked values
3. **Missing integration** - Settings existed but directives didn't check for them
4. **Static approach** - Pre-creating settings instead of dynamic, user-driven creation

---

## New Baseline: 18 Valid Settings

### Global User Settings (3)
1. **fp_strictness_level** - FP enforcement level (relaxed/standard/strict)
2. **prefer_explicit_returns** - Always use explicit return statements
3. **suppress_warnings** - Suppress warnings from specific directives

### Directive Preferences (11)

#### project_file_write (5)
1. **always_add_docstrings** - Auto-add docstrings to functions
2. **max_function_length** - Warn if function exceeds N lines
3. **prefer_guard_clauses** - Use guard clauses vs nested ifs
4. **code_style** - Overall code style (compact/verbose/explicit)
5. **indent_style** - Indentation (spaces_2/spaces_4/tabs)

#### project_task_decomposition (4)
1. **task_granularity** - Task breakdown detail (fine/medium/coarse)
2. **naming_convention** - Task naming style (descriptive/short/numbered)
3. **auto_create_items** - Auto-create items for tasks
4. **default_priority** - Default task priority (1-5)

#### project_compliance_check (3)
1. **auto_fix_violations** - Auto-refactor FP violations
2. **skip_warnings** - Skip non-critical warnings
3. **strict_mode** - Zero-tolerance FP enforcement

### Tracking Features (4)
1. **fp_flow_tracking** - Track FP directive usage
2. **ai_interaction_log** - Log corrections for learning
3. **helper_function_logging** - Log helper execution
4. **issue_reports** - Enable bug reports

---

## Design Philosophy (Confirmed)

Your vision for settings is now the documented standard:

1. **Dynamic, User-Driven** - Settings created when users express preferences, not pre-defined
2. **Directive-Specific** - Settings modify specific directive behavior
3. **Runtime Integration** - Settings loaded before directive execution via `user_preferences_sync`
4. **Minimal by Default** - Start with 18, add as needed based on user interaction
5. **Validation Required** - New settings must be integrated into directive workflows before being documented

---

## Next Steps

### Phase 1: ✅ COMPLETE
- [x] Analyze all directive files for settings mentions
- [x] Identify valid vs invalid settings
- [x] Delete COMPREHENSIVE_SETTINGS_SPEC.md
- [x] Rewrite settings-specification.json with clean baseline
- [x] Document design philosophy and integration strategy

### Phase 2: ✅ COMPLETE - Settings Evaluation
**Objective**: Review settings for relevance given FP directive changes

**Completed in settings-specification.json v3.1 (2026-01-04)**

#### Decisions Made

**Removed Settings (FP now baseline in system prompt)**:
1. ✅ **fp_strictness_level** - Removed (FP enforcement is now mandatory baseline behavior)
2. ✅ **prefer_explicit_returns** - Removed (redundant with system prompt FP rules)
3. ✅ **project_compliance_check.auto_fix_violations** - Removed (directive repurposed as tracking-only)
4. ✅ **project_compliance_check.skip_warnings** - Removed (directive repurposed as tracking-only)
5. ✅ **project_compliance_check.strict_mode** - Removed (directive repurposed as tracking-only)

**Added Settings**:
1. ✅ **project_continue_on_start** - Added (autostart feature from system prompt requirements)

**Kept Settings (Still Valid)**:
1. ✅ **project_file_write preferences (5)** - Code style preferences orthogonal to FP compliance
2. ✅ **project_task_decomposition preferences (3)** - Task management preferences still relevant
3. ✅ **suppress_warnings** - Generic warning suppression still useful
4. ✅ **tracking features (4)** - Opt-in tracking still valid (includes project_compliance_check as tracking feature)

**Result**: Reduced from 18 settings → 12 settings

#### Key Architectural Decision: project_compliance_check
- **Decision**: Repurpose as **opt-in tracking/analytics feature** (not mandatory validation)
- **Rationale**: FP is baseline behavior (system prompt), not something checked after the fact
- **New Purpose**: Optional analytics for tracking FP compliance patterns over time
- **Activation**: Only when `tracking_settings.compliance_checking = enabled`
- **Cost Warning**: Users warned about token overhead before enabling

### Phase 3: Directive Workflow Audit ✅ COMPLETE
**Objective**: Ensure directives actually check for their settings

**Tasks**:
1. ✅ Audit each directive workflow for preference-checking logic
2. ✅ Verify preference checks exist where documented
3. ✅ Confirm settings match directive implementations
4. ✅ Document which directives are "customizable" vs "fixed"

**Directives Audited**:
- [x] project_file_write - ✅ Checks all 5 preferences (lines 603-649 in directives-project.json)
- [x] project_task_decomposition - ✅ Checks all preferences (lines 403-499 in directives-project.json)
- [x] project_compliance_check - ✅ No preferences (tracking-only, lines 877-949)

**Findings**:
- All documented preferences ARE checked in directive workflows
- project_file_write: trunk="check_user_preferences", loads 5 preferences
- project_task_decomposition: trunk="check_user_preferences", loads 4 preferences
- project_compliance_check: Correctly updated to tracking-only (no preferences)

### Phase 4: System Prompt Update ✅ COMPLETE
**Objective**: Guide AI on dynamic setting creation

**Tasks**:
1. ✅ Add settings guidance to system prompt (lines 488-507)
2. ✅ Explain when to create new settings (dynamic creation workflow)
3. ✅ Document user_preferences_update workflow (5-step process)
4. ✅ Add examples of dynamic creation ("Always add docstrings", etc.)

**Updates Made**:
- sys-prompt/aifp_system_prompt.txt: Expanded USER PREFERENCES section with dynamic creation workflow
- helpers-core.json: Added implementation notes to get_directive_by_name and get_directive_content about loading preferences
- settings-specification.json: Fixed outdated note about project_compliance_check (line 305)

### Phase 5: Documentation Update ⏳ PENDING
**Objective**: Update all references to settings

**Tasks**:
1. Update directive MD files with current settings
2. Update helper function documentation
3. Update user preference directive documentation
4. Remove references to deleted settings

---

## Settings Evaluation Framework

### For Each Setting, Ask:

#### 1. Relevance (Is it still needed?)
- **Given FP in system prompt**: Does this setting still control behavior?
- **Given current architecture**: Is this setting's purpose still valid?
- **User value**: Does this setting provide value to users?

#### 2. Implementation (Does it work?)
- **Directive checks**: Does the target directive actually check this setting?
- **Behavior modification**: Does changing this setting change behavior?
- **Testing**: Has this setting been tested?

#### 3. Documentation (Is it clear?)
- **Purpose**: Is it clear what this setting does?
- **Usage**: Is it clear when/how to use this setting?
- **Examples**: Are there examples of this setting in action?

#### 4. Future (Should we keep it?)
- **Keep**: Still relevant, implemented, documented
- **Remove**: Obsolete, unused, or redundant with system prompt
- **Modify**: Relevant but needs adjustment
- **Defer**: Unsure, need more context

---

## Phase 2 Resolution Summary

### 1. FP Compliance Settings - ✅ RESOLVED
**Previous State**: 4 settings related to FP compliance
- `fp_strictness_level` (global)
- `auto_fix_violations` (project_compliance_check)
- `skip_warnings` (project_compliance_check)
- `strict_mode` (project_compliance_check)

**Decision**: **Remove all 4 settings** - FP is baseline behavior (system prompt)

**Implementation**: Completed in v3.1 (2026-01-04)

**Impact**: project_compliance_check directive repurposed as opt-in tracking feature

---

### 2. Code Style Settings - ✅ KEPT
**Current State**: 5 settings for code generation style (project_file_write)

**Assessment**: ✅ Still valid
- Code style preferences are separate from FP compliance
- Users may want different indentation, naming, docstring styles
- These don't conflict with FP rules (FP is about purity, not formatting)

**Decision**: Keep all 5 settings

---

### 3. Task Management Settings - ✅ KEPT (3 settings)
**Current State**: 3 settings for task decomposition (was 4, removed task_granularity)

**Assessment**: ✅ Still valid
- Task management is separate from FP compliance
- Users may want different task breakdown styles
- These control project management, not code quality

**Decision**: Keep 3 settings (removed task_granularity - tried to override schema)

---

### 4. Tracking Settings - ✅ KEPT + ENHANCED
**Current State**: 4 opt-in tracking features

**Assessment**: ✅ Still valid
- Tracking is independent of FP compliance changes
- Still useful for debugging and analytics
- Cost-conscious design (opt-in only)

**Enhancement**: Add compliance_checking as 5th tracking feature
- Enables project_compliance_check directive when activated
- Provides analytics on FP compliance patterns
- Token overhead warning shown to users before enabling

**Decision**: Keep 4 existing + add compliance_checking tracking

---

## Action Items

### ✅ Completed (2026-01-04)
1. ✅ **FP compliance architecture clarified**
   - Decision: project_compliance_check repurposed as opt-in tracking
   - FP is baseline behavior (system prompt), not post-write validation
   - Compliance violations prevented by baseline, not detected after

2. ✅ **FP-related settings reviewed** (4 settings removed)
   - Removed: fp_strictness_level, prefer_explicit_returns
   - Removed: All 3 project_compliance_check preferences
   - Added: project_continue_on_start
   - Result: 18 settings → 12 settings

3. ✅ **Code style settings validated** (5 settings kept)
   - Confirmed: Still relevant and orthogonal to FP
   - Decision: Keep all 5 (always_add_docstrings, max_function_length, etc.)

### ⏳ In Progress (Current)
1. **Update settings-cleanup-summary.md** - Show Phase 2 complete
2. **Modify project_compliance_check directive** - Mark as tracking-only
3. **Add compliance_checking to tracking_settings** - 5th tracking feature
4. **Remove project_compliance_check from project/git directives**
5. **Update directive flows** - Make conditional on tracking enabled

### Short-term (Next 2 Weeks)
1. **Audit directive workflows**
   - Check which directives actually load preferences
   - Add preference-checking logic where missing
   - Remove settings if directives don't check them

2. **Update system prompt**
   - Add settings guidance
   - Explain dynamic creation workflow
   - Add examples

3. **Test setting creation**
   - Test dynamic creation workflow
   - Test setting application
   - Document edge cases

### Long-term (Next Month)
1. **Documentation update**
   - Update all directive documentation
   - Update helper function documentation
   - Create user guide for settings

2. **Setting lifecycle**
   - Document setting creation process
   - Document setting deprecation process
   - Create setting audit checklist

---

## Summary

**What We Have Now**: Clean baseline of 12 validated settings (reduced from 18)

**Phase 1 Complete**: Settings cleanup and documentation
**Phase 2 Complete**: Settings evaluation and FP baseline alignment
**Phase 3 Complete**: Directive workflow audit and verification
**Phase 4 Complete**: System prompt and helper implementation notes

**Key Decisions Made**:
1. ✅ FP compliance settings removed (FP is baseline, not optional)
2. ✅ project_compliance_check repurposed as opt-in tracking feature
3. ✅ Code style and task management settings kept (orthogonal to FP)
4. ✅ project_continue_on_start added for autostart functionality
5. ✅ All directive workflows verified to check their documented preferences
6. ✅ System prompt updated with dynamic settings creation workflow
7. ✅ Helper implementation notes added for preference loading

**Next Phase**: Documentation cleanup (Phase 5)

---

**Status**: ✅ Phases 1-4 Complete, ⏳ Phase 5 Pending
**Last Updated**: 2026-01-06
**Owner**: User + AI collaboration
