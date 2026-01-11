#!/usr/bin/env python3
"""
Extract all helper functions from JSON files with source file and line numbers.
Outputs comprehensive list for implementation planning.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

def extract_helpers_from_json(json_path: Path) -> List[Tuple[str, str, Dict]]:
    """
    Extract helpers from a JSON file.

    Returns: List of (helper_name, source_file, helper_data)
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    helpers = []
    json_filename = json_path.name

    for helper in data.get('helpers', []):
        helper_name = helper.get('name', 'UNKNOWN')
        helpers.append((helper_name, json_filename, helper))

    return helpers

def categorize_helpers(all_helpers: List[Tuple[str, str, Dict]]) -> Dict[str, List[Tuple[str, str, Dict]]]:
    """
    Categorize helpers by their target database and functionality.

    Returns: Dict[category_name, List[(helper_name, source_file, helper_data)]]
    """
    categories = {
        'global': [],
        'core': [],
        'orchestrators': [],
        'project': [],
        'git': [],
        'user_preferences': [],
        'user_directives': []
    }

    for helper_name, source_file, helper_data in all_helpers:
        target_db = helper_data.get('target_database', 'unknown')

        if 'index' in source_file:
            categories['global'].append((helper_name, source_file, helper_data))
        elif 'orchestrator' in source_file:
            categories['orchestrators'].append((helper_name, source_file, helper_data))
        elif 'core' in source_file:
            categories['core'].append((helper_name, source_file, helper_data))
        elif 'git' in source_file:
            categories['git'].append((helper_name, source_file, helper_data))
        elif 'settings' in source_file:
            categories['user_preferences'].append((helper_name, source_file, helper_data))
        elif 'user-custom' in source_file:
            categories['user_directives'].append((helper_name, source_file, helper_data))
        elif 'project' in source_file:
            categories['project'].append((helper_name, source_file, helper_data))
        else:
            print(f"WARNING: Uncategorized helper: {helper_name} from {source_file}")

    return categories

def generate_markdown_output(categories: Dict[str, List[Tuple[str, str, Dict]]]) -> str:
    """Generate markdown output for all helpers."""

    output = []
    output.append("# Complete Helper Functions List")
    output.append("")
    output.append("**Total Helpers**: " + str(sum(len(helpers) for helpers in categories.values())))
    output.append("")
    output.append("---")
    output.append("")

    # Summary by category
    output.append("## Summary by Category")
    output.append("")
    for category, helpers in categories.items():
        output.append(f"- **{category}**: {len(helpers)} helpers")
    output.append("")
    output.append("---")
    output.append("")

    # Detailed listings
    category_order = ['global', 'core', 'orchestrators', 'project', 'git', 'user_preferences', 'user_directives']

    for category in category_order:
        helpers = categories[category]
        if not helpers:
            continue

        output.append(f"## {category.replace('_', ' ').title()} ({len(helpers)} helpers)")
        output.append("")

        # Group by source file
        by_file = {}
        for helper_name, source_file, helper_data in helpers:
            if source_file not in by_file:
                by_file[source_file] = []
            by_file[source_file].append((helper_name, helper_data))

        for source_file in sorted(by_file.keys()):
            output.append(f"### From: `{source_file}`")
            output.append("")

            helpers_in_file = by_file[source_file]
            for idx, (helper_name, helper_data) in enumerate(helpers_in_file, 1):
                is_tool = helper_data.get('is_tool', False)
                is_sub = helper_data.get('is_sub_helper', False)
                file_path = helper_data.get('file_path', 'TODO')
                purpose = helper_data.get('purpose', 'No purpose specified')

                tool_marker = " 🔧" if is_tool else ""
                sub_marker = " 📦" if is_sub else ""

                output.append(f"{idx}. **{helper_name}**{tool_marker}{sub_marker}")
                output.append(f"   - Purpose: {purpose}")
                output.append(f"   - Target: `{file_path}`")
                output.append("")

        output.append("---")
        output.append("")

    # Legend
    output.append("## Legend")
    output.append("")
    output.append("- 🔧 = MCP Tool (is_tool=true) - AI can call directly")
    output.append("- 📦 = Sub-helper (is_sub_helper=true) - Internal use only")
    output.append("- No marker = Directive-callable helper")
    output.append("")

    return "\n".join(output)

def main():
    # Find all helper JSON files
    helpers_dir = Path('docs/helpers/json')
    json_files = list(helpers_dir.glob('*.json'))

    print(f"Found {len(json_files)} JSON files")

    # Extract all helpers
    all_helpers = []
    for json_file in sorted(json_files):
        helpers = extract_helpers_from_json(json_file)
        all_helpers.extend(helpers)
        print(f"  {json_file.name}: {len(helpers)} helpers")

    print(f"\nTotal helpers extracted: {len(all_helpers)}")

    # Categorize
    categories = categorize_helpers(all_helpers)

    # Generate markdown
    markdown = generate_markdown_output(categories)

    # Write to file
    output_path = Path('docs/COMPLETE_HELPERS_LIST.md')
    output_path.write_text(markdown)

    print(f"\n✅ Complete list written to: {output_path}")
    print(f"\nSummary:")
    for category, helpers in categories.items():
        print(f"  {category}: {len(helpers)} helpers")

if __name__ == '__main__':
    main()
