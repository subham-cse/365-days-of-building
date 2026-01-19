# Day 042: Rust RefCell and Runtime Borrow Checking Edge Cases

**Language / Domain**: Rust

**The Core Concept / "Did You Know?"**:
Rust enforces strict aliasing rules at compile time: you can have either any number of immutable references (`&T`) OR exactly one mutable reference (`&mut T`) to a resource at a given time. To bypass compiler static checks for legitimate design patterns (like graph nodes or mock objects), Rust provides interior mutability via `RefCell<T>`.

`RefCell<T>` shifts borrow checking from compile time to runtime. However, violating aliasing rules on a `RefCell` does NOT yield a compile error; it causes an immediate runtime panic (`already borrowed: BorrowMutError`).

**The Code Snippet**:
```rust
use std::cell::RefCell;

struct DataNode {
    value: i32,
}

fn demonstrate_runtime_borrow_panic() {
    let cell = RefCell::new(DataNode { value: 42 });

    // Acquire immutable borrow
    let borrow_one = cell.borrow();
    println!("First borrow value: {}", borrow_one.value);

    // Acquire second immutable borrow - VALID!
    let borrow_two = cell.borrow();
    println!("Second borrow value: {}", borrow_two.value);

    // ATTEMPT MUTABLE BORROW WHILE IMMUTABLE BORROWS ARE ACTIVE
    // Compiles fine! But panics at runtime with:
    // "thread 'main' panicked at 'already borrowed: BorrowMutError'"
    let mut mutable_borrow = cell.borrow_mut();
    mutable_borrow.value = 100;
}

fn demonstrate_safe_try_borrow() {
    let cell = RefCell::new(DataNode { value: 42 });
    let _borrow = cell.borrow();

    // Safe pattern: Use try_borrow_mut to avoid panics
    match cell.try_borrow_mut() {
        Ok(mut mut_ref) => {
            mut_ref.value = 100;
        }
        Err(err) => {
            println!("Safely caught borrow error at runtime: {}", err);
        }
    }
}

fn main() {
    demonstrate_safe_try_borrow();
    // Uncommenting below will trigger thread panic at runtime
    // demonstrate_runtime_borrow_panic();
}
```

**Under the Hood / Why It Happens**:
`RefCell<T>` tracks active borrows using an internal `isize` counter header:
- `counter == 0`: Unborrowed.
- `counter > 0`: Active immutable borrows (`counter` equals active reader count).
- `counter < 0`: Active mutable borrow (`counter` equals `-1`).

When `.borrow()` is called, `RefCell` increments the counter if `counter >= 0`, panicking if `counter < 0`. When `.borrow_mut()` is called, `RefCell` asserts `counter == 0` and sets it to `-1`. If references (`Ref` / `RefMut` RAII guards) are held simultaneously across function calls, the runtime counter state check fails and panics.

**Key Takeaway / Safe Pattern**:
Limit the scope of `borrow()` and `borrow_mut()` calls to short code blocks or use explicit block scopes `{}` so RAII guards drop promptly. Use `try_borrow()` and `try_borrow_mut()` when non-panicking error handling is required. Prefer thread-safe `Mutex<T>` or `RwLock<T>` when multi-threading.
