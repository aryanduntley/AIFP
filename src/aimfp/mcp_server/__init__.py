"""
AIMFP MCP Server Package

Exposes AIMFP helper functions as MCP tools for AI assistants.
Communicates over stdio using the Model Context Protocol.

Usage:
    python -m aimfp
"""

from .server import run_server

__all__ = ["run_server"]
