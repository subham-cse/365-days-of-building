# Day 118: Tail-Call Recursion Optimization and TailRec Annotations
- **Language / Domain**: Scala
- **The Core Concept / "Did You Know?"**: In functional programming, recursive algorithms can cause a `StackOverflowError` if the recursion depth exceeds stack limits. Scala optimizes recursive functions using **Tail-Call Optimization (TCO)**, transforming recursive function calls into efficient bytecode loops—provided the recursive call is in the **tail position** (the final operation executed before returning).

Scala provides the `@annotation.tailrec` annotation, which instructs the compiler to verify at build time that a method can be tail-call optimized. If TCO is impossible, compilation fails instantly!

- **The Code Snippet**:
```scala
import scala.annotation.tailrec

object TailCallDemo extends App {

  // TRAP: Not in tail position! Multiplication happens AFTER recursion returns!
  def standardFactorial(n: BigInt): BigInt = {
    if (n <= 1) 1
    else n * standardFactorial(n - 1) // Unoptimized: stack frame kept alive for multiplication
  }

  // SAFE: Tail-recursive using accumulator
  def tailRecFactorial(n: BigInt): BigInt = {
    @tailrec
    def loop(current: BigInt, acc: BigInt): BigInt = {
      if (current <= 1) acc
      else loop(current - 1, current * acc) // Recursive call is strictly in tail position!
    }

    loop(n, 1)
  }

  println("Tail-rec factorial 5: " + tailRecFactorial(5))
}
```

- **Under the Hood / Why It Happens**:
The JVM bytecode architecture does not natively support general tail call elimination. 

When the Scala compiler encounters a method annotated with `@tailrec` (or verified for TCO), it rewrites the JVM bytecode instructions from method call opcodes (`invokevirtual` / `invokestatic`) into a jump loop construct using `goto` opcodes. This reuses the exact same stack frame across all iterations, executing in $O(1)$ stack space.

- **Key Takeaway / Safe Pattern**:
Always annotate recursive helper functions with `@annotation.tailrec` in Scala. Use accumulators as parameters to ensure recursive invocations are the absolute last expression executed in the function body.
