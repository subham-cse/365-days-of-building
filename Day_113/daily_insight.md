# Day 113: ARC Retain Cycles and Escaping Closure Captures
- **Language / Domain**: Swift
- **The Core Concept / "Did You Know?"**: Swift manages memory using **Automatic Reference Counting (ARC)**. While ARC frees developers from manual memory deallocation, strong reference cycles between class instances—or between a class instance and an escaping closure—will prevent memory from ever being freed, causing severe memory leaks.

When an escaping closure stored as a class property references `self` without an explicit capture list (`[weak self]` or `[unowned self]`), a strong reference cycle is established.

- **The Code Snippet**:
```swift
import Foundation

class NetworkManager {
    var onDataReceived: ((String) -> Void)?
    var status: String = "Idle"

    func setupHandlerBuggy() {
        // LEAK BUG: Strong capture of self inside escaping closure
        onDataReceived = { data in
            self.status = "Processed: \(data)"
        }
    }

    func setupHandlerSafe() {
        // SAFE PATTERN: Weak capture breaks retain cycle
        onDataReceived = { [weak self] data in
            guard let self = self else { return }
            self.status = "Processed: \(data)"
        }
    }

    deinit {
        print("NetworkManager deallocated from RAM!")
    }
}

func testLeak() {
    print("--- Testing Leak ---")
    let manager = NetworkManager()
    manager.setupHandlerBuggy()
    // manager goes out of scope, but deinit is NEVER called because onDataReceived closure holds strong ref to self!
}

func testSafe() {
    print("--- Testing Safe ---")
    let manager = NetworkManager()
    manager.setupHandlerSafe()
    // manager goes out of scope and deinit IS called!
}

testLeak()
testSafe()
```

- **Under the Hood / Why It Happens**:
Every reference object in Swift contains an inline 64-bit reference count header. 

In `setupHandlerBuggy()`, `self` holds a strong reference pointer to `onDataReceived` (a heap-allocated block object). Simultaneously, the closure heap block copies `self`'s reference pointer into its payload context with a strong reference increment (`swift_retain`). Because both reference counts never drop to `0`, neither object can be deallocated by ARC.

- **Key Takeaway / Safe Pattern**:
Always use `[weak self]` inside escaping closures assigned to properties or long-lived asynchronous tasks. Use `guard let self = self else { return }` inside the closure to safely unwrap the optional weak reference.
