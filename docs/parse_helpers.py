#!/usr/bin/env python3
"""
Parse all helper functions from helper-functions-reference.md
Extracts: name, file_path, purpose, parameters, error_handling
"""

import re
import json
from pathlib import Path

HELPER_MD = Path(__file__).parent / "helper-functions-reference.md"

def parse_helpers():
    """Parse all helper functions from MD file."""
    helpers = []

    with open(HELPER_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match helper function headers (### or ####)
    # Captures: function_name(parameters)
    pattern = r'^#{3,4}\s+([a-z_]+)\((.*?)\)'

    # Split content by helper function headers
    sections = re.split(r'^#{3,4}\s+[a-z_]+\(.*?\)', content, flags=re.MULTILINE)
    headers = re.findall(pattern, content, flags=re.MULTILINE)

    for i, (func_name, params_str) in enumerate(headers):
        # Get the section content after this header (if exists)
        section_content = sections[i+1] if i+1 < len(sections) else ""

        # Extract file path
        file_path_match = re.search(r'\*\*File Path\*\*:\s*`([^`]+)`', section_content)
        file_path = file_path_match.group(1) if file_path_match else None

        # Extract purpose (first paragraph after "Purpose:")
        purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+?)(?:\n\n|\*\*)', section_content, re.DOTALL)
        purpose = purpose_match.group(1).strip() if purpose_match else None

        # Extract error handling
        error_match = re.search(r'\*\*Error Handling\*\*:\s*(.+?)(?:\n\n|\*\*)', section_content, re.DOTALL)
        error_handling = error_match.group(1).strip() if error_match else None

        # Extract "Used By" directives
        used_by_match = re.search(r'\*\*Used By\*\*:\s*(.+?)(?:\n\n|\*\*|\-\-\-)', section_content, re.DOTALL)
        used_by = used_by_match.group(1).strip() if used_by_match else None

        # Parse parameters from function signature
        parameters = []
        if params_str.strip():
            # Simple parsing - each param is comma-separated
            param_parts = [p.strip() for p in params_str.split(',')]
            for param in param_parts:
                if param:
                    parameters.append(param)

        helper = {
            "name": func_name,
            "file_path": file_path,
            "purpose": purpose,
            "parameters": json.dumps(parameters) if parameters else None,
            "error_handling": error_handling,
            "used_by": used_by
        }

        helpers.append(helper)

    return helpers


if __name__ == "__main__":
    helpers = parse_helpers()
    print(f"Parsed {len(helpers)} helper functions from MD file:\n")

    for i, helper in enumerate(helpers, 1):
        print(f"{i}. {helper['name']}")
        if helper['file_path']:
            print(f"   Path: {helper['file_path']}")
        if helper['used_by']:
            print(f"   Used by: {helper['used_by'][:80]}...")

    print(f"\n✅ Total helpers: {len(helpers)}")

    # Save to JSON for sync script to use
    output_file = Path(__file__).parent / "helpers_parsed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(helpers, f, indent=2)
    print(f"💾 Saved to: {output_file}")
