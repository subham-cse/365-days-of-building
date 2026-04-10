# Day 141: Swift ARC Retain Cycles in Closures & `[weak self]` Traps

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
Swift uses Automatic Reference Counting (ARC) to manage heap memory. While ARC frees developers from manual memory management, strong reference cycles (retain cycles) occur when two object instances hold strong references to each other, preventing ARC retain counts from ever dropping to zero.

A frequent source of hidden memory leaks occurs inside **closures**. Closures in Swift capture variables from their surrounding scope by strong reference by default. If a class instance stores a closure as a property, and that closure captures `self` inside its body, a circular strong reference is formed (`self -> closure -> self`), causing the class instance to leak permanently!

**The Code Snippet**:
```swift
import Foundation

class NetworkManager {
    let url: String
    var onCompletion: (() -> Void)?

    init(url: String) {
        self.url = url
        print("NetworkManager initialized (\(url))")
    }

    func startTaskBuggy() {
        // TRAP: Implicit strong capture of self causes Retain Cycle!
        self.onCompletion = {
            print("Finished downloading from \(self.url)")
        }
    }

    func startTaskSafe() {
        // SAFE PATTERN: Capture list [weak self] breaks retain cycle
        self.onCompletion = { [weak self] in
            guard let self = self else {
                print("NetworkManager was deallocated before completion!")
                return
            }
            print("Finished downloading safely from \(self.url)")
        }
    }

    deinit {
        print("NetworkManager DEALLOCATED successfully! (\(url))")
    }
}

// Execution Demonstration
func triggerLeak() {
    print("--- Testing Leaky Manager ---")
    let leakyManager = NetworkManager(url: "https://api.example.com/leak")
    leakyManager.startTaskBuggy()
    // leakyManager goes out of scope, but deinit is NEVER called!
}

func triggerSafe() {
    print("\n--- Testing Safe Manager ---")
    let safeManager = NetworkManager(url: "https://api.example.com/safe")
    safeManager.startTaskSafe()
    // safeManager goes out of scope, deinit IS called!
}

triggerLeak()
triggerSafe()
```

**Under the Hood / Why It Happens**:
In Swift's runtime memory layout:
1. `NetworkManager` object is allocated on the heap. Retain count = 1.
2. `self.onCompletion = { ... self.url ... }` allocates a closure block on the heap.
3. The closure object captures the `self` heap pointer into its payload environment and increments `self`'s strong reference count to 2.
4. `self.onCompletion` assigns the closure pointer to `NetworkManager`'s property slot, incrementing the closure's retain count to 1.

When the local variable `leakyManager` leaves function scope, `self`'s retain count drops from 2 to 1. Because count is `> 0`, `deinit` is never invoked, and neither object is ever deallocated!

Using `[weak self]` instructs the Swift compiler to store an unowned/weak pointer reference in the closure's context without incrementing `self`'s ARC retain count. The reference becomes an `Optional<Self>` that automatically turns to `nil` if `self` is deallocated.

**Key Takeaway / Safe Pattern**:
Always use `[weak self]` in capture lists whenever storing a closure as a property on an instance, or when passing closures to long-lived asynchronous task handlers that outlive local method execution.
