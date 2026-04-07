# Day 139: Go Interface Nil Check Traps (`nil` Interface vs `nil` Value)

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, an interface variable is NOT a simple raw pointer. An interface variable is represented internally as a two-pointer header containing a **type descriptor** (`_type` or `itab`) and a **value pointer** (`data`).

An interface variable equals `nil` ONLY when BOTH its type and its value pointers are `nil`. If an interface holds a non-nil type pointer pointing to a concrete type (such as `*MyError`), but the underlying concrete pointer value itself is `nil`, comparing that interface variable against `nil` evaluates to `false`!

This leads to catastrophic bugs where error-handling functions return `nil` concrete pointers wrapped in an `error` interface, causing callers to falsely believe an error occurred!

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

// BUGGY FUNCTION: Returns concrete pointer typed as error interface
func getCustomErrorBuggy(flag bool) error {
	var err *CustomError = nil // concrete type pointer is nil

	if flag {
		err = &CustomError{Msg: "Something went wrong"}
	}

	// TRAP: Returning concrete (*CustomError)(nil) populates type field in interface!
	return err 
}

// FIXED FUNCTION: Returns explicit nil error interface when no error occurs
func getCustomErrorFixed(flag bool) error {
	if flag {
		return &CustomError{Msg: "Something went wrong"}
	}
	return nil // Clean nil interface header (type=nil, value=nil)
}

func main() {
	err1 := getCustomErrorBuggy(false)
	fmt.Printf("err1 == nil: %v (Type: %T, Value: %v)\n", err1 == nil, err1, err1)
	
	if err1 != nil {
		fmt.Println("--> TRAP: Error check triggered even though no error occurred!")
	}

	fmt.Println()

	err2 := getCustomErrorFixed(false)
	fmt.Printf("err2 == nil: %v (Type: %T, Value: %v)\n", err2 == nil, err2, err2)
	if err2 != nil {
		fmt.Println("--> This will NOT print.")
	}
}
```

**Under the Hood / Why It Happens**:
In the Go runtime (`runtime/iface.go`), interfaces are defined as:
```go
type eface struct { // empty interface interface{}
    _type *_type
    data  unsafe.Pointer
}

type iface struct { // interface with methods (e.g. error)
    tab  *itab
    data unsafe.Pointer
}
```

When `var err *CustomError = nil` is returned as `error`:
- Go constructs an `iface` struct where `tab` points to the `*CustomError` method table descriptor.
- `data` points to `nil` (`0x0`).

When `if err1 == nil` is evaluated:
- Go checks if `iface.tab == nil && iface.data == nil`.
- Because `iface.tab` contains `*CustomError` type metadata (`tab != nil`), the equality check yields **`false`**!

**Key Takeaway / Safe Pattern**:
Never declare concrete pointer variables for error handling (e.g., `var err *MyCustomErr`). Always return the explicit untyped `nil` literal directly when returning `error` interfaces (`return nil`), or declare the variable directly with the `error` interface type (`var err error`).
