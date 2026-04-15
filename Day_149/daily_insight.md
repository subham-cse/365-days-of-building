# Day 149: Java String Pool Caching & String Immutability Traps

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
Java maintains a special memory structure called the **String Constant Pool** inside the JVM Heap. When a string literal is created (e.g. `String s = "hello"`), the JVM checks if an identical string already exists in the pool. If so, it reuses the existing heap reference instead of allocating new memory.

However, creating strings dynamically using string concatenation in loops or calling `new String("hello")` bypasses the String Pool entirely, allocating distinct object instances on the Heap. Comparing strings using `==` checks reference identities rather than contents, causing code that worked with string literals to fail mysteriously when processing runtime string data!

**The Code Snippet**:
```java
public class StringPoolDemo {
    public static void main(String[] args) {
        // String literals automatically pooled by JVM
        String str1 = "Polyglot";
        String str2 = "Polyglot";

        // Dynamic construction bypasses string pool
        String str3 = new String("Polyglot");
        String str4 = "Poly" + "glot"; // Computed at compile-time by javac!
        
        String part1 = "Poly";
        String part2 = "glot";
        String str5 = part1 + part2; // Computed at runtime via StringBuilder!

        System.out.println("str1 == str2 (literals): " + (str1 == str2)); // true (Same pool reference)
        System.out.println("str1 == str3 (explicit new): " + (str1 == str3)); // false (Different heap objects)
        System.out.println("str1 == str4 (compile-time concat): " + (str1 == str4)); // true
        System.out.println("str1 == str5 (runtime concat): " + (str1 == str5)); // false!

        // Manually intern runtime string into pool
        String str5Interned = str5.intern();
        System.out.println("str1 == str5.intern(): " + (str1 == str5Interned)); // true

        // SAFE PATTERN: Always use equals() for content comparison
        System.out.println("str1.equals(str5): " + str1.equals(str5)); // true
    }
}
```

**Under the Hood / Why It Happens**:
In the JVM memory specification (JDK 7+):
1. **String Constant Pool**: Implemented as a hashtable (`StringTable`) storing references to `java.lang.String` objects on the heap.
2. When `javac` compiles literal constants (`"Poly" + "glot"`), constant folding optimizes the expression into `"Polyglot"` in the class file's Constant Pool table.
3. When non-final variables are concatenated (`part1 + part2`), `javac` generates bytecode instructions executing `new StringBuilder().append(part1).append(part2).toString()`. Calling `.toString()` allocates a fresh `String` object on the Heap without interning it into `StringTable`.

When `==` evaluates `str1 == str5`, the JVM compares memory addresses (`0x1004` vs `0x5088`), returning `false`. Calling `.intern()` manually searches `StringTable` and returns the canonical pooled reference.

**Key Takeaway / Safe Pattern**:
Never compare strings using `==` or `!=` in Java. Always compare string contents using `.equals()` or `.equalsIgnoreCase()`. Avoid calling `new String("...")` or excessive `.intern()` calls, as interned strings persist in memory and can pressure JVM garbage collection tables.
