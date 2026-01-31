"""
AIFP Helper Functions - Global Supportive Context

Returns the full supportive context reference document for AI sessions.
Loaded automatically by aifp_run(is_new_session=true).
Call directly to reload detailed reference material when context feels stale.

All functions are pure FP - immutable data, explicit parameters, Result types.

Helpers in this file:
- get_supportive_context: Read and return supportive_context.txt content
"""

from pathlib import Path
from typing import Tuple

# Import global utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_return_statements, Result


# ============================================================================
# Constants
# ============================================================================

SUPPORTIVE_CONTEXT_PATH: str = str(
    Path(__file__).parent.parent.parent / "reference" / "guides" / "supportive_context.txt"
)


# ============================================================================
# Public Helper Functions
# ============================================================================

def get_supportive_context() -> Result:
    """
    Read and return the full supportive context reference document.

    Contains: FP code examples, state database patterns, DRY scope levels,
    project discovery/progression details, directive execution details,
    reserve-write-finalize flow, Use Case 2 architecture, user preferences
    system, Git+FP collaboration, edge case recovery, session management.

    Returns:
        Result with data={
            content: str (full text of supportive_context.txt),
            token_estimate: int (approximate token count),
            source: str (file path)
        }

    On error:
        Result with error message if file not found or unreadable.

    Example:
        >>> result = get_supportive_context()
        >>> if result.success:
        ...     print(result.data['token_estimate'])
        3500
    """
    try:
        context_path = Path(SUPPORTIVE_CONTEXT_PATH)

        if not context_path.is_file():
            return Result(
                success=False,
                error=f"Supportive context file not found: {context_path}. "
                      "Expected at src/aifp/reference/guides/supportive_context.txt",
            )

        content = context_path.read_text(encoding="utf-8")

        # Rough token estimate: ~1 token per 4 characters
        token_estimate = len(content) // 4

        return Result(
            success=True,
            data={
                'content': content,
                'token_estimate': token_estimate,
                'source': str(context_path),
            },
            return_statements=get_return_statements("get_supportive_context"),
        )

    except Exception as e:
        return Result(
            success=False,
            error=f"Error reading supportive context: {str(e)}",
        )
