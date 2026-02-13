# Day 074: Trait Linearization Order and Diamond Inheritance in Scala

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Scala supports multiple inheritance using **Traits**. When a class extends multiple traits that override common methods or call `super`, Scala resolves the potential "Diamond Problem" of multiple inheritance through a deterministic algorithm called **Trait Linearization**.

Unlike C++ multiple inheritance (which creates diamond duplication unless virtual base classes are used), Scala linearizes mixin traits into a flat, single-inheritance chain. However, the resulting order in which `super` references are resolved can be highly unintuitive: **traits are linearized from right to left**, meaning the rightmost trait in the `extends ... with ...` clause executes its method body *first*!

**The Code Snippet**:
```scala
package com.insight.scala

trait Logger {
  def log(message: String): String = s"[Base] $message"
}

trait TimestampLogger extends Logger {
  override def log(message: String): String = {
    super.log(s"[Timestamp: 2026-10-07] $message")
  }
}

trait EncryptLogger extends Logger {
  override def log(message: String): String = {
    super.log(s"[ENCRYPTED: ${message.reverse}]")
  }
}

// Order 1: TimestampLogger THEN EncryptLogger
class ServiceA extends Logger with TimestampLogger with EncryptLogger

// Order 2: EncryptLogger THEN TimestampLogger
class ServiceB extends Logger with EncryptLogger with TimestampLogger

object TraitLinearizationApp {
  def main(args: Array[String]): Unit = {
    val serviceA = new ServiceA
    println("ServiceA Log:")
    println(serviceA.log("Hello"))
    // Linearization for ServiceA: ServiceA -> EncryptLogger -> TimestampLogger -> Logger
    // Output: [Base] [Timestamp: 2026-10-07] [ENCRYPTED: olleH]

    val serviceB = new ServiceB
    println("\nServiceB Log:")
    println(serviceB.log("Hello"))
    // Linearization for ServiceB: ServiceB -> TimestampLogger -> EncryptLogger -> Logger
    // Output: [Base] [ENCRYPTED: olleH :pmatsemiT] [Hello]
  }
}
```

**Under the Hood / Why It Happens**:
The Scala compiler computes linearization for a type $C = n \text{ with } T_1 \text{ with } ... \text{ with } T_k$ using the following formal algorithm:
$$\text{Lin}(C) = C \vec{+} \text{Lin}(T_k) \vec{+} \text{Lin}(T_{k-1}) \vec{+} ... \vec{+} \text{Lin}(T_1) \vec{+} \text{Lin}(n)$$
where $\vec{+}$ denotes concatenation with right-side deduplication (if a trait appears multiple times, earlier occurrences are removed, keeping only the rightmost instance).

When `serviceA.log()` is called:
1. `ServiceA` defers to `EncryptLogger` (the rightmost mixin trait).
2. `EncryptLogger` executes `super.log(...)`, which delegates to `TimestampLogger` (the next item in linearized hierarchy, NOT `Logger`!).
3. `TimestampLogger` executes `super.log(...)`, delegating down to `Logger`.

**Key Takeaway / Safe Pattern**:
Be explicit about trait stackability. Mixin traits that modify behavior using `super` calls depend critically on declaration order. List base mixin traits first and stacked modifier traits from left to right in order of evaluation.
