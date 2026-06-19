# Day 226: Rust Non-Lexical Lifetimes (NLL) Limits & Closure Field Disjoint Borrowing

**Language / Domain**: Rust / Memory Safety & Borrow Checker

**The Core Concept / "Did You Know?"**:
Since the introduction of **Non-Lexical Lifetimes (NLL)** in 2018, Rust's borrow checker evaluates variable lifetimes based on control-flow graphs rather than strict lexical block scopes (`{ ... }`). This allows borrows to end at their last point of use rather than continuing to the end of the enclosing block scope.

Additionally, Rust support **Disjoint Field Borrowing**: borrowing one field of a struct (`&mut my_struct.field1`) does not lock the entire struct, allowing simultaneous mutable/immutable borrowing of distinct fields (`&my_struct.field2`).

However, **closures break disjoint field borrowing**! When a closure captures a field of a struct in Rust 2018 or captures a path in Rust 2021, capturing struct paths inside closures can borrow entire parent structs or create borrow conflicts across closure invocations.

**The Code Snippet**:
```rust
struct Container {
    buffer: Vec<u8>,
    log_count: usize,
}

impl Container {
    // BUGGY PATTERN: Closure captures entire `self` or collides with mutable borrows
    pub fn process_buggy(&mut self) {
        // Closure capturing field via `self` reference
        let mut logger = || {
            self.log_count += 1; // Borrows `self` mutably!
        };

        // ERROR: Cannot borrow `self.buffer` mutably because `logger` borrowed all of `self`!
        // self.buffer.push(42); 
        logger();
    }

    // SAFE PATTERN: Local variable destructuring prior to closure creation
    pub fn process_idiomatic(&mut self) {
        // Explicitly re-borrow disjoint fields into separate local references
        let log_count = &mut self.log_count;
        let buffer = &mut self.buffer;

        let mut logger = move || {
            *log_count += 1;
        };

        buffer.push(42); // Cleanly allowed! `buffer` and `log_count` are disjoint borrows.
        logger();
    }
}

fn main() {
    let mut c = Container {
        buffer: vec![1, 2, 3],
        log_count: 0,
    };

    c.process_idiomatic();
    println!("Log Count: {}, Buffer Len: {}", c.log_count, c.buffer.len());
}
```

**Under the Hood / Why It Happens**:
1. **Field Disjoint Borrowing in Direct Code**:
   In direct statements (`self.buffer.push(1); self.log_count += 1;`), the borrow checker inspects paths (`Place::Field(Place::Local(self), 0)` vs `Place::Field(Place::Local(self), 1)`). Because paths refer to non-overlapping memory offsets, the compiler permits concurrent borrows.

2. **Closure Capture Analysis**:
   When constructing a closure `|| { self.log_count += 1; }`:
   - Prior to Rust 2021, closures always captured whole root variables (`self`).
   - In Rust 2021, closure disjoint capture was added for paths, but closures still infer captures based on how variables are accessed inside the closure body. If the closure references `self`, the borrow checker may determine that `self` as a whole is borrowed for the lifetime of the closure variable `logger`.
   - Consequently, while `logger` is in scope, any attempt to access `self.buffer` outside the closure triggers compiler error `E0500: closure requires unique access to self but self is also borrowed`.

**Key Takeaway / Safe Pattern**:
- To perform disjoint field borrows alongside closures, bind struct fields to individual local variables (`let field_a = &mut self.field_a;`) *before* instantiating closures.
- Pass individual fields as arguments into functions/closures rather than passing whole struct references (`&mut self`).
- Take advantage of Rust 2021 Edition closure capture improvements, but stay mindful when passing struct pointers across closure boundaries.
