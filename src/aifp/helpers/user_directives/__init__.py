"""
AIFP Helper Functions - User Directives

Helpers for managing user_directives.db - the per-project database
for Use Case 2 (custom automation) directive management.

Tables managed:
- user_directives: User-defined automation directives
- directive_executions: Execution statistics per directive
- directive_dependencies: Required packages/APIs
- directive_implementations: Generated code tracking
- directive_relationships: Inter-directive dependencies
- helper_functions: Directive-specific helper functions
- directive_helpers: Many-to-many helper-directive links
- source_files: User's directive source file tracking
- logging_config: Logging configuration (single row)
- notes: AI record-keeping notes

Modules:
- validation.py: CHECK constraint extraction
- schema.py: Schema introspection (tables, fields, schema)
- crud.py: Generic CRUD operations + convenience queries
- management.py: Specialized operations (get by name, activate, deactivate, notes)
"""
