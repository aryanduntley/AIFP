#!/usr/bin/env python3
"""
Extract helper→directive mappings from helper-functions-reference.md
The "Used By" sections list which directives use each helper.
"""

import json
import re
from pathlib import Path

def parse_helper_reference(filepath):
    """Parse helper-functions-reference.md to extract helper→directive mappings"""

    with open(filepath, 'r') as f:
        content = f.read()

    mappings = []
    current_helper = None

    # Split by helper function headings (### helper_name)
    sections = re.split(r'\n###\s+(\w+(?:\([^)]*\))?)', content)

    for i in range(1, len(sections), 2):
        helper_name_raw = sections[i]
        helper_section = sections[i+1]

        # Extract clean helper name (remove parameters)
        helper_name = helper_name_raw.split('(')[0].strip()

        # Find "Used By" line
        used_by_match = re.search(r'\*\*Used By\*\*:\s*(.+)', helper_section)

        if used_by_match:
            used_by_text = used_by_match.group(1).strip()

            # Extract directive names (look for backtick-quoted directives)
            directive_names = re.findall(r'`([a-z_]+)`', used_by_text)

            # Also look for plain text directive-like names
            if not directive_names:
                # Match patterns like "project_init", "git_sync_state", etc.
                plain_names = re.findall(r'\b([a-z]+_[a-z_]+)\b', used_by_text)
                directive_names = plain_names

            for directive in directive_names:
                mappings.append({
                    "helper_function": helper_name,
                    "directive": directive,
                    "usage_context": used_by_text,
                })
        else:
            # No "Used By" found - might be sub-helper or unused
            mappings.append({
                "helper_function": helper_name,
                "directive": None,
                "usage_context": "No directive mapping found - may be sub-helper",
            })

    return mappings

def group_by_directive(mappings):
    """Group mappings by directive name"""
    by_directive = {}
    unmapped = []

    for mapping in mappings:
        if mapping['directive']:
            directive = mapping['directive']
            if directive not in by_directive:
                by_directive[directive] = []
            by_directive[directive].append({
                "helper": mapping['helper_function'],
                "context": mapping['usage_context']
            })
        else:
            unmapped.append(mapping['helper_function'])

    return by_directive, unmapped

def main():
    script_dir = Path(__file__).parent
    reference_file = script_dir / "helper-functions-reference.md"

    print("Parsing helper-functions-reference.md...")
    mappings = parse_helper_reference(reference_file)

    print(f"\nTotal helper functions parsed: {len(mappings)}")

    # Group by directive
    by_directive, unmapped = group_by_directive(mappings)

    print(f"Directives with helper mappings: {len(by_directive)}")
    print(f"Unmapped helpers (sub-helpers or internal): {len(unmapped)}")

    print("\n" + "="*60)
    print("HELPER → DIRECTIVE MAPPINGS")
    print("="*60)

    for directive in sorted(by_directive.keys()):
        helpers = by_directive[directive]
        print(f"\n{directive} ({len(helpers)} helpers):")
        for h in helpers:
            print(f"  - {h['helper']}")

    if unmapped:
        print("\n" + "="*60)
        print("UNMAPPED HELPERS (likely sub-helpers or internal)")
        print("="*60)
        for helper in sorted(unmapped):
            print(f"  - {helper}")

    # Save as JSON
    output_file = script_dir / "directive-helpers-mappings.json"
    output_data = {
        "mappings_by_directive": by_directive,
        "unmapped_helpers": unmapped,
        "total_mappings": len([m for m in mappings if m['directive']]),
        "total_helpers": len(mappings)
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n\nSaved to: {output_file}")

if __name__ == "__main__":
    main()
