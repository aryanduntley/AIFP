#!/usr/bin/env python3
"""
Convert helper markdown files to JSON format.

Extracts all available data from markdown and creates structured JSON
with empty used_by_directives arrays for later mapping.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


def parse_parameters(param_text: str) -> List[Dict[str, Any]]:
    """Parse parameter text into structured array."""
    if not param_text or param_text.strip() == "None":
        return []

    params = []
    # Look for parameter patterns like: param_name (Type) - description
    # or: param_name (Type, optional) - description
    # or: param_name (Type, default value) - description

    lines = param_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('-') and len(line) == 1:
            continue

        # Remove leading dash/bullet
        line = re.sub(r'^\s*[-*]\s*', '', line)

        # Try to extract: name (type[, optional][, default X]) - description
        match = re.match(r'`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*\(([^)]+)\)\s*[-–—]\s*(.+)', line)
        if match:
            name = match.group(1)
            type_info = match.group(2)
            description = match.group(3)

            # Parse type info
            param_type = "string"  # default
            required = True
            default = None

            type_parts = [p.strip() for p in type_info.split(',')]
            if type_parts:
                param_type = type_parts[0].lower()
                # Map common type names
                if 'int' in param_type:
                    param_type = 'integer'
                elif 'bool' in param_type:
                    param_type = 'boolean'
                elif 'arr' in param_type or 'list' in param_type:
                    param_type = 'array'
                elif 'obj' in param_type or 'dict' in param_type:
                    param_type = 'object'
                elif 'str' in param_type:
                    param_type = 'string'

            # Check for optional
            if len(type_parts) > 1:
                for part in type_parts[1:]:
                    if 'optional' in part.lower():
                        required = False
                    elif 'default' in part.lower():
                        required = False
                        # Try to extract default value
                        default_match = re.search(r'default[:\s]+(.+)', part, re.IGNORECASE)
                        if default_match:
                            default = default_match.group(1).strip()

            params.append({
                "name": name,
                "type": param_type,
                "required": required,
                "default": default,
                "description": description
            })

    return params


def extract_helper_from_section(section_text: str, helper_name: str, target_database: str) -> Dict[str, Any]:
    """Extract helper data from a markdown section."""

    helper = {
        "name": helper_name,
        "file_path": f"TODO_helpers/{target_database}/module.py",  # To be filled in
        "parameters": [],
        "purpose": "",
        "error_handling": "",
        "is_tool": True,
        "is_sub_helper": False,
        "return_statements": [],
        "target_database": target_database,
        "used_by_directives": []  # Empty for now, will be filled during directive mapping
    }

    # Extract Purpose
    purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+?)(?:\n|$)', section_text)
    if purpose_match:
        helper["purpose"] = purpose_match.group(1).strip()

    # Extract Parameters
    params_match = re.search(r'\*\*Parameters?\*\*:\s*\n((?:.*?\n)*?)(?=\*\*|\n\n|$)', section_text, re.MULTILINE)
    if params_match:
        helper["parameters"] = parse_parameters(params_match.group(1))

    # Extract Returns (for return_statements)
    returns_match = re.search(r'\*\*Returns?\*\*:\s*(.+?)(?:\n|$)', section_text)
    if returns_match:
        returns_text = returns_match.group(1).strip()
        helper["return_statements"] = [returns_text]

    # Extract Note (additional return guidance)
    notes = re.findall(r'\*\*Note\*\*:\s*(.+?)(?:\n|$)', section_text)
    if notes:
        helper["return_statements"].extend(notes)

    # Extract Error Handling
    error_match = re.search(r'\*\*Error Handling\*\*:\s*(.+?)(?:\n|$)', section_text)
    if error_match:
        helper["error_handling"] = error_match.group(1).strip()

    # Extract Classification
    classif_match = re.search(r'\*\*Classification\*\*:\s*(.+?)(?:\n|$)', section_text)
    if classif_match:
        classif_text = classif_match.group(1)
        helper["is_tool"] = 'is_tool=true' in classif_text.lower()
        helper["is_sub_helper"] = 'is_sub_helper=true' in classif_text.lower()

    return helper


def parse_markdown_file(file_path: Path, target_database: str) -> List[Dict[str, Any]]:
    """Parse a consolidated helper markdown file."""

    content = file_path.read_text(encoding='utf-8')
    helpers = []

    # Try both patterns:
    # Pattern 1: **`function_name(params)`** or **`function_name()`** or **`function_name`**
    # Pattern 2: ### `function_name(params)` (orchestrators)

    # Pattern 1: matches **`name(anything)`** or **`name`**
    helper_pattern1 = r'^\*\*`([a-zA-Z_][a-zA-Z0-9_]*)(?:\([^)]*\))?`\*\*'
    matches1 = list(re.finditer(helper_pattern1, content, flags=re.MULTILINE))

    # Pattern 2: for ### `name(params)` format (orchestrators)
    helper_pattern2 = r'^###\s+`([a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)`'
    matches2 = list(re.finditer(helper_pattern2, content, flags=re.MULTILINE))

    # Use whichever pattern found more matches
    if len(matches2) > len(matches1):
        matches = matches2
    else:
        matches = matches1

    # Extract sections for each match
    for idx, match in enumerate(matches):
        helper_name = match.group(1)
        start_pos = match.end()

        # Find end position (next helper or end of file)
        if idx + 1 < len(matches):
            end_pos = matches[idx + 1].start()
        else:
            end_pos = len(content)

        section_content = content[start_pos:end_pos]

        # Skip empty names or very short sections
        if not helper_name or len(section_content.strip()) < 10:
            continue

        helper = extract_helper_from_section(section_content, helper_name, target_database)
        helpers.append(helper)

    return helpers


def split_helpers_into_files(helpers: List[Dict[str, Any]], base_name: str, output_dir: Path, max_per_file: int = 20):
    """Split helpers into multiple JSON files if needed."""

    if len(helpers) <= max_per_file:
        # Single file
        output_file = output_dir / f"{base_name}.json"
        data = {
            "helpers": helpers,
            "metadata": {
                "file": f"{base_name}.json",
                "count": len(helpers),
                "status": "converted from markdown - used_by_directives empty"
            }
        }
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Created {output_file.name} with {len(helpers)} helpers")
    else:
        # Multiple files
        file_num = 1
        for i in range(0, len(helpers), max_per_file):
            chunk = helpers[i:i + max_per_file]
            output_file = output_dir / f"{base_name}-{file_num}.json"

            data = {
                "helpers": chunk,
                "metadata": {
                    "file": f"{base_name}-{file_num}.json",
                    "range": f"helpers {i+1}-{i+len(chunk)} of {len(helpers)}",
                    "status": "converted from markdown - used_by_directives empty"
                }
            }
            output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"Created {output_file.name} with {len(chunk)} helpers")
            file_num += 1


def main():
    """Main conversion process."""

    base_dir = Path(__file__).parent
    consolidated_dir = base_dir / "consolidated"
    output_dir = base_dir / "json"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    print("Converting helper markdown files to JSON...\n")

    # Define files to convert
    conversions = [
        ("helpers-consolidated-core.md", "helpers-core", "core", 20),
        ("helpers-consolidated-git.md", "helpers-git", "project", 20),
        ("helpers-consolidated-orchestrators.md", "helpers-orchestrators", "orchestrator", 10),
        ("helpers-consolidated-project.md", "helpers-project", "project", 20),
        ("helpers-consolidated-settings.md", "helpers-settings", "settings", 20),
        ("helpers-consolidated-user-custom.md", "helpers-user-custom", "user_custom", 20),
    ]

    total_helpers = 0

    for md_file, json_base, target_db, max_per_file in conversions:
        input_file = consolidated_dir / md_file

        if not input_file.exists():
            print(f"Warning: {md_file} not found, skipping...")
            continue

        print(f"Processing {md_file}...")

        # Debug: check patterns
        content = input_file.read_text(encoding='utf-8')
        pattern1_count = len(re.findall(r'^\*\*`([a-zA-Z_][a-zA-Z0-9_]*)(?:\([^)]*\))?`\*\*', content, flags=re.MULTILINE))
        pattern2_count = len(re.findall(r'^###\s+`([a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)`', content, flags=re.MULTILINE))
        print(f"  Pattern 1 matches: {pattern1_count}, Pattern 2 matches: {pattern2_count}")

        helpers = parse_markdown_file(input_file, target_db)

        if helpers:
            print(f"  Extracted: {len(helpers)} helpers")
            split_helpers_into_files(helpers, json_base, output_dir, max_per_file)
            total_helpers += len(helpers)
        else:
            print(f"  No helpers found in {md_file}")

        print()

    print(f"Conversion complete! Total helpers converted: {total_helpers}")
    print(f"\nJSON files created in: {output_dir}")
    print("\nNext step: Review JSON files and:")
    print("  1. Fill in file_path fields (replace TODO_helpers/...)")
    print("  2. Review/standardize error_handling fields")
    print("  3. During directive mapping, add to used_by_directives arrays")


if __name__ == "__main__":
    main()
