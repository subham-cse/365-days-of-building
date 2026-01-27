# Day 055: Go Interface Nil Checks and Non-Nil Typed Pointers

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
In Go, an `interface` variable is implemented as a 2-word header containing a **type descriptor** pointer and a **data** value pointer. An interface variable evaluates to `nil` ONLY if both its type descriptor AND its data value pointer are `nil`.

If you assign a non-nil typed pointer (e.g., `*MyCustomError`) whose underlying value is `nil` to an `interface` return variable (such as `error`), the interface header stores a valid type descriptor. Consequently, testing `if err != null` evaluates to `true`, causing false-positive error handling bugs.

**The Code Snippet**:
```go
package main

import "fmt"

type CustomError struct {
	Code int
}

func (e *CustomError) Error() string {
	return fmt.Sprintf("Error Code: %d", e.Code)
}

// Anti-pattern: Returning concrete pointer type assigned to error interface
func getUnsafeError(fail bool) error {
	var err *CustomError = nil // Typed pointer initialized to nil
	if fail {
		err = &CustomError{Code: 500}
	}
	// BUG: Returns interface header with Type=*CustomError, Value=nil
	return err 
}

// Safe Pattern: Explicitly return nil error interface
func getSafeError(fail bool) error {
	if fail {
		return &CustomError{Code: 500}
	}
	return nil // Returns clean interface header (Type=nil, Value=nil)
}

main() {
	errUnsafe := getUnsafeError(false)
	fmt.Println("errUnsafe == nil:", errUnsafe == nil) // False! (Interface is NOT nil)

	if errUnsafe != nil {
		fmt.Println("Triggered false positive error check! (Unsafe)")
	}

	errSafe := getSafeError(false)
	fmt.Println("\nerrSafe == nil:", errSafe == nil) // True!

	if errSafe != nil {
		fmt.Println("This won't print.")
	}
}
```

**Under the Hood / Why It Happens**:
Go represents interfaces internally using the `iface` struct:
```go
type iface struct {
    tab  *itab          // Interface type descriptor table
    data unsafe.Pointer // Pointer to actual underlying instance
}
```
When `getUnsafeError` returns `err`, Go packages the `*CustomError` pointer into `iface`. `tab` points to the metadata struct for `*CustomError`, while `data` is `nil`.

During `if err != nil` evaluation, Go checks `iface.tab == nil && iface.data == nil`. Because `iface.tab` points to `*CustomError`'s type record, the condition evaluates to `false`.

**Key Takeaway / Safe Pattern**:
Never declare concrete pointer variables when returning standard interface types (like `error`). Return `nil` literals explicitly when no error occurs (`return nil`), or declare return variables using the interface type directly.
