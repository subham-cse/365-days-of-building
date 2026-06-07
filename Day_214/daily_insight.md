# Day 214: Scala Trait Linearization & The Diamond Problem Resolution

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
In object-oriented languages with multiple inheritance or mixin traits, the "diamond problem" occurs when a class inherits from two traits that both override a method from a shared base trait. Unlike C++ (which requires explicit virtual inheritance or scope resolution) or Java (which forces interface default method disambiguation), Scala resolves diamond conflicts deterministically using **Trait Linearization**.

Linearization constructs a single, linear hierarchy for any class by reading inheritance declarations from right to left, placing mixins after their superclasses while ensuring each type appears exactly once. This means `super` in Scala does not refer to the textual base class in the source code; instead, it dynamically targets the next trait in the linearized hierarchy chain.

**The Code Snippet**:
```scala
trait Logger {
  def log(msg: String): String = s"[Base] $msg"
}

trait TimestampLogger extends Logger {
  override def log(msg: String): String = super.log(s"[10:00] $msg")
}

trait ShortLogger extends Logger {
  override def log(msg: String): String = {
    val shortened = if (msg.length > 15) msg.take(15) + "..." else msg
    super.log(shortened)
  }
}

// Order 1: TimestampLogger mixed in first, ShortLogger second
class ServiceA extends Logger with TimestampLogger with ShortLogger

// Order 2: ShortLogger mixed in first, TimestampLogger second
class ServiceB extends Logger with ShortLogger with TimestampLogger

object Main extends App {
  val a = new ServiceA
  println(a.log("Very Long System Diagnostic Payload"))
  // Output: [Base] [10:00] Very Long System...

  val b = new ServiceB
  println(b.log("Very Long System Diagnostic Payload"))
  // Output: [Base] Very Long S...
}
```

**Under the Hood / Why It Happens**:
The Scala compiler constructs the linear hierarchy by evaluating the declaration `class C extends B with T1 with T2` using the following algorithm:
`Lin(C) = C :: Lin(T2) +: Lin(T1) +: Lin(B)`
where `+:` appends elements while removing duplicates from the left (keeping only the last occurrence).

For `ServiceA` (`class ServiceA extends Logger with TimestampLogger with ShortLogger`):
1. `Lin(Logger) = Logger :: AnyRef :: Any`
2. `Lin(TimestampLogger) = TimestampLogger :: Logger :: AnyRef :: Any`
3. `Lin(ShortLogger) = ShortLogger :: Logger :: AnyRef :: Any`
4. Computing `Lin(ServiceA)`:
   - Start with `ServiceA`
   - Prepend `Lin(ShortLogger)`: `ServiceA -> ShortLogger -> Logger -> AnyRef -> Any`
   - Interleave `Lin(TimestampLogger)` removing existing duplicates: `ServiceA -> ShortLogger -> TimestampLogger -> Logger -> AnyRef -> Any`

When `a.log(...)` is invoked on `ServiceA`, execution flows through `ShortLogger.log`, which calls `super.log(...)`. Rather than calling `Logger.log`, `super` evaluates to the next trait in `ServiceA`'s linearization list—which is `TimestampLogger.log`. `TimestampLogger.log` in turn calls its `super`, which evaluates to `Logger.log`.

In `ServiceB`, the linearized order flips to:
`ServiceB -> TimestampLogger -> ShortLogger -> Logger -> AnyRef -> Any`
Here, `TimestampLogger` formats the timestamp first, and then passes the formatted payload into `ShortLogger`, which truncates the timestamped message.

**Key Takeaway / Safe Pattern**:
Scala trait mixins act as stackable modifications. Because `super` is bound to the linearized neighbor rather than a static parent class, trait stack order dictates evaluation flow. When designing mixins with side effects or transformation pipelines:
- Design traits to be stateless and orthogonal whenever possible.
- Clearly document expected stackable ordering for user-facing API mixins.
- Be aware that reordering `with TraitA with TraitB` alters execution order of overridden methods without triggering compiler errors.
