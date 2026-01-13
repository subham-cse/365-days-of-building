# Day 030: Smart Pointer Cycles, `Weak` Pointer Traps, and Custom Allocators
**Language / Domain**: Rust

**The Core Concept / "Did You Know?"**:
While Rust guarantees thread safety and memory safety without a garbage collector, it does **NOT** prevent runtime **Memory Leaks**. Using reference-counted smart pointers (`Rc<T>` or `Arc<T>`) combined with interior mutability (`RefCell<T>` or `Mutex<T>`) makes it possible to construct reference cycles where two objects hold `Rc` pointers to each other.

Because neither object's `strong_count` ever drops to zero, Rust's `Drop` trait destructor is never invoked, leaking heap memory permanently. 

To break reference cycles, developers use `Weak<T>` pointers. However, upgrading a `Weak<T>` pointer to `Rc<T>` via `.upgrade()` creates a transient strong reference that must be checked for `None` before access.

**The Code Snippet**:
```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    value: i32,
    next: Option<Rc<RefCell<Node>>>,
    prev: Option<Weak<RefCell<Node>>>, // Weak pointer breaks retain cycle!
}

fn create_reference_cycle_leak() {
    struct LeakyNode {
        next: Option<Rc<RefCell<LeakyNode>>>,
    }

    let node1 = Rc::new(RefCell::new(LeakyNode { next: None }));
    let node2 = Rc::new(RefCell::new(LeakyNode { next: Some(Rc::clone(&node1)) }));

    // TRAP: Retain Cycle Created! node1 points to node2, node2 points to node1!
    node1.borrow_mut().next = Some(Rc::clone(&node2));

    println!("Node1 strong count: {}", Rc::strong_count(&node1)); // 2
    println!("Node2 strong count: {}", Rc::strong_count(&node2)); // 2

    // Function exits, but both nodes LEAK permanently on the heap!
}

fn main() {
    create_reference_cycle_leak();
}
```

**Under the Hood / Why It Happens**:
`Rc<T>` allocates a metadata header on the heap alongside the value:
```rust
struct RcBox<T> {
    strong: Cell<usize>,
    weak:   Cell<usize>,
    value:  T,
}
```
When an `Rc` instance is cloned, Rust increments `strong`. When an `Rc` instance goes out of scope, Rust decrements `strong`. When `strong` reaches `0`, Rust calls `Drop::drop(&mut value)` to deallocate `T`. 

In a reference cycle, `node1` holds an `Rc` clone of `node2` (`strong == 2`), and `node2` holds an `Rc` clone of `node1` (`strong == 2`). When variables `node1` and `node2` go out of scope, both `strong` counts decrement to `1`. Because neither reached `0`, neither node is ever freed from memory.

`Weak<T>` pointers increment `weak` count instead of `strong` count. A `weak` count does not prevent the underlying `value` from being dropped when `strong` reaches `0`.

**Key Takeaway / Safe Pattern**:
Use `Weak<T>` pointers (`Rc::downgrade` / `Arc::downgrade`) for parent pointers, back-references, or observer patterns to prevent reference cycles.

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct ParentNode {
    children: Vec<Rc<RefCell<ChildNode>>>,
}

struct ChildNode {
    // SAFE: Parent back-reference is Weak, preventing retain cycle!
    parent: Option<Weak<RefCell<ParentNode>>>,
}

fn safe_tree_nodes() {
    let parent = Rc::new(RefCell::new(ParentNode { children: vec![] }));
    
    let child = Rc::new(RefCell::new(ChildNode {
        parent: Some(Rc::downgrade(&parent)), // Creates Weak reference
    }));

    parent.borrow_mut().children.push(Rc::clone(&child));

    // When upgrading Weak reference to check if Parent is still alive:
    if let Some(parent_rc) = child.borrow().parent.as_ref().unwrap().upgrade() {
        println!("Parent is still alive!");
    }
}
```
