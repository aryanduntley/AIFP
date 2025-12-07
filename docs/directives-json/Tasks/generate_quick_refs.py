#!/usr/bin/env python3
"""
Generate quick reference files for helpers and directives.

Creates two markdown files:
1. HELPER_FUNCTIONS_QUICK_REF.md - All helper functions with locations
2. DIRECTIVES_QUICK_REF.md - All directives with locations
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple


def extract_helpers_from_registry() -> List[Tuple[str, str, int]]:
    """
    Extract all helper function names from registry JSON files.

    Returns: List of (name, file, line_number) tuples
    """
    registry_dir = Path(__file__).parent.parent.parent / "helpers/registry"
    helpers = []

    # Get all registry JSON files
    registry_files = sorted(registry_dir.glob("helpers_registry_*.json"))

    for registry_file in registry_files:
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data = json.loads(''.join(lines))

            # Find each helper's line number by searching for "name" field
            if "helpers" in data:
                for helper in data["helpers"]:
                    name = helper.get("name")
                    if name:
                        # Find line number where this helper's name appears
                        line_num = None
                        for i, line in enumerate(lines, 1):
                            if f'"name": "{name}"' in line:
                                line_num = i
                                break

                        helpers.append((
                            name,
                            registry_file.name,
                            line_num if line_num else 0
                        ))

        except Exception as e:
            print(f"Error reading {registry_file.name}: {e}")

    return sorted(helpers, key=lambda x: x[0])  # Sort by name


def extract_directives_from_json() -> List[Tuple[str, str, int, str]]:
    """
    Extract all directive names from directive JSON files.

    Returns: List of (name, file, line_number, category) tuples
    """
    directives_dir = Path(__file__).parent.parent
    directives = []

    # Directive JSON files to process
    directive_files = [
        "directives-fp-core.json",
        "directives-fp-aux.json",
        "directives-project.json",
        "directives-user-pref.json",
        "directives-user-system.json",
        "directives-git.json"
    ]

    for filename in directive_files:
        file_path = directives_dir / filename
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data = json.loads(''.join(lines))

            # Extract category from filename
            category = filename.replace("directives-", "").replace(".json", "")

            # Directive JSON files are arrays at root level
            if isinstance(data, list):
                directive_list = data
            elif "directives" in data:
                directive_list = data["directives"]
            else:
                directive_list = []

            # Find each directive's line number
            for directive in directive_list:
                name = directive.get("name")
                if name:
                    # Find line number where this directive's name appears
                    line_num = None
                    for i, line in enumerate(lines, 1):
                        if f'"name": "{name}"' in line:
                            line_num = i
                            break

                    directives.append((
                        name,
                        filename,
                        line_num if line_num else 0,
                        category
                    ))

        except Exception as e:
            print(f"Error reading {filename}: {e}")

    return sorted(directives, key=lambda x: x[0])  # Sort by name


def generate_helper_quick_ref(helpers: List[Tuple[str, str, int]]) -> str:
    """Generate markdown content for helper functions quick reference."""

    content = """# Helper Functions Quick Reference

**Purpose**: Quick lookup for helper function names and locations
**Generated**: 2025-12-07
**Source**: `docs/helpers/registry/*.json`

---

## Usage

Use this reference when manually updating directive MD files to verify helper function names.

**Verify a helper exists**:
1. Search this file for the helper name
2. If found, helper exists in registry
3. If not found, helper may be removed or renamed (check CONSOLIDATION_REPORT.md)

---

## All Helper Functions

Total helpers documented: **{total}**

| Helper Name | Registry File | Line |
|-------------|---------------|------|
""".format(total=len(helpers))

    # Add table rows
    for name, file, line in helpers:
        content += f"| `{name}` | {file} | {line} |\n"

    content += """
---

## Quick Search Tips

**In VS Code / IDE**:
- Ctrl+F / Cmd+F: Search this file for helper name
- Double-click helper name to select, then Ctrl+F to find in registry

**Command line**:
```bash
# Find helper in registries
grep -n "helper_name" docs/helpers/registry/*.json

# Find usage in MD files
grep -r "helper_name" src/aifp/reference/directives/
```

---

## Related Files

- `DIRECTIVES_QUICK_REF.md` - Directive names and locations
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis of helper refs in MD files
- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - Helper changes (removed, renamed, consolidated)
- `docs/helpers/registry/CURRENT_STATUS.md` - Helper registry status

---

