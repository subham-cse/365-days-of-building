# Day 212: Kotlin Value Classes and Boxing Traps Under Interfaces

**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
Kotlin introduces **Value Classes** (`@JvmInline value class UserId(val id: String)`) to create type-safe domain wrappers around underlying primitive or reference types without incurring heap allocation overhead. At compile time, the Kotlin compiler unwraps value class instances, passing raw underlying types (`String` or `Int`) directly in JVM bytecode.

However, value classes contain performance traps: when a value class instance is assigned to an **interface type**, cast to `Any`, or used as a generic type parameter (`List<UserId>`), the Kotlin compiler is forced to **box** the value back into a heap wrapper object. If you use value classes heavily inside generic collections or interface parameters, you negate the performance benefits and introduce unexpected allocation overhead.

**The Code Snippet**:
```kotlin
interface Identifiable {
    fun rawId(): String
}

@JvmInline
value class UserId(val id: String) : Identifiable {
    override fun rawId(): String = id
}

fun processUnboxed(userId: UserId) {
    // Zero allocation! Under the hood, receives raw String in JVM bytecode
    println("User ID: ${userId.id}")
}

fun processInterface(item: Identifiable) {
    // TRAP: Parameter requires interface! Kotlin BOXES UserId back onto heap!
    println("Identifiable raw: ${item.rawId()}")
}

fun main() {
    val uid = UserId("usr_100200")

    // Unboxed direct call
    processUnboxed(uid) // Passes raw String "usr_100200"

    // Interface assignment causes Heap Boxing!
    processInterface(uid) // Allocates boxed UserId wrapper instance!

    // Generic collection causes Heap Boxing for every element!
    val list: List<UserId> = listOf(uid) // Boxed into java.util.List of wrapper objects
}
```

**Under the Hood / Why It Happens**:
At the JVM bytecode level:

1. `fun processUnboxed(userId: UserId)` is compiled by `kotlinc` into `public static final void processUnboxed-impl(String userId)`. The value class parameter is flattened into a plain `java.lang.String`.
2. When calling `processInterface(Identifiable item)`, the interface signature expects an object reference implementing `Identifiable`. Because primitive `String` does not implement `Identifiable`, the compiler invokes `UserId.box-impl("usr_100200")`, instantiating a wrapper object (`new UserId("usr_100200")`) on the JVM heap.

Similarly, Java generics (`List<T>`) do not support inline unboxed value types, forcing Kotlin to store boxed wrapper instances in generic arrays and collections.

**Key Takeaway / Safe Pattern**:
Use value classes for domain safety in function signatures, state parameters, and internal method boundaries. Avoid passing value classes as interface types or storing them in generic collections where raw allocation performance is required.

```kotlin
// Safe Pattern: High-performance primitive collections or direct parameter usage
fun processUserBatch(userIds: Array<UserId>) {
    // Direct value class arrays maintain unboxed efficiency under specialized inline methods
}
```
