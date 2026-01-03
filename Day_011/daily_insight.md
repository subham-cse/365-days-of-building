# Day 011: Goroutine Leaks, Slice Reslicing Memory Traps, and Interface `nil` Checks
**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, an interface value is a tuple containing two pointers: the concrete **type descriptor** and the concrete **value pointer**. An interface variable holding a typed pointer that equals `nil` (e.g. `(*MyError)(nil)`) is **NOT** equal to an untyped `nil` interface (`nil`). Checking `if err != nil` will evaluate to `true` even if the concrete error pointer is `nil`!

Additionally, Go slices hold reference pointers to underlying backing arrays. Taking a small reslice (`slice[10:12]`) of a massive 10MB slice keeps the entire 10MB backing array allocated in heap memory indefinitely. Goroutines that block forever on unbuffered channels or context locks cause severe memory leaks because the Go garbage collector can never sweep blocked goroutine stacks.

**The Code Snippet**:
```go
package main

import (
	"fmt"
)

type CustomError struct {
	Msg string
}

func (e *CustomError) Error() string {
	return e.Msg
}

// Trap 1: Interface nil comparison anomaly
func getError(fail bool) error {
	var err *CustomError = nil
	if fail {
		err = &CustomError{Msg: "operation failed"}
	}
	// BUG: Returning typed nil (*CustomError) inside `error` interface
	return err 
}

// Trap 2: Slice backing array memory leak
func getSubSlice() []byte {
	// Allocate 10MB backing array
	largeData := make([]byte, 10,000,000) 
	// Return slice of 3 bytes
	return largeData[0:3] // Keeps whole 10MB pinned in memory!
}

func main() {
	err := getError(false)
	// Expectation: err is nil, so condition should be false
	if err != nil {
		fmt.Printf("BUG: err is NOT nil! Type: %T, Value: %v\n", err, err)
	} else {
		fmt.println("err is nil")
	}
}
```

**Under the Hood / Why It Happens**:
At the runtime layer, Go represents dynamic interfaces using two internal structures: `eface` (empty interface `interface{}`) and `iface` (interface with methods).
```go
type iface struct {
    tab  *itab          // Type information and virtual method table
    data unsafe.Pointer // Pointer to concrete value
}
```
When `getError()` returns `var err *CustomError = nil`, Go wraps it inside an `iface` struct:
`tab` points to `*CustomError` type metadata, and `data` points to `nil`. 

When executing `if err != nil`, Go compares the interface structure against an empty interface (`tab == nil && data == nil`). Because `tab` is non-nil (`*CustomError`), `err != nil` evaluates to `true`!

Regarding slices, a Go slice header (`reflect.SliceHeader`) contains `Data unsafe.Pointer`, `Len int`, and `Cap int`. Reslicing a sub-range reuses the exact same backing array pointer (`Data`), preventing GC cleanup of unreferenced leading or trailing elements.

**Key Takeaway / Safe Pattern**:
Always return explicit untyped `nil` when returning error interfaces from functions. To release large slice backing arrays, copy required sub-slices into a new slice using `copy()`.

```go
// SAFE: Explicit nil interface return
func getErrorSafe(fail bool) error {
	if fail {
		return &CustomError{Msg: "operation failed"}
	}
	return nil // Returns true empty interface (tab=nil, data=nil)
}

// SAFE: Discard large backing array by copying
func getSubSliceSafe() []byte {
	largeData := make([]byte, 10,000,000)
	sub := make([]byte, 3)
	copy(sub, largeData[0:3])
	return sub // 10MB backing array can now be collected by GC!
}
```
