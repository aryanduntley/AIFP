"""
AIFP MCP Server Package

Exposes AIFP helper functions as MCP tools for AI assistants.
Communicates over stdio using the Model Context Protocol.

Usage:
    python -m aifp
"""

from .server import run_server

__all__ = ["run_server"]
