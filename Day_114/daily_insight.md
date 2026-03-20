# Day 114: Monomorphization Code Bloat and Trait Object Dynamic Dispatch
- **Language / Domain**: Rust
- **The Core Concept / "Did You Know?"**: In Rust, generic functions (`fn process<T: Trait>(item: T)`) use **Static Dispatch**. The Rust compiler compiles a distinct duplicate of the generic function for *every single concrete type* that invokes it—a process known as **monomorphization**.

While static dispatch produces zero-cost abstractions with maximum execution speed, instantiating generic functions with many different types can result in massive binary size bloat. To reduce binary size, developers can switch to **Dynamic Dispatch** using Trait Objects (`&dyn Trait` or `Box<dyn Trait>`).

- **The Code Snippet**:
```rust
use std::fmt::Display;

// Static Dispatch (Monomorphization):
// Compiler generates 3 separate machine code functions:
// print_static_i32, print_static_f64, print_static_str!
fn print_static<T: Display>(val: T) {
    println!("Static value: {}", val);
}

// Dynamic Dispatch via Trait Objects:
// Compiler generates ONLY 1 machine code function using a vtable pointer lookup!
fn print_dynamic(val: &dyn Display) {
    println!("Dynamic value: {}", val);
}

fn main() {
    // Static dispatch calls
    print_static(42);
    print_static(3.14);
    print_static("Rust Static");

    // Dynamic dispatch calls
    let a: i32 = 42;
    let b: f64 = 3.14;
    let c: &str = "Rust Dynamic";

    print_dynamic(&a);
    print_dynamic(&b);
    print_dynamic(&c);
}
```

- **Under the Hood / Why It Happens**:
Static dispatch expands generics during LLVM IR generation. If a generic function is 500 lines long and called with 20 different type signatures across a codebase, Rust monomorphizes 10,000 lines of LLVM IR code!

Dynamic dispatch (`&dyn Trait`) creates a fat pointer consisting of two pointers:
1. Pointer to the underlying data instance.
2. Pointer to a virtual method table (`vtable`) containing function pointers for the trait implementation. 

Methods are invoked via runtime vtable pointer indirection, keeping binary sizes small at the cost of a slight dereference overhead.

- **Key Takeaway / Safe Pattern**:
Use static dispatch (generics) in performance-critical inner loops where compiler inlining is essential. Switch to dynamic dispatch (`dyn Trait`) for large functions or non-performance-critical abstractions (such as plugin handlers or IO logging interfaces) to optimize binary size and compile times.
