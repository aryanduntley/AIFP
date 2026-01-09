#!/usr/bin/env python3
"""
FP Directive Cleanup Script

Automatically cleans up FP directive files to:
1. Remove invalid note_type references
2. Add correct tracking context
3. Clarify FP compliance is baseline behavior
4. Ensure consistency across all FP directives

Usage:
    python cleanup_fp_directives.py [--dry-run] [--file FILE]
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple
import argparse
from datetime import datetime

# Valid note_types from schema
VALID_NOTE_TYPES = {
    'clarification', 'pivot', 'research', 'entry_deletion',
    'warning', 'error', 'info', 'auto_summary',
    'decision', 'evolution', 'analysis', 'task_context',
    'external', 'summary'
}

# Invalid note_types found in FP directives
INVALID_NOTE_TYPES = {
    'compliance', 'refactoring', 'optimization', 'wrapper',
    'validation', 'security', 'normalization', 'documentation',
    'metadata', 'indexing', 'determinism', 'formatting',
    'cleanup', 'performance', 'reasoning_trace'
}

# Template for Database Operations section
DATABASE_OPS_TEMPLATE = '''## Database Operations

**Project Database** (project.db):
{existing_ops}

**FP Compliance Tracking** (Optional - Disabled by Default):

This directive does NOT automatically log to project.db notes table.

If `fp_flow_tracking` is enabled in user_preferences.db (via `tracking_toggle`):
- AI may log FP pattern usage to `fp_flow_tracking` table
- Located in user_preferences.db, NOT project.db
- Token overhead: ~5% per file write
- Used for analytics and development only

**Important Context**:
- FP compliance is baseline behavior (enforced by system prompt during code writing)
- This directive is reference documentation consulted when AI is uncertain
- NO post-write validation occurs
- NO automatic logging to project.db
- Tracking is opt-in for AIFP development and debugging

**Example** (only if tracking explicitly enabled):
```sql
-- Logs to user_preferences.db.fp_flow_tracking (NOT project.db)
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    issues_json,
    created_at
) VALUES (
    'function_name',
    'src/file.py',
    '{fp_directives_list}',
    1.0,
    NULL,
    CURRENT_TIMESTAMP
);
```

**Note**: Most users will never enable fp_flow_tracking. It's primarily for:
- AIFP development and testing
- Project audits requiring compliance documentation
- Research on FP pattern adoption
'''

# Purpose section addition
PURPOSE_ADDITION = '''
**Important**: This directive is reference documentation for complex FP scenarios.
AI consults this when uncertain about implementation details or edge cases.

**NOT used for**:
- ❌ Post-write validation (FP is baseline, code is already compliant)
- ❌ Automatic checking (no validation loop)
- ❌ Standard logging (tracking is opt-in, disabled by default)
'''

# When to Apply section addition
WHEN_TO_APPLY_ADDITION = '''
**NOT applied automatically**:
- NOT called after every file write
- NOT used for validation
- Only consulted when AI needs guidance
'''


def extract_directive_name(content: str) -> str:
    """Extract directive name from file content."""
    match = re.search(r'#\s*Directive:\s*(\w+)', content)
    if match:
        return match.group(1)
    return 'unknown_directive'


def find_database_operations_section(content: str) -> Tuple[int, int]:
    """
    Find the Database Operations section.
    Returns (start_pos, end_pos) or (-1, -1) if not found.
    """
    # Find "## Database Operations"
    pattern = r'^## Database Operations\s*$'
    match = re.search(pattern, content, re.MULTILINE)

    if not match:
        return (-1, -1)

    start_pos = match.start()

    # Find next ## section or end of file
    next_section = re.search(r'\n## ', content[match.end():])
    if next_section:
        end_pos = match.end() + next_section.start()
    else:
        end_pos = len(content)

    return (start_pos, end_pos)


def extract_existing_operations(db_ops_section: str) -> List[str]:
    """
    Extract existing database operations (non-notes entries).
    Returns list of operation bullet points.
    """
    operations = []

    # Find all bullet points
    for line in db_ops_section.split('\n'):
        # Skip the header
        if line.strip().startswith('## Database Operations'):
            continue

        # Find bullet points with database table references
        if re.match(r'^\s*-\s+\*\*`\w+`\*\*:', line):
            # Skip notes table references
            if '`notes`' not in line or 'note_type' not in line:
                operations.append(line.strip())

    return operations


def has_invalid_note_type(content: str) -> bool:
    """Check if content has invalid note_type references."""
    pattern = r'note_type\s*=\s*[\'"](\w+)[\'"]'
    matches = re.findall(pattern, content)

    for note_type in matches:
        if note_type in INVALID_NOTE_TYPES:
            return True

    return False


def get_invalid_note_types(content: str) -> List[str]:
    """Get list of invalid note_types in content."""
    pattern = r'note_type\s*=\s*[\'"](\w+)[\'"]'
    matches = re.findall(pattern, content)

    invalid = []
    for note_type in matches:
        if note_type in INVALID_NOTE_TYPES:
            invalid.append(note_type)

    return list(set(invalid))


def cleanup_database_operations(content: str, directive_name: str) -> str:
    """
    Replace Database Operations section with corrected version.
    """
    start_pos, end_pos = find_database_operations_section(content)

    if start_pos == -1:
        print(f"  ⚠ No Database Operations section found")
        return content

    # Extract existing section
    db_ops_section = content[start_pos:end_pos]

    # Extract non-notes operations
    existing_ops = extract_existing_operations(db_ops_section)

    if not existing_ops:
        existing_ops_text = "- (No project database operations for this directive)"
    else:
        existing_ops_text = '\n'.join(existing_ops)

    # Build fp_directives_list for example
    fp_directives_list = f'["{directive_name}"]'

    # Generate new section
    new_section = DATABASE_OPS_TEMPLATE.format(
        existing_ops=existing_ops_text,
        fp_directives_list=fp_directives_list
    )

    # Replace section
    new_content = content[:start_pos] + new_section + content[end_pos:]

    return new_content


def add_purpose_clarification(content: str) -> str:
    """Add FP reference clarification to Purpose section if not present."""
    # Check if already has the clarification
    if 'reference documentation' in content and 'NOT used for' in content:
        return content

    # Find Purpose section
    purpose_match = re.search(r'^## Purpose\s*$', content, re.MULTILINE)
    if not purpose_match:
        return content

    # Find next section
    next_section = re.search(r'\n## ', content[purpose_match.end():])
    if not next_section:
        return content

    insert_pos = purpose_match.end() + next_section.start()

    # Insert before next section
    new_content = content[:insert_pos] + '\n' + PURPOSE_ADDITION + '\n' + content[insert_pos:]

    return new_content


def add_when_to_apply_clarification(content: str) -> str:
    """Add automatic application clarification to When to Apply section."""
    # Check if already has the clarification
    if 'NOT applied automatically' in content:
        return content

    # Find When to Apply section
    when_match = re.search(r'^## When to Apply\s*$', content, re.MULTILINE)
    if not when_match:
        return content

    # Find next section
    next_section = re.search(r'\n## ', content[when_match.end():])
    if not next_section:
        return content

    insert_pos = when_match.end() + next_section.start()

    # Insert before next section
    new_content = content[:insert_pos] + '\n' + WHEN_TO_APPLY_ADDITION + '\n' + content[insert_pos:]

    return new_content


def cleanup_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """
    Clean up a single FP directive file.
    Returns (modified, changes) tuple.
    """
    try:
        content = file_path.read_text()
        original_content = content
        changes = []

        # Extract directive name
        directive_name = extract_directive_name(content)

        # Check if has invalid note_types
        invalid_types = get_invalid_note_types(content)
        if not invalid_types:
            return (False, ["No invalid note_types found"])

        changes.append(f"Found invalid note_types: {', '.join(invalid_types)}")

        # 1. Clean up Database Operations section
        content = cleanup_database_operations(content, directive_name)
        if content != original_content:
            changes.append("✓ Replaced Database Operations section")
            original_content = content

        # 2. Add Purpose clarification
        content = add_purpose_clarification(content)
        if content != original_content:
            changes.append("✓ Added Purpose clarification")
            original_content = content

        # 3. Add When to Apply clarification
        content = add_when_to_apply_clarification(content)
        if content != original_content:
            changes.append("✓ Added When to Apply clarification")

        # Write back if modified and not dry-run
        if content != file_path.read_text() and not dry_run:
            file_path.write_text(content)
            changes.append("✓ File updated")
        elif dry_run:
            changes.append("(Dry run - no changes written)")

        return (True, changes)

    except Exception as e:
        return (False, [f"Error: {e}"])


def create_backup(directives_dir: Path) -> Path:
    """Create backup directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = directives_dir.parent.parent.parent / "docs" / "backups" / f"fp_directives_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def main():
    parser = argparse.ArgumentParser(description='Clean up FP directive files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--file', type=str, help='Process single file only')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    args = parser.parse_args()

    # Find directives directory
    script_dir = Path(__file__).parent
    directives_dir = script_dir.parent / "src" / "aifp" / "reference" / "directives"

    if not directives_dir.exists():
        print(f"Error: Directives directory not found: {directives_dir}")
        return 1

    # Create backup unless disabled
    if not args.no_backup and not args.dry_run:
        backup_dir = create_backup(directives_dir)
        print(f"📦 Backup created: {backup_dir}")

        # Copy all FP directive files to backup
        for fp_file in directives_dir.glob("fp_*.md"):
            import shutil
            shutil.copy2(fp_file, backup_dir / fp_file.name)

        print(f"   Backed up {len(list(backup_dir.glob('*.md')))} files\n")

    # Process files
    if args.file:
        # Single file
        file_path = directives_dir / args.file
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return 1

        files_to_process = [file_path]
    else:
        # All FP directive files
        files_to_process = sorted(directives_dir.glob("fp_*.md"))

    print(f"Processing {len(files_to_process)} files...\n")

    # Process each file
    modified_count = 0
    skipped_count = 0

    for file_path in files_to_process:
        print(f"📄 {file_path.name}")

        modified, changes = cleanup_file(file_path, dry_run=args.dry_run)

        if modified:
            modified_count += 1
            for change in changes:
                print(f"   {change}")
        else:
            skipped_count += 1
            for change in changes:
                print(f"   {change}")

        print()

    # Summary
    print("="*60)
    print(f"Summary:")
    print(f"  Modified: {modified_count} files")
    print(f"  Skipped:  {skipped_count} files")

    if args.dry_run:
        print(f"\n⚠️  DRY RUN - No files were actually modified")
        print(f"   Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Cleanup complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
