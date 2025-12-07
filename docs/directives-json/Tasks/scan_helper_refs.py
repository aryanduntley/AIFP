#!/usr/bin/env python3
"""
Scan directive JSON files for helper references that need to be removed.

This script identifies all helper-related fields in directive JSON files:
- "helper" fields (exact match)
- "helper_*" variant fields (helper_project_db, helper_prefs_db, etc.)
- "call_helper" fields
- "helper_functions" sections

Output: JSON report of all findings by file and directive.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def find_helper_refs_recursive(obj: Any, path: str = "", findings: List[Dict] = None) -> List[Dict]:
    """
    Recursively search for helper reference fields in JSON object.

    Args:
        obj: JSON object (dict, list, or primitive)
        path: Current JSON path (e.g., "directives[0].workflow[2].details")
        findings: Accumulated findings list

    Returns:
        List of dicts with: {path, field_name, field_value, context}
    """
    if findings is None:
        findings = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # Check if this is a helper reference field
            if key == "helper" or key.startswith("helper_") or key == "call_helper":
                findings.append({
                    "path": current_path,
                    "field_name": key,
                    "field_value": value,
                    "context": obj  # Store surrounding context
                })

            # Recurse into nested structures
            find_helper_refs_recursive(value, current_path, findings)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            find_helper_refs_recursive(item, current_path, findings)

    return findings


def scan_directive_file(file_path: Path) -> Dict[str, Any]:
    """
    Scan a single directive JSON file for helper references.

    Returns:
        Dict with file metadata and findings
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        findings = find_helper_refs_recursive(data)

        # Group findings by directive name
        by_directive = defaultdict(list)
        for finding in findings:
            # Extract directive name from path
            # Example path: "directives[0].workflow[2].details.helper"
            if "directives[" in finding["path"]:
                parts = finding["path"].split(".")
                directive_idx = None
                for part in parts:
                    if part.startswith("directives["):
                        directive_idx = int(part.split("[")[1].split("]")[0])
                        break

                if directive_idx is not None and "directives" in data:
                    directive_name = data["directives"][directive_idx].get("name", f"directive_{directive_idx}")
                    by_directive[directive_name].append(finding)
            else:
                # Top-level helper_functions field
                by_directive["_file_level_"].append(finding)

        return {
            "file": str(file_path.name),
            "total_findings": len(findings),
            "by_directive": dict(by_directive),
            "status": "success"
        }

    except Exception as e:
        return {
            "file": str(file_path.name),
            "error": str(e),
            "status": "error"
        }


def generate_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary report from scan results."""
    total_findings = sum(r.get("total_findings", 0) for r in results)
    files_with_issues = [r for r in results if r.get("total_findings", 0) > 0]

    # Count by field name
    field_counts = defaultdict(int)
    for result in results:
        for directive_findings in result.get("by_directive", {}).values():
            for finding in directive_findings:
                field_counts[finding["field_name"]] += 1

    return {
        "summary": {
            "total_files_scanned": len(results),
            "files_with_helper_refs": len(files_with_issues),
            "total_helper_refs_found": total_findings,
            "by_field_name": dict(field_counts)
        },
        "files": results
    }


def print_summary(report: Dict[str, Any]):
    """Print human-readable summary to console."""
    summary = report["summary"]

    print("\n" + "="*70)
    print("DIRECTIVE HELPER REFERENCE SCAN REPORT")
    print("="*70)

    print(f"\n📊 SUMMARY:")
    print(f"   Total files scanned: {summary['total_files_scanned']}")
    print(f"   Files with helper refs: {summary['files_with_helper_refs']}")
    print(f"   Total helper refs found: {summary['total_helper_refs_found']}")

    if summary['by_field_name']:
        print(f"\n📋 BY FIELD NAME:")
        for field_name, count in sorted(summary['by_field_name'].items(), key=lambda x: -x[1]):
            print(f"   {field_name:25s} : {count:3d} occurrences")

    print(f"\n📁 FILES WITH ISSUES:")
    for result in report["files"]:
        if result.get("total_findings", 0) > 0:
            print(f"\n   {result['file']} ({result['total_findings']} refs)")

            for directive_name, findings in sorted(result["by_directive"].items()):
                print(f"      └─ {directive_name}: {len(findings)} refs")
                for finding in findings:
                    field_name = finding["field_name"]
                    value = finding["field_value"]
                    path = finding["path"]
                    print(f"         • {field_name} = \"{value}\"")
                    print(f"           at: {path}")

    print("\n" + "="*70)


def main():
    # Directory containing directive JSON files
    directives_dir = Path(__file__).parent.parent

    # Directive JSON files to scan
    directive_files = [
        "directives-project.json",
        "directives-fp-core.json",
        "directives-fp-aux.json",
        "directives-user-system.json",
        "directives-user-pref.json",
        "directives-git.json"
    ]

    print("🔍 Scanning directive JSON files for helper references...")
    print(f"📂 Directory: {directives_dir}")

    results = []
    for filename in directive_files:
        file_path = directives_dir / filename
        if file_path.exists():
            print(f"   Scanning: {filename}")
            result = scan_directive_file(file_path)
            results.append(result)
        else:
            print(f"   ⚠ Skipping: {filename} (not found)")
            results.append({
                "file": filename,
                "error": "File not found",
                "status": "error"
            })

    # Generate report
    report = generate_report(results)

    # Print summary to console
    print_summary(report)

    # Write detailed JSON report
    output_path = Path(__file__).parent / "helper_refs_scan_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report written to: {output_path}")
    print(f"\n✅ Scan complete!")


if __name__ == "__main__":
    main()
