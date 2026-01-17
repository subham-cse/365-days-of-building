# Day 038: C Structure Padding and Memory Alignment Rules

**Language / Domain**: C

**The Core Concept / "Did You Know?"**:
In C, the physical byte size of a `struct` is often larger than the sum of the byte sizes of its individual members. Compilers automatically insert unused padding bytes between struct members to align data types with native hardware memory word boundaries.

Reordering struct fields based on alignment size can significantly reduce total structure size, lowering cache miss rates and reducing overall application memory footprint.

**The Code Snippet**:
```c
#include <stdio.h>
#include <stddef.h>

// Poorly ordered struct: Unaligned layout causes excess compiler padding
struct UnalignedStruct {
    char  a;    // 1 byte
    // 3 bytes padding inserted here
    int   b;    // 4 bytes
    char  c;    // 1 byte
    // 3 bytes padding inserted here at end
};              // Total size: 12 bytes!

// Efficiently ordered struct: Members ordered by descending size
struct AlignedStruct {
    int   b;    // 4 bytes
    char  a;    // 1 byte
    char  c;    // 1 byte
    // 2 bytes padding inserted at end
};              // Total size: 8 bytes!

int main(void) {
    printf("UnalignedStruct Size: %zu bytes\n", sizeof(struct UnalignedStruct));
    printf("  Offset of 'a': %zu\n", offsetof(struct UnalignedStruct, a));
    printf("  Offset of 'b': %zu\n", offsetof(struct UnalignedStruct, b));
    printf("  Offset of 'c': %zu\n", offsetof(struct UnalignedStruct, c));

    printf("\nAlignedStruct Size: %zu bytes\n", sizeof(struct AlignedStruct));
    printf("  Offset of 'b': %zu\n", offsetof(struct AlignedStruct, b));
    printf("  Offset of 'a': %zu\n", offsetof(struct AlignedStruct, a));
    printf("  Offset of 'c': %zu\n", offsetof(struct AlignedStruct, c));

    return 0;
}
```

**Under the Hood / Why It Happens**:
CPU architectures read and write memory most efficiently when data types reside at memory addresses that are multiples of their size (e.g., a 4-byte `int` should reside at an address divisible by 4, and an 8-byte `double` at an address divisible by 8). Unaligned memory accesses on some CPU architectures cause hardware exceptions, while on x86/x64 systems, they incur CPU latency penalties across cache lines.

To guarantee alignment without developer intervention, the C compiler pads each member to align with its alignment requirement `alignof(T)`. Furthermore, the total struct size is padded to a multiple of its largest member's alignment requirement so array elements align correctly.

**Key Takeaway / Safe Pattern**:
Order struct fields from largest alignment requirement to smallest (e.g., pointers/64-bit ints first, 32-bit ints second, shorts third, chars last). When absolute binary representation is required (such as networking headers or hardware register maps), use explicit compiler directives like `#pragma pack(push, 1)` or `__attribute__((packed))`.
