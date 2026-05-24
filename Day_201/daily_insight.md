# Day 201: Dart Const Constructors and Canonicalized Instance Sharing

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
In Dart, marking a constructor as `const` creates **compile-time constant objects**. When you instantiate an object using `const MyClass(...)`, Dart canonicalizes the object instance in memory. 

This means that no matter how many times or in how many different files you evaluate `const MyClass("fixed_val")`, Dart allocates the object **exactly once** in memory at compile time and reuses that identical instance across the entire application runtime. However, if you omit the `const` keyword during instantiation (`MyClass("fixed_val")`), Dart allocates a fresh object on the heap every single time, missing Flutter frame optimization opportunities and increasing memory allocations.

**The Code Snippet**:
```dart
class Configuration {
  final String apiUrl;
  final int timeoutSeconds;

  // Const constructor requires all fields to be final
  const Configuration({
    required this.apiUrl,
    this.timeoutSeconds = 30,
  });
}

void main() {
  // Instantiated with 'const'
  const config1 = Configuration(apiUrl: "https://api.example.com");
  const config2 = Configuration(apiUrl: "https://api.example.com");

  // Instantiated WITHOUT 'const' (standard runtime allocation)
  final config3 = Configuration(apiUrl: "https://api.example.com");

  // Reference equality check (identical memory addresses)
  print('config1 == config2: ${identical(config1, config2)}'); // true! (Canonicalized)
  print('config1 == config3: ${identical(config1, config3)}'); // false! (Different heap objects)
}
```

**Under the Hood / Why It Happens**:
During compilation, the Dart C++ frontend compiler (`front_end`) builds a constant table (canonical object store).

When the compiler encounters `const Configuration(...)`:
1. It evaluates the constructor arguments statically.
2. It hashes the object's class type and immutable constructor arguments.
3. It checks the global compile-time constant table. If an identical entry exists, it replaces the AST instantiation node with a direct memory pointer to the canonical entry.
4. If no entry exists, it writes the object into the constant pool embedded directly in the snapshot binary.

Because the object resides in read-only snapshot memory, `identical(constA, constB)` reduces to a single CPU pointer comparison instruction. In Flutter, using `const` widgets prevents framework re-build trees from re-allocating or re-evaluating unchanged widget subtree nodes during state rebuilds.

**Key Takeaway / Safe Pattern**:
Always annotate immutable data structures and Flutter UI widgets with `const` constructors wherever parameters are known at compile time.

```dart
// Safe Pattern: Leverage const widgets and data objects in Flutter UI
Widget build(BuildContext context) {
  return const Padding(
    padding: EdgeInsets.all(16.0),
    child: Text('Canonicalized Static Label'), // Prevents widget rebuild allocations!
  );
}
```
