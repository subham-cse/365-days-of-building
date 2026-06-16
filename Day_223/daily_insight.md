# Day 223: Go Slice Header Mutability & Under-the-Hood Reallocation Surprises

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, a slice is not a full-fledged dynamic object or pointer array; it is a lightweight 3-word header value struct containing three elements: a pointer to an underlying array (`unsafe.Pointer`), a length (`int`), and a capacity (`int`).

Because slice variables are passed **by value** in functions, mutating a slice element (`s[0] = 42`) modifies the shared underlying array for all slice references. However, calling `append()` can cause surprising behavior: if the slice has remaining capacity, `append()` mutates the underlying array in-place. If capacity is exhausted, Go secretly allocates a *new* backing array, copies existing elements, and returns a new slice header. Any other variables still referencing the old slice header will no longer see updates!

**The Code Snippet**:
```go
package main

import "fmt"

func appendTrap(s []int) {
	// Modifying existing index mutates the caller's memory buffer!
	s[0] = 999

	// Append within existing capacity mutates caller's underlying array at index len!
	s = append(s, 50)
	s[1] = 888

	fmt.Println("Inside function s:", s, "len:", len(s), "cap:", cap(s))
}

func main() {
	// Case 1: Slice created with capacity buffer
	buf := make([]int, 2, 4)
	buf[0] = 10
	buf[1] = 20

	fmt.Println("--- Before appendTrap ---")
	fmt.Println("buf:", buf, "len:", len(buf), "cap:", cap(buf))

	appendTrap(buf)

	fmt.Println("\n--- After appendTrap ---")
	// Notice buf[0] became 999, buf[1] became 888! But len(buf) is STILL 2!
	fmt.Println("buf:", buf, "len:", len(buf), "cap:", cap(buf))
	
	// Inspecting hidden 3rd element in backing array via reslicing:
	resliced := buf[:3]
	fmt.Println("resliced buf[:3]:", resliced) // Contains 50 appended inside function!

	// Case 2: Full Capacity Slice Reallocation
	fullSlice := []int{1, 2} // len: 2, cap: 2
	fullSlicePtr := &fullSlice[0]
	
	fullSlice = append(fullSlice, 3) // Triggers backing array reallocation!
	newSlicePtr := &fullSlice[0]

	fmt.Printf("\nBacking array address changed: %p -> %p\n", fullSlicePtr, newSlicePtr)
}
```

**Under the Hood / Why It Happens**:
The Go runtime represents slices using the `reflect.SliceHeader` struct:
```go
type SliceHeader struct {
    Data uintptr
    Len  int
    Cap  int
}
```

1. When `buf` (len: 2, cap: 4) is passed into `appendTrap(s []int)`:
   - Function parameter `s` receives a **copy** of the `SliceHeader` struct (`Data: 0x...100`, `Len: 2`, `Cap: 4`).
   - `s[0] = 999` writes directly through `s.Data` pointer, mutating index 0 of `buf`'s array.
   - `s = append(s, 50)` sees `s.Len < s.Cap` (2 < 4). It writes `50` to `s.Data[2]` and increments `s.Len` to 3 inside `appendTrap`'s local header copy.
   - `buf` in `main()` retains its original header (`Len: 2`), so `buf` only displays elements 0 and 1, even though its backing array element at index 2 was overwritten with `50`.

2. When `append()` is called on a slice where `Len == Cap`:
   - Go allocates a new array (usually double capacity for small slices), copies elements over, and returns a new `SliceHeader` pointing to the new memory block.
   - Any writes to the returned slice will no longer affect the original slice.

**Key Takeaway / Safe Pattern**:
- **Always capture `append` return values**: Treat slices as value headers and assign output back: `s = append(s, elem)`.
- **Pass slice pointers when functions modify length/capacity**: If a function must mutate slice length or reallocate, pass `*[]int`.
- **Use full slice expressions for sub-slicing isolation**: Use 3-index slicing `slice[low:high:max]` to cap capacity (e.g., `sub := buf[0:2:2]`). This forces any subsequent `append(sub, ...)` to allocate a fresh backing array instead of corrupting shared buffer slices!
