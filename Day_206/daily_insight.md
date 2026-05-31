# Day 206: Python3 `__slots__` Optimization, Memory Savings, and Inheritance Traps

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
By default, Python instances store instance attributes inside a dynamic dictionary (`__dict__`). While flexible, holding a dictionary per instance incurs significant RAM overhead (around 104+ bytes per object just for empty `__dict__` hash tables).

By defining `__slots__` in a class definition, Python suppresses the creation of `__dict__` and `__weakref__`, allocating a fixed-size array for attributes directly inside the C struct payload of the instance instead. This can reduce memory consumption by **60% to 80%** when instantiating millions of objects.

However, `__slots__` introduces inheritance traps: if a derived child class inherits from a slotted base class without explicitly defining `__slots__ = ()`, Python will silently re-enable `__dict__` on the child class, completely destroying the memory optimization!

**The Code Snippet**:
```python
import sys

class StandardPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ChildPointWithoutSlots(SlottedPoint):
    # Missing __slots__ definition!
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

# Memory Footprint Comparison
p_std = StandardPoint(10, 20)
p_slot = SlottedPoint(10, 20)
p_child = ChildPointWithoutSlots(10, 20, 30)

print(f"StandardPoint size (object + __dict__): {sys.getsizeof(p_std) + sys.getsizeof(p_std.__dict__)} bytes")
print(f"SlottedPoint size: {sys.getsizeof(p_slot)} bytes")

# TRAP: Child instance re-instantiates __dict__!
print(f"ChildPoint hasattr __dict__: {hasattr(p_child, '__dict__')}") # Output: True! Memory optimization ruined!

# Slotted classes prevent dynamic attribute assignment
try:
    p_slot.z = 99 # Raises AttributeError!
except AttributeError as e:
    print(f"AttributeError caught: {e}")
```

**Under the Hood / Why It Happens**:
In CPython runtime (`PyTypeObject`), defining `__slots__` alters descriptor creation:

1. CPython replaces `tp_dictoffset` with descriptor offsets (`PyMemberDef`) pointing directly to fixed struct member pointers.
2. When creating an instance, CPython allocates `sizeof(PyObject) + N * sizeof(PyObject*)` contiguous bytes on heap.
3. When `ChildPointWithoutSlots` inherits from `SlottedPoint`, CPython's class creation mechanism notices that the subclass does not specify `__slots__`. It automatically sets `tp_dictoffset` to non-zero, instantiating `__dict__` for every child instance.

**Key Takeaway / Safe Pattern**:
Use `__slots__` for data structures instantiated in high volumes (e.g., millions of tree nodes or data frames). In subclasses inheriting from slotted base classes, always declare `__slots__ = ('child_attr1',)` or `__slots__ = ()` if adding no new attributes.

```python
# Safe Pattern: Preserve slot optimization in inherited classes
class ChildPointSafe(SlottedPoint):
    __slots__ = ('z',) # Only allocate descriptor slot for new attribute 'z'
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z
```
