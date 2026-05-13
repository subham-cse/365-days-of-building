# Day 186: Scala Implicit Conversions and Type Class Resolution Traps

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Scala's implicit mechanism provides powerful type class pattern support and extension methods. However, implicit conversions (`implicit def`) can cause subtle, difficult-to-debug runtime behavior and unexpected compiler coercion.

When the Scala compiler encounters a type mismatch or a method call on a type that does not define that method, it searches the current implicit scope for an implicit conversion function that can adapt the source type to the expected target type. If multiple implicit conversions exist or if an unexpected implicit conversion is brought into scope via a wildcard import (`import ..._`), the compiler may silently apply conversions, altering program semantics or introducing hidden performance allocations.

**The Code Snippet**:
```scala
object ImplicitTrap extends App {

  case class Seconds(value: Int)
  case class Milliseconds(value: Int)

  // Implicit conversion: Int => Seconds
  implicit def intToSeconds(i: Int): Seconds = Seconds(i)

  // Unexpected implicit conversion: Seconds => Milliseconds
  implicit def secondsToMillis(s: Seconds): Milliseconds = Milliseconds(s.value * 1000)

  def timeout(duration: Milliseconds): Unit = {
    println(s"Timeout set to: ${duration.value} ms")
  }

  // Compiler automatically applies intToSeconds and then secondsToMillis!
  val rawDuration: Int = 5
  
  // Implicitly resolved as: timeout(secondsToMillis(intToSeconds(rawDuration)))
  timeout(rawDuration)
}
```

**Under the Hood / Why It Happens**:
During type checking, if an expression `$e$` of type `$T$` fails to satisfy expected target type `$U$`, the Scala compiler inspects implicit candidates:
1. Implicit definitions in current lexical scope.
2. Implicit definitions in companion objects of `$T$` or `$U$`.

If a single valid conversion `$f: T \Rightarrow U$` is found, the compiler rewrites `$e$` to `$f(e)$` in the AST. In Scala 2, chained or cascading implicit conversions can occur if intermediate conversions align, creating runtime object allocation overhead and surprising logic transformations without any explicit syntax clues.

**Key Takeaway / Safe Pattern**:
In modern Scala (Scala 3), explicit type class extension methods (`extension`) and `given`/`using` clauses replace unsafe `implicit def` conversions. In Scala 2, avoid general implicit conversions, enforce `scala.language.implicitConversions` imports, or prefer value classes and explicit conversion methods.

```scala
// Scala 3 / Modern Idiom: Explicit type class extension
case class Seconds(value: Int) {
  def toMillis: Milliseconds = Milliseconds(value * 1000)
}

case class Milliseconds(value: Int)

// Require explicit invocation in call-site code
timeout(Seconds(5).toMillis)
```
