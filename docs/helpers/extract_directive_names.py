#!/usr/bin/env python3
"""
Extract directive names and descriptions from JSON files.
Creates a simple reference file for used_by_directives analysis.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

def extract_directives(file_path: str) -> List[Dict[str, Any]]:
    """Extract directive names and descriptions from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        directives = []

        # Handle both array and object with 'directives' key
        if isinstance(data, list):
            directive_list = data
        elif isinstance(data, dict) and 'directives' in data:
            directive_list = data['directives']
        else:
            return []

        for directive in directive_list:
            directives.append({
                'name': directive.get('name', 'UNKNOWN'),
                'description': directive.get('description', 'No description'),
                'type': directive.get('type', 'unknown')
            })

        return directives
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def main():
    """Extract all directives and write to reference file."""
    project_root = Path(__file__).parent.parent.parent
    output_file = project_root / "docs/helpers/DIRECTIVE_NAMES_REFERENCE.md"
    directives_dir = project_root / "docs/directives-json"

    all_directives = []

    # Find all JSON files in directives-json directory
    json_files = sorted(directives_dir.glob("directives-*.json"))

    # Process each directive file
    for json_file in json_files:
        # Extract category name from filename (e.g., "directives-project.json" -> "Project")
        category = json_file.stem.replace("directives-", "").replace("-", " ").title()

        directives = extract_directives(str(json_file))

        if directives:
            all_directives.append((category, directives))
            print(f"  - {category}: {len(directives)} directives")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Directive Names Reference\n\n")
        f.write("**Purpose**: Quick reference for directive names and descriptions.\n")
        f.write("**Use**: Search this file to determine which directives might use a helper.\n\n")
        f.write("---\n\n")

        total_count = 0

        for category, directives in all_directives:
            f.write(f"## {category} Directives ({len(directives)} directives)\n\n")

            for directive in directives:
                name = directive['name']
                desc = directive['description']
                dtype = directive['type']

                f.write(f"### {name}\n")
                f.write(f"**Type**: {dtype}\n")
                f.write(f"**Description**: {desc}\n\n")

                total_count += 1

        f.write("---\n\n")
        f.write(f"**Total Directives**: {total_count}\n")
        f.write(f"**Last Generated**: 2026-01-01\n")

    print(f"✓ Extracted {total_count} directives")
    print(f"✓ Written to: {output_file}")

    # Also create a compact version for quick scanning
    compact_file = project_root / "docs/helpers/DIRECTIVE_NAMES_COMPACT.txt"
    with open(compact_file, 'w', encoding='utf-8') as f:
        f.write("DIRECTIVE NAMES - COMPACT REFERENCE\n")
        f.write("=" * 80 + "\n\n")

        for category, directives in all_directives:
            f.write(f"{category.upper()} DIRECTIVES:\n")
            f.write("-" * 80 + "\n")

            for directive in directives:
                name = directive['name']
                desc = directive['description']
                # Truncate long descriptions
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                f.write(f"{name:40} | {desc}\n")

            f.write("\n")

    print(f"✓ Written compact version to: {compact_file}")

if __name__ == "__main__":
    main()
