#!/usr/bin/env python3
"""
Replace direct SQL INSERT/UPDATE examples with guidance to use helpers.

Focuses on workflow examples, not Database Operations documentation sections.
"""

import re
from pathlib import Path

DIRECTIVES_DIR = Path(__file__).parent.parent.parent.parent / "src/aifp/reference/directives"

# Patterns to replace
PATTERNS = [
    # INSERT INTO notes patterns
    (
        r'```sql\s*INSERT INTO notes \([^)]+\)\s*VALUES \([^)]+\);?\s*```',
        '- AI uses available helpers to add notes to project database\n  - Query database for note-related helpers\n  - Use discovered helper with appropriate parameters'
    ),
    # INSERT INTO interactions patterns
    (
        r'```sql\s*INSERT INTO interactions \([^)]+\)\s*VALUES \([^)]+\);?\s*```',
        '- AI uses available helpers to add interactions to project database\n  - Query database for interaction-related helpers\n  - Use discovered helper with appropriate parameters'
    ),
    # UPDATE functions patterns
    (
        r'```sql\s*UPDATE functions SET [^;]+;?\s*```',
        '- AI uses available helpers to update function records\n  - Query database for function update helpers\n  - Use discovered helper with appropriate parameters'
    ),
    # Generic INSERT patterns (more cautious)
    (
        r'```sql\s*INSERT INTO ([a-z_]+) \([^)]+\)\s*VALUES \([^)]+\);?\s*```',
        lambda m: f'- AI uses available helpers to add {m.group(1)} records\n  - Query database for {m.group(1)}-related helpers\n  - Use discovered helper with appropriate parameters'
    ),
]

def replace_sql_with_helpers(content, filepath):
    """Replace SQL examples with helper guidance."""
    original = content
    changes = []

    # Skip if in ## Database Operations section
    # We want to keep SQL examples in documentation sections
    lines = content.split('\n')
    in_db_ops_section = False
    result_lines = []

    for i, line in enumerate(lines):
        if line.strip().startswith('## Database Operations'):
            in_db_ops_section = True
        elif line.strip().startswith('##') and not line.strip().startswith('### '):
            # Next major section
            in_db_ops_section = False

        result_lines.append((line, in_db_ops_section))

    # Reconstruct with section markers
    content_with_markers = '\n'.join([
        f"{'[DB_OPS]' if is_db else ''}{line}"
        for line, is_db in result_lines
    ])

    # Only replace in non-DB_OPS sections
    for pattern, replacement in PATTERNS:
        if callable(replacement):
            # For patterns with capture groups
            def replacer(match):
                # Don't replace if in DB Operations section
                start = content_with_markers.rfind('[DB_OPS]', 0, match.start())
                next_section = content_with_markers.find('\n## ', match.start())
                if start != -1 and (next_section == -1 or start > content_with_markers.rfind('\n## ', 0, match.start())):
                    return match.group(0)  # Keep original

                result = replacement(match)
                changes.append(f"Replaced SQL with helper guidance at position {match.start()}")
                return result

            content_with_markers = re.sub(pattern, replacer, content_with_markers, flags=re.DOTALL)
        else:
            # Simple string replacement
            matches = list(re.finditer(pattern, content_with_markers, flags=re.DOTALL))
            for match in reversed(matches):  # Reverse to maintain positions
                # Check if in DB Operations section
                start = content_with_markers.rfind('[DB_OPS]', 0, match.start())
                next_section = content_with_markers.find('\n## ', match.start())
                if start != -1 and (next_section == -1 or start > content_with_markers.rfind('\n## ', 0, match.start())):
                    continue  # Skip in DB Operations section

                content_with_markers = content_with_markers[:match.start()] + replacement + content_with_markers[match.end():]
                changes.append(f"Replaced SQL INSERT/UPDATE with helper guidance")

    # Remove markers
    final_content = re.sub(r'\[DB_OPS\]', '', content_with_markers)

    if final_content != original:
        return final_content, changes
    return None, []

def process_file(filepath):
    """Process a single MD file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        new_content, changes = replace_sql_with_helpers(content, filepath)

        if new_content:
            filepath.write_text(new_content, encoding='utf-8')
            return True, changes
        return False, []

    except Exception as e:
        return False, [f"Error: {str(e)}"]

def main():
    """Main execution."""
    if not DIRECTIVES_DIR.exists():
        print(f"Error: Directory not found: {DIRECTIVES_DIR}")
        return

    print(f"Replacing SQL examples with helper guidance in: {DIRECTIVES_DIR}")
    print("-" * 60)

    files = sorted(DIRECTIVES_DIR.glob("*.md"))
    modified_count = 0
    total_changes = 0

    for filepath in files:
        modified, changes = process_file(filepath)

        if modified:
            print(f"✅ Modified: {filepath.name}")
            for change in changes:
                print(f"   - {change}")
            modified_count += 1
            total_changes += len(changes)

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Files modified: {modified_count}")
    print(f"  Total replacements: {total_changes}")

    if modified_count > 0:
        print(f"\n✅ SQL examples replaced with helper guidance in {modified_count} files!")
    else:
        print("\n✅ No SQL examples found that need replacement.")

if __name__ == "__main__":
    main()
