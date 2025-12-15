#!/usr/bin/env python3
"""
Clean up a single FP directive file - Remove INSERT INTO notes logging.

Usage:
    python3 cleanup_single_file.py fp_api_design.md
    python3 cleanup_single_file.py fp_api_design.md --dry-run

Only removes INSERT INTO notes (opt-in debugging).
Keeps all other SQL (UPDATE functions, INSERT INTO call_graph, etc.)
"""

import re
import sys
from pathlib import Path
from datetime import datetime

DIRECTIVES_DIR = Path("/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives")
BACKUP_DIR = Path("/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/backups/sql_cleanup")

# Files that need cleaning (27 files)
FILES_TO_CLEAN = [
    "fp_api_design.md",
    "fp_chaining.md",
    "fp_concurrency_safety.md",
    "fp_conditional_elimination.md",
    "fp_const_refactoring.md",
    "fp_currying.md",
    "fp_documentation.md",
    "fp_generic_constraints.md",
    "fp_guard_clauses.md",
    "fp_inheritance_flattening.md",
    "fp_io_isolation.md",
    "fp_logging_safety.md",
    "fp_memoization.md",
    "fp_naming_conventions.md",
    "fp_ownership_safety.md",
    "fp_parallel_purity.md",
    "fp_pattern_matching.md",
    "fp_reflection_limitation.md",
    "fp_runtime_type_check.md",
    "fp_side_effects_flag.md",
    "fp_state_elimination.md",
    "fp_tail_recursion.md",
    "fp_task_isolation.md",
    "fp_test_purity.md",
    "fp_type_inference.md",
    "fp_type_safety.md",
    "fp_wrapper_generation.md",
]


def create_backup(file_path):
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    content = file_path.read_text(encoding='utf-8')
    backup_path.write_text(content, encoding='utf-8')

    return backup_path


def remove_notes_insert_sql(content):
    """
    Remove ONLY 'INSERT INTO notes' SQL from file.
    Keeps all other SQL (UPDATE functions, INSERT INTO call_graph, etc.)

    Handles three patterns:
    1. "- Update database:" + SQL block
    2. "# Database log" comment + SQL in code block
    3. Standalone SQL blocks with INSERT INTO notes
    """
    changes = []

    # Pattern 1: Remove "- Update database:" line + SQL block with INSERT INTO notes
    # Matches: "- Update database:\n    ```sql\n    INSERT INTO notes..."
    pattern1 = r'- Update database:\s*\n\s*```sql\s*\n(?:.*?\n)*?INSERT INTO notes(?:.*?\n)*?```'
    count1 = len(re.findall(pattern1, content, flags=re.DOTALL))
    modified_content = re.sub(pattern1, '', content, flags=re.DOTALL)
    if count1 > 0:
        changes.append(f"Removed {count1} 'Update database' + INSERT INTO notes SQL block(s)")

    # Pattern 2: Remove standalone SQL blocks with INSERT INTO notes (no prefix)
    # Matches: "```sql\n...INSERT INTO notes...```"
    pattern2 = r'```sql\s*\n(?:.*?\n)*?INSERT INTO notes(?:.*?\n)*?```'
    count2 = len(re.findall(pattern2, modified_content, flags=re.DOTALL))
    modified_content = re.sub(pattern2, '', modified_content, flags=re.DOTALL)
    if count2 > 0:
        changes.append(f"Removed {count2} standalone INSERT INTO notes SQL block(s)")

    # Pattern 3: Remove INSERT INTO notes from inside Python/other code blocks
    # Matches: "# Database log\nINSERT INTO notes...;"
    pattern3 = r'#\s*Database log\s*\n(?:.*?\n)*?INSERT INTO notes(?:.*?\n)*?;'
    count3 = len(re.findall(pattern3, modified_content, flags=re.DOTALL))
    modified_content = re.sub(pattern3, '', modified_content, flags=re.DOTALL)
    if count3 > 0:
        changes.append(f"Removed {count3} 'Database log' comment + INSERT INTO notes")

    # Pattern 4: Catch any remaining INSERT INTO notes (single line, no code block)
    pattern4 = r'INSERT INTO notes[^;]*;'
    count4 = len(re.findall(pattern4, modified_content))
    modified_content = re.sub(pattern4, '', modified_content)
    if count4 > 0:
        changes.append(f"Removed {count4} remaining INSERT INTO notes statement(s)")

    return modified_content, changes


def clean_empty_sql_blocks(content):
    """Remove empty SQL code blocks left after removal."""
    pattern = r'```sql\s*```'
    count = len(re.findall(pattern, content))
    modified = re.sub(pattern, '', content)
    return modified, count


def clean_multiple_blank_lines(content):
    """Reduce multiple consecutive blank lines to max 2."""
    return re.sub(r'\n{4,}', '\n\n\n', content)


