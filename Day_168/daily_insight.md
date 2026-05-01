# Day 168: Coroutine Exception Propagation: SupervisorJob vs Job

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin Coroutines, structured concurrency dictates how failure propagates through job hierarchies. By default, when a child coroutine fails with an unhandled exception, it immediately cancels its parent job, which in turn cancels all sibling coroutines in the scope.

A very common bug occurs when developers wrap a custom `CoroutineScope` with a standard `Job()` thinking it will isolate child failures. To prevent a failing child coroutine from cancelling its siblings and parent, a `SupervisorJob()` must be used instead of a standard `Job()`.

**The Code Snippet**:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    println("--- 1. Testing Standard Job (Sibling Cancellation) ---")
    val standardScope = CoroutineScope(Dispatchers.Default + Job())

    val child1 = standardScope.launch {
        delay(100)
        throw RuntimeException("Child 1 Failed!")
    }

    val child2 = standardScope.launch {
        delay(300)
        println("Child 2 Completed Successfully!") // Will NEVER run!
    }

    delay(400)

    println("--- 2. Testing SupervisorJob (Failure Isolation) ---")
    val supervisorScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    val supChild1 = supervisorScope.launch {
        delay(100)
        throw RuntimeException("Supervisor Child 1 Failed!")
    }

    val supChild2 = supervisorScope.launch {
        delay(300)
        println("Supervisor Child 2 Completed Successfully!") // WILL RUN!
    }

    delay(400)
}
```

**Under the Hood / Why It Happens**:
In `kotlinx.coroutines`, every coroutine has a `Job` in its `CoroutineContext`. Parent-child relationships form a tree of jobs.

When a child job encounters an exception:
1. If the parent job is a standard `Job`:
   - The child invokes `childCancelled(cause)`.
   - The parent cancels itself, cancels all of its other children via `cancelChildren()`, and propagates the exception upward to its own parent.
2. If the parent job is a `SupervisorJob`:
   - The `SupervisorJob` overrides `childCancelled(cause)` to return `false`.
   - The parent declines to cancel itself or its remaining children. The exception is delegated directly to the failing child's `CoroutineExceptionHandler` or uncaught exception handler.

**Key Takeaway / Safe Pattern**:
Use `supervisorScope { ... }` or `SupervisorJob()` for UI view models, background task runners, or server request handlers where individual task failures (e.g. single network request timeout) should not crash adjacent independent tasks or tear down the entire application scope.
