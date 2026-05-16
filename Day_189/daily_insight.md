# Day 189: Java Integer Caching and Autoboxing Equality Pitfalls

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
In Java, comparing reference objects using the `==` operator evaluates reference equality (memory location), whereas `.equals()` evaluates value equality. However, when autoboxing primitive `int` values into `Integer` wrapper objects, Java caches instances for values in the range **-128 to 127** via `IntegerCache`.

Because of this caching optimization, comparing two autoboxed `Integer` objects with value `100` using `==` returns `true` (they point to the exact same cached heap instance). But performing the exact same `==` comparison on autoboxed `Integer` objects with value `200` returns `false` (two distinct heap objects are allocated).

**The Code Snippet**:
```java
public class IntegerCacheTrap {
    public static void main(String[] args) {
        // Autoboxing primitives within [-128, 127]
        Integer a1 = 100;
        Integer a2 = 100;

        // Autoboxing primitives outside [-128, 127]
        Integer b1 = 200;
        Integer b2 = 200;

        System.out.println("a1 == a2 (100): " + (a1 == a2)); // Output: true
        System.out.println("b1 == b2 (200): " + (b1 == b2)); // Output: false

        // Correct structural comparison using .equals()
        System.out.println("b1.equals(b2): " + b1.equals(b2)); // Output: true
    }
}
```

**Under the Hood / Why It Happens**:
When `Integer a1 = 100;` is compiled, the Java bytecode emits a call to `Integer.valueOf(100)`.

Inside the OpenJDK `Integer` class implementation:
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```

By default, `IntegerCache.low` is `-128` and `IntegerCache.high` is `127`. For numbers within this range, `Integer.valueOf()` returns a reference to a pre-allocated static array of `Integer` objects on the heap. For values outside this range (like `200`), it executes `new Integer(i)`, allocating fresh heap objects with unique memory addresses.

**Key Takeaway / Safe Pattern**:
Never use the `==` or `!=` operators to compare wrapper objects (`Integer`, `Long`, `Short`, `Character`). Always use `.equals()` or unpack them to primitive types (`int`) prior to comparison.

```java
// Safe Pattern: Value equality or primitive unboxing
if (Objects.equals(b1, b2)) {
    // Correct comparison for any Integer object
}
```
