# Day 096: Coroutine Exception Propagation and Job Parent-Child Hierarchy
- **Language / Domain**: Kotlin
- **The Core Concept / "Did You Know?"**: In Kotlin Coroutines, uncaught exceptions propagate up the job hierarchy to the root scope, cancelling all sibling coroutines in that scope by default. Wrapping an individual `launch` block in a standard `try-catch` block **will not prevent** the parent scope or sibling coroutines from being cancelled!

To isolate child coroutine failures so that sibling tasks can continue running, developers must use `supervisorScope` or `SupervisorJob`.

- **The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // Standard CoroutineScope: failure in child 1 cancels sibling child 2
    try {
        coroutineScope {
            launch {
                delay(100)
                throw RuntimeException("Task 1 failed!")
            }
            
            launch {
                delay(500)
                println("Task 2 completed successfully") // Will NEVER print!
            }
        }
    } catch (e: Exception) {
        println("Caught in root: ${e.message}")
    }

    println("--- With supervisorScope ---")

    // SupervisorScope: failure in child 1 does NOT cancel child 2
    supervisorScope {
        launch {
            try {
                delay(100)
                throw RuntimeException("Isolated Task 1 failed!")
            } catch (e: Exception) {
                println("Handled inside child: ${e.message}")
            }
        }

        launch {
            delay(500)
            println("Isolated Task 2 completed successfully") // Will print!
        }
    }
}
```

- **Under the Hood / Why It Happens**:
Kotlin Coroutines build a tree of `Job` objects. When a child `Job` fails with an exception other than `CancellationException`, it immediately passes the exception up to its parent `Job`. 

In a standard `Job`, the parent handles this by cancelling all of its other children and then cancelling itself before rethrowing the exception. A `SupervisorJob`, on the other hand, overrides `childCancelled()` to return `false`, bypassing the automatic upward cancellation cascade and leaving sibling jobs untouched.

- **Key Takeaway / Safe Pattern**:
Use `supervisorScope` (or supply a `SupervisorJob` to your custom scope) whenever launching independent concurrent operations (such as parallel network fetches) where one failure should not tear down all concurrent operations. Always catch exceptions inside child `launch` blocks when using `SupervisorJob`.
