"""
AIFP Helper Functions - User Preferences

Helpers for managing user_preferences.db - the per-project database
for AI behavior customization and tracking settings.

Tables managed:
- user_settings: Project-wide settings (key-value pairs)
- directive_preferences: Per-directive behavior customizations
- tracking_settings: Feature flags for opt-in tracking (all disabled by default)
- tracking_notes: Notes for tracking/debugging (when tracking enabled)
- ai_interaction_log: User correction logs (when tracking enabled)
- fp_flow_tracking: FP directive usage tracking (when tracking enabled)

Modules:
- validation.py: CHECK constraint extraction
- schema.py: Schema introspection (tables, fields, schema)
- crud.py: Generic CRUD operations
- management.py: Specialized operations (directive prefs, user settings, tracking)
"""
