# Day 197: Swift ARC Retain Cycles in Closures and `[weak self]`

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
Swift uses **Automatic Reference Counting (ARC)** to manage heap memory for reference types (`class` instances). Unlike a garbage collector that periodically cleans unreferenced memory, ARC instantly deallocates a class instance when its strong reference count drops to zero.

However, ARC cannot resolve **strong reference cycles** (retain cycles). A retain cycle occurs when two class instances hold strong references to each other, or when a class instance holds a strong reference to a closure that implicitly or explicitly captures `self` strongly. When a retain cycle occurs, memory is permanently leaked because neither reference count can ever reach zero.

**The Code Snippet**:
```swift
import Foundation

class NetworkManager {
    var onDataReceived: ((String) -> Void)?
    var name: String = "MainManager"

    func fetchData() {
        // TRAP: Closure implicitly captures 'self' strongly!
        onDataReceived = { data in
            // Strong reference to 'self.name' keeps NetworkManager alive
            print("Manager '\(self.name)' received payload: \(data)")
        }
    }

    deinit {
        print("NetworkManager deallocated from RAM")
    }
}

func executeRequest() {
    let manager = NetworkManager()
    manager.fetchData()
    // 'manager' goes out of scope here... 
    // EXPECTATION: NetworkManager deallocates.
    // REALITY: Retain cycle! 'manager' retains closure, closure retains 'manager'.
}

executeRequest() // 'NetworkManager deallocated from RAM' is NEVER printed! Leaked memory!
```

**Under the Hood / Why It Happens**:
In Swift, reference-counted instances store a header containing an `inline_rc` integer tracking strong references.

When `manager.fetchData()` assigns the closure to `onDataReceived`:
1. `NetworkManager` instance holds a strong reference to the closure object via property `onDataReceived`.
2. The closure is a reference type allocated on the heap containing a context context payload capturing `self` (`NetworkManager`). This increments `NetworkManager`'s strong reference count by 1.
3. When `executeRequest()` returns, local variable `manager` leaves stack scope, decrementing strong ref count from 2 to 1.
4. Because the strong reference count remains at 1, `deinit` is never invoked, and the memory remains unreachable on the heap indefinitely.

**Key Takeaway / Safe Pattern**:
Use capture lists `[weak self]` or `[unowned self]` in closures to prevent strong reference cycles. `[weak self]` turns the captured reference into an optional `Self?`, breaking the cycle and allowing ARC to deallocate the object cleanly.

```swift
// Safe Pattern: Explicit capture list with [weak self]
func fetchDataSafe() {
    onDataReceived = { [weak self] data in
        guard let self = self else { return }
        print("Manager '\(self.name)' received payload: \(data)")
    }
}
```
