# Day 054: C Buffer Overflows and Unbounded String Functions

**Language / Domain**: C

**The Core Concept / "Did You Know?"**:
Legacy C standard library functions like `strcpy`, `strcat`, `sprintf`, and `gets` do not perform array bounds checking. They rely strictly on finding a null-terminator byte (`'\0'`) to stop copying memory into target buffers.

If source string inputs exceed the allocated stack buffer capacity, the written data overflows into neighboring stack memory frames, corrupting function return addresses and giving rise to severe stack buffer overflow security exploits (CVE vulnerabilities).

**The Code Snippet**:
```c
#include <stdio.h>
#include <string.h>

void vulnerable_copy(const char* input) {
    char stack_buffer[16];
    
    // DANGEROUS: Unbounded memory copy!
    // If input > 15 chars + null terminator, adjacent stack memory is overwritten
    strcpy(stack_buffer, input); 
    printf("Copied buffer safely: %s\n", stack_buffer);
}

void secure_copy(const char* input) {
    char stack_buffer[16];
    
    // SAFE: Bound copy to fixed destination buffer size
    // Ensures null-termination and prevents buffer overflows
    snprintf(stack_buffer, sizeof(stack_buffer), "%s", input);
    printf("Securely copied buffer: %s\n", stack_buffer);
}

int main(void) {
    const char* safe_input = "Hello C!";
    const char* malicious_input = "THIS_STRING_IS_WAY_TOO_LONG_FOR_SIXTEEN_BYTES";

    printf("--- Running Secure Copy --- \n");
    secure_copy(safe_input);
    secure_copy(malicious_input); // Truncates safely without overflow

    printf("\n--- Running Vulnerable Copy (Short Input) --- \n");
    vulnerable_copy(safe_input);

    // Uncommenting line below will trigger stack smashing detection or segfault
    // vulnerable_copy(malicious_input); 

    return 0;
}
```

**Under the Hood / Why It Happens**:
In C execution stack frames, local variables are laid out sequentially next to call frame metadata:
```
[ Local Buffer (16 bytes) ] [ Frame Pointer (EBP) ] [ Return Address (EIP) ]
```
When `strcpy` writes beyond the 16 bytes allocated for `stack_buffer`, extra bytes overwrite the stored EBP and Instruction Pointer (EIP/RIP) return addresses. When the function executes its `ret` assembly instruction, the CPU pops the overwritten pointer value into the instruction register, jumping to arbitrary code locations (stack smashing).

**Key Takeaway / Safe Pattern**:
Never use unbounded string functions (`strcpy`, `strcat`, `sprintf`, `gets`). Always use bounded variants like `snprintf`, `strncpy` (ensuring manual null-termination), or C11 `strncpy_s`. Enable compiler security features like `-fstack-protector-strong` and compile with `-Wformat-security`.
