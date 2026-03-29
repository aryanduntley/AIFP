#!/usr/bin/env python3
"""
Bulk rename: aimfp → aimfp, AIMFP → AIMFP across the codebase.
Skips docs/, .git/, build/, dist/, *.egg-info/, *.db, *.png, *.whl, *.tar.gz
Only processes: src/, dev/, sys-prompt/, tests/, examples/,
               aimfp-plugin/, .claude-plugin/, .github/,
               and root config files.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories to process
INCLUDE_DIRS = [
    ROOT / "src",
    ROOT / "dev",
    ROOT / "sys-prompt",
    ROOT / "tests",
    ROOT / "examples",
    ROOT / "aimfp-plugin",
    ROOT / ".claude-plugin",
    ROOT / ".github",
]

# Root files to process
ROOT_FILES = [
    "pyproject.toml",
    "manifest.json",
    "README.md",
    "CLAUDE.md",
    "aimfp.mcpb",
]

# Extensions to process
TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".sql", ".toml", ".yml", ".yaml",
    ".cfg", ".ini", ".mcpb", ".mcp",
}

# Skip patterns
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".egg-info", "build", "dist"}
SKIP_EXTENSIONS = {".db", ".png", ".jpg", ".whl", ".gz", ".zip"}

# Replacements — order matters: longer/more-specific first
REPLACEMENTS = [
    # Exact package/module references (lowercase)
    ("aimfp_core", "aimfp_core"),
    ("aimfp-project", "aimfp-project"),
    ("aimfp-plugin", "aimfp-plugin"),
    ("aimfp-mode", "aimfp-mode"),
    # Python module/import references
    ("from aimfp.", "from aimfp."),
    ("from aimfp ", "from aimfp "),
    ("import aimfp", "import aimfp"),
    ('"aimfp.', '"aimfp.'),
    ("'aimfp.", "'aimfp."),
    # Standalone package name in various contexts
    ('name = "aimfp"', 'name = "aimfp"'),
    ('"name": "aimfp"', '"name": "aimfp"'),
    ('"aimfp"', '"aimfp"'),
    ("'aimfp'", "'aimfp'"),
    # Tool/function name prefixes
    ("aimfp_run", "aimfp_run"),
    ("aimfp_init", "aimfp_init"),
    ("aimfp_status", "aimfp_status"),
    ("aimfp_end", "aimfp_end"),
    ("aimfp_help", "aimfp_help"),
    # Entry point / command references
    ("-m aimfp", "-m aimfp"),
    ("python -m aimfp", "python -m aimfp"),
    ("python3 -m aimfp", "python3 -m aimfp"),
    ("pip install aimfp", "pip install aimfp"),
    # Remaining lowercase aimfp (catch-all for paths, references)
    ("src/aimfp/", "src/aimfp/"),
    ("src/aimfp", "src/aimfp"),
    ("/aimfp/", "/aimfp/"),
    # URL references
    ("pypi.org/project/aimfp", "pypi.org/project/aimfp"),
    ("github.com/aryanduntley/aimfp", "github.com/aryanduntley/aimfp"),
    # Uppercase brand
    ("AIMFP", "AIMFP"),
    # Remaining lowercase catch-all (last — most general)
    ("aimfp", "aimfp"),
]


def should_process_file(path: Path) -> bool:
    if path.suffix in SKIP_EXTENSIONS:
        return False
    if path.suffix not in TEXT_EXTENSIONS:
        return False
    return True


def collect_files() -> list[Path]:
    files = []

    # Root files
    for name in ROOT_FILES:
        p = ROOT / name
        if p.exists():
            files.append(p)

    # Directory trees
    for d in INCLUDE_DIRS:
        if not d.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            # Prune skip dirs
            dirnames[:] = [dn for dn in dirnames if dn not in SKIP_DIRS]
            for fn in filenames:
                fp = Path(dirpath) / fn
                if should_process_file(fp):
                    files.append(fp)

    return files


def rename_content(text: str) -> str:
    result = text
    for old, new in REPLACEMENTS:
        result = result.replace(old, new)
    return result


def main():
    files = collect_files()
    changed = 0
    unchanged = 0
    errors = []

    for fp in files:
        try:
            original = fp.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            errors.append((fp, str(e)))
            continue

        updated = rename_content(original)
        if updated != original:
            fp.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"  UPDATED: {fp.relative_to(ROOT)}")
        else:
            unchanged += 1

    print(f"\n--- Summary ---")
    print(f"  Files updated:   {changed}")
    print(f"  Files unchanged: {unchanged}")
    if errors:
        print(f"  Errors:          {len(errors)}")
        for fp, err in errors:
            print(f"    {fp.relative_to(ROOT)}: {err}")


if __name__ == "__main__":
    main()
