# Day 077: String Pool Caching & Autoboxing Pitfalls in Java

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
Java uses optimization techniques like the **String Constant Pool** and **Integer Cache** to conserve JVM heap memory. Because of these caches, primitive wrappers (like `Integer`) and literal strings retain identical object reference addresses under certain conditions, making reference equality checks (`==`) behave deceptively.

For example, `Integer a = 127; Integer b = 127;` evaluates `a == b` to `true`, but `Integer a = 128; Integer b = 128;` evaluates `a == b` to `false`! Relying on `==` instead of `.equals()` on boxed primitives or dynamically generated strings creates non-deterministic bugs that only manifest when numeric thresholds or string creation mechanisms change.

**The Code Snippet**:
```java
package com.insight.java;

public class JavaCachePitfalls {

    public static void main(String[] args) {
        // --- 1. Integer Caching Pitfall (-128 to 127) ---
        Integer i1 = 100;
        Integer i2 = 100;
        System.out.println("100 == 100? " + (i1 == i2)); // TRUE (IntegerCache hit)

        Integer i3 = 200;
        Integer i4 = 200;
        System.out.println("200 == 200? " + (i3 == i4)); // FALSE (Heap allocation, cache miss!)
        System.out.println("200 equals 200? " + i3.equals(i4)); // TRUE (Value check)

        // --- 2. String Pool vs Dynamic Heap Objects ---
        String s1 = "Hello";
        String s2 = "Hello";
        String s3 = new String("Hello");
        String s4 = s3.intern();

        System.out.println("Literal == Literal? " + (s1 == s2)); // TRUE (Same String Pool reference)
        System.out.println("Literal == new String()? " + (s1 == s3)); // FALSE (Heap reference)
        System.out.println("Literal == interned? " + (s1 == s4)); // TRUE (Explicitly interned)

        // --- 3. Autoboxing NullPointerException Trap ---
        Integer nullableCount = null;
        try {
            // Unboxing null Integer to primitive int throws NPE!
            int total = countItems() + nullableCount; 
        } catch (NullPointerException e) {
            System.out.println("Caught NPE from unboxing null primitive wrapper!");
        }
    }

    private static int countItems() {
        return 50;
    }
}
```

**Under the Hood / Why It Happens**:
1. **Integer Cache**: Java maintains an internal static cache array `IntegerCache.cache` initialized during JVM startup for values in range `[-128, 127]` (controlled by `-XX:AutoBoxCacheMax`). When autoboxing occurs (`Integer i = 100`), Java implicitly calls `Integer.valueOf(100)`, which returns cached object references for range $[-128, 127]$ and allocates `new Integer()` for values outside it.
2. **String Pool**: String literals are stored in the PermGen / Metaspace String Table (a specialized hashtable). `new String("Hello")` explicitly forces a new object allocation on the young-generation heap, bypassing the string pool lookup unless `.intern()` is explicitly called.
3. **Autoboxing/Unboxing**: When evaluating expressions mixing primitive types (`int`) and wrapper types (`Integer`), the compiler inserts bytecode calls to `.intValue()`. Invoking `.intValue()` on a `null` reference causes an immediate `NullPointerException`.

**Key Takeaway / Safe Pattern**:
Never check equality on object references or primitive wrappers using `==`; always use `.equals()` or `Objects.equals(a, b)`. Use primitive types (`int`, `long`, `boolean`) in performance-critical loops and data structures to avoid garbage collection overhead and null unboxing exceptions.
