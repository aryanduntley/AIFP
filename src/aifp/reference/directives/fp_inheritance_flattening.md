# Directive: fp_inheritance_flattening

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: HIGH - OOP elimination

---

## Purpose

The `fp_inheritance_flattening` directive **converts class hierarchies into flattened procedural functions**, ensuring all logic is in flat procedural form without OOP hierarchies. This directive is **essential for FP compliance** because:

- **Eliminates polymorphism**: No runtime method resolution
- **Explicit behavior**: All logic visible at call site
- **No hidden state**: Class hierarchies often hide state
- **AI-friendly**: Flat functions easier to analyze than inheritance trees
- **Composability**: Functions compose better than class hierarchies

This directive flattens:
- **Single inheritance** - Child class extends parent
- **Multiple inheritance** - Class inherits from multiple parents
- **Abstract base classes** - Interfaces and abstract methods
- **Mixins** - Trait/mixin pattern
- **Method overriding** - Child overrides parent method

**Flattening principle**: Convert inheritance hierarchy to standalone functions + data structures.

---

## When to Apply

This directive applies when:
- **Inheritance detected** - `class Child(Parent):`
- **Method overriding found** - Child redefines parent method
- **Abstract methods present** - ABC or interface pattern
- **During compliance checks** - `project_compliance_check` scans for inheritance
- **User requests flattening** - "Remove inheritance", "Convert to functions"
- **Legacy code migration** - Converting OOP to FP

---

## Workflow

### Trunk: scan_inheritance

Scans code for class inheritance patterns.

**Steps**:
1. **Parse class definitions** - Extract all classes
2. **Build inheritance tree** - Map parent-child relationships
3. **Identify overridden methods** - Compare parent/child methods
4. **Route to flattening** - Convert to functions

### Branches

**Branch 1: If inheritance_chain_detected**
- **Then**: `merge_methods`
- **Details**: Flatten inheritance chain into standalone functions
  - Single inheritance pattern:
    ```python
    # ❌ Inheritance chain
    class Animal:
        def __init__(self, name):
            self.name = name

        def speak(self):
            return "Some sound"

    class Dog(Animal):
        def speak(self):  # Override
            return "Woof"

        def fetch(self):
            return f"{self.name} fetches ball"

    # Usage
    dog = Dog("Buddy")
    print(dog.speak())  # "Woof"
    print(dog.fetch())  # "Buddy fetches ball"
    ```
  - Flattened to functions + data:
    ```python
    # ✅ Flattened (pure functions)
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Animal:
        """Pure data (no methods)"""
        name: str
        species: str

    def speak(animal: Animal) -> str:
        """Pure function based on species"""
        if animal.species == "dog":
            return "Woof"
        elif animal.species == "cat":
            return "Meow"
        else:
            return "Some sound"

    def fetch(animal: Animal) -> str:
        """Pure function for dogs"""
        if animal.species != "dog":
            raise ValueError("Only dogs can fetch")
        return f"{animal.name} fetches ball"

    # Usage
    dog = Animal(name="Buddy", species="dog")
    print(speak(dog))  # "Woof"
    print(fetch(dog))  # "Buddy fetches ball"
    ```
  - Flattening strategies:
    - **Strategy 1**: Data + behavior separation
      - Classes become dataclasses (data only)
      - Methods become standalone functions
    - **Strategy 2**: Tagged unions (discriminated unions)
      - Use enum/literal for type discrimination
      - Pattern matching for behavior
    - **Strategy 3**: Function dispatch tables
      - Dictionary mapping type → function
      - Explicit dispatch instead of polymorphism
  - Benefits:
    - No dynamic dispatch (explicit)
    - All behavior visible
    - Easy to test (pure functions)
    - Composable (function composition)
- **Result**: Inheritance flattened to functions

**Branch 2: If multiple_inheritance**
- **Then**: `resolve_diamond_problem`
- **Details**: Flatten multiple inheritance, resolve method conflicts
  - Multiple inheritance pattern:
    ```python
    # ❌ Multiple inheritance (diamond problem)
    class A:
        def method(self):
            return "A"

    class B(A):
        def method(self):
            return "B"

    class C(A):
        def method(self):
            return "C"

    class D(B, C):  # Multiple inheritance
        pass

    # Which method() does D inherit? (MRO: D → B → C → A)
    obj = D()
    print(obj.method())  # "B" (method resolution order)
    ```
  - Flattened resolution:
    ```python
    # ✅ Flattened (explicit dispatch)
    from dataclasses import dataclass
    from typing import Literal

    @dataclass(frozen=True)
    class Entity:
        type: Literal["A", "B", "C", "D"]

    def method_a() -> str:
        return "A"

    def method_b() -> str:
        return "B"

    def method_c() -> str:
        return "C"

    # Explicit dispatch (no MRO confusion)
    def method(entity: Entity) -> str:
        dispatch = {
            "A": method_a,
            "B": method_b,
            "C": method_c,
            "D": method_b  # Explicit: D uses B's behavior
        }
        return dispatch[entity.type]()

    # Usage
    entity_d = Entity(type="D")
    print(method(entity_d))  # "B" (explicit)
    ```
  - Diamond problem resolution:
    - Make method resolution explicit
    - Document which implementation chosen
    - Use dispatch table for clarity
