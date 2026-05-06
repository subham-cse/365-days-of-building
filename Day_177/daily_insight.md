# Day 177: Integer Boxing Cache Pitfalls and Primitive Equality Semantics

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
Java uses autoboxing to seamlessly convert between primitive types (`int`) and object wrappers (`Integer`). To optimize memory and performance, the JVM maintains an **Integer Cache** (`IntegerCache`) for values in the range `-128` to `127`.

When autoboxing an integer within this range, `Integer.valueOf(val)` returns a cached reference to the exact same object header. However, for values outside this range (`>= 128` or `<= -129`), autoboxing allocates a new `Integer` heap object on every evaluation. Using `==` on boxed integers will yield `true` for small numbers and `false` for larger numbers!

**The Code Snippet**:

```java
public class IntegerCacheDemo {
    public static void main(String[] args) {
        // 1. Within IntegerCache range (-128 to 127)
        Integer a1 = 100;
        Integer b1 = 100;
        System.out.println("a1 == b1 (100): " + (a1 == b1)); // TRUE (Same pooled object reference!)

        // 2. Outside IntegerCache range
        Integer a2 = 200;
        Integer b2 = 200;
        System.out.println("a2 == b2 (200): " + (a2 == b2)); // FALSE (Different Heap Allocations!)

        // 3. Safe Content Comparison using .equals()
        System.out.println("a2.equals(b2): " + a2.equals(b2)); // TRUE

        // 4. Primitive Unboxing Comparison
        int primitiveA2 = 200;
        System.out.println("a2 == primitiveA2: " + (a2 == primitiveA2)); // TRUE (Unboxes a2 to primitive)
    }
}
```

**Under the Hood / Why It Happens**:
When Java code assigns `Integer a = 100;`, the javac compiler replaces it with `Integer a = Integer.valueOf(100);`.

Looking at `Integer.valueOf(int i)` source implementation:
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```
`IntegerCache.low` is fixed at `-128`, while `IntegerCache.high` defaults to `127` (configurable via `-XX:AutoBoxCacheMax=<size>`).

Comparing objects using `==` checks whether both pointers point to the exact same memory address. For `100`, both variables point to the static array element in `IntegerCache`. For `200`, two distinct `Integer` objects are created on the heap, so `a2 == b2` evaluates to reference inequality (`false`).

**Key Takeaway / Safe Pattern**:
Never use `==` to compare boxed primitive wrapper objects (`Integer`, `Long`, `Short`, `Character`). Always use `.equals()` or unbox them to primitive primitives (`int`) before comparing.
