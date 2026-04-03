# Day 134: Python Late-Binding Closures in Loop Traps

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python closures look up variables by reference, not by value, at the moment the inner function is **executed**, rather than when it is defined. This behavior is known as **late binding**.

When creating functions or lambdas inside a loop that reference the loop variable, every single function ends up referencing the exact same loop variable in the outer scope. When the functions are invoked later, they all evaluate to the *final* value of that variable after the loop finishes!

**The Code Snippet**:
```python
def create_multipliers_buggy():
    multipliers = []
    for i in range(4):
        # TRAP: 'i' is captured by reference, not by value
        multipliers.append(lambda x: x * i)
    return multipliers


def create_multipliers_fixed():
    multipliers = []
    for i in range(4):
        # SAFE PATTERN: Use default argument binding to capture current value of 'i'
        multipliers.append(lambda x, i=i: x * i)
    return multipliers


# --- Execution ---
buggy_funcs = create_multipliers_buggy()
print("Buggy closures results (expected 0, 2, 4, 6):")
print([f(2) for f in buggy_funcs])  # Output: [6, 6, 6, 6] !

fixed_funcs = create_multipliers_fixed()
print("\nFixed closures results:")
print([f(2) for f in fixed_funcs])  # Output: [0, 2, 4, 6]
```

**Under the Hood / Why It Happens**:
In Python, functions hold a reference to their enclosing scope's local variable namespace via their `__closure__` attribute. 

When `lambda x: x * i` is defined:
1. Python creates a function object whose closure cell points to the variable slot `i` in `create_multipliers_buggy`'s stack frame.
2. The loop runs to completion, incrementing `i` from `0` to `3`.
3. When `f(2)` is called later, Python evaluates the AST instruction `LOAD_DEREF` to fetch the current value stored in the closure cell `i`. Because `i` was left at `3`, all four lambdas multiply `x` by `3`.

In the fixed version `lambda x, i=i: x * i`, default parameter values are evaluated when the `def`/`lambda` expression is **parsed and executed during loop iterations**. This binds the primitive value `i` to the function object's `__defaults__` tuple instantly.

**Key Takeaway / Safe Pattern**:
When defining lambdas or inner functions inside loops or comprehensions, pass iteration variables as default arguments (`i=i`), or use `functools.partial` to bind arguments immediately at definition time.
