# Directive: fp_encoding_consistency

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - File format standardization for consistency

---

## Purpose

The `fp_encoding_consistency` directive verifies and enforces UTF-8 encoding, consistent newline characters, and uniform indentation styles across all generated AIFP code files. This directive provides **file format consistency** that ensures code portability and prevents encoding-related bugs.

Encoding consistency provides **universal file compatibility**, enabling:
- **Cross-Platform Portability**: Files work identically on Windows, Linux, macOS
- **No Encoding Bugs**: Prevent mojibake and encoding errors
- **Git-Friendly**: Consistent line endings avoid merge conflicts
- **Tool Compatibility**: All editors and tools read files correctly
- **International Support**: UTF-8 handles all human languages

This directive acts as a **file format guardian** ensuring all generated code follows universal standards.

---

## When to Apply

This directive applies when:
- **Writing new files** - Ensure proper encoding from start
- **Editing existing files** - Verify encoding not corrupted
- **Cross-platform development** - Team uses different operating systems
- **International characters** - Code contains non-ASCII characters
- **Git repository** - Ensure consistent line endings
- **Called by project directives**:
  - `project_file_write` - Validate encoding before writing
  - Works with all FP directives - Ensure generated code is properly encoded
  - `git_detect_external_changes` - Detect encoding changes

---

## Workflow

### Trunk: check_file_encoding

Analyzes file encoding, line endings, and indentation to ensure consistency with AIFP standards.

**Steps**:
1. **Detect current encoding** - Read file byte signature and content
2. **Check line endings** - Detect CRLF (Windows) vs LF (Unix)
3. **Analyze indentation** - Check tabs vs spaces, indentation width
4. **Validate UTF-8** - Ensure valid UTF-8 byte sequences
5. **Check BOM presence** - Detect UTF-8 BOM (not recommended)
6. **Apply fixes** - Convert to standard format if needed

### Branches

**Branch 1: If non_utf8_encoding**
- **Then**: `convert_to_utf8`
- **Details**: File uses non-UTF-8 encoding
  - Detect encoding (Latin-1, Windows-1252, etc.)
  - Convert content to UTF-8
  - Preserve character meaning
  - Warn if lossy conversion
  - Write UTF-8 file
- **Result**: Returns UTF-8 encoded content

**Branch 2: If inconsistent_line_endings**
- **Then**: `normalize_newlines`
- **Details**: File has mixed or wrong line endings
  - Mixed CRLF and LF in same file
  - Convert all to LF (Unix standard)
  - AIFP Standard: LF only
  - Update .gitattributes if needed
- **Result**: Returns normalized content

**Branch 3: If inconsistent_indentation**
- **Then**: `standardize_indentation`
- **Details**: File uses inconsistent indentation
  - Mixed tabs and spaces
  - Inconsistent indentation width
  - AIFP Standard: 4 spaces (Python), 2 spaces (JS/JSON)
  - Convert to consistent style
- **Result**: Returns normalized indentation

**Branch 4: If utf8_bom_present**
- **Then**: `remove_bom`
- **Details**: File has UTF-8 BOM (byte order mark)
  - BOM not needed for UTF-8
  - Can cause issues with some tools
  - Remove BOM bytes
  - Keep UTF-8 encoding
- **Result**: Returns content without BOM

**Branch 5: If already_consistent**
- **Then**: `mark_compliant`
- **Details**: File meets all encoding standards
  - UTF-8 encoding
  - LF line endings
  - Consistent indentation
  - No BOM
- **Result**: File passes check

**Fallback**: `warn_and_log`
- **Details**: Cannot automatically fix encoding issue
  - Unknown encoding
  - Binary file detected
  - Encoding conversion would lose data
  - Log warning and skip file
- **Result**: Warning logged

---

## Examples

### ✅ Compliant Code

**UTF-8 with LF Line Endings (Passes):**

