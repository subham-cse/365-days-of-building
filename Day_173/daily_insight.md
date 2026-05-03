# Day 173: Const Constructors, Object Canonicalization, and Identity vs Equality

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
In Dart, marking an object instance with the `const` keyword instantiates it as a compile-time constant. When an object is constructed with `const`, Dart performs **canonicalization**: it creates exactly *one* instance of that object in memory and reuses that identical instance everywhere across the application runtime whenever the same constant parameters are passed.

This leads to a unique behavior: two completely separate `const` object instantiation sites evaluating identical parameters point to the exact same object in memory, satisfying both structural equality (`==`) and object identity (`identical()`).

**The Code Snippet**:

```dart
class Point {
  final int x;
  final int y;

  // Const constructor creates compile-time canonicalized instances
  const Point(this.x, this.y);
}

class NonConstPoint {
  final int x;
  final int y;

  NonConstPoint(this.x, this.y);
}

void main() {
  // 1. Const Instances (Canonicalized)
  const p1 = Point(10, 20);
  const p2 = Point(10, 20);

  print('Const Equality (p1 == p2): ${p1 == p2}');           // true
  print('Const Identity (identical(p1, p2)): ${identical(p1, p2)}'); // true (SAME MEMORY ADDRESS!)

  // 2. Non-Const Instances
  final p3 = NonConstPoint(10, 20);
  final p4 = NonConstPoint(10, 20);

  print('Non-Const Identity (identical(p3, p4)): ${identical(p3, p4)}'); // false (Different Heap Allocations)

  // 3. Dynamic runtime values CANNOT be marked const
  int dynamicX = int.parse('10');
  // const p5 = Point(dynamicX, 20); // COMPILER ERROR: Arguments to a constant creation must be constant values!
  final p6 = Point(dynamicX, 20);
  print('Runtime Const Constructor (identical(p1, p6)): ${identical(p1, p6)}'); // false
}
```

**Under the Hood / Why It Happens**:
During compilation (AOT or JIT frontend compilation), the Dart compiler inspects all `const` expressions and builds a global constant table.

When the compiler encounters `const Point(10, 20)`:
1. It computes a hash of the constructor type and its constant arguments.
2. If an entry already exists in the constant table, the compiler replaces the allocation instruction with a direct reference to the existing constant object header in memory.
3. In Flutter, using `const Widgets` relies on this exact mechanism to skip widget subtree rebuilds and garbage collection passes during frame rendering.

**Key Takeaway / Safe Pattern**:
Always mark classes immutable (`@immutable`) and use `const` constructors wherever possible in Flutter and Dart applications. Using `const` minimizes heap allocations, eliminates GC churn, and enables rapid object identity checks (`identical()`).
