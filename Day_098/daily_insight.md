# Day 098: RefCell Interior Mutability and Borrow Mutex Traps
- **Language / Domain**: Rust
- **The Core Concept / "Did You Know?"**: Rust enforces aliasing XOR mutability at compile time. However, types like `RefCell<T>` provide *interior mutability*, moving borrow checker enforcement from compile-time to runtime. 

If code dynamically requests a mutable borrow (`borrow_mut()`) while an active immutable borrow (`borrow()`) or another mutable borrow still exists in scope, Rust will not give a compiler error—it will trigger a runtime `panic!`!

- **The Code Snippet**:
```rust
use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    val: i32,
    neighbors: Vec<Rc<RefCell<Node>>>,
}

fn main() {
    let node = Rc::new(RefCell::new(Node {
        val: 42,
        neighbors: vec![],
    }));

    // Obtain an immutable borrow of node contents
    let borrowed_node = node.borrow();
    println!("Node value: {}", borrowed_node.val);

    // Attempting to dynamically borrow mutably while immutable borrow is active:
    // Rust panics at runtime: AlreadyBorrowed
    let mut mutable_node = node.borrow_mut(); 
    mutable_node.val = 100;
}
```

- **Under the Hood / Why It Happens**:
`RefCell<T>` maintains an internal reference counter (`isize`) tracking active borrows:
- `0`: Unborrowed.
- `Positive (> 0)`: Number of active `Ref` (immutable) borrows.
- `-1`: Active `RefMut` (mutable) borrow.

When `borrow()` is called, `RefCell` increments the counter if it is non-negative. When `borrow_mut()` is called, it checks if the counter is exactly `0`. If not, `RefCell` immediately calls `panic!("already borrowed: ...")`.

- **Key Takeaway / Safe Pattern**:
To prevent runtime panics with `RefCell`, minimize the lifetime of borrows using explicit scope blocks `{ ... }`, or use non-panicking variants like `try_borrow()` and `try_borrow_mut()`:

```rust
use std::cell::RefCell;

fn safe_borrow_example(cell: &RefCell<i32>) {
    if let Ok(mut val) = cell.try_borrow_mut() {
        *val += 10;
        println!("Updated value: {}", *val);
    } else {
        println!("Failed to acquire mutable borrow; cell is currently borrowed elsewhere.");
    }
}
```
