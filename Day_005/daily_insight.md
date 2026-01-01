# Day 005: The Integer Cache and String Pool Mutation Trap
**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
In Java, object reference comparison (`==`) behaves unexpectedly due to runtime caching optimizations like the `IntegerCache` and the String Constant Pool. While autoboxed integers between -128 and 127 evaluate as identity-equal (`==`), values outside this range create distinct object references and return `false`.

Even more dangerously, using Java Reflection makes it possible to mutate `final` cached values (such as mutating `Integer.valueOf(42)` or private `char[]`/`byte[]` backing arrays of interned `String` objects), effectively corrupting the state of numbers and literal strings globally across the entire JVM runtime.

**The Code Snippet**:
```java
import java.lang.reflect.Field;

public class JavaCacheTrap {
    public static void main(String[] args) throws Exception {
        // Integer Caching Pitfall
        Integer a = 100;
        Integer b = 100;
        System.out.println("100 == 100: " + (a == b)); // true (cached)

        Integer x = 200;
        Integer y = 200;
        System.out.println("200 == 200: " + (x == y)); // false (new objects)

        // Corrupting the JVM Integer Cache via Reflection
        Field cacheField = Class.forName("java.lang.Integer$IntegerCache")
                               .getDeclaredField("cache");
        cacheField.setAccessible(true);
        Integer[] cache = (Integer[]) cacheField.get(null);

        // Find index for 42 (-128 offset -> index 42 + 128 = 170)
        int indexFor42 = 42 + 128;
        cache[indexFor42] = 1337; // Mutate cached 42 to 1337!

        Integer num = 42;
        System.out.printf("Integer.valueOf(42) now yields: %d\n", num);

        // Mathematical impossibility in appearance:
        int result = 40 + 2;
        System.out.println("40 + 2 autoboxed as Integer: " + Integer.valueOf(result));
    }
}
```

**Under the Hood / Why It Happens**:
The Java Virtual Machine (JVM) optimizes memory usage by maintaining a flyweight pool for immutable primitive wrappers. The `java.lang.Integer.IntegerCache` class pre-allocates an array containing `Integer` instances for values from `-128` to `127` (configurable via `-XX:AutoBoxCacheMax`). 

When autoboxing occurs (`Integer a = 100`), the compiler emits bytecode calling `Integer.valueOf(int)`. If the argument is within range, `Integer.valueOf` returns the pre-existing cached instance. Outside this range, it executes `new Integer(v)`. Comparing wrappers with `==` compares memory addresses, causing `a == b` to return `true` for cached range and `false` otherwise. Reflection bypasses language visibility rules and mutates the internal array held by `IntegerCache`.

**Key Takeaway / Safe Pattern**:
Never rely on reference equality (`==`) when comparing boxed primitives or strings in Java; always use `.equals()`. To avoid unwanted autoboxing traps in high-performance or financial applications, use primitive types (`int`, `long`) or explicit equality checks.

```java
// SAFE: Always use .equals() for wrapper objects
Integer val1 = 200;
Integer val2 = 200;

if (java.util.Objects.equals(val1, val2)) {
    System.out.println("Values are logically equal.");
}
```
