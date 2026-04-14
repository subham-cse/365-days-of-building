# Day 146: Scala `@tailrec` Annotation & Stack Overflow Traps

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Scala supports functional recursion for iterating over sequences and recursive data structures. However, unless recursive function calls are written in **tail-call position**, each recursive call allocates a new stack frame on the JVM thread stack, leading to a `StackOverflowError` when processing deep data inputs.

Scala provides the `@tailrec` annotation to instruct the compiler to verify and transform recursive calls into optimized jump loops (`goto` bytecodes). If a function marked with `@tailrec` cannot be optimized into a stack-flat loop, the Scala compiler raises a **compile-time error** instead of silently emitting stack-overflow-prone bytecode!

**The Code Snippet**:
```scala
import scala.annotation.tailrec

object TailRecursionDemo extends App {

  // NON-TAIL RECURSIVE: Multiplication occurs AFTER the recursive call returns!
  // JVM stack frames accumulate: factorial(5) = 5 * (4 * (3 * (2 * (1 * 1))))
  def factorialNonTail(n: BigInt): BigInt = {
    if (n <= 1) 1
    else n * factorialNonTail(n - 1) // NOT in tail position!
  }

  // TAIL RECURSIVE: Accumulator carries state, final call is pure recursion
  @tailrec
  def factorialTailRec(n: BigInt, accumulator: BigInt = 1): BigInt = {
    if (n <= 1) accumulator
    else factorialTailRec(n - 1, n * accumulator) // Pure tail position!
  }

  // Demonstration with large depth
  val largeN = 5000

  // factorialNonTail(largeN) // WOULD CAUSE java.lang.StackOverflowError!

  val result = factorialTailRec(largeN)
  println(s"Successfully computed factorial of $largeN without stack overflow!")
  println(s"Result bit length: ${result.bitLength} bits")
}
```

**Under the Hood / Why It Happens**:
In standard JVM bytecode execution:
1. `factorialNonTail` evaluates `n * factorialNonTail(n - 1)`. To compute the multiplication, the JVM must freeze the current stack frame, call `factorialNonTail(n - 1)` on a new frame, wait for the return value, and then execute `n * returnVal`. For $N = 10,000$, 10,000 stack frames fill the stack segment until CPU memory limit is breached.

2. `factorialTailRec` evaluates `factorialTailRec(n - 1, n * accumulator)` as the absolute final statement. Because no further computation is required after the recursive return, the Scala compiler (`scalac`) optimizes the method bytecode by replacing the `invokevirtual` opcode with a simple local `goto` jump instruction back to the start of the method byte sequence!

The resulting class file contains a flat imperative `while` loop at the bytecode level while preserving functional code semantics in source code.

**Key Takeaway / Safe Pattern**:
Always annotate recursive functions with `@scala.annotation.tailrec`. Use accumulator parameters to ensure the recursive call is the absolute final expression evaluated, allowing the Scala compiler to guarantee stack safety at compile time.
