# Day 210: C Integer Promotion Rules and Signed/Unsigned Comparison Traps

**Language / Domain**: C

**The Core Concept / "Did You Know?"**:
In C, arithmetic operations are never performed directly on types smaller than `int` (such as `char`, `short`, or bit-fields). Before any operation occurs, C automatically applies **Integer Promotion**, converting smaller integer types to `int` (or `unsigned int` if `int` cannot represent all values of the original type).

Even more dangerous are expressions comparing **signed** integers with **unsigned** integers. According to C's **Usual Arithmetic Conversions**, if an expression compares a signed integer with an unsigned integer of equal or greater rank, the signed value is implicitly converted to unsigned. If the signed value is negative (e.g., `-1`), it wraps around to a massive positive number (e.g. `4,294,967,295` on 32-bit `unsigned int`), causing logical condition inversions, infinite loops, or buffer overflow vulnerabilities!

**The Code Snippet**:
```c
#include <stdio.h>
#include <stddef.h>

void validate_buffer(int offset, size_t length) {
    // TRAP: 'offset' is signed int (-5), 'length' is unsigned size_t (100)
    // C implicitly promotes 'offset' to unsigned size_t!
    // -5 becomes (size_t)SIZE_MAX - 4 (e.g. 18446744073709551611 on 64-bit)!
    
    if (offset < length) {
        printf("TRAP: Negative offset %d considered LESS THAN length %zu!\n", offset, length);
    } else {
        printf("BUG EXPOSED: Offset %d considered GREATER THAN length %zu!\n", offset, length);
    }

    // Dangerous Array Indexing Trap
    if (offset > 0 && (size_t)offset < length) {
        printf("Safe indexing check passed.\n");
    } else {
        printf("Access rejected safely.\n");
    }
}

int main(void) {
    int negative_index = -5;
    size_t buffer_len = 100;

    validate_buffer(negative_index, buffer_len);
    return 0;
}
```

**Under the Hood / Why It Happens**:
In C standard (ISO/IEC 9899:2011, Section 6.3.1.8 "Usual Arithmetic Conversions"):

1. If both operands have the same type, no further conversion is needed.
2. Otherwise, if the operand that has unsigned integer type has rank greater than or equal to the rank of the type of the other operand, the operand with signed integer type is converted to the type of the operand with unsigned integer type.

When evaluating `-5 < (size_t)100`:
1. `-5` (type `int`) is converted to `size_t` (64-bit unsigned integer).
2. Two's complement representation of `-5` is `0xFFFFFFFFFFFFFFFB`.
3. As an unsigned value, `0xFFFFFFFFFFFFFFFB` equals `18,446,744,073,709,551,611`.
4. Comparing `18446744073709551611 < 100` evaluates to **FALSE** (`0`), inverting the intended logical check!

**Key Takeaway / Safe Pattern**:
Never mix signed and unsigned integers in comparison expressions or arithmetic calculations without explicit type checking. Always validate that signed values are non-negative before casting to `size_t` or unsigned types.

```c
// Safe Pattern: Explicit non-negative check prior to size_t comparison
void validate_buffer_safe(int offset, size_t length) {
    if (offset < 0) {
        printf("Error: Offset cannot be negative!\n");
        return;
    }
    
    // Now offset is guaranteed >= 0; safe to compare with unsigned size_t
    if ((size_t)offset < length) {
        printf("Valid offset index.\n");
    }
}
```
