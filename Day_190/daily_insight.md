# Day 190: Python3 Late-Binding Closures and Mutable Default Arguments

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python evaluates default function arguments **once** when the function definition is executed at module import time, not each time the function is invoked. If you use a mutable object (like a `list` or `dict`) as a default argument, all invocations of that function without an explicit argument share the exact same mutable instance.

A closely related trap occurs with **late-binding closures** inside loops. Functions created in a loop bind to variables in the outer scope by reference (symbol lookup), not by value snapshot. When the closure finally executes, it inspects the final mutated value of the loop index variable.

**The Code Snippet**:
```python
# Trap 1: Mutable Default Argument
def append_to_list(element, target_list=[]):
    target_list.append(element)
    return target_list

print(append_to_list(1)) # Output: [1]
print(append_to_list(2)) # Output: [1, 2] (NOT [2]!)


# Trap 2: Late-Binding Closure in Loop
def create_multipliers():
    handlers = []
    for i in range(3):
        # Closure references 'i' lazily
        handlers.append(lambda x: x * i)
    return handlers

funcs = create_multipliers()
# Expectation: 0, 2, 4
# Reality: All functions evaluate 'i' when invoked, where i == 2
print([f(2) for f in funcs]) # Output: [4, 4, 4]
```

**Under the Hood / Why It Happens**:
1. **Mutable Default**: Python function objects maintain a `__defaults__` tuple attribute holding parameter default values. Modifying `target_list` mutates `append_to_list.__defaults__[0]` directly in memory.
2. **Late Binding**: When `lambda x: x * i` is defined inside `create_multipliers()`, its `__closure__` cell references the variable slot `i` in the outer lexical scope frame. It does not store the integer value of `i` at closure creation time. When `f(2)` is executed later, the interpreter reads the current value of `i` in that scope (which is `2`).

**Key Takeaway / Safe Pattern**:
Use `None` as the default value sentinel for mutable arguments, and capture loop variables immediately via argument default values or `functools.partial`.

```python
# Safe Pattern 1: Sentinel default argument
def safe_append(element, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(element)
    return target_list

# Safe Pattern 2: Default argument binding forces snapshot copy
def create_safe_multipliers():
    return [lambda x, val=i: x * val for i in range(3)]
```
