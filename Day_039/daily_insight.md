# Day 039: Go Slice Internals and Reallocation Traps

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, a slice is a lightweight 3-word header containing a pointer to an underlying array, a length (`len`), and a capacity (`cap`). Passing a slice to a function passes this header by value, meaning modifications to elements mutate the shared array.

However, if `append()` pushes the slice length beyond its capacity, Go allocates a completely new underlying array and updates the local slice header's pointer. The caller's slice header continues pointing to the original, un-expanded array, silently severing shared mutations.

**The Code Snippet**:
```go
package main

import "fmt"

func modifySliceWithoutRealloc(s []int) {
	// Mutates element inside existing capacity - visible to caller!
	s[0] = 99
}

func modifySliceWithAppend(s []int) {
	// append exceeds capacity, triggering new array allocation
	s = append(s, 999)
	s[0] = 777 // Mutates NEW array only, caller sees nothing!
}

func main() {
	// Slice with len=3, cap=3
	original := make([]int, 3, 3)
	original[0] = 10
	original[1] = 20
	original[2] = 30

	fmt.Println("Initial slice:", original) // [10 20 30]

	modifySliceWithoutRealloc(original)
	fmt.Println("After in-bounds modification:", original) // [99 20 30]

	modifySliceWithAppend(original)
	fmt.Println("After append exceeding capacity:", original) // Still [99 20 30]!
}
```

**Under the Hood / Why It Happens**:
Go slice headers are defined internally as:
```go
type slice struct {
    array unsafe.Pointer
    len   int
    cap   int
}
```
When `modifySliceWithAppend` is called, `s` receives a copy of the `slice` struct. When `append(s, 999)` executes, Go detects `len + 1 > cap`. It allocates a new memory region (doubling capacity), copies existing elements into it, appends `999`, and updates `s.array` to point to the new location.

Because `s` was passed by value, the caller's slice struct retains its original `array` pointer and `len` values, unaware that reallocation took place.

**Key Takeaway / Safe Pattern**:
Always return the modified slice from functions that invoke `append()`, or pass a pointer to the slice (`*[]T`) if external header updates are required. Pre-allocate slices using `make([]T, len, cap)` when total capacity is known beforehand to avoid redundant allocations.
