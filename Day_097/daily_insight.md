# Day 097: Copy-on-Write Semantics and Struct Mutation Traps
- **Language / Domain**: Swift
- **The Core Concept / "Did You Know?"**: Swift collections (`Array`, `Dictionary`, `Set`) are value types that use **Copy-on-Write (COW)** optimization. Copying a collection is cheap because memory is shared until a modification occurs. 

However, if you implement custom value types holding reference type wrappers (or large raw buffers) without manually implementing Copy-on-Write using `isKnownUniquelyReferenced`, modifying copies of your struct will unexpectedly mutate shared reference state across independent instances!

- **The Code Snippet**:
```swift
import Foundation

final class StorageBuffer {
    var values: [Int]
    init(values: [Int]) { self.values = values }
}

// Custom Struct with copy-on-write logic built manually
struct SmartVector {
    private var buffer: StorageBuffer

    init(values: [Int] = []) {
        self.buffer = StorageBuffer(values: values)
    }

    var values: [Int] {
        get { buffer.values }
        set {
            // Check if reference is uniquely referenced by this struct instance
            if !isKnownUniquelyReferenced(&buffer) {
                // Perform a deep copy (Copy-on-Write) before mutating!
                buffer = StorageBuffer(values: newValue)
            } else {
                buffer.values = newValue
            }
        }
    }

    mutating func append(_ element: Int) {
        var temp = values
        temp.append(element)
        self.values = temp
    }
}

var vec1 = SmartVector(values: [1, 2, 3])
var vec2 = vec1 // Shares reference underlying buffer

vec2.append(4) // Triggers COW, mutating only vec2!

print("vec1:", vec1.values) // [1, 2, 3]
print("vec2:", vec2.values) // [1, 2, 3, 4]
```

- **Under the Hood / Why It Happens**:
Swift's runtime provides `isKnownUniquelyReferenced(_:)`, which checks the ARC reference count of a class instance directly in memory. If the reference count is exactly `1`, the instance is guaranteed to be owned uniquely by the calling struct. 

Without this check, multiple struct instances sharing a reference object will perform mutations directly on the shared pointer reference, turning value types into leaking reference mutations.

- **Key Takeaway / Safe Pattern**:
When wrapping reference types (`AnyObject`, C pointers, or helper classes) inside custom Swift `struct` types, always guard mutations with `isKnownUniquelyReferenced(&ref)` to guarantee strict value semantics without sacrificing copy efficiency.
