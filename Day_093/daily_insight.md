# Day 093: JVM Memory Layout & ConcurrentHashMap Fine-Grained Locking in Java

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
The JVM memory layout is split into two primary areas: the **Stack** (storing thread-local primitive local variables and object reference pointers) and the **Heap** (storing actual object instances and array data).

When handling high-concurrency shared state, naive synchronization using `synchronized(map)` or `Hashtable` locks the entire data structure for every read/write operation, creating severe lock contention bottlenecks across threads.

To solve this, Java provides `ConcurrentHashMap`. Unlike traditional synchronized maps, `ConcurrentHashMap` uses **Fine-Grained Locking (Bucket-Level Locking)** and Lock-Free CAS (Compare-And-Swap) operations for reads, enabling lock-free concurrent reads and parallel write operations across separate array buckets!

**The Code Snippet**:
```java
package com.insight.java;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ConcurrentHashMapPerformance {

    private static final ConcurrentHashMap<String, Integer> counterMap = new ConcurrentHashMap<>();

    // TRAP: Non-atomic compound operation on ConcurrentHashMap!
    public static void incrementUnsafe(String key) {
        Integer current = counterMap.get(key); // Step 1: Read
        if (current == null) {
            counterMap.put(key, 1);            // Step 2: Write (RACE CONDITION!)
        } else {
            counterMap.put(key, current + 1);  // Step 3: Write (LOST UPDATES!)
        }
    }

    // SAFE PATTERN: Atomic compute / merge operations
    public static void incrementSafe(String key) {
        // Atomic bucket-level operation using CAS/Lock-free bucket update!
        counterMap.compute(key, (k, current) -> (current == null) ? 1 : current + 1);
    }

    public static void main(String[] args) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(10);

        String testKey = "user_views";

        // Launch 1000 concurrent updates
        for (int i = 0; i < 1000; i++) {
            executor.submit(() -> incrementSafe(testKey));
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("Final atomic counter value for '" + testKey + "': " + counterMap.get(testKey));
        // Output: Exactly 1000!
    }
}
```

**Under the Hood / Why It Happens**:
1. **JVM Memory Layout**: Each Java thread has its own private JVM Stack containing stack frames with local variables. Objects allocated via `new` are placed on the heap shared by all threads. References (`Integer current`) on the stack point to heap addresses.
2. **ConcurrentHashMap Lock-Free Architecture**: Since Java 8, `ConcurrentHashMap` maintains an array of `Node<K,V>` bucket nodes (`table`).
   - For **Reads** (`get`): Executes completely lock-free using volatile reads (`Unsafe.getObjectVolatile`), ensuring zero thread blocking.
   - For **Writes** (`put`/`compute`): If the target bucket bin is empty, it uses **Compare-And-Swap (CAS)** (`Unsafe.compareAndSwapObject`) to insert the new node without acquiring a lock. If the bucket bin is non-empty, it synchronizes strictly on the **head node of that specific bucket array slot** (`synchronized (f)`). Multiple threads updating keys in *different* buckets execute concurrently in parallel without locking each other out!

**Key Takeaway / Safe Pattern**:
Never combine separate `get()` and `put()` calls on a `ConcurrentHashMap` for compound updates, as inter-thread race conditions will still occur. Always use atomic compound methods like `.compute()`, `.computeIfAbsent()`, or `.merge()` to guarantee thread-safe bucket updates.
