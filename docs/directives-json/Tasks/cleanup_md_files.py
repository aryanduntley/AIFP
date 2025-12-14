#!/usr/bin/env python3
"""
Cleanup script for directive MD files.

Removes:
1. ## Helper Functions Used sections (entire section)
2. Dev-only references (lines with ../../ or ../../../)
3. Replaces empty References sections with "None"
"""

import re
from pathlib import Path

DIRECTIVES_DIR = Path(__file__).parent.parent.parent.parent / "src/aifp/reference/directives"

def remove_helper_functions_section(content):
    """Remove entire ## Helper Functions Used section."""
    # Pattern matches from "## Helper Functions Used" to the next "---" or "##"
    pattern = r'## Helper Functions Used\n.*?(?=\n---|\n##|\Z)'
    return re.sub(pattern, '', content, flags=re.DOTALL)

def clean_references_section(content):
    """
    Remove dev-only reference links (../../ or ../../../).
    If References section becomes empty, replace with "None".
    """
    lines = content.split('\n')
    result = []
    in_references = False
    references_content = []
    references_start_idx = None

    for i, line in enumerate(lines):
        if line.strip() == '## References':
            in_references = True
            references_start_idx = len(result)
            result.append(line)
            continue

        if in_references:
            # Check if we hit the next section
            if line.startswith('##') or (line.strip() == '---' and references_content):
                # Process accumulated references
                # Filter out lines with ../../ or ../../../
                filtered_refs = [
                    ref for ref in references_content
                    if '../..' not in ref and not ref.strip().startswith('-')
                ]

                # Also keep lines that reference files in same directory (./filename.md)
                kept_refs = []
                for ref in references_content:
                    # Keep if it doesn't have ../../ or ../../../
                    if '../..' not in ref:
                        kept_refs.append(ref)

                # Add filtered references
                if kept_refs and any(line.strip() for line in kept_refs):
                    result.extend(kept_refs)
                else:
                    # Add "None" if nothing left
                    result.append('')
                    result.append('None')

                in_references = False
                references_content = []
                result.append(line)
                continue

            references_content.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

def replace_helper_functions_used_with_standard(content):
    """Replace ## Helper Functions Used with standard template."""
    # Match the section header and everything until next section
    pattern = r'## Helper Functions Used\n.*?(?=\n---|\n##|\Z)'

    replacement = '''## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.'''

    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def process_file(filepath):
    """Process a single MD file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        # Step 1: Replace Helper Functions Used section with standard template
        content = replace_helper_functions_used_with_standard(content)

        # Step 2: Clean References section
        content = clean_references_section(content)

        # Only write if changed
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            return True, None
        return False, None

    except Exception as e:
        return False, str(e)

def main():
    """Main execution."""
    if not DIRECTIVES_DIR.exists():
        print(f"Error: Directory not found: {DIRECTIVES_DIR}")
        return

    print(f"Processing MD files in: {DIRECTIVES_DIR}")
    print("-" * 60)

    files = sorted(DIRECTIVES_DIR.glob("*.md"))
    modified_count = 0
    error_count = 0

    for filepath in files:
        modified, error = process_file(filepath)

        if error:
            print(f"❌ ERROR: {filepath.name} - {error}")
            error_count += 1
        elif modified:
            print(f"✅ Modified: {filepath.name}")
            modified_count += 1
        else:
            print(f"⏭️  Skipped: {filepath.name} (no changes needed)")

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Total files: {len(files)}")
    print(f"  Modified: {modified_count}")
    print(f"  Skipped: {len(files) - modified_count - error_count}")
    print(f"  Errors: {error_count}")

    if modified_count > 0:
        print(f"\n✅ Cleanup complete! {modified_count} files updated.")
    else:
        print("\n✅ All files already clean!")

if __name__ == "__main__":
    main()
