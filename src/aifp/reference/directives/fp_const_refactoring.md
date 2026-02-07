# Directive: fp_const_refactoring

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: MEDIUM - Code quality and immutability enforcement

---

## Purpose

The `fp_const_refactoring` directive **promotes use of constants** by automatically lifting repeated literals to top-level immutable declarations and converting mutable bindings to const declarations. This directive is **essential for code maintainability** because:

- **Prevents magic numbers**: Named constants are self-documenting
- **Eliminates duplication**: Single source of truth for repeated values
- **Prevents accidental mutation**: Const declarations are immutable
- **Simplifies refactoring**: Change value in one place
- **Aids AI reasoning**: Constants clarify intent and constraints

This directive handles:
- **Repeated literals** - Same value used multiple times (extract to constant)
- **Mutable bindings** - Variables that should be constants (convert to const)
- **Magic numbers** - Unexplained numeric literals (name with constant)
- **Configuration values** - Hard-coded settings (extract to constants)
- **Thresholds and limits** - Business rules embedded in code (make explicit)

**Refactoring principle**: DRY (Don't Repeat Yourself) for literals and immutable bindings.

---

## When to Apply

This directive applies when:
- **Repeated literal detected** - Same value appears 3+ times
- **Mutable binding unnecessary** - Variable never reassigned
- **Magic number found** - Numeric literal without context
- **During code review** - `project_compliance_check` scans for patterns
- **User requests extraction** - "Extract constant", "Remove magic numbers"
- **Configuration hardcoded** - Settings embedded in logic

---

## Workflow

### Trunk: scan_assignments

Scans code for repeated literals and mutable bindings.

**Steps**:
1. **Parse code AST** - Extract all literals and variable declarations
2. **Identify repeated values** - Count literal occurrences
3. **Detect mutable bindings** - Find variables never reassigned
4. **Route to refactoring** - Extract or convert

### Branches

**Branch 1: If repeated_literals**
- **Then**: `extract_to_const`
- **Details**: Lift repeated literal to top-level constant
  - Detection criteria:
    - Same literal appears 3+ times in file
    - Or: Same literal in 2+ functions
    - Or: Magic number (unexplained numeric literal)
  - Refactoring process:
    ```python
    # ❌ Before: Repeated literal
    def validate_age(age):
        if age < 18:  # Magic number
            return False
        return True

    def can_vote(age):
        return age >= 18  # Same magic number

    def is_adult(age):
        return age >= 18  # Repeated again

    # ✅ After: Extracted constant
    ADULT_AGE_THRESHOLD = 18  # Named constant at module level

    def validate_age(age: int) -> bool:
        if age < ADULT_AGE_THRESHOLD:
            return False
        return True

    def can_vote(age: int) -> bool:
        return age >= ADULT_AGE_THRESHOLD

    def is_adult(age: int) -> bool:
        return age >= ADULT_AGE_THRESHOLD
    ```
  - Naming conventions:
    - UPPERCASE_WITH_UNDERSCORES for constants
    - Descriptive names (what it represents, not the value)
    - Examples: MAX_RETRIES, DEFAULT_PORT, TAX_RATE, BUFFER_SIZE
  - Placement:
    - Top of file (after imports)
    - Grouped by category if many constants
    - Documented with comment if non-obvious
- **Result**: Repeated literal extracted, code更加 maintainable

**Branch 2: If mutable_bindings**
- **Then**: `convert_to_const`
- **Details**: Replace `let`/`var` with `const`, or add `const` keyword
  - Detection:
    - Variable declared but never reassigned
    - No mutations on the variable
  - Language-specific conversions:
    - **JavaScript/TypeScript**: `let` → `const`
      ```javascript
      // ❌ Before: Mutable binding
      let maxSize = 100;  // Never reassigned
      let items = [1, 2, 3];  // Never reassigned

      // ✅ After: Const declaration
      const maxSize = 100;
      const items = [1, 2, 3];
      ```
    - **Python**: Add type hint or use UPPERCASE (convention)
      ```python
      # ❌ Before: Implicit mutable
      max_size = 100  # Could be reassigned

      # ✅ After: UPPERCASE convention (constant)
      MAX_SIZE = 100  # Convention: constants are UPPERCASE

      # Or: Type hint with Final
      from typing import Final
      MAX_SIZE: Final[int] = 100
      ```
    - **Rust**: Add `const` or `let` (already immutable)
      ```rust
      // Rust: let bindings are immutable by default
      let max_size = 100;  // Already immutable

      // For compile-time constants:
      const MAX_SIZE: i32 = 100;
      ```
    - **Go**: Use `const` keyword
      ```go
      // ❌ Before: Variable
      var maxSize = 100

      // ✅ After: Constant
      const maxSize = 100
      ```
  - Benefits:
    - Compiler/interpreter can optimize
    - Intent is clear (value won't change)
    - Prevents accidental reassignment
- **Result**: Mutable bindings converted to immutable

**Branch 3: If configuration_literals**
- **Then**: `extract_config_constants`
- **Details**: Extract configuration values to constant declarations
  - Configuration patterns:
    - API endpoints: `"https://api.example.com/v1"`
    - Database settings: `"localhost:5432"`
    - Timeouts: `30000` (milliseconds)
    - Buffer sizes: `4096` (bytes)
    - Retry limits: `3` (attempts)
  - Refactoring:
    ```python
    # ❌ Before: Hardcoded configuration
    def connect_api():
        response = requests.get("https://api.example.com/v1", timeout=30)
        return response.json()

    def retry_request():
        for i in range(3):  # Magic number
            try:
                return connect_api()
            except Exception:
                continue

    # ✅ After: Configuration constants
    API_BASE_URL = "https://api.example.com/v1"
    REQUEST_TIMEOUT_SECONDS = 30
    MAX_RETRY_ATTEMPTS = 3

    def connect_api():
        response = requests.get(API_BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        return response.json()

    def retry_request():
        for i in range(MAX_RETRY_ATTEMPTS):
            try:
                return connect_api()
            except Exception:
                continue
    ```
  - Benefits:
    - Easy to reconfigure without code changes
    - Clear what values are configurable
    - Can move to config file later
- **Result**: Configuration made explicit and centralized

**Branch 4: If threshold_literals**
- **Then**: `extract_business_rules`
- **Details**: Extract business rule thresholds to named constants
  - Business rule patterns:
    - Minimum/maximum values: `if price > 1000:`
    - Percentages: `tax = total * 0.08`
    - Limits: `if len(items) > 50:`
  - Refactoring:
    ```python
    # ❌ Before: Business rules embedded
    def calculate_shipping(price):
        if price > 100:  # Free shipping threshold
            return 0
        return 9.99  # Flat rate

    def calculate_tax(total):
        return total * 0.08  # Tax rate

    # ✅ After: Business rules as constants
    FREE_SHIPPING_THRESHOLD = 100  # dollars
    FLAT_SHIPPING_RATE = 9.99  # dollars
    TAX_RATE = 0.08  # 8%

    def calculate_shipping(price: float) -> float:
        if price > FREE_SHIPPING_THRESHOLD:
            return 0
        return FLAT_SHIPPING_RATE

    def calculate_tax(total: float) -> float:
        return total * TAX_RATE
    ```
  - Add comments to explain business rules
  - Benefits:
    - Business rules visible and auditable
    - Easy to update when rules change
    - Self-documenting code
- **Result**: Business logic clarified through named constants

**Branch 5: If string_literals**
- **Then**: `extract_string_constants`
- **Details**: Extract repeated string literals
  - String patterns:
    - Error messages: `"Invalid input"`
    - Status codes: `"SUCCESS"`, `"PENDING"`
    - Keys/identifiers: `"user_id"`, `"created_at"`
  - Refactoring:
    ```python
    # ❌ Before: Repeated strings
    def validate_user(data):
        if "username" not in data:
            raise ValueError("Username required")
        if "email" not in data:
            raise ValueError("Email required")

    def serialize_user(user):
        return {
            "username": user.name,
            "email": user.email
        }

    # ✅ After: String constants
    KEY_USERNAME = "username"
    KEY_EMAIL = "email"
    MSG_USERNAME_REQUIRED = "Username required"
    MSG_EMAIL_REQUIRED = "Email required"

    def validate_user(data: dict) -> None:
        if KEY_USERNAME not in data:
            raise ValueError(MSG_USERNAME_REQUIRED)
        if KEY_EMAIL not in data:
            raise ValueError(MSG_EMAIL_REQUIRED)

    def serialize_user(user: User) -> dict:
        return {
            KEY_USERNAME: user.name,
            KEY_EMAIL: user.email
        }
    ```
  - Benefits:
    - Typo prevention (compile-time checking)
    - Consistent naming across codebase
    - Easy to refactor keys
- **Result**: String literals deduplicated

**Branch 6: If already_constant**
- **Then**: `mark_compliant`
- **Details**: No repeated literals or mutable bindings found
  - Code already follows const conventions
  - No refactoring needed
- **Result**: Code validated as compliant

**Fallback**: `mark_compliant`
- **Details**: No actionable refactoring opportunities
  - Literals appear only once
  - All bindings appropriately declared
- **Result**: No changes needed

---

## Examples

### ✅ Compliant Usage

**Extracting Repeated Literal:**
```python
# Initial code (non-compliant)
def validate_password(password):
    if len(password) < 8:  # Magic number
        return False
    return True

def check_password_strength(password):
    if len(password) < 8:  # Repeated
        return "weak"
    if len(password) < 12:  # Another threshold
        return "medium"
    return "strong"

# AI calls: fp_const_refactoring()

# Workflow:
# 1. scan_assignments:
#    - Detects literal 8 appears 2 times
#    - Detects literal 12 appears 1 time
#    - Threshold for extraction: 2+ occurrences
#
# 2. repeated_literals: extract_to_const
#    - Extract 8 to MIN_PASSWORD_LENGTH
#    - Extract 12 to STRONG_PASSWORD_LENGTH
#
# Refactored code (compliant)
MIN_PASSWORD_LENGTH = 8  # Minimum length requirement
STRONG_PASSWORD_LENGTH = 12  # Length for strong password

def validate_password(password: str) -> bool:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    return True

def check_password_strength(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        return "weak"
    if len(password) < STRONG_PASSWORD_LENGTH:
        return "medium"
    return "strong"

# Result:
# ✅ Magic numbers replaced with named constants
# ✅ Business rules explicit
# ✅ Single source of truth for password requirements
```

---

**Converting Mutable to Const:**
```python
# Initial code (JavaScript/TypeScript)
function calculateTotal(items) {
    let taxRate = 0.08;  // Never reassigned
    let subtotal = items.reduce((sum, item) => sum + item.price, 0);  // Never reassigned
    return subtotal * (1 + taxRate);
}

// AI calls: fp_const_refactoring()

// Workflow:
// 1. scan_assignments:
//    - taxRate declared with let, never reassigned
//    - subtotal declared with let, never reassigned
//
// 2. mutable_bindings: convert_to_const
//    - Change let → const for both
//
// Refactored code (compliant)
function calculateTotal(items) {
    const taxRate = 0.08;  // Const (never changes)
    const subtotal = items.reduce((sum, item) => sum + item.price, 0);  // Const
    return subtotal * (1 + taxRate);
}

// Result:
// ✅ Immutable bindings (const)
// ✅ Intent clear (values won't change)
// ✅ Compiler can optimize
```

---

**Extracting Configuration:**
```python
# Initial code (non-compliant)
def fetch_data():
    response = requests.get("https://api.example.com/v1/data", timeout=30)
    return response.json()

def upload_file(file):
    response = requests.post("https://api.example.com/v1/upload", files={"file": file}, timeout=30)
    return response.status_code

# AI calls: fp_const_refactoring()

# Workflow:
# 1. scan_assignments:
#    - Detects repeated URL base "https://api.example.com/v1"
#    - Detects repeated timeout 30
#
# 2. configuration_literals: extract_config_constants
#    - Extract API_BASE_URL
#    - Extract REQUEST_TIMEOUT
#
# Refactored code (compliant)
# Configuration constants
API_BASE_URL = "https://api.example.com/v1"
REQUEST_TIMEOUT = 30  # seconds

def fetch_data():
    url = f"{API_BASE_URL}/data"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    return response.json()

def upload_file(file):
    url = f"{API_BASE_URL}/upload"
    response = requests.post(url, files={"file": file}, timeout=REQUEST_TIMEOUT)
    return response.status_code

# Result:
# ✅ Configuration centralized
# ✅ Easy to change API endpoint
# ✅ Self-documenting code
```

---

### ❌ Non-Compliant Usage

**Leaving Magic Numbers:**
```python
# ❌ Magic numbers not extracted
def calculate_discount(price):
    if price > 100:  # What does 100 mean?
        return price * 0.1  # What does 0.1 mean?
    return 0

# Why Non-Compliant:
# - 100 is unexplained threshold
# - 0.1 is unexplained discount rate
# - Intent unclear
```

**Corrected:**
```python
# ✅ Named constants
DISCOUNT_THRESHOLD = 100  # dollars
DISCOUNT_RATE = 0.1  # 10%

def calculate_discount(price: float) -> float:
    if price > DISCOUNT_THRESHOLD:
        return price * DISCOUNT_RATE
    return 0
```

---

## Edge Cases

### Edge Case 1: Single Occurrence of Literal

**Issue**: Literal appears only once

**Handling**:
```python
# Single occurrence - no extraction needed
def validate_age(age):
    return age >= 18  # Only usage of 18 in entire file

# Rule: Extract only if repeated (2+ times)
# Single occurrence → No action
```

**Directive Action**: Only extract if 2+ occurrences.

---

### Edge Case 2: Context-Dependent Literals

**Issue**: Same literal has different meanings

**Handling**:
```python
# Same literal, different contexts
def validate_username(name):
    if len(name) < 3:  # Minimum username length
        return False

def validate_pin(pin):
    if len(pin) < 3:  # Minimum PIN length
        return False

# Resolution: Separate constants
USERNAME_MIN_LENGTH = 3
PIN_MIN_LENGTH = 3  # Or: 4 if requirements differ

# Don't extract to generic MIN_LENGTH (loses context)
```

**Directive Action**: Consider context when naming constants.

---

### Edge Case 3: Zero, One, Empty String

**Issue**: Common literals (0, 1, "", [])

**Handling**:
```python
# Don't extract common defaults
def initialize():
    counter = 0  # Don't extract 0
    items = []  # Don't extract empty list
    name = ""  # Don't extract empty string

# Rule: Only extract meaningful values
# Exception: If 0/1 has business meaning
INITIAL_BALANCE = 0  # OK (business context)
```

**Directive Action**: Skip common default values unless meaningful.

---

## Related Directives

- **Called By**:
  - `project_compliance_check` - Scans for magic numbers
  - User requests - "Extract constants", "Remove magic numbers"
- **Calls**:
  - `project_notes_log` - Logs extraction decisions
- **Related**:
  - `fp_immutability` - Constants are immutable
  - `fp_no_reassignment` - Constants never reassigned

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`notes`**: INSERT extraction decisions and refactoring actions

---

## Testing

1. **Detect repeated literal** → Literal found 2+ times
   ```python
   code = "if x > 100: ... if y > 100: ..."
   literals = find_repeated_literals(code)
   assert 100 in literals
   ```

2. **Extract to constant** → Constant declaration added
   ```python
   refactored = extract_to_const(code, 100, "MAX_VALUE")
   assert "MAX_VALUE = 100" in refactored
   ```

3. **Convert let to const** → Mutable binding changed
   ```javascript
   code = "let x = 10; // never reassigned"
   refactored = convert_to_const(code)
   assert "const x = 10" in refactored
   ```

---

## Common Mistakes

- ❌ **Extracting single-occurrence literals** - Only extract if repeated
- ❌ **Generic constant names** - Use descriptive names (not CONST_1)
- ❌ **Extracting 0, 1, "", []** - Skip common defaults unless meaningful
- ❌ **Losing context** - Same value different contexts needs separate constants

---

## Roadblocks and Resolutions

### Roadblock 1: duplicate_literals
**Issue**: Same literal appears multiple times
**Resolution**: Extract to shared const at module level

### Roadblock 2: mutable_assignment
**Issue**: Variable declared mutable but never reassigned
**Resolution**: Enforce constant declaration (const, final, UPPERCASE)

---

## References

None
---

*Part of AIFP v1.0 - FP directive for promoting constants and eliminating magic numbers*
