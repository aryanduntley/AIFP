#!/usr/bin/env python3
"""
Clean up FP directive MD files - Remove inappropriate standard logging.

Problem:
- FP directives document "INSERT INTO notes" as standard behavior
- fp_flow_tracking is DISABLED BY DEFAULT and costs ~5% more tokens
- Logging should be opt-in for debugging, not standard practice

Solution:
- Remove SQL INSERT INTO notes examples from workflows
- Add conditional notes about fp_flow_tracking
- Update Database Operations sections with "(only if fp_flow_tracking enabled)"
"""

import re
import os
from pathlib import Path
from datetime import datetime

# Directive files directory
DIRECTIVES_DIR = Path("/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives")
BACKUP_DIR = Path("/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/backups")

# Files to process
FP_FILES = [
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
    backup_path = BACKUP_DIR / "fp_logging_cleanup" / backup_name
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return backup_path


def remove_notes_insert_sql(content):
    """
    Remove SQL INSERT INTO notes blocks from workflow sections.

    Handles two patterns:
    1. Standalone SQL blocks with "Update database:" prefix
    2. SQL inside Python/other code blocks (comments)
    """
    # Pattern 1: Remove "Update database:" line + SQL block with INSERT INTO notes
    # This handles: "- Update database:\n    ```sql\n    INSERT INTO notes...```"
    pattern1 = r'- Update database:\s*\n\s*```sql\s*\n.*?INSERT INTO notes.*?\n.*?```'
    modified_content = re.sub(pattern1, '', content, flags=re.DOTALL)

    # Pattern 2: Remove standalone SQL blocks with INSERT INTO notes (no prefix)
    pattern2 = r'```sql\s*\n.*?INSERT INTO notes.*?\n.*?```'
    modified_content = re.sub(pattern2, '', modified_content, flags=re.DOTALL)

    # Pattern 3: Remove INSERT INTO notes from inside Python/other code blocks
    # Look for "# Database log" comment followed by INSERT INTO notes
    pattern3 = r'#\s*Database log\s*\n\s*INSERT INTO notes.*?;'
    modified_content = re.sub(pattern3, '', modified_content, flags=re.DOTALL)

    # Pattern 4: Remove any remaining standalone INSERT INTO notes statements
    pattern4 = r'INSERT INTO notes[^;]*;'
    modified_content = re.sub(pattern4, '', modified_content)

    return modified_content


def add_conditional_logging_note(content):
    """
    Add note about conditional logging after workflow sections.

    Look for patterns like:
    - **Result**: [something]

    And add logging note if not present.
    """
    # Check if conditional logging note already exists
    if "fp_flow_tracking enabled" in content:
        return content

    # Pattern: Look for "## Workflow" section and add note at end
    # This is a simple approach - add note before "---" or "##" after workflow

    # Find the workflow section
    workflow_pattern = r'(## Workflow.*?)(\n---|\n##)'

    def add_note(match):
        workflow_section = match.group(1)
        delimiter = match.group(2)

        # Check if note already in this section
        if "fp_flow_tracking" in workflow_section or "Logging only occurs" in workflow_section:
            return match.group(0)

        note = """

**Note on Logging**: The workflow above describes the directive's logic. Database logging (INSERT INTO notes) only occurs if `fp_flow_tracking` is enabled. This feature is **disabled by default** as it costs ~5% more tokens and should only be used temporarily for debugging.
"""
        return workflow_section + note + delimiter

    modified_content = re.sub(workflow_pattern, add_note, content, flags=re.DOTALL)
    return modified_content


def update_database_operations_section(content):
    """
    Update Database Operations section to indicate conditional logging.

    Change:
    - **`notes`**: INSERT compliance violations

    To:
    - **`notes`**: INSERT compliance violations (only if `fp_flow_tracking` enabled - disabled by default)
    """
    # Pattern: - **`notes`**: INSERT [something]
    pattern = r'(\*\*`notes`\*\*:.*?INSERT[^\n]*?)(\n|$)'

    def add_conditional(match):
        line = match.group(1)
        ending = match.group(2)

        # Check if already has conditional note
        if "fp_flow_tracking" in line or "disabled by default" in line:
            return match.group(0)

        # Add conditional note
        return f"{line} (only if `fp_flow_tracking` enabled - disabled by default){ending}"

    modified_content = re.sub(pattern, add_conditional, content)
    return modified_content


def clean_empty_sql_blocks(content):
    """Remove empty SQL code blocks left after removal."""
    # Pattern: Empty SQL blocks or blocks with just whitespace/comments
    pattern = r'```sql\s*(?:--[^\n]*)?\s*```'
    return re.sub(pattern, '', content)


def clean_multiple_blank_lines(content):
    """Reduce multiple consecutive blank lines to max 2."""
    return re.sub(r'\n{4,}', '\n\n\n', content)


def process_file(file_path, dry_run=False):
    """Process a single directive file."""
    print(f"\nProcessing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Track changes
    changes = []

    # Step 1: Remove INSERT INTO notes SQL blocks
    modified_content = remove_notes_insert_sql(original_content)
    if modified_content != original_content:
        sql_blocks_removed = original_content.count("INSERT INTO notes") - modified_content.count("INSERT INTO notes")
        changes.append(f"Removed {sql_blocks_removed} 'INSERT INTO notes' SQL block(s)")

    # Step 2: Add conditional logging note
    modified_content = add_conditional_logging_note(modified_content)
    if "fp_flow_tracking enabled" in modified_content and "fp_flow_tracking enabled" not in original_content:
        changes.append("Added conditional logging note to workflow")

    # Step 3: Update Database Operations section
    modified_content = update_database_operations_section(modified_content)
    if "only if `fp_flow_tracking` enabled" in modified_content and "only if `fp_flow_tracking` enabled" not in original_content:
        changes.append("Updated Database Operations section with conditional clause")

    # Step 4: Clean up empty SQL blocks
    modified_content = clean_empty_sql_blocks(modified_content)

    # Step 5: Clean up excessive blank lines
    modified_content = clean_multiple_blank_lines(modified_content)

    # Report changes
    if changes:
        print(f"  Changes:")
        for change in changes:
            print(f"    - {change}")

        if not dry_run:
            # Create backup
            backup_path = create_backup(file_path)
            print(f"  Backup: {backup_path}")

            # Write modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"  ✓ Updated")
        else:
            print(f"  [DRY RUN - no changes written]")
    else:
        print(f"  ✓ No changes needed")

    return len(changes) > 0


def main():
    import sys

    dry_run = "--dry-run" in sys.argv

    print("=" * 80)
    print("FP Directive Logging Cleanup")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Files to process: {len(FP_FILES)}")
    print()

    if dry_run:
        print("Running in DRY RUN mode - no files will be modified")
        print("Remove --dry-run to execute changes")
    else:
        print("WARNING: Files will be modified (backups will be created)")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return

    print()

    # Process each file
    modified_count = 0
    for filename in FP_FILES:
        file_path = DIRECTIVES_DIR / filename

        if not file_path.exists():
            print(f"\n⚠ File not found: {filename}")
            continue

        if process_file(file_path, dry_run):
            modified_count += 1

    # Summary
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Files processed: {len(FP_FILES)}")
    print(f"Files modified: {modified_count}")
    print(f"Files unchanged: {len(FP_FILES) - modified_count}")

    if dry_run:
        print()
        print("This was a DRY RUN - no files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print()
        print("✓ Cleanup complete")
        print(f"Backups saved to: {BACKUP_DIR / 'fp_logging_cleanup'}")


if __name__ == "__main__":
    main()
