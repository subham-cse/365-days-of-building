# Day 196: Kotlin Coroutine Exception Propagation and SupervisorJob Traps

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin Structured Concurrency, exceptions thrown inside child coroutines propagate **upward** through the job hierarchy to the parent scope by default. If one child coroutine fails with an uncaught exception, its parent cancels itself and all other active child coroutines in that scope.

A common dynamic trap involves misuse of `SupervisorJob`. Developers often pass `SupervisorJob()` into `CoroutineScope(SupervisorJob())` or `launch(SupervisorJob())`. However, passing a `SupervisorJob()` as a context argument directly to `launch { ... }` or `async { ... }` inside an existing scope **does not prevent sibling cancellation**, because `launch` creates its own new child `Job` that overrides the supervisor context for its children, while still propagating exceptions up to its parent scope.

**The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val scope = CoroutineScope(Dispatchers.Default)

    // TRAP: Passing SupervisorJob() to launch does NOT isolate failure from sibling!
    scope.launch {
        // Child 1 fails
        launch(SupervisorJob()) { // Does NOT protect scope from failure!
            println("Child 1 starting...")
            throw RuntimeException("Child 1 failed!")
        }

        // Child 2 gets CANCELLED as a result of Child 1 failure!
        launch {
            delay(1000)
            println("Child 2 completed successfully") // Never executed!
        }
    }

    delay(1500)
}
```

**Under the Hood / Why It Happens**:
In Kotlin coroutines, parent-child relationships form a tree of `Job` instances:

1. When `launch(SupervisorJob())` is called inside a parent scope, `launch` constructs a standard `StandaloneCoroutine` object which creates a regular `JobImpl`.
2. The `SupervisorJob()` argument is merged into the `CoroutineContext`, but `launch` overrides its parent connection by creating a new standard child job attached to the parent's job structure.
3. When Child 1 throws an uncaught exception, `JobImpl.childCancelled()` notifies its parent `Job`. Because the parent `Job` is not a `SupervisorJob`, it cancels itself and broadcasts cancellation signals down to Child 2.

To correctly isolate failures among sibling coroutines, `supervisorScope { ... }` must be used, which installs a `SupervisorCoroutine` node in the job tree hierarchy.

**Key Takeaway / Safe Pattern**:
Use `supervisorScope` or instantiate your top-level `CoroutineScope` with `SupervisorJob()`. Never pass `SupervisorJob()` as an inline argument to nested `launch` builder calls.

```kotlin
// Safe Pattern: Use supervisorScope builder to isolate child failures
fun main() = runBlocking {
    supervisorScope {
        launch {
            println("Child 1 starting...")
            throw RuntimeException("Child 1 failed!")
        }

        launch {
            delay(500)
            println("Child 2 completed successfully!") // Executed safely!
        }
    }
}
```
