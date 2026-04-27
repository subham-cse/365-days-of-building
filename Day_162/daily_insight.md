# Day 162: Late-Binding Closures in Loops and `__slots__` Optimizations

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python functions are first-class objects that support lexical closures. However, Python uses **late binding** for variable lookup inside closures: variables referenced inside inner functions are looked up at the time the closure is *executed*, not at the time it is *defined*.

Creating lambdas or local functions inside a loop that reference the loop variable often leads to dynamic lookup bugs where all closures evaluate using the loop's final iteration value. Additionally, Python objects by default use dynamic instance dictionaries (`__dict__`), which consume significant RAM compared to class definitions using `__slots__`.

**The Code Snippet**:

```python
# Part 1: Late-Binding Closure Pitfall & Fix
def create_multipliers_buggy():
    # BUG: Every inner function binds to the variable `i` by reference!
    return [lambda x: x * i for i in range(4)]

def create_multipliers_fixed():
    # SAFE: Early binding using default argument trick `i=i`
    return [lambda x, i=i: x * i for i in range(4)]

print("Buggy multipliers for 2:", [f(2) for f in create_multipliers_buggy()])
# Output: [6, 6, 6, 6] (because `i` is 3 when lambdas are executed)

print("Fixed multipliers for 2:", [f(2) for f in create_multipliers_fixed()])
# Output: [0, 2, 4, 6]

# Part 2: Memory Optimization with __slots__
class DynamicPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ('x', 'y')  # Prevents creation of __dict__ per instance
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
p1 = DynamicPoint(10, 20)
p2 = SlottedPoint(10, 20)
print(f"Dynamic instance size: {sys.getsizeof(p1) + sys.getsizeof(p1.__dict__)} bytes")
print(f"Slotted instance size: {sys.getsizeof(p2)} bytes")
```

**Under the Hood / Why It Happens**:
In Python, when a nested function references a variable from an outer scope, CPython stores it in a cell object (`co_freevars` / `co_cellvars`). The inner function holds a reference to the cell container itself, not the value inside it. As the `for i in range(4)` loop runs, the single cell container bound to `i` is overwritten repeatedly until its value settles at `3`.

For instance memory, standard Python objects allocate a dictionary (`__dict__`) to support arbitrary runtime attribute assignments (e.g. `obj.custom_attr = 123`). Defining `__slots__` tells CPython to allocate a fixed-size struct array for instance attributes directly, bypassing `__dict__` creation and saving ~60% of per-object memory overhead.

**Key Takeaway / Safe Pattern**:
1. When generating closures inside loops, pass loop variables as default argument values (`lambda x, i=i: ...`) or use `functools.partial`.
2. For high-volume data classes created millions of times, use `__slots__` or `@dataclass(slots=True)` to drastically reduce memory overhead.
