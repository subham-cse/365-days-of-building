# Day 150: Python Mutable Default Arguments & Shared State Traps

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
In Python, default arguments in function definitions are evaluated **only once**, at the time the function is defined when the module is first loaded—NOT each time the function is invoked!

If you use a mutable object (such as a `list`, `dict`, or custom class instance) as a default parameter value, that exact same object instance is shared across **every single call** to that function where the argument is omitted! Mutating the default parameter modifies state for all subsequent invocations across the entire application.

**The Code Snippet**:
```python
# BUGGY FUNCTION: Mutable default argument shared across all invocations
def add_item_buggy(item, item_list=[]):
    item_list.append(item)
    return item_list


# SAFE PATTERN: Use None sentinel value and initialize inside function
def add_item_safe(item, item_list=None):
    if item_list is None:
        item_list = []  # Instantiate a fresh list on EVERY call
    item_list.append(item)
    return item_list


# Execution Demonstration
print("--- Buggy Behavior (Shared Mutable State) ---")
user1_cart = add_item_buggy("Laptop")
print("User 1 Cart:", user1_cart)  # ['Laptop']

user2_cart = add_item_buggy("Headphones")
print("User 2 Cart:", user2_cart)  # TRAP: ['Laptop', 'Headphones'] !

print("\n--- Safe Behavior (Isolated State) ---")
user1_safe = add_item_safe("Laptop")
print("User 1 Safe Cart:", user1_safe)  # ['Laptop']

user2_safe = add_item_safe("Headphones")
print("User 2 Safe Cart:", user2_safe)  # ['Headphones']
```

**Under the Hood / Why It Happens**:
In Python's CPython implementation:
1. When a `def` statement is executed at module load time, Python constructs a function object (`PyFunctionObject`).
2. Default argument expressions are evaluated immediately, and their resulting references are stored in the function object's `__defaults__` tuple attribute (or `__kwdefaults__` for keyword arguments).
3. Inspecting `add_item_buggy.__defaults__` reveals `([],)`.

When `add_item_buggy("Laptop")` is called:
- Python assigns `item_list = add_item_buggy.__defaults__[0]`.
- `item_list.append(...)` mutates the list object held *inside* the function object's internal `__defaults__` attribute!
- On the next call without arguments, Python fetches the exact same mutated list from `__defaults__`.

**Key Takeaway / Safe Pattern**:
Never use mutable objects (`[]`, `{}`, `set()`, class instances) as default arguments in Python function signatures. Always use `None` as the default argument value and conditionally instantiate a fresh mutable container inside the function body (`if arg is None: arg = []`).