- **Result**: Multiple inheritance flattened

**Branch 3: If abstract_methods**
- **Then**: `convert_to_protocol`
- **Details**: Convert abstract base classes to protocols or function types
  - Abstract class pattern:
    ```python
    # ❌ Abstract base class
    from abc import ABC, abstractmethod

    class Shape(ABC):
        @abstractmethod
        def area(self) -> float:
            pass

        @abstractmethod
        def perimeter(self) -> float:
            pass

    class Rectangle(Shape):
        def __init__(self, width, height):
            self.width = width
            self.height = height

        def area(self) -> float:
            return self.width * self.height

        def perimeter(self) -> float:
            return 2 * (self.width + self.height)
    ```
  - Flattened to protocols:
    ```python
    # ✅ Flattened (data + functions)
    from dataclasses import dataclass
    from typing import Protocol

    @dataclass(frozen=True)
    class Rectangle:
        width: float
        height: float

    @dataclass(frozen=True)
    class Circle:
        radius: float

    # Protocol (structural typing, not inheritance)
    class HasArea(Protocol):
        def area(self) -> float: ...

    # Pure functions
    def rectangle_area(rect: Rectangle) -> float:
        return rect.width * rect.height

    def rectangle_perimeter(rect: Rectangle) -> float:
        return 2 * (rect.width + rect.height)

    def circle_area(circle: Circle) -> float:
        from math import pi
        return pi * circle.radius ** 2

    def circle_perimeter(circle: Circle) -> float:
        from math import pi
        return 2 * pi * circle.radius

    # Dispatch table for polymorphism
    from typing import Union

    Shape = Union[Rectangle, Circle]

    def area(shape: Shape) -> float:
        if isinstance(shape, Rectangle):
            return rectangle_area(shape)
        elif isinstance(shape, Circle):
            return circle_area(shape)
        else:
            raise TypeError(f"Unknown shape: {type(shape)}")
    ```
  - Benefits:
    - No abstract classes
    - Structural typing (Protocol)
    - Pure functions
    - Explicit dispatch
- **Result**: Abstract classes converted

**Branch 4: If mixin_pattern**
- **Then**: `extract_mixin_functions`
- **Details**: Convert mixins to composable functions
  - Mixin pattern:
    ```python
    # ❌ Mixin (behavior composition via inheritance)
    class TimestampMixin:
        def add_timestamp(self):
            from datetime import datetime
            self.created_at = datetime.now()

    class SerializeMixin:
        def to_json(self):
            import json
            return json.dumps(self.__dict__)

    class User(TimestampMixin, SerializeMixin):
        def __init__(self, name):
            self.name = name
            self.add_timestamp()

    # Usage
    user = User("Alice")
    print(user.to_json())
    ```
  - Flattened to composable functions:
    ```python
    # ✅ Flattened (composable functions)
    from dataclasses import dataclass, asdict
    from datetime import datetime
    import json

    @dataclass(frozen=True)
    class User:
        name: str
        created_at: datetime

    # Pure functions (composable)
    def with_timestamp(name: str) -> User:
        return User(name=name, created_at=datetime.now())

    def to_json(user: User) -> str:
        return json.dumps(asdict(user), default=str)

    # Usage (function composition)
    user = with_timestamp("Alice")
    json_str = to_json(user)
    print(json_str)

    # Or: Pipeline
    from functools import reduce

    def pipe(initial, *functions):
        return reduce(lambda acc, f: f(acc), functions, initial)

    result = pipe(
        "Alice",
        with_timestamp,
        to_json
    )
    ```
  - Benefits:
    - No multiple inheritance
    - Functions compose explicitly
    - Pure (when possible)
    - Testable in isolation
- **Result**: Mixins converted to functions

