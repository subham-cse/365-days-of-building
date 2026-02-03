# Day 062: Scala Tail-Call Recursion Optimization `@tailrec`

**Language / Domain**: Scala

**The Core Concept / "Did You Know?"**:
Recursion is the foundational looping mechanism in functional Scala. However, deep standard recursion risks throwing `java.lang.StackOverflowError` on the JVM as each recursive invocation pushes a new frame onto the stack.

Scala's compiler optimizes **Tail-Call Recursion** by rewriting recursive functions whose final operation is a direct call to themselves into efficient imperative `while` loops in JVM bytecode. Annotating recursive functions with `@annotation.tailrec` forces the compiler to verify tail-call optimization or fail with a compile error.

**The Code Snippet**:
```scala
import scala.annotation.tailrec

object TailCallOptimizationDemo {

  // Non-tail-recursive function: Addition happens AFTER recursive call returns
  def nonTailRecursiveFactorial(n: BigInt): BigInt = {
    if (n <= 1) 1
    else n * nonTailRecursiveFactorial(n - 1) // Unsafe: Stack frame kept open for multiplication!
  }

  // Tail-recursive function: Recursive call is absolute LAST operation
  @tailrec
  def tailRecursiveFactorial(n: BigInt, accumulator: BigInt = 1): BigInt = {
    if (n <= 1) accumulator
    else tailRecursiveFactorial(n - 1, n * accumulator) // Safe: Reuses current stack frame!
  }

  def main(args: Array[String]): Unit = {
    println("--- Tail-Recursive Factorial Calculation ---")
    val result = tailRecursiveFactorial(5)
    println(s"Factorial(5) = $result")

    // Demonstrating stack safety on large inputs
    val largeResult = tailRecursiveFactorial(10000)
    println(s"Factorial(10000) successfully computed (digits count: ${largeResult.toString().length})")
  }
}
```

**Under the Hood / Why It Happens**:
The JVM bytecode specification does not natively support automatic tail-call elimination across method invocations.

When Scala compiles `@tailrec`, it analyzes the method AST. If the recursive call `tailRecursiveFactorial(n - 1, ...)` is in tail position (meaning no further computations depend on its return value), the Scala compiler replaces `invokevirtual` bytecode instructions with a local `goto` jump instruction targeting the start of the method's local variable table frame.

If a function annotated with `@tailrec` cannot be optimized (e.g. `n * recursiveCall()` retains math operations post-return), the compiler aborts with `Could not optimize @tailrec annotated method`.

**Key Takeaway / Safe Pattern**:
Always annotate recursive functions intended for unbounded or large datasets with `@annotation.tailrec`. Use accumulator parameters to ensure the recursive call is the absolute final expression evaluated by the function.
