#!/usr/bin/env python3
"""
Clear all return_statements from helper JSON files.

This script:
1. Reads each helpers-*.json file
2. Sets return_statements to empty array for all helpers
3. Preserves all other fields
4. Writes back with proper formatting
"""

import json
from pathlib import Path

def clear_return_statements(json_file: Path):
    """Clear return_statements from a single JSON file."""
    print(f"Processing {json_file.name}...")

    # Read the file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count helpers modified
    count = 0

    # Clear return_statements for each helper
    if 'helpers' in data:
        for helper in data['helpers']:
            if 'return_statements' in helper:
                if helper['return_statements']:  # Only count if not already empty
                    count += 1
                helper['return_statements'] = []

    # Write back
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Cleared return_statements from {count} helpers")
    return count

def main():
    """Process all helper JSON files."""
    # Get the json directory
    json_dir = Path(__file__).parent / 'json'

    if not json_dir.exists():
        print(f"Error: Directory not found: {json_dir}")
        return

    # Find all helpers-*.json files
    json_files = sorted(json_dir.glob('helpers-*.json'))

    if not json_files:
        print("No helpers-*.json files found")
        return

    print(f"Found {len(json_files)} helper JSON files\n")

    total_cleared = 0
    for json_file in json_files:
        cleared = clear_return_statements(json_file)
        total_cleared += cleared

    print(f"\n✅ Complete: Cleared return_statements from {total_cleared} helpers across {len(json_files)} files")
    print("\nReady to start fresh with simple, conceptual guidance.")

if __name__ == '__main__':
    main()
