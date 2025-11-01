#!/usr/bin/env python3
"""
Generate directive-helper-interactions.json from two sources:
1. Directive JSON workflows (explicit helper references)
2. Helper-functions-reference.md ("Used By" sections)

Output format matches directive_helpers junction table schema.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def load_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'directives' in data:
            return data['directives']
        return []

def extract_from_workflows(directives_dir):
    """Extract helper references from directive JSON workflows"""
    mappings = []

    for json_file in directives_dir.glob('directives-*.json'):
        if json_file.name == 'directives-interactions.json':
            continue

        directives = load_json(json_file)
        for directive in directives:
            directive_name = directive['name']

            if 'workflow' in directive:
                helpers = extract_helpers_from_workflow(directive['workflow'])

                for idx, (helper_name, context) in enumerate(helpers):
                    mappings.append({
                        'directive_name': directive_name,
                        'helper_name': helper_name,
                        'execution_context': context,
                        'sequence_order': idx,
                        'is_required': True,
                        'description': f"{directive_name} uses {helper_name} in workflow",
                        'source': 'directive_json_workflow'
                    })

    return mappings

def extract_helpers_from_workflow(workflow, helpers=None, context_prefix=''):
    """Recursively extract helpers from workflow"""
    if helpers is None:
        helpers = []

    if isinstance(workflow, dict):
        # Check for 'helper' key
        if 'helper' in workflow:
            context = workflow.get('then', workflow.get('if', 'workflow_step'))
            helpers.append((workflow['helper'], f"{context_prefix}{context}"))

        # Check for helper_* keys
        for key, value in workflow.items():
            if key.startswith('helper') and key != 'helper' and isinstance(value, str):
                context = workflow.get('then', key)
                helpers.append((value, f"{context_prefix}{context}"))

        # Recurse
        for key, value in workflow.items():
            if key not in ['helper'] and not (key.startswith('helper') and isinstance(value, str)):
                extract_helpers_from_workflow(value, helpers, context_prefix)

    elif isinstance(workflow, list):
        for item in workflow:
            extract_helpers_from_workflow(item, helpers, context_prefix)

    return helpers

def parse_used_by_sections(reference_file):
    """Parse helper-functions-reference.md to extract Used By mappings"""
    with open(reference_file) as f:
        content = f.read()

    mappings = []

    # Split by helper sections
    sections = re.split(r'\n###\s+(\w+(?:\([^)]*\))?)', content)

    for i in range(1, len(sections), 2):
        helper_name_raw = sections[i]
        helper_section = sections[i+1]

        # Extract clean helper name
        helper_name = helper_name_raw.split('(')[0].strip()

        # Skip numeric artifacts
        if helper_name.isdigit():
            continue

        # Find "Used By" line
        used_by_match = re.search(r'\*\*Used By\*\*:\s*(.+)', helper_section)

        if used_by_match:
            used_by_text = used_by_match.group(1).strip()

            # Extract directive names (backtick-quoted)
            directive_names = re.findall(r'`([a-z_]+)`', used_by_text)

            for directive_name in directive_names:
                # Skip non-directive terms
                if directive_name in ['user_request', 'completion_path', 'project_metadata']:
                    continue

                mappings.append({
                    'directive_name': directive_name,
                    'helper_name': helper_name,
                    'execution_context': used_by_text[:150],  # Truncate long descriptions
                    'sequence_order': 0,  # Will be updated when merging
                    'is_required': True,
                    'description': f"{directive_name} uses {helper_name}",
                    'source': 'helper_reference_used_by'
                })

    return mappings

def merge_and_deduplicate(workflow_mappings, reference_mappings):
    """Merge mappings from both sources, prioritizing workflow (more specific)"""

    # Track (directive, helper) pairs
    seen = set()
    merged = []

    # Add workflow mappings first (higher priority)
    for mapping in workflow_mappings:
        key = (mapping['directive_name'], mapping['helper_name'])
        if key not in seen:
            merged.append(mapping)
            seen.add(key)

    # Add reference mappings for pairs not in workflow
    for mapping in reference_mappings:
        key = (mapping['directive_name'], mapping['helper_name'])
        if key not in seen:
            merged.append(mapping)
            seen.add(key)

    # Re-sequence by directive
    by_directive = defaultdict(list)
    for mapping in merged:
        by_directive[mapping['directive_name']].append(mapping)

    # Update sequence_order within each directive
    final = []
    for directive_name in sorted(by_directive.keys()):
        helpers = by_directive[directive_name]
        for idx, mapping in enumerate(helpers):
            mapping['sequence_order'] = idx
            final.append(mapping)

    return final

def main():
    script_dir = Path(__file__).parent
    directives_dir = script_dir / 'directives-json'
    reference_file = script_dir / 'helper-functions-reference.md'
    helpers_file = script_dir / 'helpers_parsed.json'

    # Load helper definitions
    helpers_data = load_json(helpers_file)
    all_helper_names = {h['name'] for h in helpers_data}
    print(f"Total helpers defined: {len(all_helper_names)}")

    # Extract from workflows
    print("\n1. Extracting from directive JSON workflows...")
    workflow_mappings = extract_from_workflows(directives_dir)
    print(f"   Found {len(workflow_mappings)} mappings")

    # Extract from reference
    print("\n2. Extracting from helper-functions-reference.md...")
    reference_mappings = parse_used_by_sections(reference_file)
    print(f"   Found {len(reference_mappings)} mappings")

    # Merge
    print("\n3. Merging and deduplicating...")
    final_mappings = merge_and_deduplicate(workflow_mappings, reference_mappings)
    print(f"   Total unique mappings: {len(final_mappings)}")

    # Validate all helpers are mapped
    mapped_helpers = {m['helper_name'] for m in final_mappings}
    unmapped_helpers = all_helper_names - mapped_helpers

    print(f"\n4. Validation:")
    print(f"   Helpers with directive mappings: {len(mapped_helpers)}")
    print(f"   Helpers without mappings (candidates for is_internal): {len(unmapped_helpers)}")

    if unmapped_helpers:
        print(f"\n   Unmapped helpers:")
        for h in sorted(unmapped_helpers):
            print(f"     - {h}")

    # Generate output
    output = {
        "description": "Helper-Directive interaction mappings for directive_helpers junction table",
        "generated_from": [
            "Directive JSON workflows (explicit references)",
            "Helper-functions-reference.md (Used By sections)"
        ],
        "statistics": {
            "total_mappings": len(final_mappings),
            "total_helpers_defined": len(all_helper_names),
            "helpers_mapped": len(mapped_helpers),
            "helpers_unmapped": len(unmapped_helpers),
            "unique_directives": len(set(m['directive_name'] for m in final_mappings))
        },
        "unmapped_helpers": sorted(unmapped_helpers),
        "mappings": final_mappings
    }

    output_file = script_dir / 'directive-helper-interactions.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Generated: {output_file}")
    print(f"   {len(final_mappings)} helper-directive mappings ready for sync-directives.py")

    # Show summary by directive
    by_directive = defaultdict(int)
    for mapping in final_mappings:
        by_directive[mapping['directive_name']] += 1

    print(f"\n📊 Top directives by helper count:")
    for directive, count in sorted(by_directive.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {directive}: {count} helpers")

if __name__ == '__main__':
    main()
