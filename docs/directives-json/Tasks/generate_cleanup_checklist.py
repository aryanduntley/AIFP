#!/usr/bin/env python3
"""
Generate a progress tracking checklist for MD file cleanup.

Creates MD_CLEANUP_CHECKLIST.md with:
- Checkboxes for each file needing review
- Sub-checkboxes for specific issues found
- Priority ordering (high-priority files first)
"""

import json
from pathlib import Path
from typing import Dict, List


def load_scan_report() -> Dict:
    """Load the scan report JSON."""
    report_path = Path(__file__).parent / "md_helper_refs_scan_report.json"
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_priority(filename: str, findings: Dict) -> int:
    """
    Calculate priority score for a file (higher = more urgent).

    Priority factors:
    - High-priority files (project_init, user_directive_*, aifp_help): +100
    - Number of issues: +10 per issue
    - Module paths: +5 per path (high impact)
    """
    score = 0

    # High-priority files
    high_priority = [
        "project_init.md",
        "user_directive_parse.md",
        "user_directive_validate.md",
        "aifp_help.md",
        "user_preferences_update.md",
        "aifp_run.md",
        "aifp_status.md"
    ]

    if filename in high_priority:
        score += 100

    # Count issues
    total_issues = sum(len(items) for key, items in findings.items() if key != "error")
    score += total_issues * 10

    # Module paths are high impact
    if "helper_module_paths" in findings:
        score += len(findings["helper_module_paths"]) * 5

    return score


