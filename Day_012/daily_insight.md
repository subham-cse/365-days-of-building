# Day 012: Companion Object Initialization Order and Coroutine Exception Propagation
**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin, companion object initialization timing depends strictly on static class loading order. Accessing fields of a class before its `companion object` has finished initializing can lead to uninitialized property access returning `null` in non-nullable property types.

Furthermore, exceptions thrown inside structured Kotlin Coroutines behave completely differently depending on whether `launch` or `async` is used. An unhandled exception inside `launch` immediately propagates up the parent job hierarchy, canceling all sibling coroutines regardless of try-catch blocks surrounding the child launch statement.

**The Code Snippet**:
```kotlin
import kotlinx.coroutines.*

class ConfigManager private constructor(val configName: String) {
    companion object {
        // Initialization order dependency trap!
        val DEFAULT_CONFIG = ConfigManager(DEFAULT_NAME)
        val DEFAULT_NAME = "Production_DB"
    }
}

fun main() = runBlocking {
    // Trap 1: Static Companion Init Order Trap
    // Output: "Config name: null"! Even though configName is non-nullable String!
    println("Config name: ${ConfigManager.DEFAULT_CONFIG.configName}")

    // Trap 2: Coroutine Exception Propagation
    val scope = CoroutineScope(Job())

    val job = scope.launch {
        // Child 1
        launch {
            delay(100)
            throw RuntimeException("Child 1 Crashed!")
        }

        // Child 2
        launch {
            delay(500)
            println("Child 2 completed work") // NEVER EXECUTED!
        }
    }

    job.join()
    println("Scope active: ${scope.isActive}") // false! Whole scope cancelled!
}
```

**Under the Hood / Why It Happens**:
Kotlin compiles companion objects into a static inner class `Companion` with static field initializers on the outer class. When `ConfigManager` is loaded, static fields are initialized top-to-bottom:
1. `DEFAULT_CONFIG` is initialized by invoking `ConfigManager(DEFAULT_NAME)`.
2. At this moment, `DEFAULT_NAME` has not yet been initialized by the JVM class loader, so its static slot holds default memory `null`.
3. `ConfigManager` constructor reads `DEFAULT_NAME` (`null`) and stores it into `configName`.
4. `DEFAULT_NAME` is finally assigned `"Production_DB"`, but `DEFAULT_CONFIG.configName` is permanently stuck holding `null`.

In Kotlin Coroutines, exceptions propagate **upwards** to parent `Job` objects before being thrown. Surrounding a child `launch` block with `try-catch` does not catch the exception because `launch` delegates uncaught exception handling to the parent job's `JobSupport.childCancelled()`. The parent cancels itself and all child sub-trees before rethrowing.

**Key Takeaway / Safe Pattern**:
Always declare static constants used by companion objects before dependent object instances in the companion block. For coroutines, use `SupervisorJob` or `supervisorScope` when sibling coroutine failures should not cancel adjacent concurrent operations.

```kotlin
// SAFE Companion Initialization: Declare constants FIRST!
class ConfigManagerSafe private constructor(val configName: String) {
    companion object {
        const val DEFAULT_NAME = "Production_DB" // Initialized FIRST
        val DEFAULT_CONFIG = ConfigManagerSafe(DEFAULT_NAME)
    }
}

// SAFE Coroutines: Use supervisorScope to isolate child failures
suspend fun safeConcurrentTasks() = supervisorScope {
    launch {
        try {
            throw RuntimeException("Child 1 failed!")
        } catch (e: Exception) {
            println("Caught child 1 exception safely")
        }
    }

    launch {
        delay(200)
        println("Child 2 completed successfully!") // Runs normally!
    }
}
```
