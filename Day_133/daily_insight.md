# Day 133: Java Integer Boxing & Identity Cache Pitfalls

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
In Java, comparing object references using the `==` operator checks for memory address equality, while `.equals()` checks for value equality. When auto-boxing primitive `int` values into wrapper `Integer` objects, Java caches instances for small numbers within a specific range (-128 to 127).

Because of this hidden caching mechanism, comparing two `Integer` references with `==` yields `true` for numbers like `100`, but yields `false` for numbers like `200`! Relying on `==` for object wrappers introduces sporadic bugs when numeric thresholds cross boundary values in production.

**The Code Snippet**:
```java
public class IntegerCacheDemo {
    public static void main(String[] args) {
        // Auto-boxing values within cache range [-128, 127]
        Integer a1 = 100;
        Integer a2 = 100;

        // Auto-boxing values OUTSIDE cache range
        Integer b1 = 200;
        Integer b2 = 200;

        System.out.println("a1 == a2 (100): " + (a1 == a2)); // true! (Same cached instance)
        System.out.println("b1 == b2 (200): " + (b1 == b2)); // false! (Different heap objects)

        // Correct comparison using equals()
        System.out.println("b1.equals(b2) (200): " + b1.equals(b2)); // true

        // Explicit heap instantiation bypasses cache entirely
        Integer c1 = new Integer(100);
        Integer c2 = new Integer(100);
        System.out.println("c1 == c2 (explicit new): " + (c1 == c2)); // false
    }
}
```

**Under the Hood / Why It Happens**:
When auto-boxing occurs (e.g., `Integer x = 100`), the Java compiler translates the code into a call to `Integer.valueOf(100)`.

Inside `java.lang.Integer`:
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```
- By default, `IntegerCache` pre-allocates an array of `Integer` objects covering `-128` to `127` during JVM bootstrap initialization.
- For numbers in this range, `valueOf()` returns a reference to the existing static array element.
- For numbers outside this range, `valueOf()` executes `new Integer(i)`, allocating a fresh object on the Java Heap.

Similar caching mechanisms exist for `Byte`, `Short`, `Long` (-128 to 127), and `Character` (0 to 127), as well as `Boolean` (`TRUE`/`FALSE`).

**Key Takeaway / Safe Pattern**:
Never use `==` or `!=` to compare boxed primitives (`Integer`, `Long`, `Short`). Always use `.equals()` or unbox variables explicitly to primitive types (`int`, `long`) before performing comparison operations.
