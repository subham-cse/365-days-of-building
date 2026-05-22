# Day 198: Rust RefCell Interior Mutability and Runtime Borrowing Panics

**Language / Domain**: Rust

**The Core Concept / "Did You Know?"**:
Rust enforces strict aliasing rules at compile time: you can have either any number of immutable references (`&T`) **OR** exactly one mutable reference (`&mut T`) to a resource at any given moment, but never both simultaneously.

To bypass compile-time mutability checks in single-threaded scenarios, Rust provides **Interior Mutability** types like `RefCell<T>`. Instead of enforcing borrow rules at compile time, `RefCell<T>` defers checks to **runtime**. If your code attempts to create a mutable borrow (`borrow_mut()`) while an active immutable borrow (`borrow()`) or another mutable borrow is currently alive in scope, Rust will not issue a compiler error—it will **panic at runtime**, crashing the thread.

**The Code Snippet**:
```rust
use std::cell::RefCell;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // Acquire an immutable borrow in current scope
    let first_ref = data.borrow();
    println!("First element: {}", first_ref[0]);

    // TRAP: Attempting to acquire a mutable borrow while first_ref is still in scope!
    // At compile time, this compiles cleanly!
    // At runtime, thread main panics: 'already borrowed: BorrowMutError'
    let mut mut_ref = data.borrow_mut();
    mut_ref.push(4);

    println!("Length: {}", mut_ref.len());
}
```

**Under the Hood / Why It Happens**:
Inside `std::cell::RefCell<T>`, Rust maintains a private counter (`isize`) tracking active references:
- `0`: Unborrowed.
- `> 0`: Currently borrowed immutably by `N` references.
- `< 0` (`-1`): Currently borrowed mutably by 1 reference.

When `data.borrow()` is called, `RefCell` checks if counter `< 0`. If false, it increments the counter and returns a `Ref<T>` RAII guard wrapper.

When `data.borrow_mut()` is called, `RefCell` checks if counter `!= 0`. Because `first_ref` is still active, counter is `1`. Seeing `counter != 0`, `borrow_mut()` immediately calls `panic!("already borrowed: BorrowMutError")`.

**Key Takeaway / Safe Pattern**:
To prevent runtime `BorrowError` panics when using `RefCell`, explicitly limit the scope of borrows using block scopes `{ ... }`, or use non-panicking borrow methods like `try_borrow()` and `try_borrow_mut()`.

```rust
use std::cell::RefCell;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // Safe Pattern 1: Enclose immutable borrow inside explicit block scope
    {
        let first_ref = data.borrow();
        println!("First element: {}", first_ref[0]);
    } // first_ref RAII guard goes out of scope here; RefCell counter decremented to 0!

    // Now borrow_mut succeeds cleanly
    data.borrow_mut().push(4);

    // Safe Pattern 2: Non-panicking check using try_borrow_mut
    if let Ok(mut mut_ref) = data.try_borrow_mut() {
        mut_ref.push(5);
    } else {
        println!("Could not acquire mutable reference safely!");
    }
}
```
