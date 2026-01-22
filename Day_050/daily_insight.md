# Day 050: Python `is` vs `==` and Small Integer Caching

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
In Python, `==` tests for **value equality** (calling `__eq__()`), checking if two objects contain equivalent content. The `is` operator tests for **reference identity**, checking whether two variables point to the exact same location in memory (`id(a) == id(b)`).

Python caches and reuses small integer objects (integers from `-5` to `256`) and single-word string constants at CPython startup. Relying on `is` for integer or string equality comparisons introduces bugs that manifest only when integer values exceed `256`.

**The Code Snippet**:
```python
def demonstrate_identity_vs_equality():
    # Integers within small integer cache (-5 to 256)
    x = 250
    y = 250

    print(f"x = {x}, y = {y}")
    print("x == y:", x == y)  # True
    print("x is y:", x is y)  # True (Cached single object in CPython!)

    # Integers OUTSIDE small integer cache
    a = 257
    b = 257

    print(f"\na = {a}, b = {b}")
    print("a == b:", a == b)  # True (Values match)
    print("a is b:", a is b)  # False (Different heapPyObject pointers!)

    # Dynamic string allocation
    str1 = "hello_world"
    str2 = "".join(["hello", "_", "world"])

    print(f"\nstr1 = '{str1}', str2 = '{str2}'")
    print("str1 == str2:", str1 == str2)  # True
    print("str1 is str2:", str1 is str2)  # False (Runtime string creation)

if __name__ == "__main__":
    demonstrate_identity_vs_equality()
```

**Under the Hood / Why It Happens**:
In CPython, integer objects are instances of `PyLongObject`. To avoid frequent memory allocation overhead for common loop indices and counters, CPython pre-allocates a static array of 262 `PyLongObject` instances representing integers in the range `[-5, 256]` during interpreter initialization.

When any expression creates an integer in this range (e.g., `x = 250`), CPython returns a pointer to the existing static memory block. For numbers `< -5` or `> 256`, CPython allocates a new `PyLongObject` on the C heap, resulting in distinct memory addresses (`id(a) != id(b)`).

**Key Takeaway / Safe Pattern**:
Use `==` for value comparisons (numbers, strings, lists, dictionaries, custom data objects). Use `is` ONLY when checking identity against singleton constants like `None`, `True`, or `False` (e.g., `if val is None:`).
