# Day 028: Inline Classes, Smart Cast Invalidations, and Value Classes
**Language / Domain**: Kotlin

**The Core Concept / "Did You Know?"**:
Kotlin provides `@JvmInline value class` to wrap primitive types or objects without creating heap object allocations at runtime. However, passing an inline value class to a generic parameter, an interface, or a nullable type forces the Kotlin compiler to **box** the value class back into a heap object, eliminating its zero-allocation memory advantages.

Additionally, Kotlin's **Smart Cast** compiler feature automatically casts variables after checking types (`if (x is String)`). But smart casting fails on `var` properties or open/delegated properties because the compiler cannot guarantee another thread won't mutate the property between the type check and its usage.

**The Code Snippet**:
```kotlin
// Zero-allocation inline value class
@JvmInline
value class UserId(val id: String)

interface Identifiable

@JvmInline
value class ProductId(val id: String) : Identifiable

fun processUserId(id: UserId) {
    println("User ID: ${id.id}") // Compiles to primitive String parameter! Zero boxing!
}

fun processGeneric<T>(item: T) {
    println("Generic item: $item")
}

class SmartCastDemo {
    var mutableProperty: String? = "Hello World"

    fun demonstrateSmartCastFailure() {
        if (mutableProperty != null) {
            // COMPILE ERROR: Smart cast to 'String' is impossible,
            // because 'mutableProperty' is a mutable property that could be changed by another thread!
            // println(mutableProperty.length) 
        }
    }
}

fun main() {
    val uid = UserId("usr_100")
    processUserId(uid) // Zero Boxing

    // TRAP: Passing inline value class to generic function forces BOXING!
    processGeneric(uid) // Boxed into java.lang.Object / UserId instance on heap!

    val pid: Identifiable = ProductId("prod_500") // Interface assignment forces BOXING!
}
```

**Under the Hood / Why It Happens**:
Kotlin inline value classes exist as their underlying primitive or wrapped type in JVM bytecode wherever possible. The compiler renames (mangles) method signatures accepting value classes (`processUserId-x89a(String id)`).

However, the JVM type system requires all generic parameters (`T`) and interface types to be represented as `java.lang.Object` references. When an inline value class instance is passed to a generic function (`processGeneric<T>`) or assigned to an interface (`Identifiable`), the Kotlin compiler invokes `UserId.box-impl(id)`, instantiating a wrapper instance on the JVM heap.

For smart casts, Kotlin's type checker (`kotlinc`) guarantees thread safety only for immutable local variables (`val`) or private immutable properties. Because mutable `var` properties can be modified concurrently by background threads or custom getters, the compiler refuses to narrow the type automatically.

**Key Takeaway / Safe Pattern**:
To maintain zero allocation benefits with `@JvmInline value class`, avoid assigning them to interface types, nullable types, or generic parameters. To fix smart cast failures on mutable properties, capture the property into an immutable local variable (`val local = property`).

```kotlin
class SmartCastSafe {
    var mutableProperty: String? = "Hello World"

    fun demonstrateSafeSmartCast() {
        // SAFE: Capture property into immutable local variable `val`
        val prop = mutableProperty
        if (prop != null) {
            // Smart cast succeeds cleanly on local variable!
            println("Length: ${prop.length}") 
        }
    }
}
```
