# Day 078: Mutable Default Arguments and Late-Binding Closures in Python3

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
Python evaluates function default arguments **once when the function definition is executed** (at module load time), NOT each time the function is called.

If a default parameter value is a mutable object (such as a `list`, `dict`, or custom object instance), that single shared mutable object is reused across every function invocation! Any modifications made to that default argument persist indefinitely across subsequent calls.

A second common trap is **Late-Binding Closures**: Python closures capture variables by reference rather than by value, causing functions created inside loops to evaluate variables at call time rather than definition time.

**The Code Snippet**:
```python
# --- TRAP 1: Mutable Default Argument ---
def append_to_cache(item, cache=[]):
    # BAD: 'cache' list is initialized once at function definition time!
    cache.append(item)
    return cache

print("Call 1:", append_to_cache("User_A")) # Output: ['User_A']
print("Call 2:", append_to_cache("User_B")) # Output: ['User_A', 'User_B'] (UNEXPECTED SHARING!)

# --- SAFE PATTERN 1: Use None as default sentinel ---
def safe_append_to_cache(item, cache=None):
    if cache is None:
        cache = []
    cache.append(item)
    return cache

print("Safe Call 1:", safe_append_to_cache("User_A")) # Output: ['User_A']
print("Safe Call 2:", safe_append_to_cache("User_B")) # Output: ['User_B'] (ISOLATED!)


# --- TRAP 2: Late-Binding Closures in Loops ---
callbacks_unsafe = []
for i in range(3):
    # BAD: 'i' is captured by reference, not value!
    callbacks_unsafe.append(lambda: i * 10)

print("Unsafe Loop Closures:", [cb() for cb in callbacks_unsafe])
# Expected [0, 10, 20], but prints [20, 20, 20]!

# --- SAFE PATTERN 2: Early binding via default parameters or functools.partial ---
callbacks_safe = []
for i in range(3):
    # Bound immediately via default parameter argument
    callbacks_safe.append(lambda val=i: val * 10)

print("Safe Loop Closures:", [cb() for cb in callbacks_safe])
# Output: [0, 10, 20]
```

**Under the Hood / Why It Happens**:
1. **Mutable Defaults**: In CPython, function objects (`PyFunctionObject`) store default parameter values inside their `__defaults__` tuple attribute. When `def append_to_cache(...)` is compiled, CPython allocates a list object and attaches it to `append_to_cache.__defaults__`. Calling the function without arguments points the local parameter directly to `__defaults__[0]`, mutating the underlying object in place.
2. **Late-Binding Closures**: Python functions look up non-local variables using lexical scope closure cells (`__closure__`). The cell stores a reference/pointer to the outer scope variable `i`. When the loop finishes, `i` evaluates to `2`. When the lambdas execute later, they resolve `i` dynamically from the shared cell, yielding `2 * 10 = 20` for every closure.

**Key Takeaway / Safe Pattern**:
Always use `None` as the default value for optional mutable arguments, initializing the object inside the function body. For closures defined inside loops, use default parameter binding (`lambda val=i: ...`) or `functools.partial` to freeze parameter values at definition time.
