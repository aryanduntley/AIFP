# FP Directive Update Guide

**Purpose**: Fix FP directives to correctly reference tracking_notes and clarify FP as baseline behavior

---

## What Needs Fixing

### 1. Database Operations Section

**OLD (Wrong)**:
```markdown
## Database Operations

- **`functions`**: Updates function metadata
- **`notes`**: Logs violations with `note_type = 'compliance'`
```

**Problems**:
- ❌ References project.db `notes` table
- ❌ Invalid note_type ('compliance' not in project.db schema)
- ❌ Implies automatic logging

**NEW (Correct)**:
```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: Updates function metadata with [specific details]

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.
```

---

### 2. Purpose Section

**Add this clarification**:
```markdown
**Important**: This directive is reference documentation for FP patterns.
AI consults this when uncertain about implementation details or complex edge cases.

**FP compliance is baseline behavior**:
- AI writes FP-compliant code naturally (enforced by system prompt)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes
```

---

### 3. When to Apply Section

**Add this clarification**:
```markdown
**When AI Consults This Directive**:
- Uncertainty about specific FP pattern implementation
- Complex edge case not covered by baseline knowledge
- Advanced scenario requiring detailed guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop
```

---

### 4. Workflow Section

**Review for validation implications**:

**BAD (implies validation loop)**:
```markdown
### Workflow
1. AI writes function
2. Check for violations ← WRONG!
3. Log to notes table ← WRONG!
```

**GOOD (consultation during writing)**:
```markdown
### Workflow

This is reference guidance consulted DURING code writing when needed.

**Consultation triggers**:
- AI uncertain about [specific FP pattern]
- Complex composition scenario
- Edge case not covered by baseline FP knowledge

**NOT a validation workflow** - FP compliance is enforced during writing by system prompt.
```

---

### 5. Remove Workflow References to notes

**Find and remove**:
- Lines like: "Log to notes table"
- Lines like: "Log uncertainty to notes"
- Lines like: "Log violation to notes"

These should either:
- Be removed entirely (most cases)
- Or changed to reference tracking_notes if truly needed for tracking

---

## Step-by-Step Update Process

For each FP directive:

1. **Find Database Operations section**
2. **Identify the note_type reference** (compliance, optimization, refactoring, etc.)
3. **Replace entire section** with new template
4. **Update directive name** in template (e.g., replace `fp_purity` with actual directive)
5. **Check Purpose section** - add FP baseline clarification if missing
6. **Check When to Apply section** - add consultation trigger clarification
7. **Review Workflow section** - remove validation implications
8. **Search for "notes" in file** - remove logging references in workflow steps

---

## Template for Database Operations

```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: [Keep existing function table operations]
- **`interactions`**: [Keep if directive uses this]
- **`types`**: [Keep if directive uses this]

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.

**Example** (only if tracking enabled):
```sql
-- user_preferences.db.tracking_notes
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity
) VALUES (
    '[Specific message for this directive]',
    'fp_analysis',
    'function',
    'function_name',
    '[this_directive_name]',
    'info'
);
```
```

---

## Priority Order

### Critical (Do First):
1. fp_purity.md - Most fundamental
2. fp_immutability.md - Core concept
3. fp_no_oop.md - Critical pattern
4. fp_result_types.md - Error handling
5. fp_optionals.md - Option type usage

### High Priority:
6-15. Common FP patterns (monadic composition, error pipeline, list operations, etc.)

### Medium Priority:
16-34. Specialized FP directives

---

## Verification Checklist

After updating each file:

- [ ] Database Operations section references `tracking_notes` (NOT `notes`)
- [ ] References `user_preferences.db` (NOT `project.db`)
- [ ] Uses `note_type='fp_analysis'` (NOT compliance/optimization/refactoring)
- [ ] Mentions tracking is opt-in and disabled by default
- [ ] Purpose section clarifies FP is baseline behavior
- [ ] When to Apply section clarifies consultation triggers
- [ ] Workflow section doesn't imply post-write validation
- [ ] No "log to notes" references in workflow steps
- [ ] No invalid note_types anywhere in file

---

## Example: fp_immutability.md

### Before:
```markdown
## Database Operations

This directive updates the following tables:

- **`functions`**: Updates functions with immutability analysis results
- **`notes`**: Logs immutability violations with `note_type = 'compliance'`
```

### After:
```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: Updates function metadata with immutability analysis results

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.

**Example** (only if tracking enabled):
```sql
-- user_preferences.db.tracking_notes
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity,
    metadata_json
) VALUES (
    'Function refactored for immutability: eliminated in-place mutation',
    'fp_analysis',
    'function',
    'update_user',
    'fp_immutability',
    'info',
    '{"mutation_type": "in-place list modification", "refactored": true}'
);
```
```

---

**Ready to start updating FP directives manually with this guide.**
