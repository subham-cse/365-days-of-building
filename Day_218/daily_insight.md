# Day 218: Python Late-Binding Closures & Mutable Default Arguments

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python functions are first-class objects evaluated at runtime. Two notorious semantics trap Python developers:
1. **Late-Binding Closures**: Variables referenced inside nested functions or lambda expressions are looked up when the outer function is *called*, not when the function is *defined*.
2. **Mutable Default Arguments**: Default parameter values (`def fn(arg=[])`) are evaluated *once* when the function definition is executed at module import time, not each time the function is called.

Combining these two rules can lead to unexpected state leaks across function calls and loop iteration bugs in event handlers, factory functions, or callbacks.

**The Code Snippet**:
```python
def create_handlers_buggy():
    handlers = []
    # BUG 1: Late-binding closure trap in loops
    for i in range(3):
        handlers.append(lambda: i * 10)
    return handlers

def append_to_list_buggy(element, target_list=[]):
    # BUG 2: Mutable default argument trap
    target_list.append(element)
    return target_list

def create_handlers_fixed():
    handlers = []
    # FIX 1: Bind variable scope at definition time via default parameter
    for i in range(3):
        handlers.append(lambda val=i: val * 10)
    return handlers

def append_to_list_fixed(element, target_list=None):
    # FIX 2: Sentinel pattern for default parameter
    if target_list is None:
        target_list = []
    target_list.append(element)
    return target_list

if __name__ == "__main__":
    # Demonstrating Late-Binding Trap
    buggy_fns = create_handlers_buggy()
    print("Buggy Closure Outputs:")
    print([fn() for fn in buggy_fns])  # Expected [0, 10, 20], Got [20, 20, 20]!

    fixed_fns = create_handlers_fixed()
    print("Fixed Closure Outputs:")
    print([fn() for fn in fixed_fns])  # Output: [0, 10, 20]

    # Demonstrating Mutable Default Parameter Trap
    print("\nMutable Default Argument Trap:")
    res1 = append_to_list_buggy("A")
    res2 = append_to_list_buggy("B")
    print(f"res1: {res1}")  # Output: ['A', 'B'] (Leaked into res1!)
    print(f"res2: {res2}")  # Output: ['A', 'B']

    print("\nSentinel Default Pattern:")
    clean1 = append_to_list_fixed("A")
    clean2 = append_to_list_fixed("B")
    print(f"clean1: {clean1}")  # Output: ['A']
    print(f"clean2: {clean2}")  # Output: ['B']
```

**Under the Hood / Why It Happens**:
1. **Closure Lookup**:
   When `lambda: i * 10` is defined inside a loop, Python creates a function object holding a reference to the enclosing scope's local variable cell (`__closure__`), rather than copying the primitive scalar value of `i`. When the lambda is eventually called, it looks up `i` in the cell dictionary. By then, the loop has completed, and `i` evaluates to `2` for every call.
   Using default arguments (`lambda val=i: val * 10`) forces Python to evaluate `i` at definition time and store the value in `fn.__defaults__`.

2. **Function Definition Objects**:
   When Python parses `def fn(target_list=[]):`, it evaluates `[]` immediately and attaches the resulting list instance to `fn.__defaults__`. Every subsequent call that relies on the default parameter receives a reference to that *same exact list instance* residing on `fn.__defaults__[0]`.

**Key Takeaway / Safe Pattern**:
- **For Closures inside loops**: Pass iteration variables as default argument values (`lambda i=i: ...`) or use `functools.partial(func, i)`.
- **For Mutable Default Arguments**: Use `None` as a sentinel default value and initialize mutable collections (lists, dicts, sets) conditionally inside the function body.
