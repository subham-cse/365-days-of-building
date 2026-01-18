# Day 041: Swift Copy-on-Write Semantics for Value Types

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, standard value types like `Array`, `Dictionary`, and `Set` exhibit Copy-on-Write (CoW) semantics. Assigning a struct or array to a new variable does not immediately trigger a deep memory copy of its contents. Instead, both instances share the same underlying memory buffer until one of them is modified.

When custom structs encapsulate reference types (like heap buffers or class handles), CoW must be implemented manually using `isKnownUniquelyReferenced(_:)`. Failing to do so can result in unexpected state mutations across instance copies.

**The Code Snippet**:
```swift
import Foundation

// Custom reference buffer class
final class StorageBuffer {
    var payload: [Int]
    init(payload: [Int]) {
        self.payload = payload
    }
}

// Custom value type wrapping storage with manual Copy-on-Write
struct CustomCoWVector {
    private var storage: StorageBuffer

    init(values: [Int]) {
        self.storage = StorageBuffer(payload: values)
    }

    // Mutable accessor enforcing CoW
    private var mutatingStorage: StorageBuffer {
        mutating get {
            // Checks if storage is uniquely referenced by this struct instance
            if !isKnownUniquelyReferenced(&storage) {
                // Perform deep copy of internal heap buffer!
                storage = StorageBuffer(payload: storage.payload)
            }
            return storage
        }
    }

    var values: [Int] {
        return storage.payload
    }

    mutating func append(_ value: Int) {
        mutatingStorage.payload.append(value)
    }
}

// Usage demonstration
var vec1 = CustomCoWVector(values: [10, 20])
var vec2 = vec1 // Shared memory reference initially

print("Initial vec1:", vec1.values) // [10, 20]
print("Initial vec2:", vec2.values) // [10, 20]

vec2.append(30) // Triggers CoW copy for vec2 only!

print("After mutation vec1:", vec1.values) // [10, 20] (unaffected!)
print("After mutation vec2:", vec2.values) // [10, 20, 30]
```

**Under the Hood / Why It Happens**:
Copy-on-Write combines the performance efficiency of reference semantics (cheap initialization and assignment) with the safety guarantees of value semantics (immutability boundaries).

The Swift Runtime function `isKnownUniquelyReferenced` inspects the reference counting header of an Objective-C / Swift class instance. If the strong reference count is strictly `1`, the data structure mutates its backing buffer in place, avoiding heap allocations. If the strong count is `> 1`, indicating that other structs are sharing the backing allocation, a new buffer is allocated and populated before applying changes.

**Key Takeaway / Safe Pattern**:
When wrapping reference types inside custom value structs, implement CoW explicitly using `isKnownUniquelyReferenced(&storage)` inside mutating getters/methods. This guarantees value-type isolation without incurring performance penalties on value assignment.