def generate_checklist(report: Dict) -> str:
    """Generate markdown checklist content."""

    # Get files with issues
    files_with_issues = []
    for filename, findings in report["files"].items():
        total = sum(len(v) for k, v in findings.items() if k != "error")
        if total > 0:
            priority = calculate_priority(filename, findings)
            files_with_issues.append((filename, findings, total, priority))

    # Sort by priority (high to low)
    files_with_issues.sort(key=lambda x: -x[3])

    content = """# Directive MD Files - Cleanup Progress Checklist

**Created**: 2025-12-07
**Purpose**: Track manual cleanup progress for 94 directive markdown files
**Total Files**: {total}
**Status**: ⏳ In Progress

---

## Progress Summary

- [ ] **Phase 1**: High-Priority Files (7 files)
- [ ] **Phase 2**: Files with Module Paths (4 files)
- [ ] **Phase 3**: Files with Multiple Issues (15+ files)
- [ ] **Phase 4**: Remaining Files (~70 files)

**Completion**: 0 / {total} files complete

---

## How to Use This Checklist

1. **Pick a file** from the list below (high-priority first)
2. **Review** the file using:
   - `MD_HELPER_REFS_ANALYSIS.md` - Replacement templates
   - `HELPER_FUNCTIONS_QUICK_REF.md` - Verify helper names
   - `DIRECTIVES_QUICK_REF.md` - Cross-reference directives
3. **Check off sub-items** as you fix each issue
4. **Check off main item** when file review is complete
5. **Update completion count** at top when done

---

## Issue Type Key

- 🔗 **Helper Ref Link** - Link to `helper-functions-reference.md` (REMOVE)
- 📂 **Module Path** - Hardcoded `src/aifp/helpers/*.py` path (REMOVE)
- 📋 **Section Header** - "## Helper Functions" section (REPLACE with DB guidance)
- 📝 **Function List** - Hardcoded helper function list (VERIFY & UPDATE)
- ⚙️ **Call Instruction** - Workflow mentions specific helper (VERIFY helper exists)

---

## High-Priority Files (Phase 1)

These files are core directives or heavily affected by helper changes.

""".format(total=len(files_with_issues))

    # Track which phase we're in
    phase_thresholds = {
        "high_priority": 90,  # Priority score >= 90
        "module_paths": 50,    # Has module paths
        "multiple_issues": 20, # 2+ issues
        "remaining": 0         # Everything else
    }

    current_phase = "high_priority"
    phase_headers = {
        "module_paths": "\n---\n\n## Files with Module Paths (Phase 2)\n\nThese expose implementation details that should be removed.\n\n",
        "multiple_issues": "\n---\n\n## Files with Multiple Issues (Phase 3)\n\nThese have 2+ issues requiring careful review.\n\n",
        "remaining": "\n---\n\n## Remaining Files (Phase 4)\n\nSingle-issue files (mostly helper ref links).\n\n"
    }

    for filename, findings, total, priority in files_with_issues:
        # Check if we need to start a new phase
        if current_phase == "high_priority" and priority < 90:
            if "helper_module_paths" in findings and len(findings["helper_module_paths"]) > 0:
                content += phase_headers["module_paths"]
                current_phase = "module_paths"
            elif total >= 2:
                content += phase_headers["multiple_issues"]
                current_phase = "multiple_issues"
            else:
                content += phase_headers["remaining"]
                current_phase = "remaining"
        elif current_phase == "module_paths" and "helper_module_paths" not in findings:
            if total >= 2:
                content += phase_headers["multiple_issues"]
                current_phase = "multiple_issues"
            else:
                content += phase_headers["remaining"]
                current_phase = "remaining"
        elif current_phase == "multiple_issues" and total < 2:
            content += phase_headers["remaining"]
            current_phase = "remaining"

        # File header with priority indicator
        priority_indicator = ""
        if priority >= 100:
            priority_indicator = " 🔴 **HIGH PRIORITY**"
        elif priority >= 50:
            priority_indicator = " 🟡 **MEDIUM PRIORITY**"

        content += f"\n### [ ] {filename}{priority_indicator}\n\n"
        content += f"**Issues**: {total} | **Priority Score**: {priority}\n\n"

        # Add sub-checkboxes for each issue type
        issue_types = {
            "helper_ref_links": "🔗 Helper Ref Links",
            "helper_module_paths": "📂 Module Paths",
            "helper_sections": "📋 Section Headers",
            "helper_function_lists": "📝 Function Lists",
            "call_instructions": "⚙️ Call Instructions"
        }

        for issue_key, issue_label in issue_types.items():
            if issue_key in findings and len(findings[issue_key]) > 0:
                items = findings[issue_key]
                content += f"- [ ] **{issue_label}** ({len(items)} found)\n"

                # Show first 3 instances with line numbers
                for line_num, line_content in items[:3]:
                    truncated = line_content[:70] + "..." if len(line_content) > 70 else line_content
                    content += f"  - Line {line_num}: `{truncated}`\n"

                if len(items) > 3:
                    content += f"  - _(+ {len(items) - 3} more)_\n"

        content += "\n"

    # Add footer with resources
    content += """---

## Resources

**Analysis & Templates**:
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis with replacement templates
- `DIRECTIVE_CLEANUP_TASK.md` - Overall cleanup task doc

**Quick References**:
- `HELPER_FUNCTIONS_QUICK_REF.md` - All 337 helpers with locations
- `DIRECTIVES_QUICK_REF.md` - All 125 directives with locations

**Helper Registry** (verify removals/changes):
- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - What changed
- `docs/helpers/registry/CURRENT_STATUS.md` - Registry overview

---

## Standard Replacement Templates

### Template 1: Remove Helper Ref Link
Simply delete the line:
```markdown
- [Helper Functions Reference](../../../docs/helper-functions-reference.md#section)
```

### Template 2: Replace Helper Section
Replace:
```markdown
## Helper Functions

- `helper_name()` - Description
```

With:
```markdown
## Helper Functions

This directive's helpers are dynamically mapped in `aifp_core.db`.

Query at runtime:
\```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
\```
```

### Template 3: Remove Module Path
Remove the Module line, keep other details:
```markdown
**Helper Function**:
- **Name**: `function_name`
- **Module**: `src/aifp/helpers/module.py`  ← DELETE THIS
- **Parameters**: ...  ← KEEP THIS
```

---

## Completion Tracking

Update this section as you progress:

**By Phase**:
- [ ] Phase 1 Complete: 0 / 7 high-priority files
- [ ] Phase 2 Complete: 0 / 4 module path files
- [ ] Phase 3 Complete: 0 / ~15 multi-issue files
- [ ] Phase 4 Complete: 0 / ~70 remaining files

**By Issue Type**:
- [ ] All helper ref links removed (71 total)
- [ ] All module paths removed (4 total)
- [ ] All section headers reviewed (23 total)
- [ ] All function lists verified (3 total)
- [ ] All call instructions verified (4 total)

**Final Steps**:
- [ ] Review 5 high-priority files end-to-end for accuracy
- [ ] Spot-check 10 random files for quality
- [ ] Update system prompt if needed
- [ ] Mark DIRECTIVE_CLEANUP_TASK.md as complete

---

**Last Updated**: 2025-12-07
**Status**: Ready for manual cleanup
"""

    return content


def main():
    print("📋 Generating cleanup checklist...")

    # Load scan report
    report = load_scan_report()
    print(f"   Loaded scan report")

    # Generate checklist
    checklist = generate_checklist(report)

    # Write to file
    output_path = Path(__file__).parent / "MD_CLEANUP_CHECKLIST.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(checklist)

    print(f"\n✅ Checklist created: {output_path}")
    print(f"\n📊 Summary:")

    files_with_issues = sum(1 for findings in report["files"].values()
                           if sum(len(v) for k, v in findings.items() if k != "error") > 0)

    print(f"   Total files to review: {files_with_issues}")
    print(f"   High-priority files: ~7")
    print(f"   Total issues: {report['summary']['total_issues']}")

    print(f"\n💡 Next step: Open {output_path} and start with Phase 1 (high-priority files)")


if __name__ == "__main__":
    main()
