# Day 176: Destructor Exception Invariants and `std::terminate` Traps

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, RAII (Resource Acquisition Is Initialization) relies on destructors running automatically when an object goes out of scope. Since C++11, all destructors are implicitly marked `noexcept(true)` by default.

If a destructor throws an exception while stack unwinding is *already* in progress (due to another unhandled exception moving up the call stack), C++ cannot handle two active exceptions simultaneously. The runtime immediately invokes `std::terminate()`, aborting the process abruptly without calling remaining destructors or cleanup handlers.

**The Code Snippet**:

```cpp
#include <iostream>
#include <exception>
#include <stdexcept>

class DangerousResource {
public:
    ~DangerousResource() noexcept(false) { // Explicitly marking noexcept(false) for demo
        std::cout << "Destructor running..." << std::endl;
        // BUG: Throwing an exception inside a destructor!
        throw std::runtime_error("Exception inside destructor!");
    }
};

void trigger_double_exception() {
    try {
        DangerousResource res; // Stack-allocated RAII object
        std::cout << "Throwing primary exception from function..." << std::endl;
        throw std::runtime_error("Primary exception"); // Triggers stack unwinding
        // Stack unwinding begins: `res` destructor is invoked automatically!
    } catch (const std::exception& e) {
        std::cout << "Caught exception: " << e.what() << std::endl;
    }
}

int main() {
    std::set_terminate([]() {
        std::cout << "FATAL: std::terminate called due to double exception propagation!" << std::endl;
        std::exit(1);
    });

    // Calling this will invoke std::terminate!
    trigger_double_exception();
    return 0;
}
```

**Under the Hood / Why It Happens**:
The C++ Itanium ABI exception handling specification tracks exception propagation state using `std::uncaught_exceptions()`.

When an exception is thrown (`throw` instruction):
1. The runtime allocates an exception object in memory and begins **Stack Unwinding**.
2. As frames unwind, local RAII object destructors are invoked.
3. If a destructor throws a *second* exception while `std::uncaught_exceptions() > 0`, the ABI unwinder recognizes an irreconcilable exception conflict.
4. The unwinder calls `std::terminate()`, immediately calling `std::abort()` to crash the process.

Even without double-throwing, throwing an exception from a standard destructor marked `noexcept(true)` (C++11 default) triggers `std::terminate()` directly.

**Key Takeaway / Safe Pattern**:
Destructors must **never** allow exceptions to escape. Wrap all cleanup code inside destructors with internal `try { ... } catch (...) { log or handle }` blocks. If an operation can fail (such as flushing a network socket), expose an explicit close/flush method (`close()`) that the caller can invoke and catch exceptions from before the object is destroyed.
