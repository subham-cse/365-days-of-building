# Day 066: Strict Aliasing Violations and Undefined Behavior in C

**Language / Domain**: C

**The Core Concept / "Did You Know?"**:
In C, accessing an object of one type through a pointer of an incompatible type (with limited exceptions like `char*`) violates the **Strict Aliasing Rule** (C11 standard §6.5/7). 

Modern optimizing compilers (such as GCC and Clang) assume under `-O2` and `-O3` optimization levels that pointers of incompatible types never refer to the exact same memory location. When strict aliasing is violated, compilers may reorder, cache, or eliminate load and store instructions, leading to severe runtime bugs where values written through one pointer are completely ignored when read from another.

**The Code Snippet**:
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// TRAP: Violating Strict Aliasing via Type Punning with Pointers
uint32_t unsafe_swap_bytes(uint32_t val) {
    // Undefined Behavior: Casting uint32_t* to uint16_t*
    uint16_t *p = (uint16_t *)&val;
    uint16_t tmp = p[0];
    p[0] = p[1];
    p[1] = tmp;
    return val; // Compiler may optimize this to return unmodified 'val'!
}

// SAFE PATTERN 1: Safe Type Punning via Standard memcpy
uint32_t safe_swap_memcpy(uint32_t val) {
    uint16_t parts[2];
    // memcpy operates on char/unsigned char level, which is standard-compliant
    memcpy(parts, &val, sizeof(val));
    
    uint16_t tmp = parts[0];
    parts[0] = parts[1];
    parts[1] = tmp;
    
    uint32_t result;
    memcpy(&result, parts, sizeof(result));
    return result; // Compilers optimize memcpy away into a single native swap instruction!
}

// SAFE PATTERN 2: Safe Type Punning via C Union
union TypePunner {
    uint32_t full;
    uint16_t half[2];
};

uint32_t safe_swap_union(uint32_t val) {
    union TypePunner pun;
    pun.full = val;
    uint16_t tmp = pun.half[0];
    pun.half[0] = pun.half[1];
    pun.half[1] = tmp;
    return pun.full; // Well-defined in C99/C11 (explicit standard exception for unions)
}

int main(void) {
    uint32_t x = 0x123489AB;
    printf("Original: 0x%X\n", x);
    printf("Unsafe Swap (UB): 0x%X\n", unsafe_swap_bytes(x));
    printf("Safe Swap (memcpy): 0x%X\n", safe_swap_memcpy(x));
    printf("Safe Swap (union):  0x%X\n", safe_swap_union(x));
    return 0;
}
```

**Under the Hood / Why It Happens**:
During type-based alias analysis (TBAA), the compiler assigns alias sets to intermediate code instructions. If a pointer of type `int*` and a pointer of type `float*` point to the same address, the optimizer treats their operations as independent because their types belong to non-overlapping alias sets. 

Consequently, a write through `(float*)p` followed by a read through `(int*)p` will allow the compiler to reuse the cached register value of `(int*)p` from before the write, completely missing the store operation. Modern compilers will generate optimized assembly assuming no alias collision occurred.

**Key Takeaway / Safe Pattern**:
Never use pointer casting (e.g., `*(float*)&uint_var`) for type punning or bit reinterpretation. Use `memcpy()` or C `union` types. `memcpy()` is explicitly exempt from aliasing violations and is recognized by modern compilers, producing optimal zero-cost assembly instructions (such as `mov`, `bswap`, or SIMD loads).
