# Day 225: Swift Copy-on-Write (COW) Custom Implementation & Reference Escapes

**Language / Domain**: Swift / ARC & Memory Optimization

**The Core Concept / "Did You Know?"**:
In Swift, collection types such as `Array`, `Dictionary`, and `Set` are value types that exhibit **Copy-on-Write (COW)** optimization. Passing or assigning collections copies cheap structural descriptors without duplicating underlying heap storage. Allocation of a separate underlying buffer occurs only when a instance is modified **and** its underlying buffer reference is shared across multiple variables.

However, Swift does *not* automatically synthesize Copy-on-Write for custom value structs wrapping heap allocations! If you build a custom value struct around a class instance holding data, modifying one copy will silently mutate all other copies unless you explicitly implement COW using `isKnownUniquelyReferenced`.

**The Code Snippet**:
```swift
import Foundation

// Internal heap storage class
final class StorageBuffer {
    var bytes: [UInt8]

    init(bytes: [UInt8]) {
        self.bytes = bytes
    }
}

// Custom Value Type Struct
struct CoWDataBuffer {
    private var storage: StorageBuffer

    init(bytes: [UInt8] = []) {
        self.storage = StorageBuffer(bytes: bytes)
    }

    var bytes: [UInt8] {
        return storage.bytes
    }

    // Explicit Copy-on-Write Mutating Method
    mutating func append(_ byte: UInt8) {
        // Check if underlying ARC reference count is strictly 1
        if !isKnownUniquelyReferenced(&storage) {
            print("Reference is shared! Performing deep copy of StorageBuffer...")
            storage = StorageBuffer(bytes: storage.bytes)
        } else {
            print("Reference is uniquely owned. Mutating in-place!")
        }
        storage.bytes.append(byte)
    }
}

// Execution Demonstration
var original = CoWDataBuffer(bytes: [0x01, 0x02])
var copy = original // Value assignment copies struct pointer, retain count of StorageBuffer becomes 2

print("--- Mutating copy ---")
copy.append(0x03) // Triggers deep copy because storage is shared!

print("--- Mutating original ---")
original.append(0x04) // Retain count is now 1, mutates in-place!

print("Original Bytes: \(original.bytes)") // Output: [1, 2, 4]
print("Copy Bytes:     \(copy.bytes)")     // Output: [1, 2, 3]
```

**Under the Hood / Why It Happens**:
1. `isKnownUniquelyReferenced(&object)` checks ARC runtime refcounts:
   - It takes an `inout` reference parameter to a Swift class instance.
   - It returns `true` if and only if the strong reference count of the object is exactly 1 (meaning no other variables or data structures share this heap object).

2. **The Reference Escape Trap**:
   If you accidentally expose the internal reference type via a getter or capture it inside a closure:
   ```swift
   var buffer = CoWDataBuffer(bytes: [1, 2])
   let leakedRef = buffer.internalStorage // Retain count increases to 2!
   buffer.append(3) // isKnownUniquelyReferenced fails, triggering unnecessary allocation!
   ```
   Even if `buffer` is structurally the sole struct instance in scope, `isKnownUniquelyReferenced` evaluates to `false` because `leakedRef` holds a strong ARC pointer to the storage object.

**Key Takeaway / Safe Pattern**:
- Implement explicit COW for custom value types encapsulating reference types (`class`, unmanaged memory pointers) using `isKnownUniquelyReferenced(&storage)`.
- Keep internal reference properties strictly `private` to prevent retain count escapes.
- Call `isKnownUniquelyReferenced` directly inside `mutating` methods prior to performing destructive memory updates.
