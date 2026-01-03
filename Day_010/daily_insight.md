# Day 010: Strict Aliasing Violations and Integer Promotion Traps
**Language / Domain**: C

**The Core Concept / "Did You Know?"**:
In standard C (C99/C11/C17), the **Strict Aliasing Rule** specifies that two pointers of incompatible types cannot point to the same memory location. The compiler assumes that pointers of different types (e.g., `int*` and `float*`) never alias each other, allowing it to reorder or re-read cache variables aggressively. Violating this rule by typecasting memory pointers produces undefined behavior where compiler optimizations silently eliminate writes or read stale values.

Additionally, C performs automatic **Integer Promotion**: operands smaller than `int` (such as `char` or `short`) are promoted to `signed int` before executing arithmetic, causing subtle integer sign-extension and buffer calculation bugs.

**The Code Snippet**:
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Undefined Behavior: Strict Aliasing Violation
uint32_t swap_bytes_bad(uint32_t val) {
    // Typecasting a uint32_t* to uint16_t* breaks strict aliasing!
    uint16_t *p = (uint16_t *)&val;
    uint16_t temp = p[0];
    p[0] = p[1];
    p[1] = temp;
    return val; // Optimizing compiler may optimize out changes to `val`!
}

// Undefined Behavior / Integer Promotion Trap
void integer_promotion_trap() {
    uint8_t a = 0xFE; // 254
    uint8_t b = 0x02; // 2

    // `a` and `b` promoted to `int` before addition!
    // Result of (a + b) is signed int 256.
    // Right shifting signed int by bitwise complement creates sign issues!
    int res = (a + b) >> 1; 
    printf("Result: %d\n", res);

    uint8_t x = 0xFF;
    // ~x promotes `x` to `int` 255 (0x000000FF), then flips bits to 0xFFFFFF00 (-256 in 32-bit signed)!
    if (~x == 0x00) {
        printf("This will never print!\n");
    } else {
        printf("~x evaluated as signed int: 0x%X\n", (unsigned int)~x);
    }
}

int main() {
    uint32_t orig = 0x12345678;
    printf("Swapped (bad): 0x%X\n", swap_bytes_bad(orig));
    integer_promotion_trap();
    return 0;
}
```

**Under the Hood / Why It Happens**:
Under C strict aliasing rules (C11 §6.5/7), an object's stored value may only be accessed through an lvalue expression of a compatible type, a signed/unsigned variant thereof, or `char*` / `unsigned char*`. 

When compiling with high optimizations (`-O2` or `-O3`), GCC and Clang use strict aliasing (`-fstrict-aliasing`) to assume that writes through `p[0]` (`uint16_t*`) cannot alter the value of `val` (`uint32_t`). Consequently, the compiler loads `val` into a CPU register before the writes and returns that cached register value directly, ignoring the memory writes altogether.

For integer promotions (C11 §6.3.1.1), rank conversions mandate that any integer type with a rank smaller than `int` is silently converted to `int` if `int` can represent all values of the original type. Bitwise operations like `~x` on `uint8_t` first promote `x` to a 32-bit signed integer, producing negative values when bit-flipped.

**Key Takeaway / Safe Pattern**:
To inspect byte representations legally without violating strict aliasing, use `memcpy` or cast through `char*` / `unsigned char*` (which are explicitly permitted to alias any pointer type). For integer bitwise operations on smaller types, explicitly mask or cast the result.

```c
#include <string.h>
#include <stdint.h>

// SAFE: Using memcpy for pointer reinterpretation
uint32_t swap_bytes_safe(uint32_t val) {
    uint16_t p[2];
    memcpy(p, &val, sizeof(val));
    
    uint16_t temp = p[0];
    p[0] = p[1];
    p[1] = temp;
    
    uint32_t result;
    memcpy(&result, p, sizeof(result));
    return result; // Compiler optimizes memcpy away into single CPU instruction (e.g. `ror`)!
}

// SAFE: Bitwise mask for integer promotion
uint8_t x = 0xFF;
if ((uint8_t)(~x) == 0x00) {
    // Explicit truncation/mask works as expected
}
```
