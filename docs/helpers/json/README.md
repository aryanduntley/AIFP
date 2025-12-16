# Helper Functions JSON Files

**Purpose**: Complete helper function definitions with all database fields for import into aifp_core.db

**Status**: Empty templates - ready for mapping

---

## File Structure

### Estimation Basis
- Each helper averages 40-50 lines in JSON format
- Target: <900 lines per file
- Total helpers: ~227

### Files Created

**Core Helpers** (33 total, ~1,320 lines → 2 files):
- `helpers-core-1.json` (1-20 helpers, ~800 lines)
- `helpers-core-2.json` (21-33 helpers, ~520 lines)

**Git Helpers** (11 total, ~440 lines → 1 file):
- `helpers-git.json`

**Orchestrator Helpers** (estimated 24 total, ~1,440 lines → 2 files):
- `helpers-orchestrators-1.json` (1-15 helpers, ~900 lines)
- `helpers-orchestrators-2.json` (16-24 helpers, ~540 lines)

**Project Helpers** (117 total, ~4,680 lines → 6 files):
- `helpers-project-1.json` (1-20 helpers, ~800 lines)
- `helpers-project-2.json` (21-40 helpers, ~800 lines)
- `helpers-project-3.json` (41-60 helpers, ~800 lines)
- `helpers-project-4.json` (61-80 helpers, ~800 lines)
- `helpers-project-5.json` (81-100 helpers, ~800 lines)
- `helpers-project-6.json` (101-117 helpers, ~680 lines)

**Settings Helpers** (17 total, ~680 lines → 1 file):
- `helpers-settings.json`

**User Custom Helpers** (16 total, ~640 lines → 1 file):
- `helpers-user-custom.json`

**Total**: 14 JSON files

---

## JSON Structure Template

Each file contains an array of helper objects:

```json
{
  "helpers": [
    {
      "name": "helper_function_name",
      "file_path": "helpers/database/module.py",
      "parameters": [
        {
          "name": "param_name",
          "type": "string|integer|boolean|array|object",
          "required": true,
          "default": null,
          "description": "Parameter description"
        }
      ],
      "purpose": "Brief description of what this helper does",
      "error_handling": "How errors are handled (returns null, raises exception, etc.)",
      "is_tool": true,
      "is_sub_helper": false,
      "return_statements": [
        "AI guidance statement 1",
        "AI guidance statement 2"
      ],
      "target_database": "core|project|settings|user_custom|orchestrator",
      "used_by_directives": [
        {
          "directive_name": "directive_name",
          "execution_context": "context_description",
          "sequence_order": 1,
          "is_required": true,
          "parameters_mapping": {},
          "description": "Why this directive uses this helper"
        }
      ]
    }
  ]
}
```

---

## Mapping Progress

Track progress in:
- `docs/directives-json/Tasks/HELPER_MAPPING_PROGRESS.md`

---

## Import Strategy

After all files are complete:
1. Modify `docs/directives-json/sync-directives.py`
2. Import all helpers into `helper_functions` table
3. Populate `directive_helpers` junction table from `used_by_directives` arrays

---

**Created**: 2025-12-16
**Last Updated**: 2025-12-16
