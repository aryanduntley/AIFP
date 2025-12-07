#!/usr/bin/env python3
"""
Remove helper references from directive JSON files.

This script removes all helper-related fields from directive JSON files:
- "helper" fields (exact match)
- "helper_*" variant fields (helper_project_db, helper_prefs_db, etc.)
- "call_helper" fields
- "helper_functions" top-level sections

Modes:
- --dry-run: Show what would be removed without making changes
- --execute: Create backups and remove helper references
- --restore: Restore from backups
"""

import json
import os
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


def remove_helper_refs_recursive(obj: Any, removed: List[Dict] = None) -> Tuple[Any, List[Dict]]:
    """
    Recursively remove helper reference fields from JSON object.

    Args:
        obj: JSON object (dict, list, or primitive)
        removed: List to accumulate removed items

    Returns:
        Tuple of (modified_obj, removed_items_list)
    """
    if removed is None:
        removed = []

    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # Check if this is a helper reference field to remove
            if key == "helper" or key.startswith("helper_") or key == "call_helper":
                removed.append({
                    "field_name": key,
                    "field_value": value
                })
                # Skip this field (don't add to new_dict)
                continue

            # Recurse into nested structures
            new_value, removed = remove_helper_refs_recursive(value, removed)
            new_dict[key] = new_value

        return new_dict, removed

    elif isinstance(obj, list):
        new_list = []
        for item in obj:
            new_item, removed = remove_helper_refs_recursive(item, removed)
            new_list.append(new_item)
        return new_list, removed

    else:
        # Primitive value, return as-is
        return obj, removed


def backup_file(file_path: Path, backup_dir: Path) -> Path:
    """
    Create timestamped backup of file.

    Args:
        file_path: File to backup
        backup_dir: Directory for backups

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    return backup_path


def process_file(file_path: Path, dry_run: bool = True, backup_dir: Path = None) -> Dict[str, Any]:
    """
    Process a single directive JSON file.

    Args:
        file_path: Path to directive JSON file
        dry_run: If True, show changes without writing
        backup_dir: Directory for backups (required if not dry_run)

    Returns:
        Dict with processing results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # Remove helper references
        cleaned_data, removed_items = remove_helper_refs_recursive(original_data)

        result = {
            "file": str(file_path.name),
            "removed_count": len(removed_items),
            "removed_items": removed_items,
            "status": "success"
        }

        if not dry_run:
            if backup_dir is None:
                raise ValueError("backup_dir required when not in dry_run mode")

            # Create backup
            backup_path = backup_file(file_path, backup_dir)
            result["backup_path"] = str(backup_path)

            # Write cleaned data back to original file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            result["action"] = "cleaned"
        else:
            result["action"] = "dry_run"

        return result

    except Exception as e:
        return {
            "file": str(file_path.name),
            "error": str(e),
            "status": "error"
        }


def restore_from_backup(backup_dir: Path, target_dir: Path) -> List[Dict[str, Any]]:
    """
    Restore directive files from most recent backups.

    Args:
        backup_dir: Directory containing backups
        target_dir: Directory to restore files to

    Returns:
        List of restoration results
    """
    if not backup_dir.exists():
        return [{"error": f"Backup directory not found: {backup_dir}", "status": "error"}]

    # Group backups by original filename
    backups = {}
    for backup_file in backup_dir.glob("*.json"):
        # Extract original filename (everything before timestamp)
        # Example: directives-project_20251207_143022.json -> directives-project
        parts = backup_file.stem.split("_")
        if len(parts) >= 3:  # name_date_time
            original_name = "_".join(parts[:-2])  # Everything except last 2 parts
            timestamp = "_".join(parts[-2:])

            if original_name not in backups:
                backups[original_name] = []
            backups[original_name].append((timestamp, backup_file))

    # Restore most recent backup for each file
    results = []
    for original_name, backup_list in backups.items():
        # Sort by timestamp (most recent first)
        backup_list.sort(reverse=True, key=lambda x: x[0])
        most_recent_backup = backup_list[0][1]

        target_file = target_dir / f"{original_name}.json"

        try:
            shutil.copy2(most_recent_backup, target_file)
            results.append({
                "file": target_file.name,
                "restored_from": most_recent_backup.name,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "file": target_file.name,
                "error": str(e),
                "status": "error"
            })

    return results


