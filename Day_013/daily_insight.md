# Day 013: ARC Retain Cycles in Closures and Value Type Copy-on-Write Semantics
**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
Swift uses **Automatic Reference Counting (ARC)** to manage object lifetime for reference types (`class`). Capturing `self` inside a closure creates a strong reference to `self`, while `self` simultaneously holds a strong reference to the closure. This forms a **Retain Cycle**, causing permanent memory leaks where neither instance is ever deallocated.

Conversely, Swift arrays and collections are value types (`struct`) that implement **Copy-on-Write (CoW)**. Modifying a value-type collection inside a loop or function triggers deep memory copies if multiple references share the underlying buffer, unexpectedly multiplying dynamic heap allocation costs.

**The Code Snippet**:
```swift
import Foundation

class NetworkManager {
    var onDataReceived: ((Data) -> Void)?
    var buffer: Data = Data()

    func setupHandler() {
        // RETAIN CYCLE TRAP: Closure captures strong self reference!
        onDataReceived = { data in
            self.buffer.append(data)
            print("Received \(data.count) bytes in \(self)")
        }
    }

    deinit {
        print("NetworkManager deallocated!") // NEVER CALLED!
    }
}

func simulateMemoryLeak() {
    var manager: NetworkManager? = NetworkManager()
    manager?.setupHandler()
    
    // Attempting to release manager
    manager = nil // Object leaks! `deinit` never runs!
}

// Copy-on-Write Performance Trap
func CoWBufferTrap() {
    let originalArray = Array(repeating: 42, count: 10_000_000)
    var copyArray = originalArray // Shares underlying heap buffer (O(1))

    // Modifying element triggers Copy-on-Write deep duplicate!
    copyArray[0] = 99 // O(N) heap allocation & element copy!
}

simulateMemoryLeak()
```

**Under the Hood / Why It Happens**:
ARC manages instance memory by maintaining an explicit reference counter inside every class instance header. When a closure captures an object reference without explicit modifiers, ARC increments that object's retain count. 

In `NetworkManager`, `self` owns `onDataReceived` (retain count 1). `onDataReceived` closure captures `self` (retain count increments to 2). Setting `manager = nil` decrements `self` retain count to 1. Because the closure still retains `self`, and `self` still retains the closure, the counter never drops to 0, permanently stranding both objects on the heap.

For CoW structs like `Array` or `Dictionary`, Swift uses `isUniquelyReferencedNonObjC` internal runtime calls. When a collection mutation is requested, Swift checks if its internal buffer has a reference count of exactly 1. If greater than 1 (because `copyArray` shares `originalArray`'s buffer), Swift allocates a fresh heap array and copies all elements before mutating.

**Key Takeaway / Safe Pattern**:
Always use explicit capture lists `[weak self]` or `[unowned self]` in closures to break strong retain cycles. When handling large collections, avoid unintended buffer sharing before mutations.

```swift
class NetworkManagerSafe {
    var onDataReceived: ((Data) -> Void)?
    var buffer: Data = Data()

    func setupHandler() {
        // SAFE: Capture self weakly to prevent retain cycle
        onDataReceived = { [weak self] data in
            guard let self = self else { return }
            self.buffer.append(data)
            print("Received \(data.count) bytes safely")
        }
    }

    deinit {
        print("NetworkManagerSafe deallocated cleanly!") // Successfully called!
    }
}
```
