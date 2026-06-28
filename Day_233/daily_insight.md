# Day 233: JVM ConcurrentHashMap TreeBin Conversion & Node Locking Granularity

**Language / Domain**: Java / JVM Concurrency & Data Structures

**The Core Concept / "Did You Know?"**:
Java's `java.util.concurrent.ConcurrentHashMap` is designed for high-concurrency read/write access. Unlike legacy `Hashtable` or `Collections.synchronizedMap` (which lock the entire map table for every operation), `ConcurrentHashMap` uses **lock stripping** and bucket-level synchronizations (`synchronized` on individual bucket head nodes) alongside Lock-Free Compare-And-Swap (CAS) reads.

Starting in Java 8, when a bucket experiences severe hash collisions and accumulates more than 8 entries, `ConcurrentHashMap` converts the bucket's linked list into a red-black balanced search tree structure wrapped in a **`TreeBin`** node.

However, mutating keys within a `TreeBin` bucket undergoes **Read-Write Locking escalation**. If a thread mutates a red-black `TreeBin` while concurrent reads occur, reader threads cannot perform lock-free traversals—they are forced to wait on a secondary lock, introducing unexpected thread latency.

**The Code Snippet**:
```java
package com.concurrency;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Objects;

public class ConcurrentHashMapCollisionDemo {

    // Bad Hash Key designed to force Hash Collisions into a single bucket
    static class CollidingKey implements Comparable<CollidingKey> {
        private final int id;

        public CollidingKey(int id) {
            this.id = id;
        }

        @Override
        public int hashCode() {
            // Constant hashcode forces ALL instances into the exact same map bucket!
            return 42;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            CollidingKey that = (CollidingKey) o;
            return id == that.id;
        }

        @Override
        public int compareTo(CollidingKey o) {
            return Integer.compare(this.id, o.id);
        }
    }

    public static void main(String[] args) {
        ConcurrentHashMap<CollidingKey, String> map = new ConcurrentHashMap<>();

        // Inserting elements to trigger bucket TreeBin conversion threshold (> 8 elements)
        System.out.println("Inserting 12 colliding key entries into ConcurrentHashMap...");
        for (int i = 0; i < 12; i++) {
            map.put(new CollidingKey(i), "Payload_" + i);
        }

        // Concurrent reads and writes on colliding bucket
        long start = System.nanoTime();
        String val = map.get(new CollidingKey(5));
        long duration = System.nanoTime() - start;

        System.out.println("Read Result: " + val + " (Lookup took " + duration + " ns)");
    }
}
```

**Under the Hood / Why It Happens**:
1. **TreeBin Conversion Thresholds**:
   - `TREEIFY_THRESHOLD = 8`: When a linked list bucket length exceeds 8, `ConcurrentHashMap` transforms nodes into a `TreeBin`.
   - `MIN_TREEIFY_CAPACITY = 64`: The map must also have a total array capacity of at least 64 bins. If capacity is smaller, it resizes the table instead of treeifying.

2. **Locking Mechanics in `TreeBin`**:
   Standard `ConcurrentHashMap` reads (`get()`) on linked list buckets are 100% lock-free because nodes are linked via `volatile` next pointers.
   However, a `TreeBin` structure must maintain red-black tree balancing operations (rotations).
   - `TreeBin` maintains a custom reader-writer lock bit state integer.
   - When a writer thread mutates or rebalances a `TreeBin`, it acquires the writer lock bit.
   - If reader threads (`get()`) arrive while a rebalance is occurring, they cannot navigate the red-black pointers safely.
   - Instead of blocking on a heavy OS mutex, reader threads fall back to iterating through a secondary `volatile` doubly-linked list (`first` / `next`) attached to the `TreeBin` container.

3. **Performance Impact**:
   While `TreeBin` prevents worst-case \(O(N)\) hash collision degradation by reducing lookup time to \(O(\log N)\), hash collisions still cause thread contention and break lock-free read optimizations.

**Key Takeaway / Safe Pattern**:
- Implement high-entropy `hashCode()` methods using prime multipliers (`Objects.hash(field1, field2)`) to ensure uniform distribution across map buckets.
- Implement `Comparable<K>` for custom map key classes. When `TreeBin` conversion occurs, `ConcurrentHashMap` uses `compareTo` to order tree nodes; without `Comparable`, it falls back to slow identity hash code comparisons.
