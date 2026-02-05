"""
AIFP MCP Server Entry Point

Enables running the MCP server via: python -m aifp

The server communicates over stdio using the Model Context Protocol,
exposing AIFP helper functions as tools for AI assistants.
"""

from .mcp_server import run_server


def main() -> None:
    """Start the AIFP MCP server."""
    run_server()


if __name__ == "__main__":
    main()