```python
# File: src/calculator.py
# Encoding: UTF-8 (no BOM)
# Line Endings: LF (\n)
# Indentation: 4 spaces

def calculate_total(items: list[float]) -> float:
    """Calculate total with UTF-8 support: €, ¥, £"""
    return sum(items)

# Unicode characters work correctly
CURRENCY_SYMBOLS = {
    'EUR': '€',  # Euro symbol
    'JPY': '¥',  # Yen symbol
    'GBP': '£',  # Pound symbol
}

# File bytes: Valid UTF-8, LF line endings, 4-space indent
```

**Why Compliant**:
- UTF-8 encoding (handles all characters)
- LF line endings (Unix standard)
- Consistent 4-space indentation
- No BOM (clean UTF-8)
- International characters work

---

**JavaScript with 2-Space Indent (Passes):**

```javascript
// File: src/calculator.js
// Encoding: UTF-8 (no BOM)
// Line Endings: LF (\n)
// Indentation: 2 spaces

function calculateTotal(items) {
  /**
   * Calculate total with UTF-8 support: €, ¥, £
   */
  return items.reduce((acc, x) => acc + x, 0);
}

// Unicode works correctly
const CURRENCY_SYMBOLS = {
  EUR: '€',  // Euro symbol
  JPY: '¥',  // Yen symbol
  GBP: '£',  // Pound symbol
};

// File bytes: Valid UTF-8, LF line endings, 2-space indent
```

**Why Compliant**:
- UTF-8 encoding
- LF line endings
- Consistent 2-space indentation (JS standard)
- No BOM
- Portable across platforms

---

### ❌ Non-Compliant Code

**Mixed Line Endings (Violation):**

```python
# ❌ VIOLATION: Mixed CRLF and LF line endings
# File bytes (showing line endings):
def foo():\r\n    # ← CRLF (Windows)
    return 42\n  # ← LF (Unix)
\r\n
def bar():\r\n
    return 100\n

# Problem:
# - Inconsistent line endings in same file
# - Git diffs show as changed when they're not
# - Some tools may misinterpret
# - Cross-platform issues
```

**Why Non-Compliant**:
- Mixed line ending styles
- Git merge conflicts likely
- Inconsistent across platforms
- Should use LF only

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Consistent LF line endings
# File bytes (all LF):
def foo():\n
    return 42\n
\n
def bar():\n
    return 100\n

# All line endings normalized to LF
# Git handles consistently
# Works across all platforms
```

---

**Non-UTF-8 Encoding (Violation):**

```python
# ❌ VIOLATION: Latin-1 encoding with special characters
# File encoding: ISO-8859-1 (Latin-1)
def get_message():
    # Café - encoded as Latin-1 bytes
    return "Welcome to the caf\xe9"  # \xe9 is é in Latin-1

# Problem:
# - Not UTF-8 encoded
# - Will display as mojibake on UTF-8 systems
# - Not portable
# - Special characters break
```

**Why Non-Compliant**:
- Uses Latin-1 encoding instead of UTF-8
- Special characters won't display correctly
- Not internationally compatible
- Causes encoding errors

**Refactored (Compliant):**

```python
# ✅ REFACTORED: UTF-8 encoding
# File encoding: UTF-8
def get_message():
    # Café - properly encoded as UTF-8
    return "Welcome to the café"  # é encoded as UTF-8 \xc3\xa9

# UTF-8 encoding handles all characters correctly
# Works on all modern systems
# Internationally compatible
```

---

**UTF-8 with BOM (Violation):**

```python
# ❌ VIOLATION: UTF-8 with BOM
# File starts with: \xef\xbb\xbf (UTF-8 BOM)
\xef\xbb\xbf# Python file with BOM

def foo():
    return 42

# Problem:
# - UTF-8 BOM not needed (only for UTF-16/32)
# - Can cause issues with interpreters
# - Some tools don't expect BOM
# - Wastes 3 bytes
```

**Why Non-Compliant**:
- Contains unnecessary UTF-8 BOM
- Can confuse some tools
- Not standard for UTF-8
- Should be removed

**Refactored (Compliant):**

```python
# ✅ REFACTORED: UTF-8 without BOM
# File starts directly with content (no BOM)
# Python file without BOM

