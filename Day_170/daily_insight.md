# Day 170: RefCell Dynamic Borrowing and Runtime Panic Traps

**Language / Domain**: Rust

**The Core Concept / "Did You Know?"**:
Rust enforces single-writer / multi-reader XOR borrowing rules at compile time (`&mut T` XOR `&T`). However, when building graph structures, callbacks, or mock objects, compile-time borrow rules can be overly restrictive.

Rust provides **Interior Mutability** types like `RefCell<T>` to defer borrow checking to runtime. While `RefCell` allows mutating data behind an immutable reference `&RefCell<T>`, violating aliasing rules at runtime will not be caught by the compiler. Instead, it triggers an immediate thread panic (`AlreadyBorrowed` / `AlreadyBorrowedMut`).

**The Code Snippet**:

```rust
use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    value: i32,
    neighbors: Vec<Rc<RefCell<Node>>>,
}

fn buggy_traverse(node: &RefCell<Node>) {
    // Acquire a dynamic mutable borrow
    let mut borrow_mut = node.borrow_mut();
    borrow_mut.value += 10;

    // BUG: Attempt to acquire an immutable borrow while `borrow_mut` is still active!
    // In safe compile-time Rust, `&mut T` and `&T` cannot overlap.
    // With RefCell, this compiles cleanly, but panics at RUNTIME!
    let borrow_immut = node.borrow(); 
    println!("Node value: {}", borrow_immut.value);
}

fn safe_traverse(node: &RefCell<Node>) {
    // Limit scope of borrow_mut using explicit block scope
    {
        let mut borrow_mut = node.borrow_mut();
        borrow_mut.value += 10;
    } // borrow_mut drops here, resetting RefCell borrow counter!

    // Now immutable borrow succeeds cleanly
    let borrow_immut = node.borrow();
    println!("Safe Node value: {}", borrow_immut.value);
}

fn main() {
    let n = Rc::new(RefCell::new(Node { value: 5, neighbors: vec![] }));

    println!("Executing safe traversal:");
    safe_traverse(&n);

    println!("Executing buggy traversal:");
    // Uncommenting buggy_traverse will crash with:
    // thread 'main' panicked at 'already borrowed: BorrowMutError'
    // buggy_traverse(&n);
}
```

**Under the Hood / Why It Happens**:
`RefCell<T>` maintains an internal signed integer counter (`isize`) tracking active borrows:
- `0`: Unborrowed.
- `> 0`: Active immutable references (`borrow()` incremented the count).
- `< 0` (`-1`): Active mutable reference (`borrow_mut()` set the count to -1).

When `borrow()` is called, `RefCell` checks if `borrow_count < 0`. If true, it raises a panic.
When `borrow_mut()` is called, `RefCell` checks if `borrow_count != 0`. If non-zero, it raises a panic.

Because `RefCell` checks these invariants dynamically via CPU instructions at runtime, it circumvents zero-cost compile-time abstractions, introducing lightweight runtime checking overhead and panic risk.

**Key Takeaway / Safe Pattern**:
Always minimize the scope of `RefCell::borrow_mut()` guards using explicit block scopes `{ ... }` or `std::mem::drop()`. Use `try_borrow()` or `try_borrow_mut()` when dynamic borrow conflicts are possible to return a handleable `Result` instead of crashing the thread with a panic.
