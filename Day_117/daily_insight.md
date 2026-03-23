# Day 117: Const Constructors and Sound Null Safety Flow Analysis
- **Language / Domain**: Dart
- **The Core Concept / "Did You Know?"**: Dart uses **Sound Null Safety**. Unlike languages with dynamic null checks, Dart's compiler guarantees that non-nullable types can *never* contain `null` at runtime.

Dart achieves this through **Flow Analysis** (type promotion). However, flow analysis cannot promote mutable instance fields of classes (e.g. `String? _name`), because the compiler cannot guarantee that another method or thread will not modify the field between the null check and its subsequent usage!

- **The Code Snippet**:
```dart
class UserProfile {
  String? name; // Mutable field

  void printNameLengthBug() {
    if (name != null) {
      // COMPILER ERROR: Property 'name' cannot be promoted to 'String'!
      // print(name.length); 
    }
  }

  void printNameLengthSafe() {
    // Safe Pattern 1: Assign to local variable (local variables promote!)
    final localName = name;
    if (localName != null) {
      print("Length: ${localName.length}"); // Promoted to String!
    }

    // Safe Pattern 2: Null-aware operator
    print("Length: ${name?.length}");
  }
}

// Const Constructors for Memory Canonicalization
class ImmutablePoint {
  final int x;
  final int y;

  const ImmutablePoint(this.x, this.y);
}

void main() {
  // Canonicalization: Shared single compile-time instance!
  const p1 = ImmutablePoint(10, 20);
  const p2 = ImmutablePoint(10, 20);

  print("p1 identical to p2: ${identical(p1, p2)}"); // true!
}
```

- **Under the Hood / Why It Happens**:
For class fields, Dart's analyzer avoids type promotion because getters can be overridden or mutated asynchronously.

For `const` constructors, the Dart compiler canonicalizes constant expressions into immutable entries inside the binary's constant pool. When Flutter widgets or Dart objects are instantiated with `const`, the VM reuses a single shared memory reference, bypassing runtime heap allocations entirely.

- **Key Takeaway / Safe Pattern**:
Always capture mutable instance fields into local variables (`final localVal = field`) before performing null checks. Mark Flutter widget constructors and data transfer objects `const` wherever possible to reduce GC churn and optimize UI repaint cycles.