def foo():
    return 42

# Clean UTF-8 without BOM
# Works with all tools
# Standard UTF-8 encoding
```

---

**Mixed Tabs and Spaces (Violation):**

```python
# ❌ VIOLATION: Mixed tabs and spaces
def foo():
\t# ← Tab character
    return 42  # ← 4 spaces
\t\t# ← Two tabs
    result = 100  # ← 4 spaces

# Problem:
# - Inconsistent indentation
# - Different editors show differently
# - Python may reject (TabError)
# - Not portable
```

**Why Non-Compliant**:
- Mixes tabs and spaces
- Inconsistent indentation
- Visual ambiguity
- May cause Python errors

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Consistent 4-space indentation
def foo():
    # ← 4 spaces
    return 42  # ← 4 spaces

    # ← 4 spaces
    result = 100  # ← 4 spaces

# All indentation uses 4 spaces consistently
# Clear and unambiguous
# Works in all editors
```

---

## Edge Cases

### Edge Case 1: Binary Files

**Issue**: File contains binary data, not text

**Handling**:
```python
# Detect binary files and skip encoding checks

def is_binary_file(file_path: str) -> bool:
    """Check if file is binary"""
    try:
        with open(file_path, 'rb') as f:
            # Check first 8KB for null bytes
            chunk = f.read(8192)
            return b'\x00' in chunk
    except:
        return False

# Skip encoding checks for binary files
if is_binary_file('image.png'):
    # Skip - binary file
    pass
else:
    # Check encoding - text file
    check_utf8_encoding('script.py')
```

**Directive Action**: Skip encoding checks for binary files.

---

### Edge Case 2: Lossy Encoding Conversion

**Issue**: Source encoding contains characters not in UTF-8 (rare)

**Handling**:
```python
# Detect lossy conversion and warn user

def convert_to_utf8_safe(content: bytes, source_encoding: str) -> tuple[str, bool]:
    """Convert to UTF-8, detect if lossy"""
    try:
        # Try lossless conversion
        text = content.decode(source_encoding)
        utf8_bytes = text.encode('utf-8')
        return text, False  # Not lossy
    except UnicodeDecodeError:
        # Lossy conversion needed
        text = content.decode(source_encoding, errors='replace')
        return text, True  # Lossy - warn user

# Usage
content, is_lossy = convert_to_utf8_safe(file_bytes, 'latin-1')
if is_lossy:
    print("WARNING: Some characters could not be converted to UTF-8")
```

**Directive Action**: Warn user if conversion loses information.

---

### Edge Case 3: Shebang Lines with Encoding

**Issue**: Python files may have encoding declarations

**Handling**:
```python
# Python files may have encoding declarations (PEP 263)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def foo():
    return "hello"

# AIFP Standard: Remove encoding declaration (UTF-8 is default)
# Modern Python (3+) assumes UTF-8 by default

# ✅ Refactored: No encoding declaration needed
#!/usr/bin/env python3

def foo():
    return "hello"

# UTF-8 is default, no declaration needed
```

**Directive Action**: Remove encoding declarations (UTF-8 is standard).

---

## AIFP Encoding Standards

### Standard Encoding: UTF-8 (No BOM)

```
✅ AIFP Standard:
- Encoding: UTF-8
- BOM: None (clean UTF-8)
- Line Endings: LF (\n) only
- Indentation: Spaces (not tabs)
  - Python: 4 spaces
  - JavaScript/TypeScript: 2 spaces
  - JSON/YAML: 2 spaces
  - Other: 4 spaces default
```

### Line Ending Standards

```
✅ AIFP Standard: LF (\n) - Unix style

Reasons:
- Universal compatibility
- Git-friendly (default)
- Smaller file size
- Standard on Linux/macOS
- Windows tools support LF
```

