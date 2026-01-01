# Day 006: Late-Binding Closures and Mutable Default Arguments
**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python evaluates default function arguments exactly once when the function definition is executed (at module import time), NOT when the function is called. Passing mutable objects like `list`, `dict`, or `set` as default arguments leads to shared state across all function invocations.

Similarly, Python closures capture variables by reference rather than by value (late binding). If functions are created in a loop and reference a loop variable, all generated functions will read the final value of the loop variable when executed, leading to identical runtime behavior across all callbacks.

**The Code Snippet**:
```python
# Trap 1: Mutable Default Argument
def append_to_list(element, target_list=[]):
    target_list.append(element)
    return target_list

print(append_to_list(1)) # Output: [1]
print(append_to_list(2)) # Output: [1, 2] (NOT [2]!)
print(append_to_list(3)) # Output: [1, 2, 3]

# Trap 2: Late-Binding Closures in Loops
def create_multipliers():
    handlers = []
    for i in range(4):
        # Closure captures variable `i`, not its current value!
        handlers.append(lambda x: x * i)
    return handlers

multipliers = create_multipliers()
print([f(10) for f in multipliers]) 
# Expected: [0, 10, 20, 30]
# Actual Output: [30, 30, 30, 30]!
```

**Under the Hood / Why It Happens**:
When Python executes a `def` statement, it constructs a function object. Default argument expressions are evaluated immediately, and the resulting objects are stored in the function's `__defaults__` attribute. Every call to the function that doesn't supply an explicit argument accesses this single object reference stored in `__defaults__`.

For closures, free variables used inside inner functions are resolved via cell objects (`__closure__` tuple). A cell holds a pointer to the variable in the outer scope's namespace. By the time the loop finishes in `create_multipliers()`, `i` has been incremented to `3`. When the lambda is called, it dereferences the cell containing `i`, which currently evaluates to `3`.

**Key Takeaway / Safe Pattern**:
Use `None` as the default value for mutable arguments and initialize them dynamically inside the body. For closures in loops, bind loop variables as default argument values or use `functools.partial` to force early binding.

```python
# SAFE Pattern 1: Sentinel default argument
def append_to_list_safe(element, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(element)
    return target_list

# SAFE Pattern 2: Default parameter trick for early closure binding
def create_multipliers_safe():
    # Binding `i=i` evaluates `i` during function definition time
    return [lambda x, i=i: x * i for i in range(4)]

print([f(10) for f in create_multipliers_safe()]) # Output: [0, 10, 20, 30]
```
