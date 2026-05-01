# Day 169: Copy-on-Write Semantics for Custom Value Types

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, basic value types like `Array`, `Dictionary`, and `String` feature **Copy-on-Write (CoW)** optimizations built into the standard library. Assigning an array to another variable does not immediately copy all underlying elements in memory; both variables share the same memory buffer until one of them is modified.

However, custom `struct` definitions in Swift do *not* automatically get Copy-on-Write behavior for internal reference components! If your custom `struct` encapsulates a reference type (like a class or heap buffer), assigning or copying the struct duplicates only the reference pointer, creating shared mutable state between struct instances unless CoW is manually implemented.

**The Code Snippet**:

```swift
import Foundation

// A reference type wrapping an underlying heap buffer
final class StorageBuffer {
    var rawData: [Int]
    init(data: [Int]) { self.rawData = data }
    
    func copy() -> StorageBuffer {
        return StorageBuffer(data: self.rawData)
    }
}

// Custom Struct implementing Manual Copy-On-Write (CoW)
struct CowVector {
    private var buffer: StorageBuffer

    init(elements: [Int]) {
        self.buffer = StorageBuffer(data: elements)
    }

    var values: [Int] {
        return buffer.rawData
    }

    // Explicit CoW Mutating Check
    mutating func append(_ element: Int) {
        // isKnownUniquelyReferenced checks if reference count is exactly 1
        if !isKnownUniquelyReferenced(&buffer) {
            print("Buffer is shared! Performing real heap copy...")
            buffer = buffer.copy() // Clone buffer before mutating
        } else {
            print("Buffer is unique! Mutating inline without memory copy...")
        }
        buffer.rawData.append(element)
    }
}

// Execution
var vec1 = CowVector(elements: [1, 2, 3])
var vec2 = vec1 // Copy-on-Write: Buffer reference is shared initially!

print("Appending to vec1:")
vec1.append(4) // Trigger CoW duplicate because reference count was 2

print("Appending to vec1 again:")
vec1.append(5) // Mutates inline because reference count is now uniquely 1!

print("vec1: \(vec1.values)") // [1, 2, 3, 4, 5]
print("vec2: \(vec2.values)") // [1, 2, 3] (Independent value semantics maintained!)
```

**Under the Hood / Why It Happens**:
Swift uses Automatic Reference Counting (ARC) for class objects. `isKnownUniquelyReferenced(&ref)` is a built-in standard library function that inspects the ARC strong reference count header of an object instance inline.

If `isKnownUniquelyReferenced` returns `true`, the struct instance knows it holds the sole reference to the heap object, so mutating internal data inline is completely safe and fast. If it returns `false`, another struct variable shares the reference, so a deep copy of the class buffer must be allocated before performing mutations.

**Key Takeaway / Safe Pattern**:
When designing custom Swift structs that wrap reference-type resources (such as raw memory buffers, C handles, or classes), always implement manual Copy-on-Write using `isKnownUniquelyReferenced` in `mutating` methods to maintain value semantics while preserving optimal memory performance.
