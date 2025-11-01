#!/usr/bin/env python3
"""
Extract helper function references from directive JSON workflows.
Compare with helpers_parsed.json to find unmapped helpers.
"""

import json
import os
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'directives' in data:
            return data['directives']
        return []

def extract_helpers_from_workflow(workflow, helpers_found):
    """Recursively extract helper references from workflow JSON"""
    if isinstance(workflow, dict):
        # Check for 'helper' key
        if 'helper' in workflow:
            helpers_found.add(workflow['helper'])

        # Check for helper_* keys (like helper_project_db, helper_prefs_db)
        for key, value in workflow.items():
            if key.startswith('helper'):
                if isinstance(value, str):
                    helpers_found.add(value)

        # Recurse into all nested structures
        for value in workflow.values():
            extract_helpers_from_workflow(value, helpers_found)

    elif isinstance(workflow, list):
        for item in workflow:
            extract_helpers_from_workflow(item, helpers_found)

def main():
    script_dir = Path(__file__).parent
    directives_dir = script_dir / "directives-json"

    # Load all helpers
    helpers_file = script_dir / "helpers_parsed.json"
    all_helpers = {h['name'] for h in load_json(helpers_file)}
    print(f"Total helpers defined: {len(all_helpers)}")

    # Extract helpers referenced in directives
    referenced_helpers = set()

    for json_file in directives_dir.glob("directives-*.json"):
        if json_file.name == "directives-interactions.json":
            continue

        directives = load_json(json_file)
        for directive in directives:
            if 'workflow' in directive:
                extract_helpers_from_workflow(directive['workflow'], referenced_helpers)

    print(f"Helpers referenced in directives: {len(referenced_helpers)}")
    print(f"\nReferenced helpers:")
    for h in sorted(referenced_helpers):
        print(f"  - {h}")

    # Find unmapped helpers
    unmapped = all_helpers - referenced_helpers
    print(f"\n\nUnmapped helpers ({len(unmapped)}):")
    for h in sorted(unmapped):
        print(f"  - {h}")

    # Categorize unmapped by module
    by_module = {}
    helpers_data = load_json(helpers_file)
    for helper in helpers_data:
        if helper['name'] in unmapped:
            module = helper['file_path'].split('/')[-1].replace('.py', '')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(helper['name'])

    print(f"\n\nUnmapped helpers by module:")
    for module, helpers in sorted(by_module.items()):
        print(f"\n{module}.py ({len(helpers)} helpers):")
        for h in sorted(helpers):
            print(f"  - {h}")

if __name__ == "__main__":
    main()
