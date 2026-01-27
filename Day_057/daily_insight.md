# Day 057: Swift ARC Retain Cycles and Weak/Unowned References

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
Swift uses Automatic Reference Counting (ARC) to manage heap memory for class instances. Every time a reference to a class instance is created, its strong reference count increments. ARC automatically deallocates an instance when its strong reference count drops to zero.

A **Strong Reference Cycle (Retain Cycle)** occurs when two class instances hold strong references to each other, or when a closure captures `self` strongly inside an instance property. Retain cycles prevent strong reference counts from ever reaching zero, causing permanent heap memory leaks.

**The Code Snippet**:
```swift
import Foundation

class NetworkManager {
    var onDataReceived: ((String) -> Void)?
    let name = "MainNetworkService"

    func setupHandlersUnsafe() {
        // Retain Cycle Trap: Closure strongly captures `self`
        onDataReceived = { data in
            // Implicit strong capture of self!
            print("[\(self.name)] Processing: \(data)") 
        }
    }

    func setupHandlersSafe() {
        // Safe Pattern: Capture list with [weak self]
        onDataReceived = { [weak self] data in
            guard let self = self else { return }
            print("[\(self.name)] Processing safely: \(data)")
        }
    }

    deinit {
        print("NetworkManager deallocated from heap memory!")
    }
}

func demonstrateRetainCycle() {
    print("--- Running Unsafe Handler (Leaked Memory) ---")
    var manager1: NetworkManager? = NetworkManager()
    manager1?.setupHandlersUnsafe()
    manager1 = nil // Strong count remains > 0 due to closure capture! deinit NOT called!

    print("\n--- Running Safe Handler ([weak self]) ---")
    var manager2: NetworkManager? = NetworkManager()
    manager2?.setupHandlersSafe()
    manager2 = nil // Clean deallocation! deinit called immediately!
}

demonstrateRetainCycle()
```

**Under the Hood / Why It Happens**:
Every Swift class instance contains a hidden runtime header holding two reference counters: `strongRC` and `unownedRC` / `weakRC`.

In `setupHandlersUnsafe()`, `manager1` owns the `onDataReceived` closure object. When the closure body references `self.name`, Swift's compiler automatically generates a strong increment call (`swift_retain(self)`) inside the closure object frame. `manager1` holds strong ownership of closure $\to$ closure holds strong ownership of `manager1`. Setting `manager1 = nil` decrements `strongRC` from 2 to 1, leaving both objects stranded in memory.

Using `[weak self]` creates a non-owning weak reference backed by a side-table pointer, allowing `strongRC` to drop to zero cleanly.

**Key Takeaway / Safe Pattern**:
Use `[weak self]` in delegate properties, asynchronous closures, and completion handlers that reference instance properties or methods. Use `[unowned self]` only when guaranteed that the referenced class instance will never be deallocated before the closure is invoked.