def add_conditional_logging_note(content):
    """
    Add note about conditional logging to Database Operations section.

    Updates lines like:
    - **`notes`**: INSERT [something]

    To:
    - **`notes`**: INSERT [something] (only if `fp_flow_tracking` enabled - disabled by default)
    """
    # Check if already has note
    if "fp_flow_tracking enabled" in content:
        return content, []

    changes = []

    # Pattern: Find "**`notes`**: INSERT" and add conditional clause
    pattern = r'(\*\*`notes`\*\*:[^\n]*INSERT[^\n]*?)(\n)'

    def add_clause(match):
        line = match.group(1)
        ending = match.group(2)

        # Check if already has conditional note
        if "fp_flow_tracking" in line or "disabled by default" in line:
            return match.group(0)

        return f"{line} (only if `fp_flow_tracking` enabled - disabled by default){ending}"

    modified = re.sub(pattern, add_clause, content)

    if modified != content:
        changes.append("Updated Database Operations section with conditional clause")

    return modified, changes


def show_diff_summary(original, modified, filename):
    """Show a summary of what changed."""
    orig_lines = original.split('\n')
    mod_lines = modified.split('\n')

    print(f"\n📊 Changes Summary for {filename}:")
    print(f"   Original lines: {len(orig_lines)}")
    print(f"   Modified lines: {len(mod_lines)}")
    print(f"   Lines removed: {len(orig_lines) - len(mod_lines)}")

    # Count INSERT INTO notes occurrences
    orig_notes = original.count("INSERT INTO notes")
    mod_notes = modified.count("INSERT INTO notes")
    print(f"   INSERT INTO notes: {orig_notes} → {mod_notes}")

    # Verify we didn't remove other SQL
    orig_update = original.count("UPDATE functions")
    mod_update = modified.count("UPDATE functions")
    if orig_update != mod_update:
        print(f"   ⚠️  WARNING: UPDATE functions changed: {orig_update} → {mod_update}")

    orig_insert_other = original.count("INSERT INTO") - orig_notes
    mod_insert_other = modified.count("INSERT INTO") - mod_notes
    if orig_insert_other != mod_insert_other:
        print(f"   ⚠️  WARNING: Other INSERT INTO changed: {orig_insert_other} → {mod_insert_other}")


def process_file(filename, dry_run=False):
    """Process a single file."""
    file_path = DIRECTIVES_DIR / filename

    if not file_path.exists():
        print(f"❌ File not found: {filename}")
        return False

    print("=" * 80)
    print(f"Processing: {filename}")
    print("=" * 80)

    # Read original content
    original_content = file_path.read_text(encoding='utf-8')

    # Track all changes
    all_changes = []

    # Step 1: Remove INSERT INTO notes
    modified_content, changes = remove_notes_insert_sql(original_content)
    all_changes.extend(changes)

    # Step 2: Clean empty SQL blocks
    modified_content, empty_count = clean_empty_sql_blocks(modified_content)
    if empty_count > 0:
        all_changes.append(f"Removed {empty_count} empty SQL block(s)")

    # Step 3: Add conditional logging note to Database Operations
    modified_content, changes = add_conditional_logging_note(modified_content)
    all_changes.extend(changes)

    # Step 4: Clean up excessive blank lines
    modified_content = clean_multiple_blank_lines(modified_content)

    # Show changes
    if all_changes:
        print("\n✓ Changes Made:")
        for i, change in enumerate(all_changes, 1):
            print(f"  {i}. {change}")

        # Show diff summary
        show_diff_summary(original_content, modified_content, filename)

        if dry_run:
            print("\n🔍 DRY RUN - No files modified")
            print("\nFirst 50 lines of modified content:")
            print("-" * 80)
            print('\n'.join(modified_content.split('\n')[:50]))
            print("-" * 80)
            return True
        else:
            # Create backup
            backup_path = create_backup(file_path)
            print(f"\n💾 Backup created: {backup_path}")

            # Write modified content
            file_path.write_text(modified_content, encoding='utf-8')
            print(f"✅ File updated: {file_path}")

            return True
    else:
        print("\n✓ No changes needed - file already clean")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cleanup_single_file.py <filename> [--dry-run]")
        print(f"\nFiles that need cleaning ({len(FILES_TO_CLEAN)}):")
        for i, f in enumerate(FILES_TO_CLEAN, 1):
            print(f"  {i:2d}. {f}")
        sys.exit(1)

    filename = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # Validate filename
    if filename not in FILES_TO_CLEAN:
        print(f"⚠️  Warning: {filename} not in the cleanup list")
        print("Continue anyway? [y/N]: ", end='')
        response = input()
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)

    # Process the file
    success = process_file(filename, dry_run)

    if success:
        print("\n" + "=" * 80)
        if dry_run:
            print("DRY RUN COMPLETE")
            print("Remove --dry-run to apply changes")
        else:
            print("CLEANUP COMPLETE")
            print(f"Review the file and verify changes look good")
        print("=" * 80)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
