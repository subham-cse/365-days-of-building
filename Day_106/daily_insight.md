# Day 106: Late-Binding Closures and Mutable Default Argument Traps
- **Language / Domain**: Python3
- **The Core Concept / "Did You Know?"**: Python functions are first-class objects evaluated at definition time, not runtime. This introduces two classic traps:
1. **Mutable Default Arguments**: Default parameters (e.g. `def foo(acc=[])`) are evaluated **once** when the module is loaded. Subsequent function calls reuse the same mutable object across calls.
2. **Late-Binding Closures**: Variables captured in lambdas or nested functions look up values in the enclosing namespace **when the function is called**, not when it is created.

- **The Code Snippet**:
```python
# Trap 1: Mutable Default Argument
def add_item(item, target_list=[]):
    target_list.append(item)
    return target_list

print(add_item("A")) # ['A']
print(add_item("B")) # ['A', 'B'] - reused default list!

# Trap 2: Late-Binding Closures in Loops
def create_multipliers():
    handlers = []
    for i in range(3):
        # i is looked up dynamically when handler() is executed later
        handlers.append(lambda x: x * i)
    return handlers

multipliers = create_multipliers()
print([m(10) for m in multipliers]) # Expected [0, 10, 20], actual: [20, 20, 20]!

# Safe Patterns
def add_item_safe(item, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list

def create_multipliers_safe():
    # Capture current value of i using default argument binding
    return [lambda x, i=i: x * i for i in range(3)]

print([m(10) for m in create_multipliers_safe()]) # Output: [0, 10, 20]
```

- **Under the Hood / Why It Happens**:
For default arguments, Python stores default parameter values in the function object's `__defaults__` tuple. Because a list is mutable, modifying `target_list` directly mutates `add_item.__defaults__[0]`.

For closures, nested functions capture cell references (`cell` objects stored in `__closure__`) pointing to variable names in the outer scope, rather than copy values. When the loop finishes, `i` in the parent namespace equals `2`, so all lambdas accessing `cell.cell_contents` read `2`.

- **Key Takeaway / Safe Pattern**:
Always use `None` as the default value for mutable arguments (`list`, `dict`, `set`) and instantiate a fresh object inside the function body. For closures in loops, bind loop variables immediately using keyword argument defaults (`lambda x, i=i: x * i`).
