-- Standard User Settings
-- Populated during project initialization with default values
-- User can modify via update_user_setting helper

INSERT OR IGNORE INTO user_settings (setting_key, setting_value, description, scope) VALUES
  ('backup_count', '3', 'Maximum number of backup zip files to retain', 'project'),
  ('backup_duration', '30', 'Days of project inactivity before auto-backup triggers on new session', 'project'),
  ('backup_path', '.aifp-project', 'Directory to store backup zip files (relative to project root)', 'project');
