# Day 046: Scala Trait Linearization and Mixin Order Resolution

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Scala supports multiple inheritance via Trait mixins. To solve the classic "Diamond Problem" (where a class inherits from multiple traits sharing a common parent with conflicting implementations), Scala uses a deterministic algorithm called **Trait Linearization**.

Linearization constructs a single, flat inheritance hierarchy at compile time. The order in which traits are mixed in using `with` determines the precise evaluation order of method calls using `super`.

**The Code Snippet**:
```scala
trait Logger {
  def log(message: String): String = s"Base: $message"
}

trait TimestampLogger extends Logger {
  override def log(message: String): String = {
    super.log(s"[2026-10-07] $message")
  }
}

trait UpperCaseLogger extends Logger {
  override def log(message: String): String = {
    super.log(message.toUpperCase)
  }
}

// Order 1: TimestampLogger mixed first, UpperCaseLogger mixed second
class OutputA extends Logger with TimestampLogger with UpperCaseLogger

// Order 2: UpperCaseLogger mixed first, TimestampLogger mixed second
class OutputB extends Logger with UpperCaseLogger with TimestampLogger

object TraitLinearizationDemo {
  def main(args: Array[String]): Unit = {
    val a = new OutputA
    val b = new OutputB

    // In OutputA, UpperCaseLogger comes LAST in mixin list, so its super points to TimestampLogger
    println(a.log("hello world")) 
    // Output: Base: [2026-10-07] HELLO WORLD

    // In OutputB, TimestampLogger comes LAST in mixin list, so its super points to UpperCaseLogger
    println(b.log("hello world")) 
    // Output: Base: HELLO WORLD [2026-10-07]
  }
}
```

**Under the Hood / Why It Happens**:
Scala computes linearization right-to-left. For a declaration `class C extends B with T1 with T2`:
1. Start with class `C`.
2. Compute linearization of `T2`, remove classes already present in linearization.
3. Compute linearization of `T1`, append.
4. Compute linearization of `B`, append.
5. Append `AnyRef` and `Any`.

For `OutputA`: `OutputA` -> `UpperCaseLogger` -> `TimestampLogger` -> `Logger` -> `AnyRef` -> `Any`.

When `super.log(...)` is invoked inside `UpperCaseLogger`, Scala dispatches the call to the *next* entity in the linearized hierarchy (`TimestampLogger`), rather than `Logger` directly.

**Key Takeaway / Safe Pattern**:
When designing stackable trait modifications in Scala, remember that trait execution order flows right-to-left through the mixin list. Design mixin traits so their order independence can be maintained, or explicitly document mandatory trait stacking sequences.
