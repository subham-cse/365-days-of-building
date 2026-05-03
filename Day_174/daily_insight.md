# Day 174: Tail-Call Recursion Optimization `@tailrec` Mechanics

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Recursive functions in functional programming provide clean mathematical abstractions, but deep recursion risks exhausting the JVM thread call stack and throwing a fatal `java.lang.StackOverflowError`.

Scala provides automatic **Tail-Call Optimization (TCO)**. If a recursive call is in the *tail position* (meaning the recursive call is the absolute final expression evaluated before returning), the Scala compiler rewrites the recursive logic into an iterative `while` loop at the bytecode level, using zero extra stack frames. Annotating the function with `@scala.annotation.tailrec` forces the compiler to verify this optimization at compile time.

**The Code Snippet**:

```scala
import scala.annotation.tailrec

object TailCallOptimizationDemo {

  // 1. NON-TAIL-RECURSIVE: Multiplication happens AFTER recursive call returns
  def factorialNonTail(n: BigInt): BigInt = {
    if (n <= 1) 1
    else n * factorialNonTail(n - 1) // Multiplication requires holding current stack frame!
  }

  // 2. TAIL-RECURSIVE: Recursive call is the absolute final expression
  @tailrec
  def factorialTail(n: BigInt, accumulator: BigInt = 1): BigInt = {
    if (n <= 1) accumulator
    else factorialTail(n - 1, n * accumulator) // Tail position!
  }

  def main(args: Array[String]): Unit = {
    val largeN = 50000

    println("Testing Tail-Recursive Factorial:")
    val result = factorialTail(largeN)
    println(s"Successfully computed factorial for $largeN (Result length: ${result.toString.length} digits)")

    println("\nTesting Non-Tail-Recursive Factorial (Will StackOverflow):")
    try {
      factorialNonTail(largeN)
    } catch {
      case _: StackOverflowError =>
        println("Caught Expected StackOverflowError from non-tail recursive call!")
    }
  }
}
```

**Under the Hood / Why It Happens**:
The JVM bytecode instruction set natively lacks a dedicated tail-call instruction. Therefore, the Scala compiler (`scalac`) performs transformation during code generation.

For `factorialTail`:
Instead of generating a `invokevirtual` or `invokestatic` instruction to call itself recursively, `scalac` rewrites the method AST into an explicit loop using local variable mutation (`GOTO` bytecode instruction jumping back to label `0`).

If a method annotated with `@tailrec` cannot be optimized (e.g. because operations occur *after* the recursive call, or the method is open for subclass overriding), the compiler emits a hard compilation error: `@tailrec annotated method contains a recursive call not in tail position`.

**Key Takeaway / Safe Pattern**:
Always annotate recursive helper functions with `@tailrec`. Use accumulator parameters to ensure the recursive invocation is the final expression evaluated in the method body, preventing `StackOverflowError` on large datasets.
