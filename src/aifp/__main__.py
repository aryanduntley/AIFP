"""
AIFP MCP Server Entry Point

Enables running the MCP server via: python -m aifp

The server communicates over stdio using the Model Context Protocol,
exposing AIFP helper functions as tools for AI assistants.

Usage:
    python -m aifp                  Start the MCP server (stdio)
    python -m aifp --system-prompt  Print the AIFP system prompt to stdout
"""

import sys
from pathlib import Path


def main() -> None:
    """Start the AIFP MCP server, or print system prompt if --system-prompt flag is given."""
    if "--system-prompt" in sys.argv:
        prompt_path = Path(__file__).parent / "reference" / "system_prompt.txt"
        if not prompt_path.exists():
            print("Error: system_prompt.txt not found at expected location:", file=sys.stderr)
            print(f"  {prompt_path}", file=sys.stderr)
            sys.exit(1)
        print(prompt_path.read_text(), end="")
        return

    from .mcp_server import run_server
    run_server()


if __name__ == "__main__":
    main()
