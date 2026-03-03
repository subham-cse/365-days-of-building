# Day 094: Strict Aliasing and Undefined Behavior in Pointer Casts
- **Language / Domain**: C
- **The Core Concept / "Did You Know?"**: In C, casting a pointer of one type to a pointer of an incompatible type and dereferencing it violates the *Strict Aliasing Rule* (C11 §6.5 p7). The compiler assumes that pointers of incompatible types never refer to the same memory location. 

When you violate this rule, modern optimizing compilers (like GCC or Clang with `-O2` or `-O3`) will reorder, optimize away, or cache register loads under the assumption that writes through one pointer type cannot affect reads through another. This leads to non-deterministic, highly confusing bugs where code works fine in unoptimized debug builds but fails catastrophically in release builds.

- **The Code Snippet**:
```c
#include <stdio.h>
#include <stdint.h>

void inspect_float(float *f, uint32_t *i) {
    *f = 1.0f;
    *i = 0x40400000; // Intended to overwrite memory as IEEE 754 float 3.0f

    // Under strict aliasing rules, compiler assumes *f was not modified by *i!
    printf("Float value: %f\n", *f);
}

int main(void) {
    uint32_t data = 0;
    // Dangerous pointer cast violating strict aliasing
    float *f_ptr = (float *)&data;
    uint32_t *i_ptr = (uint32_t *)&data;

    inspect_float(f_ptr, i_ptr);
    return 0;
}
```

- **Under the Hood / Why It Happens**:
Compilers construct Type-Based Alias Analysis (TBAA) graphs. Because `float` and `uint32_t` are incompatible types in C's aliasing rules, the optimizer concludes `*f` and `*i` in `inspect_float` point to disjoint memory locations. 

Consequently, the compiler keeps `*f` (1.0f) cached in a floating-point register (`xmm0` on x86_64) across the write to `*i`. The assembly generated under `-O2` omits reloading `*f` from memory for the `printf` call, resulting in `1.000000` being printed instead of `3.000000`, even though both pointers alias the exact same stack memory `data`.

- **Key Takeaway / Safe Pattern**:
To inspect or reinterpret raw bit patterns safely in C without violating strict aliasing, use `char*` / `unsigned char*` (which are explicitly allowed to alias any object) or use `memcpy` / `union`:

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

uint32_t float_to_bits(float f) {
    uint32_t bits;
    // Safe: memcpy is optimized away by compilers to register moves
    memcpy(&bits, &f, sizeof(bits));
    return bits;
}

int main(void) {
    float f = 3.0f;
    uint32_t bits = float_to_bits(f);
    printf("Bits: 0x%08X\n", bits);
    return 0;
}
```
