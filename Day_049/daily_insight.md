# Day 049: Java String Interning and Constant Pool Pitfalls

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
In Java, String literals (`"hello"`) are automatically cached in a special memory region within the Heap called the **String Constant Pool**. When string literals with identical character sequences are evaluated, the JVM returns a reference to the exact same pooled `String` instance.

However, creating strings dynamically at runtime via `new String("hello")` or string concatenation (`+`) allocates distinct heap objects outside the pool. Comparing strings with reference equality (`==`) instead of logical value equality (`.equals()`) causes intermittent bugs when dynamic string data is introduced.

**The Code Snippet**:
```java
public class StringPoolDemo {
    public static void main(String[] args) {
        // String Literals: Retained in JVM String Constant Pool
        String literal1 = "JavaPlatform";
        String literal2 = "JavaPlatform";

        // Explicit heap instance allocation
        String heapInstance = new String("JavaPlatform");

        // Runtime string concatenation (computed at runtime)
        String prefix = "Java";
        String dynamicString = prefix + "Platform";

        // Manually interned reference
        String internedString = heapInstance.intern();

        System.out.println("--- Reference Comparison (==) Results ---");
        System.out.println("literal1 == literal2: " + (literal1 == literal2));             // true (same pooled object)
        System.out.println("literal1 == heapInstance: " + (literal1 == heapInstance));       // false (different heap refs)
        System.out.println("literal1 == dynamicString: " + (literal1 == dynamicString));     // false (runtime string builder)
        System.out.println("literal1 == internedString: " + (literal1 == internedString));   // true (retrieved from pool)

        System.out.println("\n--- Logical Content Comparison (.equals) Results ---");
        System.out.println("literal1.equals(heapInstance): " + literal1.equals(heapInstance));   // true
        System.out.println("literal1.equals(dynamicString): " + literal1.equals(dynamicString)); // true
    }
}
```

**Under the Hood / Why It Happens**:
During class file loading, the JVM parses literal string constants into the `Constant_String_info` table.

When the JVM executes literal string bytecode instructions (`ldc`), it queries an internal native C++ hash map (`StringTable`). If the string string value already exists, `ldc` pushes the existing pooled reference onto the operand stack. 

When invoking `new String(...)` or runtime concatenation (`StringBuilder.toString()`), the JVM bypasses `StringTable` lookup and allocates a new instance on the normal Garbage-Collected Heap. Calling `.intern()` queries `StringTable`, inserting the heap string if absent and returning the pooled reference.

**Key Takeaway / Safe Pattern**:
Always compare strings using `.equals()` or `Objects.equals(a, b)` rather than `==`. Avoid unnecessary calls to `.intern()` on large dynamic strings, as filling the `StringTable` increases JVM GC pause overhead and native table lock contention.
