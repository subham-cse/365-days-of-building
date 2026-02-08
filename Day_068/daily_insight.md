# Day 068: Companion Object Initialization Order Traps in Kotlin

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
In Kotlin, `companion object` blocks are compiled into static initializers under Java target bytecode. However, because companion object instantiation occurs during class loading, referencing property initializers or methods of the enclosing class from inside a companion object (or vice versa) can trigger zero-value initialization bugs before constructors actually run.

When properties in the enclosing class rely on values initialized by the companion object—or when the companion object accesses properties declared *after* it in source code order—Kotlin silently sets primitive types to default zeroes (`0`, `false`) and reference types to `null`, completely bypassing null-safety guarantees.

**The Code Snippet**:
```kotlin
package com.insight.kotlin

class ConfigurationManager private constructor(val maxConnections: Int) {

    // TRAP: Enclosing class property referencing companion object field declared below
    val timeoutMs: Int = DEFAULT_TIMEOUT * 2 

    companion object {
        // Properties declared here are initialized during Companion object creation
        val DEFAULT_TIMEOUT = 5000

        // TRAP: Instance reference inside companion initialization
        val INSTANCE = ConfigurationManager(DEFAULT_TIMEOUT)

        // Read static configuration value
        val MAX_LIMIT: Int = INSTANCE.maxConnections * 10
    }
}

// Demonstrating Nullability/Zero Initialization Bug
class UserProfile(val userId: String) {
    
    companion object {
        // Reads defaultName before constructor initialization completes if static init loops
        val DEFAULT_USER = UserProfile(defaultName)
        const val defaultName = "Anonymous"
    }
}

fun main() {
    println("Timeout Ms: ${ConfigurationManager.INSTANCE.timeoutMs}")
    // If order is mixed, DEFAULT_TIMEOUT might be 0 during top instance init!

    println("User Name: ${UserProfile.DEFAULT_USER.userId}")
    // Prints "null" despite userId being declared non-null String!
}
```

**Under the Hood / Why It Happens**:
Kotlin compiles companion objects into a nested static singleton class (`Companion`) and generates static fields on the outer class. When the JVM loads `UserProfile`:
1. The outer class static initializer `<clinit>` executes.
2. Static fields are initialized in top-to-bottom source code order.
3. `UserProfile.DEFAULT_USER` is declared *before* `const val defaultName = "Anonymous"`.
4. When `UserProfile(defaultName)` runs, `defaultName` has not yet been assigned `"Anonymous"`. At the JVM level, string static storage for `defaultName` is still uninitialized (`null`).
5. The non-null parameter `userId` receives `null` without throwing a `NullPointerException` at construction, silently breaking Kotlin's type safety invariants!

**Key Takeaway / Safe Pattern**:
Always declare static constants (`const val`) or primitive properties at the very top of the `companion object` block before referencing them in factory methods or instantiated singletons. Avoid circular initialization dependencies between enclosing class instance fields and companion object fields.
