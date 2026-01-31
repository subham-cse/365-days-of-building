# Day 061: Dart Const Constructors and Canonicalized Instances

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart allows developers to declare `const` constructors for classes whose fields are all `final`. Using the `const` keyword when instantiating objects triggers **Instance Canonicalization** at compile time.

Instead of allocating distinct heap objects every time a constructor is invoked, Dart's compiler creates a single immutable instance per unique set of constructor arguments and reuses that instance globally across the application lifetime.

**The Code Snippet**:
```dart
class ConfigurationPoint {
  final int x;
  final int y;

  // Const constructor requires all fields to be final
  const ConfigurationPoint(this.x, this.y);
}

void main() {
  // Non-const instantiation (allocates new heap instances)
  var point1 = ConfigurationPoint(10, 20);
  var point2 = ConfigurationPoint(10, 20);

  // Const instantiation (Canonicalized at compile time)
  var constPoint1 = const ConfigurationPoint(10, 20);
  var constPoint2 = const ConfigurationPoint(10, 20);
  var constPoint3 = const ConfigurationPoint(30, 40);

  print('--- Non-const Reference Equality (identical) ---');
  print('identical(point1, point2): ${identical(point1, point2)}'); // false

  print('\n--- Const Reference Equality (identical) ---');
  print('identical(constPoint1, constPoint2): ${identical(constPoint1, constPoint2)}'); // true!
  print('identical(constPoint1, constPoint3): ${identical(constPoint1, constPoint3)}'); // false (different values)
}
```

**Under the Hood / Why It Happens**:
During compile-time phase parsing (in both Dart AOT compiler and dart2js web compiler), Dart builds a canonical constant table of all `const` expression invocations.

When the compiler encounters `const ConfigurationPoint(10, 20)`:
1. It hashes the type (`ConfigurationPoint`) and the constant constructor argument values (`10, 20`).
2. If an identical constant hash already exists in the global constant pool table, the compiler replaces the creation site with a direct reference to the pre-existing pool object.

In Flutter apps, using `const Widgets` prevents Flutter's framework from rebuilding child widget subtrees during layout updates, yielding significant rendering performance gains.

**Key Takeaway / Safe Pattern**:
Mark immutable data objects and Flutter UI widgets with `const` constructors whenever their values are known at compile time. Prefer prefixing widget instantiations with `const` to minimize Garbage Collection churn and eliminate unnecessary UI redraw passes.
