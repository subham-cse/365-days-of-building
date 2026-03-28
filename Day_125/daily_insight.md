# Day 125: Swift Copy-on-Write Semantics & Custom Struct Traps

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, Standard Library collections such as `Array`, `Dictionary`, and `Set` use Copy-on-Write (CoW) optimizations to avoid unnecessary buffer copying when passing value types around. However, creating a `struct` containing reference types (like instances of `class`) does NOT automatically grant your custom `struct` Copy-on-Write behavior!

If a custom `struct` wraps a class instance or reference type, mutating the struct's internal state through reference members alters the underlying object for **all** copies of that struct. To ensure true value semantics and avoid mutating shared reference state, developers must manually implement CoW using `isKnownUniquelyReferenced(_:)`.

**The Code Snippet**:
```swift
import Foundation

// Reference storage container
final class Storage {
    var buffer: [Int]
    init(buffer: [Int]) {
        self.buffer = buffer
    }
}

// Custom value type implementing Copy-on-Write manually
struct SafeBuffer {
    private var storage: Storage

    init(elements: [Int]) {
        self.storage = Storage(buffer: elements)
    }

    var elements: [Int] {
        return storage.buffer
    }

    mutating func append(_ element: Int) {
        // Check if storage is uniquely referenced by this struct instance
        if !isKnownUniquelyReferenced(&storage) {
            // Allocate a new copy of storage before mutation
            storage = Storage(buffer: storage.buffer)
        }
        storage.buffer.append(element)
    }
}

// Usage demonstration
var buf1 = SafeBuffer(elements: [1, 2, 3])
var buf2 = buf1 // Shallow copy of struct, sharing 'storage' reference

buf2.append(4) // Triggers CoW clone due to reference count > 1

print("buf1 elements:", buf1.elements) // [1, 2, 3]
print("buf2 elements:", buf2.elements) // [1, 2, 3, 4]
```

**Under the Hood / Why It Happens**:
Swift structs copy their member fields byte-by-byte (bitwise copy) upon assignment. When a struct contains a reference (a class pointer), the reference pointer value is copied, incrementing the retain count of the target heap object. 

Without explicit CoW checks, modifying a property on the underlying reference mutates the shared heap object directly. `isKnownUniquelyReferenced(&ref)` performs a fast internal atomic check against the ARC retain counter. If the strong reference count is strictly `1`, Swift knows no other struct instance shares this reference, permitting in-place mutation without memory allocation. If the retain count is `> 1`, a deep copy of the reference target is instantiated first.

**Key Takeaway / Safe Pattern**:
When wrapping reference types inside custom value types (`struct`), always implement Copy-on-Write explicitly via `isKnownUniquelyReferenced(&storage)` inside all mutating methods to prevent silent shared-state corruption across struct copies.