def print_results(results: List[Dict[str, Any]], mode: str):
    """Print processing results to console."""
    print("\n" + "="*70)
    if mode == "dry_run":
        print("DRY RUN - HELPER REFERENCE REMOVAL PREVIEW")
    elif mode == "execute":
        print("HELPER REFERENCE REMOVAL RESULTS")
    elif mode == "restore":
        print("BACKUP RESTORATION RESULTS")
    print("="*70)

    total_removed = sum(r.get("removed_count", 0) for r in results)
    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")

    if mode in ["dry_run", "execute"]:
        print(f"\n📊 SUMMARY:")
        print(f"   Files processed: {len(results)}")
        print(f"   Successful: {success_count}")
        print(f"   Errors: {error_count}")
        print(f"   Total refs removed: {total_removed}")

        print(f"\n📁 DETAILED RESULTS:")
        for result in results:
            if result["status"] == "error":
                print(f"\n   ❌ {result['file']}")
                print(f"      Error: {result['error']}")
            elif result.get("removed_count", 0) > 0:
                print(f"\n   ✓ {result['file']} ({result['removed_count']} refs removed)")

                if mode == "execute" and "backup_path" in result:
                    print(f"      Backup: {Path(result['backup_path']).name}")

                for item in result.get("removed_items", []):
                    print(f"      • Removed: {item['field_name']} = \"{str(item['field_value'])[:60]}...\"")
            else:
                print(f"\n   ✓ {result['file']} (no changes needed)")

    elif mode == "restore":
        print(f"\n📊 SUMMARY:")
        print(f"   Files restored: {success_count}")
        print(f"   Errors: {error_count}")

        print(f"\n📁 RESTORED FILES:")
        for result in results:
            if result["status"] == "error":
                print(f"   ❌ {result['file']}: {result['error']}")
            else:
                print(f"   ✓ {result['file']} <- {result['restored_from']}")

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Remove helper references from directive JSON files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without making changes"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create backups and remove helper references"
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore files from most recent backups"
    )

    args = parser.parse_args()

    # Validate arguments
    if not (args.dry_run or args.execute or args.restore):
        parser.error("Must specify --dry-run, --execute, or --restore")
    if sum([args.dry_run, args.execute, args.restore]) > 1:
        parser.error("Can only specify one mode: --dry-run, --execute, or --restore")

    # Paths
    directives_dir = Path(__file__).parent.parent
    backup_dir = directives_dir / "backups"

    # Directive JSON files to process
    directive_files = [
        "directives-project.json",
        "directives-fp-core.json",
        "directives-fp-aux.json",
        "directives-user-system.json",
        "directives-user-pref.json",
        "directives-git.json"
    ]

    if args.restore:
        # Restore mode
        print(f"🔄 Restoring directive files from backups...")
        print(f"📂 Backup directory: {backup_dir}")
        print(f"📂 Target directory: {directives_dir}")

        results = restore_from_backup(backup_dir, directives_dir)
        print_results(results, "restore")

    else:
        # Dry run or execute mode
        mode = "dry_run" if args.dry_run else "execute"

        if args.execute:
            print(f"🗑️  Removing helper references from directive JSON files...")
            print(f"📂 Directory: {directives_dir}")
            print(f"💾 Backups will be saved to: {backup_dir}")
            backup_dir.mkdir(exist_ok=True)
        else:
            print(f"👁️  DRY RUN - Previewing helper reference removal...")
            print(f"📂 Directory: {directives_dir}")

        results = []
        for filename in directive_files:
            file_path = directives_dir / filename
            if file_path.exists():
                print(f"   Processing: {filename}")
                result = process_file(file_path, dry_run=args.dry_run, backup_dir=backup_dir)
                results.append(result)
            else:
                print(f"   ⚠ Skipping: {filename} (not found)")
                results.append({
                    "file": filename,
                    "error": "File not found",
                    "status": "error"
                })

        print_results(results, mode)

        if args.dry_run:
            print(f"\n💡 TIP: Run with --execute to apply these changes")
            print(f"   Backups will be saved to: {backup_dir}")
        else:
            print(f"\n✅ Changes applied! Backups saved to: {backup_dir}")
            print(f"   To undo: python3 {Path(__file__).name} --restore")


if __name__ == "__main__":
    main()
