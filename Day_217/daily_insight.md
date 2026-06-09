# Day 217: JVM G1GC String Deduplication vs String Interning (`String.intern()`)

**Language / Domain**: Java / JVM Memory Management

**The Core Concept / "Did You Know?"**:
In Java applications processing high volumes of text (e.g., JSON payloads, database entities, web requests), duplicate String objects often consume up to 30–50% of heap space. Developers often reach for `String.intern()` to collapse duplicates. However, `String.intern()` relies on a global, fixed-capacity native String Table outside the managed JVM garbage collection generation bounds, which can cause severe thread contention, stop-the-world GC pauses, and memory leaks if fed unbounded, dynamically generated strings.

Starting in Java 8 Update 20, HotSpot introduced **G1 Garbage Collector String Deduplication** (`-XX:+UseStringDeduplication`). Unlike `String.intern()`, string deduplication runs transparently in the background during garbage collection cycles, updating internal `char[]` / `byte[]` object references without mutating String identities or polluting the global string table.

**The Code Snippet**:
```java
public class StringOptimizationDemo {

    public static void main(String[] args) throws Exception {
        int count = 1_000_000;
        
        // TRAP: Bad pattern using intern() on high-cardinality dynamic strings
        long startIntern = System.currentTimeMillis();
        for (int i = 0; i < count; i++) {
            // Dynamic key generation causes huge StringTable lock contention
            String dynamicKey = ("USER_SESSION_" + i).intern();
        }
        long durationIntern = System.currentTimeMillis() - startIntern;
        System.out.println("Time taken with intern(): " + durationIntern + " ms");

        // RECOMMENDED: Let G1GC handle deduplication automatically via JVM flags:
        // java -XX:+UseG1GC -XX:+UseStringDeduplication -XX:StringDeduplicationAgeThreshold=3 StringOptimizationDemo
        
        // Demonstrating array reference identity vs value equivalence
        String str1 = new String("DEDUPLICATED_VALUE");
        String str2 = new String("DEDUPLICATED_VALUE");

        System.out.println("Before GC Deduplication:");
        System.out.println("Reference equal: " + (str1 == str2)); // false
        System.out.println("Value equal: " + str1.equals(str2));   // true

        // Force GC invocation to allow G1 String Deduplication thread to inspect candidates
        System.gc();
        Thread.sleep(200);

        System.out.println("After GC run (objects remain separate references, but share underlying byte[] array):");
        System.out.println("Reference equal: " + (str1 == str2)); // false (Identity preserved!)
        System.out.println("Value equal: " + str1.equals(str2));   // true
    }
}
```

**Under the Hood / Why It Happens**:
Java `String` objects (since Java 9) consist of a shallow object header, an `int hash`, and a reference to an underlying `byte[] value` array.

1. **`String.intern()`**:
   - Checks the native C++ `StringTable` hash map.
   - If present, returns the existing canonical `String` object pointer. If absent, adds the string to the table.
   - **Problems**: StringTable uses global bucket locks. When millions of unique strings are interned, bucket chains grow long, causing latency spikes in GC safepoints and permanent memory allocation in Native Memory.

2. **G1GC String Deduplication (`-XX:+UseStringDeduplication`)**:
   - During minor GC cycles, G1 examines strings that have survived a specified number of GC generations (configured via `-XX:StringDeduplicationAgeThreshold`, default is 3).
   - It computes a weak hash of the underlying `byte[]` array and looks up an internal deduplication hashtable.
   - If a duplicate `byte[]` array is found, G1 alters the pointer of `str2.value` to point directly to `str1.value`.
   - The original `str2` object identity (`str1 == str2`) remains `false`, preserving Java object reference semantics, while the duplicate byte array is reclaimed during the next GC cycle.

**Key Takeaway / Safe Pattern**:
- Avoid using `String.intern()` for dynamic, high-cardinality user data or dynamic keys.
- For modern JVM applications running on G1, ZGC, or Shenandoah GC, enable background automatic string deduplication via `-XX:+UseG1GC -XX:+UseStringDeduplication`.
- For domain models with bounded enum-like strings, use an explicit `ConcurrentHashMap` cache or `Enum` rather than standard `intern()`.
