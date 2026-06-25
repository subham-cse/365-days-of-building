# Day 230: Scala `@tailrec` Annotation & Trampolining Mutually Recursive Stack Safety

**Language / Domain**: Scala / Functional Programming & Compiler Optimization

**The Core Concept / "Did You Know?"**:
Recursive functions in functional programming risk throwing `java.lang.StackOverflowError` when processing deep data structures. The Scala compiler optimizes self-recursive functions into standard imperative while-loops via **Tail-Call Optimization (TCO)**, provided the recursive call is in strict tail position.

Annotating a function with `@scala.annotation.tailrec` forces the Scala compiler to verify TCO at compile time. If the function cannot be optimized (e.g. computation occurs after the recursive call, or the function is mutually recursive), the compilation fails.

To make **mutually recursive** functions (where Function A calls Function B, which calls Function A) stack-safe without rewriting them into complex iterative loops, Scala provides **Trampolining** via `scala.util.control.TailCalls`.

**The Code Snippet**:
```scala
import scala.annotation.tailrec
import scala.util.control.TailCalls._

object RecursiveDemo extends App {

  // --- SAFE: Self-tail-recursive function optimized to JVM loop ---
  @tailrec
  def sumTailRec(list: List[Long], acc: Long): Long = list match {
    case Nil => acc
    case head :: tail => sumTailRec(tail, acc + head) // Pure tail call
  }

  // --- TRAP: Mutually recursive functions (Cause StackOverflowError without Trampoline) ---
  def isEvenBad(n: Int): Boolean = if (n == 0) true else isOddBad(n - 1)
  def isOddBad(n: Int): Boolean = if (n == 0) false else isEvenBad(n - 1)

  // --- SAFE PATTERN: Trampolined Mutually Recursive Functions ---
  def isEvenTrampolined(n: Int): TailRec[Boolean] = {
    if (n == 0) done(true)
    else tailcall(isOddTrampolined(n - 1))
  }

  def isOddTrampolined(n: Int): TailRec[Boolean] = {
    if (n == 0) done(false)
    else tailcall(isEvenTrampolined(n - 1))
  }

  val numbers = (1L to 1000000L).toList
  println(s"Sum: ${sumTailRec(numbers, 0L)}")

  // Executing 100,000 deep mutually recursive calls safely via trampoline result evaluation
  val deepCheck = result(isEvenTrampolined(100000))
  println(s"Is 100,000 even? $deepCheck")
}
```

**Under the Hood / Why It Happens**:
1. **Self Tail-Call Optimization (`@tailrec`)**:
   When the Scala compiler detects a function ending with `return sumTailRec(...)`, it re-writes the bytecode to reuse the current JVM stack frame:
   - Registers are updated with new argument values.
   - A JVM `goto` instruction jumps back to the top of the bytecode method block.
   - Stack frame depth remains constant at \(O(1)\).

2. **Why Mutual Recursion Fails Self TCO**:
   Method `isEvenBad` calls `isOddBad`. The JVM cannot replace `invokevirtual isOddBad` with a simple local `goto` because `isOddBad` lives in a separate stack frame context. Deep calls fill up the JVM call stack until `StackOverflowError` crashes the thread.

3. **Trampolining Mechanism (`TailRec[A]`)**:
   Trampolining converts recursion into heap-allocated data structures (`Call` / `Done`).
   - `tailcall(...)` creates a suspended `Call(() => TailRec[A])` thunk object without executing the function.
   - `result(...)` runs a tight while-loop on the main thread, unwinding thunk objects iteratively:
     ```scala
     @tailrec final def result: A = this match {
       case Done(value) => value
       case Call(thunk) => thunk().result
     }
     ```
   Stack allocation is swapped for small heap object allocations, preserving stack safety regardless of recursion depth.

**Key Takeaway / Safe Pattern**:
- Always annotate self-recursive functions with `@scala.annotation.tailrec` to verify TCO at compile time.
- For mutually recursive methods or tree-traversal algorithms, use `scala.util.control.TailCalls` trampolining to guarantee zero risk of stack overflow.
