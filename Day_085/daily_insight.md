# Day 085: Copy-On-Write Semantics & Protocol Extensions in Swift

**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, `struct`, `enum`, `Array`, `Dictionary`, and `String` are **Value Types**. When you assign a struct or array to a new variable, conceptually a full copy of the value is created.

To avoid performance degradation when passing large arrays or strings, Swift standard library types implement **Copy-On-Write (CoW)**. The underlying memory buffer is shared between variables until one of the variables is mutated.

However, custom value types containing reference objects do NOT get CoW behavior automatically! If a `struct` contains a class reference property, assigning the struct copies only the *class pointer reference*, sharing the underlying class instance across all copies and creating unintended mutation side-effects!

**The Code Snippet**:
```swift
import Foundation

// TRAP: Struct containing Class Reference lacks automatic Copy-On-Write!
class SharedBuffer {
    var bytes: [UInt8]
    init(bytes: [UInt8]) { self.bytes = bytes }
}

struct UnsafeDataPacket {
    var buffer: SharedBuffer // Class reference inside struct!

    init(bytes: [UInt8]) {
        self.buffer = SharedBuffer(bytes: bytes)
    }
}

// SAFE PATTERN: Custom Copy-On-Write Implementation
struct SafeDataPacket {
    private var _buffer: SharedBuffer

    init(bytes: [UInt8]) {
        self._buffer = SharedBuffer(bytes: bytes)
    }

    // CoW Mutating Property
    var bytes: [UInt8] {
        get { return _buffer.bytes }
        set {
            // Check if reference is uniquely referenced by this struct instance
            if !isKnownUniquelyReferenced(&_buffer) {
                // Duplicate backing buffer before mutation!
                _buffer = SharedBuffer(bytes: newValue)
            } else {
                _buffer.bytes = newValue
            }
        }
    }
}

// Testing CoW behavior
func runCoWTest() {
    print("--- 1. Unsafe Struct Mutation (Shared Reference Trap) ---")
    var packet1 = UnsafeDataPacket(bytes: [1, 2, 3])
    let packet2 = packet1 // Value copy of struct

    packet1.buffer.bytes.append(99) // Mutating packet1
    print("Packet 1 bytes: \(packet1.buffer.bytes)") // [1, 2, 3, 99]
    print("Packet 2 bytes: \(packet2.buffer.bytes)") // [1, 2, 3, 99] -> MUTATED UNEXPECTEDLY!

    print("\n--- 2. Safe Custom CoW Mutation ---")
    var safe1 = SafeDataPacket(bytes: [10, 20, 30])
    let safe2 = safe1 // Value copy

    safe1.bytes = [10, 20, 30, 99] // CoW triggers duplicate allocation
    print("Safe 1 bytes: \(safe1.bytes)") // [10, 20, 30, 99]
    print("Safe 2 bytes: \(safe2.bytes)") // [10, 20, 30] -> ISOLATED!
}

runCoWTest()
```

**Under the Hood / Why It Happens**:
Swift value types (like `struct`) perform memberwise byte copies when assigned to new variables. If a struct field is a value primitive (`Int`, `Double`), its bytes are copied. If a struct field is a reference type (`class`), its 8-byte pointer reference address is copied, leaving both struct instances pointing to the exact same class object on the heap.

The standard library function `isKnownUniquelyReferenced(&ref)` queries ARC retain count headers directly. If the retain count is strictly `1`, Swift knows no other variable shares the reference, allowing mutations to occur in-place without memory allocation. If the retain count is $> 1$, `isKnownUniquelyReferenced` returns `false`, signaling that a deep clone of the heap reference must be performed before applying mutations.

**Key Takeaway / Safe Pattern**:
When creating custom data structures (`struct`) that encapsulate reference types (classes or raw pointers), use `isKnownUniquelyReferenced(&_reference)` inside `mutating` getters/setters to implement proper Copy-On-Write semantics.
