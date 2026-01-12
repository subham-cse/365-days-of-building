# Day 027: Slice Internals, Reallocation Surprises, and `sync.Mutex` Pitfalls
**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, passing a slice into a function passes a copy of the **slice header** (pointer, length, capacity). If the function appends elements to the slice using `append()` and triggers a capacity reallocation, Go allocates a new backing array for the slice. Any subsequent modifications made inside the function operate on the new array, leaving the caller's slice untouched!

Furthermore, passing a struct containing a `sync.Mutex` by value copies the mutex's internal state. Locking a copied mutex locks a completely separate lock instance, failing to protect shared critical sections against data races.

**The Code Snippet**:
```go
package main

import (
	"fmt"
	"sync"
)

// Trap 1: Slice Reallocation inside Function
func appendValue(s []int) {
	// Triggers capacity growth and new backing array allocation!
	s = append(s, 42)
	s[0] = 999 // Mutates NEW backing array only!
	fmt.Println("Inside function:", s) // Output: [999 2 3 42]
}

// Trap 2: Copied sync.Mutex Trap
type SafeCounter struct {
	mu    sync.Mutex
	count int
}

// BUG: Receiver is value `SafeCounter`, NOT pointer `*SafeCounter`!
func (c SafeCounter) IncrUnsafe() {
	c.mu.Lock() // Locks COPY of mutex!
	defer c.mu.Unlock()
	c.count++
}

func main() {
	// Slice Reallocation Demo
	slice := make([]int, 3, 3) // len=3, cap=3
	slice[0], slice[1], slice[2] = 1, 2, 3

	appendValue(slice)
	fmt.Println("Outside function:", slice) // Output: [1 2 3]! Value unchanged!

	// Mutex Copy Demo
	counter := SafeCounter{}
	counter.IncrUnsafe()
	fmt.Println("Counter value:", counter.count) // Output: 0!
}
```

**Under the Hood / Why It Happens**:
A Go slice is represented internally by `reflect.SliceHeader`:
```go
type SliceHeader struct {
    Data uintptr
    Len  int
    Cap  int
}
```
When `appendValue(slice)` is called, `SliceHeader` is copied onto the function's stack frame. When `append()` exceeds `Cap`, Go's runtime allocates a double-sized backing array, updates `Data` on the function's stack slice copy, and copies original elements over. The caller's `SliceHeader.Data` remains pointing to the old array.

For `sync.Mutex`, a mutex is a struct holding atomic state flags (`state int32`, `sema uint32`). Copying a struct value copies these flags. Locking the copy changes `state` on the copy, leaving the original mutex unlocked and creating data races across threads.

**Key Takeaway / Safe Pattern**:
To modify slice length/capacity in a caller function, return the modified slice from the function or pass a slice pointer (`*[]int`). Always use pointer receivers (`(c *SafeCounter)`) for structs containing synchronization primitives like `sync.Mutex`.

```go
// SAFE: Return modified slice or use slice pointer
func appendValueSafe(s []int) []int {
	s = append(s, 42)
	s[0] = 999
	return s // Caller receives slice pointing to new backing array
}

// SAFE: Pointer receiver for structs with sync.Mutex
func (c *SafeCounter) IncrSafe() {
	c.mu.Lock() // Locks original mutex instance!
	defer c.mu.Unlock()
	c.count++
}
```
