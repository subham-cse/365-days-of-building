# Day 095: Interface Nil Check Trap in Go
- **Language / Domain**: Go
- **The Core Concept / "Did You Know?"**: In Go, an interface variable is stored as a tuple of two underlying pointers: `(type, value)`. An interface is `nil` **only** if both its `type` pointer and its `value` pointer are `nil`. 

If an interface variable holds a concrete type pointer (such as `*MyError`) that happens to be `nil`, the interface itself is **not nil** because its type descriptor is populated. Comparing this interface variable against `nil` will yield `false`, leading to silent bugs and runtime panics when calling interface methods.

- **The Code Snippet**:
```go
package main

import (
	"fmt"
)

type CustomError struct {
	Code int
}

func (e *CustomError) Error() string {
	return fmt.Sprintf("error code: %d", e.Code)
}

func process() error {
	var err *CustomError = nil // Typed nil pointer
	// ... logic that might set err ...
	return err // Returns (*CustomError)(nil) wrapped in interface error
}

func main() {
	err := process()
	if err != nil {
		fmt.Println("ERROR DETECTED:", err) // Unwanted execution!
		// Accessing methods on underlying nil pointer will panic if not checked internally
	} else {
		fmt.Println("Success!")
	}
}
```

- **Under the Hood / Why It Happens**:
Under the hood, Go represents interfaces using `eface` (empty interface) or `iface` (interface with methods):

```go
type iface struct {
    tab  *itab          // Type info and method table
    data unsafe.Pointer // Pointer to actual data
}
```

When returning `err` from `process()`, Go converts `*CustomError` into `iface{tab: &CustomErrorType, data: nil}`. When evaluating `err != nil`, Go checks if `iface.tab == nil && iface.data == nil`. Because `iface.tab` points to the `CustomError` type metadata, `err != nil` evaluates to `true`.

- **Key Takeaway / Safe Pattern**:
Never declare concrete pointer variables for error handling unless returning explicit `nil` interface values when no error occurs:

```go
package main

import "fmt"

func processSafe() error {
	// Return literal nil when no error occurs
	return nil
}

func main() {
	if err := processSafe(); err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Println("Success!")
	}
}
```