**Branch 5: If method_overriding**
- **Then**: `flatten_override_hierarchy`
- **Details**: Merge overridden methods into dispatch table
  - Method overriding pattern:
    ```python
    # ❌ Method overriding
    class Animal:
        def speak(self):
            return "Some sound"

    class Dog(Animal):
        def speak(self):  # Override
            return "Woof"

    class Cat(Animal):
        def speak(self):  # Override
            return "Meow"
    ```
  - Flattened dispatch:
    ```python
    # ✅ Flattened (dispatch table)
    from dataclasses import dataclass
    from typing import Literal

    AnimalType = Literal["dog", "cat", "generic"]

    @dataclass(frozen=True)
    class Animal:
        species: AnimalType
        name: str

    # Pure functions (one per type)
    def speak_dog() -> str:
        return "Woof"

    def speak_cat() -> str:
        return "Meow"

    def speak_generic() -> str:
        return "Some sound"

    # Dispatch table
    SPEAK_DISPATCH = {
        "dog": speak_dog,
        "cat": speak_cat,
        "generic": speak_generic
    }

    def speak(animal: Animal) -> str:
        return SPEAK_DISPATCH[animal.species]()

    # Usage
    dog = Animal(species="dog", name="Buddy")
    cat = Animal(species="cat", name="Whiskers")
    print(speak(dog))  # "Woof"
    print(speak(cat))  # "Meow"
    ```
  - Dispatch strategies:
    - Dictionary: Fast lookup
    - Pattern matching (Python 3.10+): Structural dispatch
    - if-elif chain: Simple fallback
- **Result**: Overrides flattened to dispatch

**Fallback**: `mark_as_functional`
- **Details**: No inheritance detected, code already functional
  - Code uses:
    - Standalone functions
    - Dataclasses without methods
    - No class hierarchies
  - No refactoring needed
- **Result**: Code validated as FP-compliant

---

## Examples

### ✅ Compliant Usage

**Flattening Single Inheritance:**
```python
# Initial code (inheritance)
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    def start(self):
        return f"{self.brand} vehicle starting"

class Car(Vehicle):  # Inheritance
    def __init__(self, brand, model):
        super().__init__(brand)
        self.model = model

    def start(self):  # Override
        return f"{self.brand} {self.model} car starting"

# AI calls: fp_inheritance_flattening()

# Workflow:
# 1. scan_inheritance:
#    - Car inherits from Vehicle
#    - Method override: start()
#
# 2. inheritance_chain_detected: merge_methods
#    - Flatten hierarchy to functions
#
# Refactored code (compliant)
from dataclasses import dataclass
from typing import Literal

VehicleType = Literal["generic", "car"]

@dataclass(frozen=True)
class Vehicle:
    """Pure data (no methods)"""
    vehicle_type: VehicleType
    brand: str
    model: str = ""

# Pure functions (explicit dispatch)
def start_generic(vehicle: Vehicle) -> str:
    return f"{vehicle.brand} vehicle starting"

def start_car(vehicle: Vehicle) -> str:
    return f"{vehicle.brand} {vehicle.model} car starting"

# Dispatch function
def start(vehicle: Vehicle) -> str:
    dispatch = {
        "generic": start_generic,
        "car": start_car
    }
    return dispatch[vehicle.vehicle_type](vehicle)

# Usage
car = Vehicle(vehicle_type="car", brand="Toyota", model="Camry")
print(start(car))  # "Toyota Camry car starting"

# Database log
INSERT INTO notes (
  content,
  note_type,
  source,
  directive_name
) VALUES (
  'Flattened inheritance: Vehicle → Car to dispatch table',
  'research',
  'directive',
  'fp_inheritance_flattening'
);

# Result:
# ✅ No inheritance
# ✅ Flat functions
# ✅ Explicit dispatch
# ✅ Pure and composable
```

---

**Converting Abstract Base Class:**
```python
# Initial code (abstract base class)
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class StripeProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Stripe API call
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # PayPal API call
        return True

# AI calls: fp_inheritance_flattening()

# Workflow:
# 1. scan_inheritance:
#    - Abstract base class: PaymentProcessor
#    - Concrete implementations: Stripe, PayPal
#
# 2. abstract_methods: convert_to_protocol
#    - Convert ABC to protocol/dispatch
#
# Refactored code (compliant)
from dataclasses import dataclass
from typing import Literal

PaymentMethod = Literal["stripe", "paypal"]

@dataclass(frozen=True)
class PaymentConfig:
    method: PaymentMethod
    api_key: str

# Pure functions (one per payment method)
def process_stripe_payment(amount: float, api_key: str) -> bool:
    # Stripe API call (isolated I/O)
    return True

def process_paypal_payment(amount: float, api_key: str) -> bool:
    # PayPal API call (isolated I/O)
    return True

# Dispatch function
def process_payment(amount: float, config: PaymentConfig) -> bool:
    dispatch = {
        "stripe": lambda: process_stripe_payment(amount, config.api_key),
        "paypal": lambda: process_paypal_payment(amount, config.api_key)
    }
    return dispatch[config.method]()

# Usage
stripe_config = PaymentConfig(method="stripe", api_key="sk_test_...")
success = process_payment(100.0, stripe_config)

# Result:
# ✅ No abstract classes
# ✅ Explicit dispatch
# ✅ Pure functions (I/O isolated)
# ✅ Configuration explicit
```

---

