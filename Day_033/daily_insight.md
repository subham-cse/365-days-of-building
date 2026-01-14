# Day 033: Null Safety Flow Analysis and Late-Bound Field Promotion
**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart features Sound Null Safety. The Dart compiler uses **Flow Analysis** to automatically promote nullable variables (`String?`) to non-nullable types (`String`) inside conditional check blocks (`if (variable != null)`).

However, Dart's flow analysis **only promotes local variables**. It cannot promote class fields or property getters. Because a class property getter could theoretically return different values on consecutive invocations or be overridden by a subclass, Dart forces developers to explicitly unwrap or copy class fields before calling non-null methods.

**The Code Snippet**:
```dart
class UserProfile {
  String? title; // Class Field

  void updateTitleUnsafe() {
    if (title != null) {
      // COMPILE ERROR: The property 'title' cannot be unconditionally accessed 
      // because it can be null! Flow analysis does NOT promote class fields!
      // print(title.toUpperCase()); 
    }
  }
}

class Parent {
  String? _name;
  
  // Custom getter could return non-deterministic values across reads!
  String? get name => _name; 
}

void demonstrateLocalPromotion() {
  String? localName = "Alice"; // Local Variable

  if (localName != null) {
    // Flow analysis WORKS for local variables! Promoted to non-nullable String!
    print(localName.toUpperCase()); // SAFE!
  }
}

void main() {
  demonstrateLocalPromotion();
}
```

**Under the Hood / Why It Happens**:
Dart's type system analyzer (`analyzer` package) performs Control Flow Graph (CFG) analysis. When analyzing a local variable inside an `if (x != null)` block, Dart proves that no other code execution path can mutate `x` between the check and its usage within that stack frame.

For class fields, Dart cannot guarantee variable immutability across expressions. A getter method can execute arbitrary code on every invocation:
```dart
int _count = 0;
String? get name => (_count++ % 2 == 0) ? "Alice" : null;
```
If flow analysis promoted `name` based on an `if (name != null)` check, a subsequent read of `name.toUpperCase()` within the body would invoke the getter a second time, receiving `null` and crashing with a null pointer exception!

**Key Takeaway / Safe Pattern**:
To perform type promotion on class fields, copy the field into an immutable local variable (`final title = this.title`), or use local shadow variables, patterns (Dart 3+ object pattern matching), or the null-aware operator (`?.let` / `title?.toUpperCase()`).

```dart
class UserProfileSafe {
  String? title;

  void updateTitleSafe() {
    // SAFE Pattern 1: Capture in local variable
    final currentTitle = title;
    if (currentTitle != null) {
      print(currentTitle.toUpperCase()); // Flow analysis promotes currentTitle to String!
    }

    // SAFE Pattern 2: Dart 3 Object Pattern Matching
    if (title case final newTitle?) {
      print(newTitle.toUpperCase()); // Promoted!
    }

    // SAFE Pattern 3: Null-aware call
    print(title?.toUpperCase());
  }
}
```
