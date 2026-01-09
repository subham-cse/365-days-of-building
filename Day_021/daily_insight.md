# Day 021: Streams vs Loops Overhead and ConcurrentHashMap Mutability Traps
**Language / Domain**: Java

**The Core Concept / "Did You Know?"**:
Java 8 Streams provide elegant functional abstractions, but using complex Stream pipelines (`.stream().filter().map().collect()`) inside performance-critical, hot execution paths can be up to **3x to 5x slower** than standard primitive `for` loops due to lambda object allocations, pipeline iterator chaining, and boxing overhead.

Additionally, while Java's `ConcurrentHashMap` guarantees thread-safe internal structure reads and writes, performing compound operations (such as `if (!map.containsKey(k)) map.put(k, v)`) without atomic API methods like `.putIfAbsent()` or `.computeIfAbsent()` introduces severe multi-threading race conditions.

**The Code Snippet**:
```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

public class JavaPerformanceTrap {

    // Benchmark comparison: Stream vs primitive loop
    public static long sumLoop(int[] data) {
        long sum = 0;
        for (int i = 0; i < data.length; i++) {
            sum += data[i];
        }
        return sum;
    }

    public static long sumStream(int[] data) {
        return java.util.Arrays.stream(data).asLongStream().sum();
    }

    // ConcurrentHashMap Compound Check Trap
    private static final ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

    public static void unsafeIncrement(String key) {
        // RACE CONDITION: containsKey + put is NOT atomic!
        if (!map.containsKey(key)) {
            map.put(key, 1);
        } else {
            map.put(key, map.get(key) + 1);
        }
    }

    public static void safeIncrement(String key) {
        // ATOMIC: Single atomic thread-safe update!
        map.compute(key, (k, v) -> (v == null) ? 1 : v + 1);
    }

    public static void main(String[] args) throws InterruptedException {
        ExecutorService service = Executors.newFixedThreadPool(10);
        for (int i = 0; i < 1000; i++) {
            service.submit(() -> unsafeIncrement("counter"));
        }
        service.shutdown();
        service.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("Unsafe counter value (expected 1000): " + map.get("counter"));
        // Frequently outputs < 1000 due to lost updates!
    }
}
```

**Under the Hood / Why It Happens**:
In Java Streams, pipeline construction allocates pipeline stage objects (`Head`, `StatelessOp`, `Sink`), lambda captured environment references, and iterator state machines on the heap. Modern JIT compilers (HotSpot C2) struggle to inline multi-stage stream pipelines across deep call graphs compared to contiguous memory access in primitive array loops.

For `ConcurrentHashMap`, segment or bin locks protect individual structural mutations during single method calls (`.put()`, `.get()`). However, executing `containsKey()` followed by `put()` releases the bin lock between the two calls. Another thread can intervene during this gap, leading to lost updates or corrupted counter states.

**Key Takeaway / Safe Pattern**:
For high-frequency or zero-allocation algorithms, prefer primitive `for` loops over streams. For concurrent operations on shared maps, always use atomic methods like `.computeIfAbsent()`, `.compute()`, or `.merge()`.

```java
// SAFE: Atomic ConcurrentHashMap operations
ConcurrentHashMap<String, Integer> safeMap = new ConcurrentHashMap<>();

// Atomic increment without lost updates:
safeMap.merge("counter", 1, Integer::sum);

// Atomic lazy initialization without race condition:
safeMap.computeIfAbsent("configKey", k -> loadExpensiveConfig(k));
```