**Flattening Mixin Pattern:**
```python
# Initial code (mixins)
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class ValidateMixin:
    def validate(self):
        return hasattr(self, 'name') and self.name != ""

class User(JsonMixin, ValidateMixin):
    def __init__(self, name, email):
        self.name = name
        self.email = email

# AI calls: fp_inheritance_flattening()

# Workflow:
# 1. scan_inheritance:
#    - Multiple inheritance (mixins)
#    - JsonMixin, ValidateMixin
#
# 2. mixin_pattern: extract_mixin_functions
#    - Convert to composable functions
#
# Refactored code (compliant)
from dataclasses import dataclass, asdict
import json

@dataclass(frozen=True)
class User:
    name: str
    email: str

# Pure functions (composable)
def to_json(user: User) -> str:
    return json.dumps(asdict(user))

def validate_user(user: User) -> bool:
    return user.name != "" and user.email != ""

# Usage (composition)
user = User(name="Alice", email="alice@example.com")
if validate_user(user):
    json_str = to_json(user)
    print(json_str)

# Or: Pipeline
def pipe(value, *functions):
    from functools import reduce
    return reduce(lambda acc, f: f(acc), functions, value)

# Validation + serialization pipeline
def validate_and_serialize(user: User) -> str:
    if not validate_user(user):
        raise ValueError("Invalid user")
    return to_json(user)

result = validate_and_serialize(user)

# Result:
# ✅ No mixins
# ✅ Composable functions
# ✅ Pure (deterministic)
# ✅ Testable in isolation
```

---

### ❌ Non-Compliant Usage

**Leaving Inheritance:**
```python
# ❌ Inheritance not flattened
class Animal:
    def speak(self):
        return "Sound"

class Dog(Animal):  # Still has inheritance
    def speak(self):
        return "Woof"

# Why Non-Compliant:
# - Uses inheritance
# - Polymorphism via inheritance
# - Not flat procedural code
```

**Corrected:**
```python
# ✅ Flattened
@dataclass(frozen=True)
class Animal:
    species: str

def speak(animal: Animal) -> str:
    if animal.species == "dog":
        return "Woof"
    return "Sound"
```

---

## Edge Cases

### Edge Case 1: Deep Inheritance Chain

**Issue**: Multiple levels of inheritance (A → B → C → D)

**Handling**:
- Flatten entire chain at once
- Extract all methods to functions
- Create dispatch table for all types

**Directive Action**: Process inheritance tree depth-first.

---

### Edge Case 2: Property Decorators

**Issue**: Class uses @property for computed attributes

**Handling**:
```python
# ❌ Property decorator
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14 * self.radius ** 2

# ✅ Flattened to function
@dataclass(frozen=True)
class Circle:
    radius: float

def circle_area(circle: Circle) -> float:
    return 3.14 * circle.radius ** 2
```

**Directive Action**: Convert properties to functions.

---

### Edge Case 3: Static/Class Methods

**Issue**: Class has @staticmethod or @classmethod

**Handling**:
```python
# ❌ Static method
class Math:
    @staticmethod
    def add(x, y):
        return x + y

# ✅ Already functional!
def add(x: int, y: int) -> int:
    return x + y
```

**Directive Action**: Extract as standalone function (already functional).

---

## Related Directives

- **Called By**:
  - `fp_no_oop` - Part of OOP elimination
  - `project_compliance_check` - Scans for inheritance
  - `project_file_write` - Validates no inheritance
- **Calls**:
  - Database helpers - Updates functions table
  - `project_notes_log` - Logs flattening decisions
- **Related**:
  - `fp_wrapper_generation` - Wraps external OOP libraries
  - `fp_class_elimination` - Removes classes entirely

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`notes`**: INSERT flattening decisions and inheritance removal logs

---

## Testing

1. **Detect inheritance** → Inheritance chain found
   ```python
   tree = build_inheritance_tree(code)
   assert "Dog" in tree["Animal"]["children"]
   ```

2. **Flatten to functions** → Methods extracted
   ```python
   flattened = flatten_inheritance(tree)
   assert "def speak_dog" in flattened
   ```

3. **No inheritance** → Code validated
   ```python
   assert has_inheritance(code) == False
   ```

---

## Common Mistakes

- ❌ **Partial flattening** - Leaving some inheritance
- ❌ **Not handling super()** - Parent method calls
- ❌ **Missing dispatch** - No way to choose implementation
- ❌ **Breaking encapsulation** - Exposing internal implementation

---

## Roadblocks and Resolutions

### Roadblock 1: deep_inheritance
**Issue**: Multiple levels of inheritance
**Resolution**: Flatten to module functions, use dispatch tables

### Roadblock 2: overridden_methods
**Issue**: Child overrides parent methods
**Resolution**: Preserve order manually, explicit dispatch

---

## References

None
---

*Part of AIFP v1.0 - FP directive for flattening class inheritance hierarchies*
