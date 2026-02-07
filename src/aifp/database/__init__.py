"""
AIFP Database - Foundation Layer

Provides all database connection management, path resolution,
result types, and query utilities used throughout the AIFP package.

This is the single source of truth for database operations.
All other modules import from here — no direct sqlite3 usage elsewhere.
"""