**Note**: If a helper mentioned in an MD file is NOT in this list, it may have been:
- Removed (AI directive-driven, like `parse_directive_file`)
- Consolidated (like `create_project_directory` → `initialize_aifp_project`)
- Renamed (check CONSOLIDATION_REPORT.md)
"""

    return content


def generate_directive_quick_ref(directives: List[Tuple[str, str, int, str]]) -> str:
    """Generate markdown content for directives quick reference."""

    # Group by category
    by_category = {}
    for name, file, line, category in directives:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((name, file, line))

    content = """# Directives Quick Reference

**Purpose**: Quick lookup for directive names and locations
**Generated**: 2025-12-07
**Source**: `docs/directives-json/*.json`

---

## Usage

Use this reference when updating directive MD files to cross-reference directive definitions.

**Find a directive definition**:
1. Search this file for the directive name
2. Open the JSON file listed
3. Jump to the line number for the definition

---

## All Directives

Total directives: **{total}**

""".format(total=len(directives))

    # Add sections by category
    category_names = {
        "fp-core": "FP Core Directives",
        "fp-aux": "FP Auxiliary Directives",
        "project": "Project Management Directives",
        "user-pref": "User Preference Directives",
        "user-system": "User Directive System",
        "git": "Git Integration Directives"
    }

    for category in sorted(by_category.keys()):
        category_directives = by_category[category]
        category_title = category_names.get(category, category.upper())

        content += f"### {category_title}\n\n"
        content += f"**Count**: {len(category_directives)}\n\n"
        content += "| Directive Name | JSON File | Line |\n"
        content += "|----------------|-----------|------|\n"

        for name, file, line in sorted(category_directives):
            content += f"| `{name}` | {file} | {line} |\n"

        content += "\n"

    content += """---

## Quick Search Tips

**In VS Code / IDE**:
- Ctrl+F / Cmd+F: Search this file for directive name
- Double-click directive name to select, then Ctrl+F to find in JSON

**Command line**:
```bash
# Find directive definition
grep -n "directive_name" docs/directives-json/*.json

# Find corresponding MD file
ls src/aifp/reference/directives/directive_name.md

# Search MD file content
grep -n "pattern" src/aifp/reference/directives/directive_name.md
```

---

## Related Files

- `HELPER_FUNCTIONS_QUICK_REF.md` - Helper function names and locations
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis of helper refs in MD files
- `DIRECTIVE_CLEANUP_TASK.md` - Overall directive cleanup task

---

## Directive JSON → MD File Mapping

**JSON files** (dev staging): `docs/directives-json/*.json`
**MD files** (shipped with package): `src/aifp/reference/directives/*.md`

Each directive has:
- JSON definition (workflows, keywords, thresholds)
- MD documentation (purpose, examples, workflows, edge cases)

Both files should have matching directive names.
"""

    return content


def main():
    print("🔍 Extracting helper functions from registry...")
    helpers = extract_helpers_from_registry()
    print(f"   Found {len(helpers)} helpers")

    print("🔍 Extracting directives from JSON files...")
    directives = extract_directives_from_json()
    print(f"   Found {len(directives)} directives")

    # Generate helper quick ref
    output_dir = Path(__file__).parent
    helper_ref_path = output_dir / "HELPER_FUNCTIONS_QUICK_REF.md"

    print(f"\n📄 Writing helper quick reference...")
    helper_content = generate_helper_quick_ref(helpers)
    with open(helper_ref_path, 'w', encoding='utf-8') as f:
        f.write(helper_content)
    print(f"   ✅ Created: {helper_ref_path}")

    # Generate directive quick ref
    directive_ref_path = output_dir / "DIRECTIVES_QUICK_REF.md"

    print(f"\n📄 Writing directive quick reference...")
    directive_content = generate_directive_quick_ref(directives)
    with open(directive_ref_path, 'w', encoding='utf-8') as f:
        f.write(directive_content)
    print(f"   ✅ Created: {directive_ref_path}")

    print(f"\n✅ Quick reference files generated!")
    print(f"\n📋 Summary:")
    print(f"   Helpers: {len(helpers)}")
    print(f"   Directives: {len(directives)}")

    # Show breakdown by category
    print(f"\n📊 Directives by category:")
    by_cat = {}
    for _, _, _, cat in directives:
        by_cat[cat] = by_cat.get(cat, 0) + 1
    for cat, count in sorted(by_cat.items()):
        print(f"   {cat:15s}: {count:3d}")


if __name__ == "__main__":
    main()
