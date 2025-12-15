#!/usr/bin/env python3
"""Preview what the cleanup script would do to specific sections."""

import re

# Test Pattern 1: Workflow step with SQL block
test1_before = """  - Update database:
    ```sql
    INSERT INTO notes (
      content,
      note_type,
      source,
      directive_name
    ) VALUES (
      'Converted sequential calls to pipeline in process_data',
      'research',
      'directive',
      'fp_chaining'
    );
    ```
- **Result**: Sequential calls chained in pipeline"""

# Test Pattern 2: SQL in Python code block
test2_before = """```python
# Database log
INSERT INTO notes (
  content,
  note_type,
  source,
  directive_name
) VALUES (
  'Converted nested calls to pipeline in process function',
  'research',
  'directive',
  'fp_chaining'
);

# Result:
# ✅ Clear linear flow
```"""

# Improved regex patterns
def remove_notes_insert_sql(content):
    # Pattern 1: Remove "Update database:" line + SQL block with INSERT INTO notes
    pattern1 = r'- Update database:\s*\n\s*```sql\s*\n.*?INSERT INTO notes.*?\n.*?```'
    modified_content = re.sub(pattern1, '', content, flags=re.DOTALL)

    # Pattern 2: Remove standalone SQL blocks with INSERT INTO notes (no prefix)
    pattern2 = r'```sql\s*\n.*?INSERT INTO notes.*?\n.*?```'
    modified_content = re.sub(pattern2, '', modified_content, flags=re.DOTALL)

    # Pattern 3: Remove INSERT INTO notes from inside Python/other code blocks
    pattern3 = r'#\s*Database log\s*\n\s*INSERT INTO notes.*?;'
    modified_content = re.sub(pattern3, '', modified_content, flags=re.DOTALL)

    # Pattern 4: Remove any remaining standalone INSERT INTO notes statements
    pattern4 = r'INSERT INTO notes[^;]*;'
    modified_content = re.sub(pattern4, '', modified_content)

    return modified_content

print("=" * 80)
print("PATTERN 1: Workflow step with SQL block")
print("=" * 80)
print("\nBEFORE:")
print(test1_before)
print("\nAFTER (current script):")
test1_after = remove_notes_insert_sql(test1_before)
print(test1_after)
print("\n⚠ PROBLEM: 'Update database:' left hanging")

print("\n" + "=" * 80)
print("PATTERN 2: SQL in Python code block")
print("=" * 80)
print("\nBEFORE:")
print(test2_before)
print("\nAFTER (current script):")
test2_after = remove_notes_insert_sql(test2_before)
print(test2_after)
print("\n⚠ PROBLEM: SQL not removed (inside Python code block)")
