# Day 067: Nil Interface Values vs Typed Nil Pointers in Go

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, an interface variable is not simply a raw pointer—it is a two-word internal data structure containing a type descriptor (`_type` or `itab`) and a pointer to the actual data (`data`).

Because of this design, **a nil pointer of a concrete type assigned to an interface is NOT equal to a nil interface!** Comparing a typed nil pointer stored inside an interface variable against `nil` evaluates to `false`. This distinction causes subtle runtime panics in production software when functions return dynamic errors or custom struct pointers wrapped in interface return types.

**The Code Snippet**:
```go
package main

import (
	"fmt"
)

// Custom error type
type CustomError struct {
	Code    int
	Message string
}

func (e *CustomError) Error() string {
	return fmt.Sprintf("Error %d: %s", e.Code, e.Message)
}

// BUG TRAP: Returning a concrete nil pointer as an interface type
func processRequestUnsafe(fail bool) error {
	var err *CustomError = nil
	if fail {
		err = &CustomError{Code: 500, Message: "Internal failure"}
	}
	// BUG: Returning typed nil pointer (*CustomError) as interface (error)
	return err 
}

// SAFE PATTERN: Return explicit nil interface when no error occurs
func processRequestSafe(fail bool) error {
	if fail {
		return &CustomError{Code: 500, Message: "Internal failure"}
	}
	// Return true interface nil!
	return nil 
}

func main() {
	// Call unsafe function with fail = false
	err1 := processRequestUnsafe(false)
	fmt.Printf("err1 == nil? %v\n", err1 == nil) // Outputs: FALSE!
	
	// Triggers nil pointer dereference panic if caller assumes err1 is nil!
	if err1 != nil {
		fmt.Println("Handled error (will panic if called):", err1.Error())
	}

	// Call safe function
	err2 := processRequestSafe(false)
	fmt.Printf("err2 == nil? %v\n", err2 == nil) // Outputs: TRUE!
}
```

**Under the Hood / Why It Happens**:
Go represents interfaces under the hood as two distinct C-like structs in runtime package header (`runtime/iface.go`):
1. `eface` for empty interfaces (`interface{}`): contains dynamic `*_type` and `data` pointer.
2. `iface` for non-empty interfaces (e.g., `error`): contains `*itab` (interface table with methods) and `data` pointer.

An interface value is strictly equal to `nil` (`val == nil`) **if and only if** both its type descriptor (`itab`/`_type`) and its data pointer (`data`) are `nil`. 

When assigning `var err *CustomError = nil` to return type `error`, Go populates the interface's `itab` with the concrete type signature `*CustomError`, while setting `data` to `nil`. Since `itab` is non-nil, `err != nil` evaluates to `true`! Attempting to invoke interface methods on it subsequently dereferences the dynamic `nil` pointer, panicking at runtime.

**Key Takeaway / Safe Pattern**:
When returning an interface (such as `error`), never declare a concrete pointer variable at the top of the function and return it directly. Always return an explicit literal `nil` when indicating success or absence of data.
