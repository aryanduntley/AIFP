#!/usr/bin/env python3
"""
Scan directive markdown files for helper references that need cleanup.

FOCUS: Replace hardcoded helper lists with database query instructions.

Identifies for REMOVAL:
1. Links to helper-functions-reference.md (outdated reference doc)
2. Hardcoded helper module paths (src/aifp/helpers/*.py)
3. "Referenced Helper Functions" sections with hardcoded lists
4. Specific helper function bullet lists

Identifies for REVIEW:
- Workflow instructions mentioning specific helpers (verify they exist)

Does NOT flag:
- Code examples with "helper" as variable names
- Generic descriptive mentions like "database helpers"
- Database query instructions (these are GOOD)

GOAL: Direct AI to query directive_helpers and helper_functions tables instead.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def scan_file_for_helper_refs(file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
    """
    Scan a single MD file for helper reference patterns.

    Returns dict with pattern types as keys and list of (line_num, line_content) tuples.
    """
    findings = {
        "helper_ref_links": [],      # Links to helper-functions-reference.md
        "helper_module_paths": [],   # Hardcoded module paths
        "helper_sections": [],       # Section headers about helpers
        "helper_function_lists": [], # Lists of specific helper functions
        "call_instructions": []      # "Call X helper" workflow instructions
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_code_block = False

        for line_num, line in enumerate(lines, 1):
            # Track code blocks to avoid false positives
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Pattern 1: Links to helper-functions-reference.md
            if re.search(r'\[Helper Functions Reference\]\([^)]*helper-functions-reference\.md[^)]*\)', line):
                findings["helper_ref_links"].append((line_num, line.strip()))

            # Pattern 2: Hardcoded helper module paths
            if not in_code_block and re.search(r'src/aifp/helpers/\w+\.py', line):
                findings["helper_module_paths"].append((line_num, line.strip()))

            # Pattern 3: Section headers about helpers
            if re.search(r'^#{1,4}\s+.*[Hh]elper [Ff]unctions?\s*$', line):
                findings["helper_sections"].append((line_num, line.strip()))

            # Pattern 4: Lists of specific helper functions (not in code blocks)
            if not in_code_block:
                # Look for bullet points with helper function names and descriptions
                if re.search(r'^\s*[-*]\s+`?\w+\(\).*helper', line, re.IGNORECASE):
                    findings["helper_function_lists"].append((line_num, line.strip()))

            # Pattern 5: "Call X helper" or "Use X helper" workflow instructions
            if not in_code_block and re.search(r'(Call|Use|Calls?|Uses?)\s+[`\w]+\s+helper', line):
                findings["call_instructions"].append((line_num, line.strip()))

        return findings

    except Exception as e:
        return {"error": [(0, str(e))]}


def generate_report(results: Dict[str, Dict]) -> Dict:
    """Generate summary report from scan results."""
    total_files = len(results)
    files_with_issues = sum(1 for findings in results.values()
                           if any(len(v) > 0 for k, v in findings.items() if k != "error"))

    # Count by pattern type
    pattern_counts = {
        "helper_ref_links": 0,
        "helper_module_paths": 0,
        "helper_sections": 0,
        "helper_function_lists": 0,
        "call_instructions": 0
    }

    for findings in results.values():
        for pattern_type, items in findings.items():
            if pattern_type in pattern_counts:
                pattern_counts[pattern_type] += len(items)

    return {
        "summary": {
            "total_files_scanned": total_files,
            "files_with_issues": files_with_issues,
            "total_issues": sum(pattern_counts.values()),
            "by_pattern_type": pattern_counts
        },
        "files": results
    }


def print_summary(report: Dict):
    """Print human-readable summary to console."""
    summary = report["summary"]

    print("\n" + "="*70)
    print("DIRECTIVE MARKDOWN HELPER REFERENCE SCAN")
    print("="*70)

    print(f"\n📊 SUMMARY:")
    print(f"   Files scanned: {summary['total_files_scanned']}")
    print(f"   Files with issues: {summary['files_with_issues']}")
    print(f"   Total issues found: {summary['total_issues']}")

    if summary['by_pattern_type']:
        print(f"\n📋 BY PATTERN TYPE:")
        pattern_names = {
            "helper_ref_links": "Links to helper-functions-reference.md",
            "helper_module_paths": "Hardcoded helper module paths",
            "helper_sections": "Helper function section headers",
            "helper_function_lists": "Helper function lists",
            "call_instructions": "Helper call instructions"
        }

        for pattern_type, count in sorted(summary['by_pattern_type'].items(),
                                         key=lambda x: -x[1]):
            if count > 0:
                name = pattern_names.get(pattern_type, pattern_type)
                print(f"   {name:45s} : {count:3d}")

    print(f"\n📁 FILES WITH ISSUES:")

    # Sort files by total issue count
    file_issues = []
    for filename, findings in report["files"].items():
        total = sum(len(v) for k, v in findings.items() if k != "error")
        if total > 0:
            file_issues.append((filename, total, findings))

    file_issues.sort(key=lambda x: -x[1])

    for filename, total, findings in file_issues[:20]:  # Show top 20
        print(f"\n   {filename} ({total} issues)")

        for pattern_type, items in findings.items():
            if items and pattern_type != "error":
                pattern_names = {
                    "helper_ref_links": "Helper ref links",
                    "helper_module_paths": "Module paths",
                    "helper_sections": "Section headers",
                    "helper_function_lists": "Function lists",
                    "call_instructions": "Call instructions"
                }
                name = pattern_names.get(pattern_type, pattern_type)
                print(f"      {name}: {len(items)}")

                # Show first 2 examples
                for line_num, line_content in items[:2]:
                    truncated = line_content[:80] + "..." if len(line_content) > 80 else line_content
                    print(f"         L{line_num}: {truncated}")

    if len(file_issues) > 20:
        print(f"\n   ... and {len(file_issues) - 20} more files")

    print("\n" + "="*70)


def main():
    # Directory containing directive MD files
    directives_dir = Path(__file__).parent.parent.parent.parent / "src/aifp/reference/directives"

    if not directives_dir.exists():
        print(f"❌ Directives directory not found: {directives_dir}")
        return

    print(f"🔍 Scanning directive markdown files...")
    print(f"📂 Directory: {directives_dir}")

    # Scan all MD files
    md_files = list(directives_dir.glob("*.md"))
    print(f"📄 Found {len(md_files)} markdown files")

    results = {}
    for md_file in md_files:
        findings = scan_file_for_helper_refs(md_file)
        if findings:
            results[md_file.name] = findings

    # Generate and print report
    report = generate_report(results)
    print_summary(report)

    # Save detailed report
    import json
    output_path = Path(__file__).parent / "md_helper_refs_scan_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {output_path}")
    print(f"✅ Scan complete!")


if __name__ == "__main__":
    main()
