# Day 122: GIL Impact on Multithreading and __slots__ Memory Optimization
- **Language / Domain**: Python3
- **The Core Concept / "Did You Know?"**: Python (CPython) uses a **Global Interpreter Lock (GIL)**, a mutex that prevents multiple native OS threads from executing Python bytecodes concurrently. Consequently, CPU-bound multithreading in Python does not achieve multi-core parallel speedup!

For memory optimization, Python classes store dynamic attributes inside a per-instance dictionary `__dict__`. By explicitly defining `__slots__`, you can bypass `__dict__` creation entirely, reducing object memory footprint by up to 60–70% for high-volume data instances!

- **The Code Snippet**:
```python
import sys

# Standard Python class (uses dynamic __dict__)
class StandardUser:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email

# Memory-Optimized Python class using __slots__
class SlottedUser:
    __slots__ = ('user_id', 'email')

    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email

u1 = StandardUser(101, "alice@example.com")
u2 = SlottedUser(101, "alice@example.com")

print("StandardUser memory overhead:")
print("  Object size:", sys.getsizeof(u1), "bytes")
print("  __dict__ size:", sys.getsizeof(u1.__dict__), "bytes")

print("\nSlottedUser memory overhead:")
print("  Object size:", sys.getsizeof(u2), "bytes")
# u2 has no __dict__ attribute! Attaching unexpected attributes will raise AttributeError.
```

- **Under the Hood / Why It Happens**:
By default, CPython instances store attributes in an instance-level hash map (`PyDictObject`). This dictionary provides flexible dynamic attribute assignment (`obj.new_attr = 1`), but incurs significant hash table allocation overhead per object.

When `__slots__` is declared, the CPython class creation mechanism allocates a fixed array of struct member pointers (`PyMemberDef`) directly in the object layout. Attributes are accessed via direct array index offsets rather than dictionary hash lookups.

- **Key Takeaway / Safe Pattern**:
Declare `__slots__` for classes that will be instantiated millions of times (such as DTOs, AST nodes, or data processing items). For CPU-bound parallel workloads constrained by the GIL, use Python's `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` instead of `Threading`.
