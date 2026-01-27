# Day 056: Kotlin Coroutine Exception Propagation and SupervisorJob

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin Coroutines, structured concurrency dictates that exceptions propagate upward through the coroutine parent-child hierarchy. By default, if any child coroutine fails with an unhandled exception (other than `CancellationException`), it immediately cancels its parent scope, which in turn cancels all sibling coroutines.

To prevent a single failing background task from tearing down the entire scope and failing unrelated concurrent operations, Kotlin provides `SupervisorJob` and `supervisorScope`.

**The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    println("--- Default Job Exception Propagation ---")
    val defaultScope = CoroutineScope(Dispatchers.Default + Job())

    val job1 = defaultScope.launch {
        delay(100)
        throw RuntimeException("Network request failed!")
    }

    val job2 = defaultScope.launch {
        delay(300)
        println("Job 2 completed successfully!") // WILL NEVER PRINT!
    }

    delay(400)
    println("Default Scope active status: ${defaultScope.isActive}") // false

    println("\n--- SupervisorJob Protected Exception Propagation ---")
    val supervisorScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    val superJob1 = supervisorScope.launch {
        delay(100)
        throw RuntimeException("Background synchronization failed!")
    }

    val superJob2 = supervisorScope.launch {
        delay(300)
        println("Supervisor Sibling Job 2 completed successfully!") // PRINTS FINE!
    }

    delay(400)
    println("Supervisor Scope active status: ${supervisorScope.isActive}") // true
}
```

**Under the Hood / Why It Happens**:
Every coroutine created inside a `CoroutineScope` inherits a `Job` context node. In a standard `Job`, parent-child exception handling follows a bi-directional propagation pattern:
1. Child catches unhandled exception.
2. Child forwards failure to parent Job via `notifyCancelled(cause)`.
3. Parent cancels itself, propagates cancellation downward to all other children, and passes exception up to its own parent.

`SupervisorJob` overrides the default `childCancelled(cause)` implementation. When a child coroutine fails inside a `SupervisorJob`, the supervisor ignores the child cancellation request, allowing siblings to continue execution unhindered.

**Key Takeaway / Safe Pattern**:
Use `SupervisorJob` or `supervisorScope { ... }` for independent concurrent tasks (such as parallel UI component loading or multi-file downloads) where one child failure should not cancel remaining sibling tasks. Handle exceptions inside individual child coroutines using `try/catch` or `CoroutineExceptionHandler`.
