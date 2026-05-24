# Day 202: Scala Tail-Call Recursion `@tailrec` and Stack Safety

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
In functional programming, recursive functions are the standard idiomatic replacement for mutable `while` loops. However, standard recursive functions allocate a new stack frame on the call stack for every recursive call. If the recursion depth is large (e.g., 100,000 iterations), the program will crash with a `java.lang.StackOverflowError`.

Scala solves this issue through **Tail-Call Optimization (TCO)**. If the recursive call is in **tail position**—meaning the recursive invocation is the final operation evaluated before returning, with no pending arithmetic or frame transformations—the Scala compiler rewrites the recursive method into an optimized imperative loop inside JVM bytecode.

To guarantee that TCO occurs, Scala provides the `@annotation.tailrec` annotation, which triggers a compile-time error if a method cannot be optimized into a stack-safe loop.

**The Code Snippet**:
```scala
import scala.annotation.tailrec

object TailRecDemo extends App {

  // TRAP: NOT Tail Recursive!
  // Pending operation (n * ...) requires keeping stack frame alive!
  def unsafeFactorial(n: BigInt): BigInt = {
    if (n <= 1) 1
    else n * unsafeFactorial(n - 1) // Operations remain after recursive call returns!
  }

  // SAFE: Tail Recursive with Accumulator Pattern
  @tailrec
  def safeFactorial(n: BigInt, acc: BigInt = 1): BigInt = {
    if (n <= 1) acc
    else safeFactorial(n - 1, n * acc) // Recursive call is the ABSOLUTE FINAL expression!
  }

  // safeFactorial(100000) runs in O(1) stack space!
  println(s"Safe Factorial calculated cleanly: ${safeFactorial(5)}")
}
```

**Under the Hood / Why It Happens**:
In standard recursion (`n * unsafeFactorial(n - 1)`), the JVM stack must preserve the local variable `n` while waiting for `unsafeFactorial(n - 1)` to return so it can execute the multiplication operation (`invokevirtual`).

When `@tailrec` is applied to `safeFactorial(n, acc)`:
1. The compiler verifies that the return value of `safeFactorial` is directly equal to the return value of its nested call.
2. The compiler emits bytecode using `goto` instructions instead of `invokevirtual` recursive calls.
3. The method reuses its existing JVM stack frame, updating local variables `n` and `acc` in place. This converts memory complexity from \(O(N)\) stack depth to \(O(1)\) constant stack space.

**Key Takeaway / Safe Pattern**:
Always annotate recursive functions meant to process arbitrary depth data with `@scala.annotation.tailrec`. Use **accumulator parameters** to pass intermediate state forward so the recursive call remains in tail position.

```scala
// Safe Pattern: Tail-recursive list processing
@tailrec
def sumList(list: List[Int], accumulator: Long = 0L): Long = list match {
  case Nil => accumulator
  case head :: tail => sumList(tail, accumulator + head)
}
```
