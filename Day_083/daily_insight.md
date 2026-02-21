# Day 083: Goroutine Leaks & Slice Reallocation Surprises in Go

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
Go's concurrency and data structure abstractions make rapid development easy, but harbor two high-concurrency production traps:

1. **Goroutine Leaks**: A Goroutine blocked indefinitely on an unbuffered channel send/receive operation will never be garbage collected. Its stack memory, open file descriptors, and captured references remain leaked in heap RAM for the lifetime of the program.
2. **Slice Reallocation Surprises**: A Go slice is a header pointing to an underlying array. When passing a slice to a function or appending items, if `append()` exceeds the slice's capacity (`cap`), Go allocates a brand-new underlying array, detaching modifications from the original slice reference.

**The Code Snippet**:
```go
package main

import (
	"fmt"
	"time"
)

// TRAP 1: Goroutine Leak via Unbuffered Channel
func queryFastestServerUnsafe() string {
	// Unbuffered channel!
	ch := make(chan string) 

	// Launch two concurrent worker Goroutines
	go func() { ch <- "Server A" }()
	go func() { ch <- "Server B" }()

	// Reader reads the FIRST arriving response, then returns immediately!
	// The second Goroutine blocks FOREVER attempting to write to 'ch'! (LEAK!)
	return <-ch 
}

// SAFE PATTERN 1: Buffered Channel prevents sender blockage
func queryFastestServerSafe() string {
	// Buffer size 2 ensures both senders can complete without blocking
	ch := make(chan string, 2)

	go func() { ch <- "Server A" }()
	go func() { ch <- "Server B" }()

	return <-ch // Second write succeeds into buffer and GC reclaims channel!
}

// TRAP 2: Slice Reallocation Detachment
func modifySlice(s []int) {
	// If len == cap, append allocates a NEW backing array!
	s = append(s, 99) 
	s[0] = 777
}

func main() {
	// 1. Goroutine Leak Test
	result := queryFastestServerUnsafe()
	fmt.Println("Fastest result:", result)
	time.Sleep(50 * time.Millisecond) // Leaked Goroutine is stuck in background!

	// 2. Slice Reallocation Test
	original := make([]int, 2, 2) // len: 2, cap: 2
	original[0] = 10
	original[1] = 20

	modifySlice(original)
	fmt.Println("Original slice after append:", original) 
	// Output: [10, 20] -> NOT modified to 777 because backing array reallocated!
}
```

**Under the Hood / Why It Happens**:
1. **Goroutine Leaks**: The Go scheduler (`runtime/proc.go`) tracks Goroutines using the `g` struct. When a Goroutine performs an unbuffered channel send (`ch <- val`), it executes `chansend()`. If no receiver is waiting on `ch`, the scheduler changes the Goroutine state from `_Grunning` to `_Gwaiting` and attaches it to the channel's `waitq` list. Because the caller function returned, no entity ever reads `ch` again, leaving `g` in `_Gwaiting` permanently. Garbage collection ignores active Goroutine stacks.
2. **Slice Headers**: A slice in Go (`reflect.SliceHeader`) is a 3-word struct: `Data unsafe.Pointer`, `Len int`, and `Cap int`. Passing a slice to a function passes this 3-word header **by value**. Inside `modifySlice`, when `append()` exceeds `Cap`, Go invokes `growslice()`, allocating a new memory block and updating the local `Data` pointer. The caller's `SliceHeader` still points to the old memory array!

**Key Takeaway / Safe Pattern**:
Always use buffered channels (`make(chan T, N)`) when launching worker Goroutines whose responses may be ignored. When passing slices intended for modification, return the updated slice (`s = modifySlice(s)`) or pass a pointer to the slice (`*[]int`).
