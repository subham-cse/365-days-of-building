# Day 034: Python's Late-Binding Closures in Loops

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
When defining functions inside a loop that reference a loop variable, Python does not bind the value of the loop variable at the time the function is defined. Instead, Python looks up the variable's value when the inner function is actually called (late binding). Because the loop finishes executing before any of the created functions are typically invoked, all generated functions reference the exact same variable in the enclosing scope, evaluating to its final iteration value.

This counterintuitive behavior frequently trips up developers building event handlers, callbacks, or list comprehensions containing lambda expressions.

**The Code Snippet**:
```python
def create_multipliers():
    # Buggy version: Late binding causes all multipliers to use the final value of i (4)
    buggy_multipliers = [lambda x: x * i for i in range(5)]
    
    # Correct version 1: Bind i at definition time using a default argument
    fixed_multipliers_default = [lambda x, i=i: x * i for i in range(5)]
    
    # Correct version 2: Use functools.partial to explicitly bind arguments
    from functools import partial
    fixed_multipliers_partial = [partial(lambda i, x: x * i, i) for i in range(5)]
    
    return buggy_multipliers, fixed_multipliers_default, fixed_multipliers_partial

if __name__ == "__main__":
    buggy, fixed_default, fixed_partial = create_multipliers()
    
    print("Buggy output (expected 0, 2, 4, 6, 8):")
    print([func(2) for func in buggy])  # Prints: [8, 8, 8, 8, 8]
    
    print("\nFixed output with default arg:")
    print([func(2) for func in fixed_default])  # Prints: [0, 2, 4, 6, 8]
    
    print("\nFixed output with partial:")
    print([func(2) for func in fixed_partial])  # Prints: [0, 2, 4, 6, 8]
```

**Under the Hood / Why It Happens**:
In Python, closures store a cell object referencing the scope variable, not a copy of the variable's current value. When `lambda x: x * i` is defined inside the loop, the cell object references the variable `i` in the frame of `create_multipliers()`. 

During each iteration, the variable `i` is mutated in place within the same scope frame. When the lambda is eventually called via `func(2)`, Python performs a scope lookup for `i`, follows the cell reference to `create_multipliers`'s scope, and retrieves whatever value `i` currently holds (which is `4` after the loop completes). Using default arguments (`lambda x, i=i: ...`) evaluates `i` during function *definition* and stores the value in the function object's `__defaults__` tuple, bypassing late-binding scope lookups.

**Key Takeaway / Safe Pattern**:
To capture iteration variables inside local functions or lambdas, explicitly bind them at definition time using default argument parameters (`i=i`) or `functools.partial`. Never assume a closure captures primitive snapshot values across loop iterations.
