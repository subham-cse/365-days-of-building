# Day 234: Python `__slots__` Memory Optimization & Inheritance Pitfalls

**Language / Domain**: Python3 / CPython Internals & Memory Layout

**The Core Concept / "Did You Know?"**:
By default, Python class instances store their attributes inside a dynamic dictionary (`__dict__`). This grants flexibility—allowing arbitrary property creation at runtime—but carries a significant memory footprint (typically 100 to 150 bytes of hash table overhead per object).

By declaring `__slots__` inside a class definition, Python replaces the dynamic instance `__dict__` dictionary with a compact C-level array of descriptor pointers. Instantiating millions of small data objects with `__slots__` reduces memory usage by up to 60-80% and accelerates attribute access speeds.

However, `__slots__` introduces subtle inheritance traps: if a derived class forgets to define `__slots__`, Python automatically re-creates instance `__dict__` dictionaries for child instances, silently invalidating all memory savings!

**The Code Snippet**:
```python
import sys

class StandardPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# INHERITANCE TRAP: Child class omits __slots__
class UnslottedChildPoint(SlottedPoint):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y)
        self.z = z # Re-creates __dict__ for child instances!

# CORRECT INHERITANCE: Child class defines __slots__ for new fields
class SlottedChildPoint(SlottedPoint):
    __slots__ = ('z',) # Inherits ('x', 'y') and adds 'z'
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y)
        self.z = z

if __name__ == "__main__":
    p_std = StandardPoint(1.0, 2.0)
    p_slot = SlottedPoint(1.0, 2.0)
    p_child_bad = UnslottedChildPoint(1.0, 2.0, 3.0)
    p_child_good = SlottedChildPoint(1.0, 2.0, 3.0)

    print("--- Memory Footprint Comparison ---")
    print(f"StandardPoint size: {sys.getsizeof(p_std)} bytes + dict {sys.getsizeof(p_std.__dict__)} bytes")
    print(f"SlottedPoint size:  {sys.getsizeof(p_slot)} bytes (No __dict__!)")

    print("\n--- Inheritance Behavior ---")
    print(f"UnslottedChildPoint has __dict__? {hasattr(p_child_bad, '__dict__')}") # True! Memory optimization broken.
    print(f"SlottedChildPoint has __dict__?   {hasattr(p_child_good, '__dict__')}") # False! Slotted efficiency retained.

    # Dynamic attribute injection test:
    try:
        p_slot.z = 99 # Raises AttributeError because 'z' is not in __slots__
    except AttributeError as e:
        print(f"\nCaught expected SlottedPoint error: {e}")
```

**Under the Hood / Why It Happens**:
1. **Dynamic `__dict__` vs Descriptor Array**:
   - In `StandardPoint`, CPython allocates a `PyObject` structure containing a pointer to a `PyDictObject` (`instance.__dict__`).
   - In `SlottedPoint`, CPython allocates member descriptors directly inside the C `PyHeapTypeObject` structure at fixed byte offsets (`PyMemberDef`). Attribute access `p.x` bypasses dictionary key hashing and fetches the memory offset directly, similar to a C struct field.

2. **Inheritance Resolution**:
   When CPython constructs a class hierarchy:
   - If a subclass does not define `__slots__`, CPython assumes the subclass requires dynamic attribute assignment. It automatically adds `__dict__` and `__weakref__` descriptors to instances of the child class.
   - To preserve memory optimization in derived classes, child classes must explicitly define `__slots__ = ('child_field1', ...)` (or `__slots__ = ()` if introducing no new attributes).

**Key Takeaway / Safe Pattern**:
- Use `__slots__` on high-cardinality data classes (e.g., ORM models, telemetry events, graph nodes) where millions of instances exist concurrently.
- In class inheritance trees using `__slots__`, ensure **every** subclass declares `__slots__` (even an empty tuple `__slots__ = ()` if adding no fields).
- Be aware that `__slots__` prevents default `pickle` serialization and dynamic attribute injection unless `'__dict__'` is explicitly included in the `__slots__` tuple.
