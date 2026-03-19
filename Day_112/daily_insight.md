# Day 112: Inline Classes and Value Class Boxed Overhead Traps
- **Language / Domain**: Kotlin
- **The Core Concept / "Did You Know?"**: Kotlin introduced Value Classes (`@JvmInline value class`) to allow lightweight domain type wrapping (such as wrapping a `String` inside a `UserId` value class) without object allocation overhead at runtime.

However, `@JvmInline` value classes do **not** eliminate object allocation in all scenarios! Whenever a value class is used as a generic type argument (e.g. `List<UserId>`), cast to an interface, or assigned to a nullable type (`UserId?`), Kotlin is forced to **box** the primitive value back into a wrapper object on the heap!

- **The Code Snippet**:
```kotlin
@JvmInline
value class Password(val raw: String) : CharSequence by raw

fun printRaw(pass: Password) {
    // Unboxed performance: translated directly to String parameter in JVM bytecode!
    println("Length: ${pass.length}")
}

fun printBoxedInList(passwords: List<Password>) {
    // Generics force boxing: Creates java.lang.Object instances on heap!
    for (p in passwords) {
        println(p.raw)
    }
}

fun printNullableBoxed(pass: Password?) {
    // Nullable reference forces boxing to represent null reference!
    if (pass != null) {
        println(pass.raw)
    }
}

fun main() {
    val secret = Password("SuperSecret123")
    
    printRaw(secret) // Zero-overhead unboxed call
    printNullableBoxed(secret) // Forces object allocation (Boxing)
}
```

- **Under the Hood / Why It Happens**:
At the JVM bytecode level, `@JvmInline` value class method parameters are mangled into the underlying primitive type signature (e.g. `printRaw(Ljava/lang/String;)V`).

However, because the JVM generic type system operates strictly on reference objects (`Object`), passing a value class instance to a generic method or storing it in a collection (`List<T>`) requires Kotlin to instantiate a wrapper object (`Password.box-impl(raw)`).

- **Key Takeaway / Safe Pattern**:
Use `@JvmInline value class` for domain-driven type safety on function arguments and return types. Avoid storing value classes in standard generic collections or using nullable value class types (`Type?`) in hot loops where heap allocations cause garbage collection latency.
