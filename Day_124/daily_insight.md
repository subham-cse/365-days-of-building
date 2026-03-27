# Day 124: Kotlin Coroutine Exception Propagation & SupervisorJob Traps

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin Coroutines, exception propagation flows upward to parent jobs by default, cancelling the entire hierarchy unless explicitly handled by a `SupervisorJob` or `supervisorScope`. However, a common pitfall occurs when developer pass `SupervisorJob()` as a context argument directly to a child builder such as `launch(SupervisorJob())`. 

Because `launch` creates its own child `Job` and overrides the parent job in context, passing `SupervisorJob()` inside a scope child builder does NOT prevent exceptions in sibling coroutines from cancelling the scope itself or sibling coroutines! To achieve true supervisor behavior where siblings survive a child's failure, `supervisorScope` or a scope backed by a `SupervisorJob` must be used.

**The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    println("--- Broken Supervisor Pattern ---")
    val scope = CoroutineScope(Job())

    // WRONG: Passing SupervisorJob() to child launch does not make parent scope a supervisor
    scope.launch(SupervisorJob()) {
        delay(100)
        throw RuntimeException("Child 1 failed!")
    }

    scope.launch {
        delay(300)
        println("Child 2 finished (This will NOT print because scope gets cancelled!)")
    }

    delay(500)

    println("\n--- Correct Supervisor Pattern ---")
    supervisorScope {
        launch {
            delay(100)
            throw RuntimeException("Isolated Child failed!")
        }

        launch {
            delay(300)
            println("Isolated Sibling succeeded! (This WILL print)")
        }
    }
}
```

**Under the Hood / Why It Happens**:
When a coroutine is started with `launch(context)`, the builder constructs a new `StandaloneCoroutine` object. It establishes a parent-child link with the `Job` present in the current `CoroutineScope`. 

If you pass `launch(SupervisorJob())`, the newly created `SupervisorJob()` becomes the parent of that specific child coroutine only. The top-level `CoroutineScope` still holds a normal cancellation-propagating `Job`. When the child fails, the uncaught exception travels up from the child to its parent (`SupervisorJob()`). Because `SupervisorJob` ignores child failures, it swallows cancellation of *itself*, but the uncaught exception handler in the coroutine context still triggers scope cancellation or uncaught exception handling if the scope parent was connected to the root scope. More importantly, siblings attached to the root scope `Job` still get cancelled if the failure is propagated to the root `Job`. 

Using `supervisorScope { ... }` attaches children directly to a `SupervisorCoroutine` scope implementation where child cancellations are explicitly trapped before reaching parent hierarchy.

**Key Takeaway / Safe Pattern**:
Never pass `SupervisorJob()` directly into `launch` or `async` expecting sibling isolation. Always wrap failing coroutine pools inside `supervisorScope { ... }` or create a standalone `CoroutineScope(SupervisorJob() + CoroutineExceptionHandler { ... })`.
