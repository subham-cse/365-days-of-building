# Day 205: Java ConcurrentHashMap `computeIfAbsent` Recursive Deadlocks

**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
Java's `ConcurrentHashMap` is engineered for high throughput, using fine-grained bucket-level locking (`synchronized` on individual hash bin nodes) rather than global table locks.

However, invoking `computeIfAbsent` recursively on the same `ConcurrentHashMap` instance inside the computation mapping function will cause an **irrecoverable thread deadlock** or throw an `IllegalStateException`. If key `$K_1$` maps to the same hash bucket bin as key `$K_2$`, thread $T_1$ will acquire a bin lock for `$K_1$` and then synchronously attempt to acquire the lock for `$K_2$` inside its lambda callback, deadlocking itself indefinitely.

**The Code Snippet**:
```java
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentHashMapDeadlock {

    private static final ConcurrentHashMap<String, String> map = new ConcurrentHashMap<>();

    public static void main(String[] args) {
        System.out.println("Starting ConcurrentHashMap computeIfAbsent demo...");

        // TRAP: Recursive computeIfAbsent call inside mapping function
        map.computeIfAbsent("KeyA", key -> {
            System.out.println("Computing value for KeyA...");

            // If "KeyB" hashes to the same bucket bin, thread DEADLOCKS here!
            // Even if different bin, in JDK 8/9 it triggers infinite loop or exception.
            return map.computeIfAbsent("KeyB", subKey -> "ValueB");
        });

        System.out.println("Computation complete!"); // Never reached! Thread deadlocked!
    }
}
```

**Under the Hood / Why It Happens**:
Inside JDK `ConcurrentHashMap.computeIfAbsent(K key, Function mappingFunction)`:

1. The map computes `h = spread(key.hashCode())` and locates the hash table bin index `i`.
2. It enters a `synchronized (node)` block locking the head node of bin `i`.
3. While holding this bucket node lock, it invokes `mappingFunction.apply(key)`.
4. Inside `mappingFunction`, the nested call `map.computeIfAbsent("KeyB", ...)` executes.
5. If `"KeyB"` evaluates to the same bucket index `i`, it attempts to acquire `synchronized (node)` on bin `i`. Because current thread already holds lock `i`, but `computeIfAbsent` internal node traversal state is incomplete, the method blocks or spins infinitely, deadlocking the execution thread.

Even if keys fall into different bins, nested modifications of `ConcurrentHashMap` during active computation violate internal invariants and risk infinite `ReservationNode` retries.

**Key Takeaway / Safe Pattern**:
Never mutate or execute recursive `computeIfAbsent` calls on the same `ConcurrentHashMap` instance inside mapping functions. Compute nested values prior to map insertion, or use traditional `get` checks paired with `putIfAbsent`.

```java
// Safe Pattern: Compute nested values outside computeIfAbsent callback
String valueB = map.computeIfAbsent("KeyB", k -> "ValueB");
String valueA = map.computeIfAbsent("KeyA", k -> "Prefix_" + valueB);
```
