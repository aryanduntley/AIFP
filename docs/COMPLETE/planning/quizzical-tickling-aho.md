# Plan: Initialize AIFP Project Helper & OOP Handling Strategy

## Context

From verification of 27 "likely exists" helpers, we need to:
1. Create unified `initialize_aifp_project()` helper function
2. Decide OOP handling strategy for existing non-FP projects
3. Resolve 3 ambiguous helpers (validate_initialization, infer_architecture, query_mcp_db)

## Current State Analysis

### Existing Directive Capabilities (from project_init.md)

**Already Handles Existing Projects:**
- Lines 394-421: "Converting Existing Project" example
- Scans existing codebase
- Detects language and files
- Prompts: "Import existing code into AIFP tracking?"
- Indexes existing files if user approves

**Referenced Helper Functions:**
- `scan_existing_files(project_root)` - Returns structure map
- `infer_architecture(project_root)` - Detects architectural style (MVC, microservices, monolithic)
- `detect_primary_language()` - Infers language from files
- `create_project_blueprint()` - Generates blueprint from analysis

**Gap Identified:** NO handling for OOP vs FP distinction during initialization

### Existing Compliance Framework (from project_compliance_check.md)

**Already Has OOP Handling Mechanisms:**
1. **Strictness Levels** (Lines 226-251):
   - `strict`: Zero tolerance, all FP rules enforced
   - `moderate`: Core FP (purity, immutability, no_oop), minor violations warned
   - `relaxed`: Critical FP only (no_oop), allows mutations in effect functions

2. **User-Approved Exceptions** (Lines 256-271):
   - Stored in `approved_exceptions` table
   - Per-file or per-function approval
   - Requires justification

3. **Auto-Fix Capabilities** (Lines 28-31):
   - `auto_fix_violations` preference
   - Escalates to FP directives for refactoring
   - Re-runs compliance after fixes

**Critical Insight:** This framework exists for POST-WRITE compliance but NOT for INITIALIZATION-TIME decisions.

## Recommended Approach

### 1. Unified `initialize_aifp_project()` Helper Design

**Function Signature:**
```python
def initialize_aifp_project(
    base_path: str,
    project_name: str,
    project_type: str,  # "new" | "existing"
    use_case: str = "development",  # "development" | "automation"
    **metadata  # Additional project metadata
) -> Result[InitStatus, InitError]
```

**Behavior - New Projects:**
1. Create `.aifp-project/` directory structure
2. Initialize all databases from schemas
3. Create blank ProjectBlueprint.md
4. Set `user_directives_status = NULL` (Use Case 1)
5. Return success → AI populates per directives

**Behavior - Existing Projects:**
1. Create `.aifp-project/` directory structure
2. Initialize all databases from schemas
3. **Scan and analyze existing code:**
   - Call `scan_existing_files(base_path)` → get file structure
   - Call `infer_architecture(base_path)` → detect patterns
   - Call `detect_primary_language()` → identify language
4. **Detect OOP vs FP:**
   - Scan for classes, inheritance, methods
   - Determine: `code_style = "oop" | "fp" | "mixed"`
5. **Route to OOP handler** if OOP detected
6. Return project analysis + initialization result

**Where to Add:** `helpers_registry_project_core.json`

### 2. OOP Handling Strategy (RECOMMENDATION)

**Leverage Existing Compliance Framework:**

Use the EXISTING strictness level system from `project_compliance_check`, but apply it UPFRONT during initialization:

#### Option A: Gradual Migration (RECOMMENDED)

**Why Recommended:**
- Leverages existing strictness/exception framework
- Practical for real-world codebases
- Allows iterative improvement
- Already has DB fields for tracking compliance

**Implementation:**
1. **At Initialization:**
   - Detect OOP code during `scan_existing_files()`
   - Set project-level `fp_compliance_mode = "migration"`
   - Set initial `fp_strictness_level = "relaxed"`
   - Track OOP files with `fp_readiness_level` field in `files` table

2. **Database Schema Addition:**
   ```sql
   -- Add to project table
   ALTER TABLE project ADD COLUMN fp_compliance_mode TEXT
     CHECK(fp_compliance_mode IN ('strict', 'migration', 'disabled'));

   -- Add to files table
   ALTER TABLE files ADD COLUMN fp_readiness_level INTEGER DEFAULT 0
     CHECK(fp_readiness_level BETWEEN 0 AND 5);
   -- 0 = OOP, 1 = Basic FP, 2 = Moderate FP, ... 5 = Full FP compliance
   ```

3. **Initial Tracking:**
   - Populate `files` table with existing OOP code
   - Mark each file with `fp_readiness_level = 0`
   - Set `oop_compliant = false` in `functions` table
   - Log in `notes`: "Project initialized with OOP codebase, migration mode enabled"

4. **Progressive Improvement:**
   - As AI refactors functions → increment `fp_readiness_level`
   - When file reaches level 5 → mark as FP-compliant
   - Compliance checks respect current readiness level
   - User can increase strictness over time

