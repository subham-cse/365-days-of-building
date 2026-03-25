# Day 121: JVM Memory Layout and Concurrent HashMap Under the Hood
- **Language / Domain**: Java
- **The Core Concept / "Did You Know?"**: Java's `ConcurrentHashMap` allows high-throughput concurrent reads and writes without locking the entire map. In Java 7, this was achieved via Segment locking. In Java 8+, `ConcurrentHashMap` abandoned segments entirely in favor of fine-grained **Compare-And-Swap (CAS)** instructions and per-hash-bucket `synchronized` node locks!

Furthermore, when a bucket accumulates more than 8 entries, `ConcurrentHashMap` automatically transforms the linked list bucket into a balanced **Red-Black Tree** ($O(\log N)$ lookup), mitigating HashDoS algorithmic complexity attacks.

- **The Code Snippet**:
```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ConcurrentHashMapDemo {
    private static final ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

    public static void main(String[] args) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(4);

        for (int i = 0; i < 10; i++) {
            final int id = i;
            executor.submit(() -> {
                // Atomic computeIfAbsent: Guarantees single thread computation per key!
                map.computeIfAbsent("shared_key", k -> {
                    System.out.println("Thread " + id + " initializing key");
                    return 42;
                });
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("Final Map Result: " + map.get("shared_key"));
    }
}
```

- **Under the Hood / Why It Happens**:
Java 8+ `ConcurrentHashMap` uses an internal node array `Node<K,V>[] table`. 

1. **Insertion via CAS**: When inserting into an empty bin (`table[i] == null`), CHM uses lock-free hardware CAS operations (`Unsafe.compareAndSwapObject` / `VarHandle.compareAndSet`) to insert the new Node without taking any lock.
2. **Synchronized Bucket**: If the bin is already populated, CHM locks *only* the first node of that specific bucket using `synchronized(firstNode)`. Threads writing to completely separate buckets run in parallel with zero lock contention!

- **Key Takeaway / Safe Pattern**:
Use atomic methods like `computeIfAbsent`, `merge`, or `putIfAbsent` when modifying `ConcurrentHashMap` elements. Avoid manual check-then-act code sequences (`if (!map.containsKey(k)) map.put(k, v)`), which reintroduce race conditions.
