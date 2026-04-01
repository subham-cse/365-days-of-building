# Day 130: Scala Trait Linearization & Method Resolution Order

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Scala supports multiple inheritance through traits. When a class extends multiple traits that share a common supertype or override the same method, Scala avoids the classic C++ "Diamond Problem" through a deterministic algorithm called **Trait Linearization**.

Unlike standard left-to-right inheritance resolution, Scala evaluates traits from **right to left** when resolving `super` calls! This means that in `class D extends A with B with C`, calling `super.method()` inside `C` does NOT call `A`—it calls `B`. Understanding linearization order is essential for correctly designing mixin compositions and stackable modifications.

**The Code Snippet**:
```scala
trait Base {
  def message: String = "Base"
}

trait Logger extends Base {
  override def message: String = s"Logger -> ${super.message}"
}

trait Timestamp extends Base {
  override def message: String = s"Timestamp -> ${super.message}"
}

trait Encryptor extends Base {
  override def message: String = s"Encryptor -> ${super.message}"
}

// Right-to-left mixin evaluation order
class ServicePipeline extends Base with Logger with Timestamp with Encryptor

object LinearizationDemo extends App {
  val pipeline = new ServicePipeline
  println(pipeline.message)
  // Output: Encryptor -> Timestamp -> Logger -> Base
}
```

**Under the Hood / Why It Happens**:
Scala constructs a single linear inheritance hierarchy for any class definition using the following linearization rules:
1. Start with the class type itself as the first element.
2. Expand the linearizations of all traits in `with` clauses from **right to left**.
3. Append the direct superclass linearization.
4. Remove duplicate traits, keeping only the **last** occurrence of each trait in the list.
5. Append `AnyRef` and `Any`.

For `ServicePipeline`:
- Linearization of `Encryptor`: `Encryptor -> Base`
- Linearization of `Timestamp`: `Timestamp -> Base`
- Linearization of `Logger`: `Logger -> Base`
- Un-deduplicated list: `ServicePipeline, Encryptor, Base, Timestamp, Base, Logger, Base`
- After deduplication (keeping last instance): `ServicePipeline -> Encryptor -> Timestamp -> Logger -> Base`

When `super` is invoked inside `Encryptor`, Scala looks up the *next* entry in the linearized sequence (`Timestamp`), enabling dynamic stackable trait modifications.

**Key Takeaway / Safe Pattern**:
Order mixin traits carefully: traits listed further to the right in `extends ... with T1 with T2` take precedence and wrap calls to traits on their left. Design stackable traits so that `super` invocations match your intended processing pipeline.
