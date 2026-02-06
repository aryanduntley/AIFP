"""
AIFP Test Suite - Root conftest

Shared fixtures for all tests.
Adds src/ to Python path for imports.
"""

import sys
from pathlib import Path

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
