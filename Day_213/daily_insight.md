# Day 213: Swift Copy-on-Write Semantics and Custom CoW Implementation

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, `struct` types are value types, meaning they are passed by value with copy semantics. Swift standard library collections (such as `Array`, `Dictionary`, and `Set`) use **Copy-on-Write (CoW)** optimization under the hood: assigning an array to a new variable does not copy the array elements in memory until one of the variables mutates the data.

However, custom `struct` types containing reference type members (e.g. a class instance field inside a struct) **do NOT automatically get Copy-on-Write behavior**! If you copy a custom struct that contains a class instance property, both struct instances will point to the **exact same reference object** on the heap. Mutating the internal class object through one struct variable will mutate the state of the other struct variable, violating value semantics!

**The Code Snippet**:
```swift
import Foundation

// Reference storage class
class Storage {
    var buffer: [Int] = [1, 2, 3]
}

// TRAP: Custom Struct without manual Copy-on-Write logic!
struct FlawedBuffer {
    var storage = Storage() // Reference type member!

    mutating func append(_ element: Int) {
        // Shared reference modified! Violates Value Semantics!
        storage.buffer.append(element)
    }
}

// SAFE: Custom Struct with manual Copy-on-Write implementation
struct SafeCoWBuffer {
    private var storage = Storage()

    mutating func append(_ element: Int) {
        // Check if storage reference is uniquely referenced!
        if !isKnownUniquelyReferenced(&storage) {
            // Allocate a deep copy of class instance before mutating!
            let newStorage = Storage()
            newStorage.buffer = storage.buffer
            storage = newStorage
        }
        storage.buffer.append(element)
    }

    var values: [Int] {
        return storage.buffer
    }
}

// Demonstration of Violation vs Safe Behavior
var b1 = FlawedBuffer()
var b2 = b1 // Shallow copy of struct copies pointer to Storage!

b2.append(99)
print("b1 storage: \(b1.storage.buffer)") // Output: [1, 2, 3, 99] (MUTATED b1 unintentionally!)

var s1 = SafeCoWBuffer()
var s2 = s1

s2.append(99)
print("s1 values: \(s1.values)") // Output: [1, 2, 3] (Preserved value semantics!)
print("s2 values: \(s2.values)") // Output: [1, 2, 3, 99]
```

**Under the Hood / Why It Happens**:
When Swift copies a `struct` on the stack:

1. It performs a bitwise copy (`memcpy`) of all instance properties.
2. For reference fields (`class` pointers), it copies the memory address and increments the ARC reference count of the target class instance.
3. Therefore, `b1` and `b2` hold identical pointer addresses pointing to the same `Storage` instance on the heap.
4. `isKnownUniquelyReferenced(&storage)` is a Swift runtime intrinsic that checks if the reference count of an object is exactly 1. If refcount > 1, another struct variable holds a copy, signaling that a deep copy is necessary before applying mutations.

**Key Takeaway / Safe Pattern**:
When creating custom value types in Swift that hold reference members (like class buffers or native pointers), implement custom Copy-on-Write using `isKnownUniquelyReferenced(&ref)` before mutating shared underlying reference properties.

```swift
// Safe Pattern: Standard CoW Mutation Guard
mutating func mutateStorage() {
    if !isKnownUniquelyReferenced(&storage) {
        storage = storage.copy() // Deep clone reference object
    }
    // Perform mutation on unique reference instance safely
}
```