5. **ProjectBlueprint.md Documentation:**
   ```markdown
   ## FP Compliance Status
   - Mode: Migration (existing OOP codebase)
   - Strictness: Relaxed → will gradually increase
   - Files tracked: 45
   - FP-ready files: 0/45 (0%)
   - Migration strategy: Refactor incrementally as changes are made
   ```

#### Options B-D: Not Recommended (with rationale)

**Option B: Dual-Track** - Creates complexity, separate codebases hard to manage
**Option C: Reject Initialization** - Too restrictive, limits AIFP usefulness
**Option D: Relaxed Standards Only** - Defeats purpose of AIFP FP enforcement

### 3. Resolution of Ambiguous Helpers

#### validate_initialization
**Decision:** Directive-based, not helper function

**Rationale:**
- Validation requires AI reasoning (check multiple conditions, interpret results)
- Can use existing helpers: `get_project()`, file system checks
- Should be part of `project_init` directive workflow

**Action:** Add validation step to `project_init` directive (optional sanity check)

#### infer_architecture
**Decision:** KEEP as helper function (already referenced in project_init.md)

**Rationale:**
- Already called by `project_init` at lines 244, 494-496
- Returns architecture description for blueprint
- Useful for existing project analysis
- Code-based analysis more reliable than AI "thought"

**Action:** Add to `helpers_registry_project_structure_getters.json`

**Spec:**
```json
{
  "name": "infer_architecture",
  "purpose": "Analyze existing codebase to detect architectural patterns (MVC, microservices, monolithic, etc.)",
  "parameters": [{"name": "project_root", "type": "str", "required": true}],
  "return_statements": [
    "Returns architecture description string for ProjectBlueprint.md",
    "Detects patterns: MVC, microservices, monolithic, hexagonal, etc.",
    "Also detects OOP vs FP style"
  ],
  "is_tool": false,
  "is_sub_helper": false
}
```

#### query_mcp_db
**Decision:** REMOVE - not needed

**Rationale:**
- `aifp_core.db` is read-only
- All queries should go through specific helpers (enforces structure)
- Generic query bypasses helper/directive patterns
- AI can request new helpers if gaps found

**Action:** Mark as not needed in verification report

### 4. Implementation Steps

**Phase 1: Schema Updates**
1. Add `fp_compliance_mode` to `project` table
2. Add `fp_readiness_level` to `files` table
3. Update `schemaExampleProject.sql`

**Phase 2: Helper Function Creation**
1. Implement `initialize_aifp_project()` with OOP detection
2. Implement `infer_architecture()` (if not exists)
3. Update `scan_existing_files()` to detect OOP patterns
4. Add to `helpers_registry_project_core.json`

**Phase 3: Directive Updates**
1. Update `project_init` directive to use new helper
2. Add OOP handling workflow
3. Update `project_compliance_check` to respect `fp_compliance_mode`
4. Add migration guidance to ProjectBlueprint.md template

**Phase 4: Documentation**
1. Update VERIFICATION_REPORT.md with final decisions
2. Update CONSOLIDATION_REPORT.md with implementation status
3. Update helper-registry-guide.md with OOP strategy
4. Add migration workflow documentation

## Critical Files to Modify

1. `src/aifp/database/schemas/project.sql` - Add new fields
2. `docs/helpers/registry/helpers_registry_project_core.json` - Add init helper
3. `docs/helpers/registry/helpers_registry_project_structure_getters.json` - Add infer_architecture
4. `src/aifp/reference/directives/project_init.md` - Add OOP handling workflow
5. `src/aifp/reference/directives/project_compliance_check.md` - Document migration mode
6. `docs/helpers/registry/VERIFICATION_REPORT.md` - Final decisions
7. `docs/helpers/registry/CONSOLIDATION_REPORT.md` - Implementation status

## Key Benefits of This Approach

1. **Leverages Existing Infrastructure:** Uses compliance framework already built
2. **Practical:** Works with real-world OOP codebases
3. **Progressive:** Allows gradual improvement over time
4. **Trackable:** Clear metrics on migration progress
5. **Flexible:** User can adjust strictness as project improves
6. **Non-Breaking:** Doesn't force immediate refactoring
7. **Guided:** AI can suggest refactoring opportunities during normal work

## User Interaction Example

```
User: "Initialize AIFP for my existing Node.js project"

AI:
1. Scans codebase
2. Detects: 45 files, mostly OOP classes
3. Prompts: "Detected OOP codebase. Enable gradual FP migration mode?"
4. User: "Yes"
5. AI:
   - Creates .aifp-project/
   - Initializes databases
   - Sets fp_compliance_mode = "migration"
   - Sets fp_strictness_level = "relaxed"
   - Tracks all 45 files with readiness level 0
   - Generates blueprint with migration plan

Result: "Project initialized in migration mode. I'll gradually refactor OOP to FP as we work together. Current progress: 0/45 files FP-ready."
```

## Open Questions for User

None - this approach is self-contained and leverages existing architecture.

## Next Steps After Plan Approval

1. Implement schema changes
2. Create `initialize_aifp_project()` helper
3. Add `infer_architecture()` helper if missing
4. Update directives with OOP workflow
5. Update all verification/consolidation reports
6. Test initialization on sample OOP project
