# Day 102: Trait Linearization Order and Diamond Inheritance Resolution
- **Language / Domain**: Scala
- **The Core Concept / "Did You Know?"**: Scala resolves multiple inheritance diamond problems using **Trait Linearization**. Unlike languages like C++ (which require explicit virtual inheritance or scope resolution), Scala constructs a single flat linear hierarchy for any class mixing in multiple traits.

The order in which traits are mixed into a class (`class A extends B with C with D`) determines the exact order of `super` call invocation: Scala linearizes traits from **right to left**, meaning method execution under `super` actually flows from right to left in the `with` clause list!

- **The Code Snippet**:
```scala
trait Logger {
  def log(msg: String): String = s"Log: $msg"
}

trait TimestampLogger extends Logger {
  override def log(msg: String): String = super.log(s"[${System.currentTimeMillis()}] $msg")
}

trait EncryptedLogger extends Logger {
  override def log(msg: String): String = super.log(s"ENCRYPTED($msg)")
}

// Order 1: TimestampLogger then EncryptedLogger
class ServiceA extends Logger with TimestampLogger with EncryptedLogger

// Order 2: EncryptedLogger then TimestampLogger
class ServiceB extends Logger with EncryptedLogger with TimestampLogger

object Main extends App {
  val a = new ServiceA
  val b = new ServiceB

  println("ServiceA: " + a.log("hello"))
  // Output: Log: [1690000000] ENCRYPTED(hello)

  println("ServiceB: " + b.log("hello"))
  // Output: Log: ENCRYPTED([1690000000] hello)
}
```

- **Under the Hood / Why It Happens**:
The Scala compiler constructs a linearized precedence list for class `ServiceA`:
`ServiceA -> EncryptedLogger -> TimestampLogger -> Logger -> AnyRef -> Any`

When `a.log("hello")` is invoked, `EncryptedLogger.log` executes first. Its `super.log` call points to the next class in the *linearized list* (`TimestampLogger`), NOT its direct structural superclass `Logger`. This allows stackable modifications where traits decorate behavioral layers cleanly.

- **Key Takeaway / Safe Pattern**:
Be explicit and conscious of trait order when stacking behavior modifications in Scala. Place core foundational traits first and stack modifying/decorating traits to the right so that `super` chains process leftwards as intended.
