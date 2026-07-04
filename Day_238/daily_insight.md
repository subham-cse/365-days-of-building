# Day 238: C Struct Padding, Alignment Rules, & False Sharing in Multithreaded Systems

**Language / Domain**: C / Systems Memory Architecture & Cache Alignment

**The Core Concept / "Did You Know?"**:
In C, the memory size of a `struct` is rarely equal to the sum of its individual field sizes. To maximize CPU memory bus access efficiency, compilers insert invisible empty bytes—**Structure Padding**—so that each struct field aligns to a memory address divisible by its byte size (e.g., 4-byte `int` on 4-byte boundary, 8-byte `double` on 8-byte boundary).

Beyond struct padding, inefficient memory layout in multithreaded systems causes **False Sharing**. When two threads running on separate CPU cores concurrently modify independent variables that happen to reside on the same 64-byte L1 CPU Cache Line, the CPU hardware cache-coherency bus forces constant cache line invalidation and reload cycles, severely degrading throughput.

**The Code Snippet**:
```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

// UNPACKED / INEFFICIENT STRUCT LAYOUT
struct InefficientStruct {
    uint8_t  flag1;     // 1 byte
    // 7 bytes padding inserted by compiler here!
    uint64_t timestamp; // 8 bytes
    uint8_t  flag2;     // 1 byte
    // 3 bytes padding inserted by compiler here!
    uint32_t counter;   // 4 bytes
    // 4 bytes trailing padding inserted to match 8-byte struct alignment boundary!
};

// OPTIMIZED STRUCT LAYOUT (Sorted by descending member size)
struct OptimizedStruct {
    uint64_t timestamp; // 8 bytes
    uint32_t counter;   // 4 bytes
    uint8_t  flag1;     // 1 byte
    uint8_t  flag2;     // 1 byte
    // 2 bytes trailing padding inserted for 8-byte alignment
};

// MULTITHREADED CACHE ALIGNMENT (Preventing False Sharing)
typedef struct {
    // Force 64-byte alignment matching CPU Cache Line size!
    _Alignas(64) uint64_t thread1_counter;
    _Alignas(64) uint64_t thread2_counter;
} CacheAlignedCounters;

int main(void) {
    printf("InefficientStruct size: %zu bytes\n", sizeof(struct InefficientStruct)); // Outputs 24 bytes!
    printf("OptimizedStruct size:   %zu bytes\n", sizeof(struct OptimizedStruct));   // Outputs 16 bytes!

    printf("\nInefficient Member Offsets:\n");
    printf("  flag1:     %zu\n", offsetof(struct InefficientStruct, flag1));
    printf("  timestamp: %zu (Padding gap of 7 bytes before timestamp)\n", offsetof(struct InefficientStruct, timestamp));
    printf("  flag2:     %zu\n", offsetof(struct InefficientStruct, flag2));
    printf("  counter:   %zu (Padding gap of 3 bytes before counter)\n", offsetof(struct InefficientStruct, counter));

    printf("\nCacheAlignedCounters Size: %zu bytes (Prevents False Sharing across L1 Cache Lines!)\n", 
            sizeof(CacheAlignedCounters));

    return 0;
}
```

**Under the Hood / Why It Happens**:
1. **Alignment Rules**:
   Modern CPUs fetch data from memory in 32-bit (4-byte) or 64-bit (8-byte) words. Reading an unaligned `uint64_t` spanning across a word boundary requires the hardware to execute two separate memory read cycles and stitch the bytes together via bitwise shifts. To prevent this penalty, compilers pad addresses automatically.

2. **False Sharing Cache Invalidation**:
   - Modern CPUs cache memory in 64-byte **Cache Lines**.
   - If `Thread A` on Core 0 mutates `counters.thread1_counter` (bytes 0–7) and `Thread B` on Core 1 mutates `counters.thread2_counter` (bytes 8–15), both fields reside inside the *same 64-byte L1 cache line*.
   - When Core 0 writes to its variable, the MESI cache coherency protocol marks Core 1's cache line as **INVALID**.
   - Core 1 is forced to stall, flush its pipeline, and re-fetch the entire 64-byte line from L2/L3 cache, despite the threads operating on completely separate variables!

**Key Takeaway / Safe Pattern**:
- **Sort struct fields by descending size**: Group 8-byte types first, followed by 4-byte, 2-byte, and 1-byte types to minimize compiler padding gaps naturally.
- **Prevent False Sharing in multithreaded state**: Use C11 `_Alignas(64)` or GCC `__attribute__((aligned(64)))` to isolate thread-local atomic counters onto distinct CPU cache lines.
