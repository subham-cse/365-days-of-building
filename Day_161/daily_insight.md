# Day 161: String Interning Mechanics and Heap Placement Leaks

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
In Java, string literals are automatically interned into a special JVM structure called the **String Constant Pool**. However, strings dynamically constructed at runtime (e.g., using `new String(...)`, `StringBuilder`, or `String.format()`) reside in normal Heap memory unless explicitly added to the pool via `String.intern()`.

Before Java 7, the String Pool lived in PermGen memory, where excessive interning caused fatal `OutOfMemoryError: PermGen space`. Since Java 7, the pool resides in the main Heap memory. Despite this change, manually calling `String.intern()` on millions of unique dynamically generated strings (such as UUIDs or web request payloads) can severely degrade GC performance and leak memory.

**The Code Snippet**:

```java
public class StringPoolDemo {
    public static void main(String[] args) {
        String literal = "Hello World";
        String heapString = new String("Hello World");
        
        // 1. Reference comparison vs Content comparison
        System.out.println("literal == heapString: " + (literal == heapString)); // false
        
        // 2. Explicit interning fetches the pooled reference
        String internedString = heapString.intern();
        System.out.println("literal == internedString: " + (literal == internedString)); // true
        
        // 3. Substring behavior quirk (Java 7+)
        String largeBuffer = "DATABUFFER_" + "x".repeat(10_000_000);
        // Prior to Java 7, substring shared internal char[] of parent string!
        // In Java 7+, substring copies char[]/byte[], avoiding heap leaks.
        String smallSubstring = largeBuffer.substring(0, 10);
        System.out.println("Substring extracted safely: " + smallSubstring);
    }
}
```

**Under the Hood / Why It Happens**:
The JVM String Pool is implemented natively as a fixed-capacity hashtable (`StringTable`) storing references to `java.lang.String` instances on the heap. When `String.intern()` is invoked:
1. The JVM calculates the hash of the string and checks the native `StringTable` bucket.
2. If found, it returns the reference to the existing pooled string.
3. If not found, it inserts the current string reference into `StringTable` and returns it.

If an application interns millions of dynamic keys, the `StringTable` bucket linked lists grow long. Because entries in `StringTable` act as strong GC roots unless cleaned up during full GC passes, excessive interning leads to severe hashtable lookup slowdowns and elevated GC pause times.

**Key Takeaway / Safe Pattern**:
Rely on string literals for static constants. Avoid calling `String.intern()` on dynamic inputs (e.g., API payloads, database keys). If memory deduplication is required for massive datasets, enable JVM native string deduplication via `-XX:+UseStringDeduplication` (available with G1 and ZGC).
