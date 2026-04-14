# Day 145: Dart Sound Null Safety Flow Analysis & Field Promotion Limits

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart 2.12 introduced **Sound Null Safety** with type flow analysis. The Dart compiler can track null checks across control flow branches and automatically promote a nullable variable (e.g. `String?`) to a non-nullable type (`String`) without requiring explicit casts.

However, Dart's type flow analysis **refuses to promote non-final class fields**! Even if you write `if (myClass.name != null)`, accessing `myClass.name` inside the block will still trigger a type error: `Sound Null Safety: The property 'name' cannot be promoted because it is a gettable field`.

**The Code Snippet**:
```dart
class UserProfile {
  String? name; // Nullable non-final field
  final String? id; // Nullable FINAL field

  UserProfile(this.name, this.id);

  void printDetailsBuggy() {
    // FINAL field promotes automatically!
    if (id != null) {
      print("ID length: ${id.length}"); // OK: 'id' is promoted to String
    }

    // NON-FINAL field DOES NOT promote!
    if (name != null) {
      // COMPILER ERROR: The property 'name' cannot be promoted
      // print("Name length: ${name.length}");

      // UNSAFE WORKAROUND: Force bang operator !
      print("Name length bang: ${name!.length}");
    }
  }

  void printDetailsSafe() {
    // SAFE PATTERN 1: Local variable shadow binding
    final localName = name;
    if (localName != null) {
      print("Safe localName length: ${localName.length}"); // Promoted!
    }

    // SAFE PATTERN 2: Object pattern matching (Dart 3+)
    if (name case final String validName) {
      print("Dart 3 Pattern match length: ${validName.length}");
    }
  }
}

void main() {
  final user = UserProfile("Alice", "usr_100");
  user.printDetailsSafe();
}
```

**Under the Hood / Why It Happens**:
Dart's Flow Analysis engine (`flow_analysis.dart`) tracks the nullability state of local variables across execution paths.

For local variables and `final` fields:
- `final` fields and local stack variables cannot be mutated by external code after initialization.
- Once `if (localName != null)` passes, Dart's flow analyzer safely marks the variable state as `NonNull` for the remainder of the block scope.

For non-final class fields (`var name` or `String? name`):
- Non-final fields can be overridden by a subclass getter:
  ```dart
  class TrappyUser extends UserProfile {
    @override String? get name => Random().nextBool() ? "Bob" : null;
  }
  ```
- Additionally, multithreaded isolate messages or callback re-entrancy could mutate `name` between the `if (name != null)` check and the next line!
Because Dart cannot guarantee field immutability, flow analysis skips field promotion for non-final properties.

**Key Takeaway / Safe Pattern**:
Never use the `!` assertion operator on non-final class fields. Shadow non-final fields into local `final` variables (`final name = this.name`) or use Dart 3 object pattern matching (`if (name case String s)`) to ensure type promotion.
