# Day 211: Go Slice Reslicing and Capacity Memory Leaks

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, a slice is not a full array itself, but a lightweight 3-word header containing a pointer to an underlying array, a length (`len`), and a capacity (`cap`).

When you reslice a slice (e.g. `smallSlice := largeSlice[0:2]`), Go creates a new slice header pointing to the **exact same underlying backing array**. Even though `smallSlice` has a length of only 2, its capacity preserves the reference to the entire original backing array. If `largeSlice` contained millions of elements or large data structures, keeping `smallSlice` in memory will prevent the entire underlying multi-megabyte backing array from being garbage collected, causing silent memory leaks!

**The Code Snippet**:
```go
package main

import (
	"fmt"
	"runtime"
)

func getHeaderData() []byte {
	// Allocate a massive 10 MB payload array
	largePayload := make([]byte, 10*1024*1024)
	for i := range largePayload {
		largePayload[i] = 'A'
	}

	// Reslice first 10 bytes
	// TRAP: Retains pointer reference to entire 10 MB array in capacity!
	return largePayload[:10]
}

func main() {
	var m runtime.MemStats

	runtime.GC()
	runtime.ReadMemStats(&m)
	fmt.Printf("Allocated memory before: %d KB\n", m.Alloc/1024)

	// Obtain 10 byte header
	header := getHeaderData()

	runtime.GC()
	runtime.ReadMemStats(&m)
	fmt.Printf("Allocated memory after GC: %d KB\n", m.Alloc/1024)
	// Output: ~10,000 KB still allocated in heap memory because header retains cap!

	fmt.Printf("Header len: %d, cap: %d\n", len(header), cap(header))
	// Output: Header len: 10, cap: 10485760 (10 MB backing array leaked!)
}
```

**Under the Hood / Why It Happens**:
Go slice headers are defined in `reflect.SliceHeader`:

```go
type SliceHeader struct {
	Data uintptr
	Len  int
	Cap  int
}
```

When `largePayload[:10]` is evaluated:
1. `Data` pointer points to index `0` of the 10 MB array allocation on the heap.
2. `Len` is set to `10`.
3. `Cap` remains `10,485,760` (the total length of the backing buffer from offset 0).

Because Go's garbage collector traces object reachability by scanning pointer references, as long as `header` is reachable in code, the GC sees an active pointer (`Data`) referencing the heap block. The GC cannot free partial array allocations; it must keep the entire 10 MB contiguous memory block alive.

**Key Takeaway / Safe Pattern**:
When extracting a small sub-slice from a large slice or temporary buffer, use `copy()` to duplicate the needed elements into a fresh, tightly-sized slice, or use full slice expressions (`s[low:high:max]`) to clip capacity.

```go
// Safe Pattern: Copy data to a fresh slice to free backing array memory
func getHeaderDataSafe() []byte {
	largePayload := make([]byte, 10*1024*1024)
	
	// Allocate fresh 10 byte slice with cap == 10
	detachedHeader := make([]byte, 10)
	copy(detachedHeader, largePayload[:10])

	// largePayload goes out of scope and is collected cleanly by GC!
	return detachedHeader
}
```
