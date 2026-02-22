# Day 084: Inline Classes and Coroutine Exception Propagation in Kotlin

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
Kotlin provides **Inline Value Classes** (`@JvmInline value class`) to wrap primitive domain types without runtime heap allocation overhead. However, when an inline class is cast to an interface, passed as a generic type parameter `T`, or stored in a nullable reference (`ValueClass?`), Kotlin is forced to **box** the value at runtime, completely negating the zero-cost performance optimization!

In structured concurrency, Kotlin handles exceptions differently based on the builder used:
- Exceptions thrown inside `launch` propagate immediately up the `Job` parent hierarchy, cancelling sibling coroutines.
- Exceptions thrown inside `async` are deferred and captured inside the returned `Deferred<T>` object, manifesting only when `.await()` is called—**UNLESS** `async` is called from a root `coroutineScope`, in which case it *still* cancels parent scopes!

**The Code Snippet**:
```kotlin
package com.insight.kotlin

import kotlinx.coroutines.*

// 1. Inline Value Class Definition
@JvmInline
value class UserId(val id: Long)

interface Identifiable

@JvmInline
value class DeviceId(val id: Long) : Identifiable

fun processUserId(userId: UserId) {
    // Zero-allocation path: compiled to raw primitive long in bytecode!
    println("Processing user ID: ${userId.id}")
}

fun processGeneric<T>(item: T) {
    // Generic T forces boxing of inline value classes!
    println("Processing generic: $item")
}

fun main() = runBlocking {
    val uid = UserId(42L)
    processUserId(uid) // Unboxed raw primitive long!
    
    processGeneric(uid) // BOXED! Allocated java.lang.Object wrapper!

    // 2. Coroutine Exception Propagation Trap
    println("\n--- Coroutine Exception Propagation ---")

    val customScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // TRAP: launch propagates exception up parent hierarchy immediately
    val job = customScope.launch {
        println("Child coroutine launching...")
        throw RuntimeException("Unhandled error in launch!")
    }

    job.join()
    println("Scope active after supervisor job handles exception? ${customScope.isActive}")
}
```

**Under the Hood / Why It Happens**:
1. **Inline Classes**: Kotlin compiles `@JvmInline value class UserId(val id: Long)` into raw `long` primitive parameter types in JVM method signatures. However, because Java collections and generic type parameters (`T`) operate exclusively on `java.lang.Object` references, Kotlin compiler generates static boxing methods (`UserId.box-impl(long)`) and unboxing methods (`UserId.unbox-impl()`). Whenever an inline type is passed as an interface or generic, Kotlin calls `box-impl()`, instantiating a wrapper object on the heap.
2. **Coroutine Exception Propagation**: In Kotlin Coroutines, `Job` nodes form a tree. When a child coroutine fails with an exception, it cancels itself and passes the exception up to its parent `Job`. By default, a parent `Job` cancels all its other children and itself. Using `SupervisorJob()` breaks the upward propagation path, preventing sibling cancellation when a child fails.

**Key Takeaway / Safe Pattern**:
Avoid casting inline value classes to generic type parameters or nullable types in performance-critical loops to prevent unintended boxing allocations. Use `SupervisorJob` or `supervisorScope` when launching independent parallel coroutines where individual failures should not cancel the entire execution parent context.
