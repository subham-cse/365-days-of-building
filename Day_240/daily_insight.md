# Day 240: Kotlin Coroutine Exception Propagation, `SupervisorJob`, & Structured Concurrency

**Language / Domain**: Kotlin / Coroutines & Asynchronous Concurrency

**The Core Concept / "Did You Know?"**:
Kotlin Coroutines enforce **Structured Concurrency**: parent coroutine scopes supervise child coroutines. In standard coroutine scopes (`coroutineScope { ... }` or `Job()`), if a single child coroutine throws an unhandled exception, that exception propagates **upwards to the parent job**, immediately cancelling the parent and all other sibling coroutines running in that scope!

To prevent a single failing worker task from cascading and cancelling independent peer tasks, Kotlin provides **`SupervisorJob`** and **`supervisorScope { ... }`**. Under a supervisor scope, exception propagation is unidirectional—failures flow downward from parent to child, but an uncaught child exception does **not** cancel the supervisor parent or its sibling coroutines.

**The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    println("--- CASE 1: Standard Coroutine Scope (Cascading Cancellation Trap) ---")
    try {
        coroutineScope {
            val child1 = launch {
                delay(50)
                println("Child 1: Throwing exception!")
                throw RuntimeException("Child 1 Failed!")
            }

            val child2 = launch {
                delay(200)
                println("Child 2: Completed successfully")
            }
        }
    } catch (e: Exception) {
        println("Parent Scope caught: ${e.message}")
        // Result: Child 2 was CANCELLED before reaching 200ms!
    }

    println("\n--- CASE 2: Supervisor Scope (Fault Isolation Pattern) ---")
    supervisorScope {
        val child1 = launch(CoroutineExceptionHandler { _, throwable ->
            println("Child 1 Exception Handler: Handled '${throwable.message}'")
        }) {
            delay(50)
            println("Supervisor Child 1: Throwing exception!")
            throw RuntimeException("Child 1 Failed!")
        }

        val child2 = launch {
            delay(200)
            println("Supervisor Child 2: Completed successfully despite sibling failure!")
        }
    }
}
```

**Under the Hood / Why It Happens**:
Kotlin coroutines manage lifecycle via internal **`Job`** hierarchy nodes:

1. **Standard `Job` Exception Flow**:
   - When a child coroutine fails with an exception, it notifies its parent job via `childCancelled(cause)`.
   - A standard parent `Job` responds by cancelling itself, cancelling all its remaining active child jobs, and re-throwing the exception up its own parent chain.

2. **`SupervisorJob` Exception Handling**:
   - A `SupervisorJob` overrides `childCancelled(cause)` to return `false`.
   - Returning `false` tells the parent node: *"Do NOT cancel me or my other children."*
   - The failing child completes in a `Cancelled` state, while the `SupervisorJob` remains `Active` and allows sibling coroutines to continue execution uninterrupted.

3. **`CoroutineExceptionHandler` Trap**:
   In standard coroutines created via `launch`, attaching a `CoroutineExceptionHandler` to a *child* inside a non-supervisor scope does **not** prevent upward cancellation propagation! The exception still cancels the parent job. `CoroutineExceptionHandler` only handles uncaught exceptions after they reach a root `SupervisorJob` or top-level coroutine scope.

**Key Takeaway / Safe Pattern**:
- Use `supervisorScope { ... }` or `CoroutineScope(SupervisorJob() + Dispatchers.IO)` when launching independent concurrent tasks (e.g., fetching data from multiple parallel API endpoints) where one failure should not terminate other requests.
- Always attach a `CoroutineExceptionHandler` or wrap individual task logic in `try-catch` inside supervisor scopes to catch uncaught child exceptions and avoid logging unhandled coroutine errors.
- Use `async` with caution: calling `.await()` on a failed deferred object re-throws the underlying exception at the callsite.