### Indentation Standards

```
✅ AIFP Standard:
- Use spaces, not tabs
- Python: 4 spaces per indent level
- JavaScript/TypeScript: 2 spaces
- JSON/YAML: 2 spaces
- Other languages: 4 spaces

Reason: Spaces display consistently across all editors
```

---

## Git Configuration

### .gitattributes

```gitattributes
# Ensure consistent line endings
* text=auto eol=lf

# Python files
*.py text eol=lf

# JavaScript/TypeScript
*.js text eol=lf
*.ts text eol=lf

# JSON/YAML
*.json text eol=lf
*.yaml text eol=lf
*.yml text eol=lf

# Markdown
*.md text eol=lf

# Binary files
*.png binary
*.jpg binary
*.pdf binary
```

### .editorconfig

```ini
# EditorConfig for AIFP projects
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{js,ts,json,yaml,yml}]
indent_style = space
indent_size = 2

[*.md]
indent_style = space
indent_size = 2
trim_trailing_whitespace = false
```

---

## Related Directives

- **Depends On**: None (file-level directive)
- **Triggers**: None
- **Called By**:
  - `project_file_write` - Check encoding before writing
  - All file-writing directives - Ensure encoding consistency
- **Escalates To**: None

---

## Helper Functions Used

- `detect_file_encoding(file_path: str) -> str` - Detect current encoding
- `detect_line_endings(content: bytes) -> str` - Detect CRLF/LF/CR
- `convert_to_utf8(content: bytes, source_encoding: str) -> str` - Convert encoding
- `normalize_line_endings(content: str) -> str` - Convert to LF
- `detect_indentation(content: str) -> dict` - Analyze indent style
- `standardize_indentation(content: str, indent_size: int) -> str` - Fix indentation
- `update_files_table(file_id: int, encoding: str, line_endings: str)` - Update database

---

## Database Operations

This directive updates the following tables:

- **`files`**: Sets `encoding = 'utf-8'`, `line_endings = 'LF'`
- **`notes`**: Logs encoding fixes with `note_type = 'formatting'`

---

## Testing

How to verify this directive is working:

1. **Non-UTF-8 file** → Directive converts to UTF-8
   ```bash
   # Before: ISO-8859-1 encoding
   # After: UTF-8 encoding
   file script.py  # script.py: UTF-8 Unicode text
   ```

2. **Mixed line endings** → Directive normalizes to LF
   ```bash
   # Before: Mixed CRLF/LF
   # After: All LF
   dos2unix -i script.py  # No conversion needed
   ```

3. **Check database** → Verify encoding tracked
   ```sql
   SELECT path, encoding, line_endings
   FROM files
   WHERE encoding = 'utf-8' AND line_endings = 'LF';
   ```

---

## Common Mistakes

- ❌ **Using non-UTF-8 encoding** - Causes international character issues
- ❌ **Mixed line endings** - Git merge conflicts
- ❌ **Including UTF-8 BOM** - Unnecessary and problematic
- ❌ **Using tabs** - Inconsistent display across editors
- ❌ **Inconsistent indentation** - Hard to read, may cause errors

---

## Roadblocks and Resolutions

### Roadblock 1: non_utf8_encoding
**Issue**: File uses non-UTF-8 encoding
**Resolution**: Convert to UTF-8, warn if lossy conversion

### Roadblock 2: mixed_line_endings
**Issue**: File has mixed CRLF and LF
**Resolution**: Normalize all to LF (Unix standard)

### Roadblock 3: inconsistent_indentation
**Issue**: Mixed tabs and spaces or inconsistent width
**Resolution**: Standardize to spaces with consistent width (4 for Python, 2 for JS)

### Roadblock 4: utf8_bom
**Issue**: File has UTF-8 BOM (not needed)
**Resolution**: Remove BOM, keep UTF-8 encoding

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-encoding-consistency)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#language-adaptation)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for file encoding and format consistency*
