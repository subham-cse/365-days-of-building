# Day 110: Structure Padding, Alignment, and Memory Footprint Optimization
- **Language / Domain**: C
- **The Core Concept / "Did You Know?"**: In C, the memory size of a `struct` is often significantly larger than the sum of its individual fields. Compilers automatically insert invisible **padding bytes** between struct members to align fields with CPU hardware memory access boundaries.

Reordering struct fields from largest to smallest alignment requirement can dramatically reduce memory usage and improve cache line utilization.

- **The Code Snippet**:
```c
#include <stdio.h>
#include <stdint.h>

// Poorly aligned struct (Size: 24 bytes on 64-bit platforms)
struct UnpaddedStruct {
    char      c1; // 1 byte
    // 7 padding bytes inserted here!
    uint64_t  u2; // 8 bytes (must be aligned to 8-byte boundary)
    uint32_t  u1; // 4 bytes
    char      c2; // 1 byte
    // 3 padding bytes inserted at the end to align overall struct to 8 bytes!
};

// Optimally aligned struct (Size: 16 bytes)
struct OptimizedStruct {
    uint64_t  u2; // 8 bytes
    uint32_t  u1; // 4 bytes
    char      c1; // 1 byte
    char      c2; // 1 byte
    // 2 padding bytes at end
};

int main(void) {
    printf("UnpaddedStruct size:  %zu bytes\n", sizeof(struct UnpaddedStruct));  // 24
    printf("OptimizedStruct size: %zu bytes\n", sizeof(struct OptimizedStruct)); // 16
    return 0;
}
```

- **Under the Hood / Why It Happens**:
Modern CPUs access system memory in word chunks (e.g. 64-bit / 8-byte words). If a 64-bit integer (`uint64_t`) starts at an unaligned memory address (e.g. byte address `0x0001`), the CPU must execute two separate memory bus read cycles and stitch the bits together in registers, causing severe performance degradation.

To prevent this, C compilers enforce structural alignment rules: every primitive member of size $S$ must be placed at an offset that is a multiple of $S$. Furthermore, the overall struct size is padded to a multiple of the largest member's alignment requirement so arrays of structs remain aligned.

- **Key Takeaway / Safe Pattern**:
Order struct members in descending order of size (64-bit pointers/ints first, followed by 32-bit ints, 16-bit shorts, and 8-bit chars last) to minimize memory padding overhead.
