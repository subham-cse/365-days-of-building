# Day 029: Optional Chaining Side Effects and Struct Copy-on-Write Custom Triggers
**Language / Domain**: Swift

**The Core Concept / "Did You Know?"**:
In Swift, **Optional Chaining** (`object?.method()`) short-circuits evaluation. If the optional reference evaluates to `nil`, the entire chain stops immediately and returns `nil`. However, if optional chaining is used on the left-hand side of an assignment (`object?.property = computeValue()`), the function on the right-hand side (`computeValue()`) is **still evaluated**, executing side effects even if `object` was `nil`!

Additionally, custom structs implementing manual Copy-on-Write (CoW) must explicitly check `isUniquelyReferenced(&ref)` before mutating internal heap storage; omitting this check causes silent shared-state mutations across value-type copies.

**The Code Snippet**:
```swift
import Foundation

class Player {
    var score: Int = 0
}

func computeNewScore() -> Int {
    print("SIDE EFFECT: Expensive score calculation performed!")
    return 100
}

func optionalChainingSideEffectTrap() {
    var player: Player? = nil

    // TRAP: Assignment via optional chaining
    // `player` is nil! Will `computeNewScore()` run?
    player?.score = computeNewScore()
    
    // Output: "SIDE EFFECT: Expensive score calculation performed!"
    // The side effect executed despite player being nil!
}

// Custom Copy-on-Write Struct Implementation Trap
final class StorageBuffer {
    var data: [Int] = []
}

struct CustomDataBuffer {
    private var storage = StorageBuffer()

    var values: [Int] {
        get { storage.data }
        set {
            // BUG: Fails to check isUniquelyReferenced!
            // Mutating shares heap storage across copied struct instances!
            storage.data = newValue
        }
    }
}

optionalChainingSideEffectTrap();
```

**Under the Hood / Why It Happens**:
In Swift AST compilation rules, when evaluating assignment expressions `A?.B = C`, the compiler evaluates operand `C` before attempting the member assignment to `A?.B`. Even though the assignment to `B` is short-circuited because `A` is `nil`, the expression `C` is evaluated during statement execution, triggering any embedded side-effects or network calls.

For value types using reference backing buffers, Swift's Automatic Reference Counting (ARC) does not duplicate heap instances automatically unless told to. To implement true Copy-on-Write for custom wrapper structs, developers must invoke Swift's runtime function `isUniquelyReferenced(&objectRef)`. If `isUniquelyReferenced` returns `false` (meaning ARC retain count > 1), a fresh duplicate instance of the backing class must be allocated before mutation.

**Key Takeaway / Safe Pattern**:
Avoid placing side-effecting function calls directly on the right-hand side of optional chaining assignments. Wrap assignments inside explicit `if let` or `guard let` unwrapping blocks. Implement `isUniquelyReferenced` for custom value CoW types.

```swift
// SAFE: Explicit unwrapping avoids unnecessary side effects
func safeOptionalAssignment(player: Player?) {
    guard let player = player else { return }
    // Only executed if player is non-nil!
    player.score = computeNewScore()
}

// SAFE: Custom Copy-on-Write using isUniquelyReferenced
struct CustomDataBufferSafe {
    private var storage = StorageBuffer()

    mutating func append(_ value: Int) {
        if !isUniquelyReferenced(&storage) {
            // Copy underlying storage buffer when reference count > 1
            let newStorage = StorageBuffer()
            newStorage.data = storage.data
            storage = newStorage
        }
        storage.data.append(value)
    }
}
```
