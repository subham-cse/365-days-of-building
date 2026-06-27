# Day 232: C++ Non-Virtual Interface (NVI) & Virtual Table Layout Overhead

**Language / Domain**: C++ / Object-Oriented Design & Runtime Mechanics

**The Core Concept / "Did You Know?"**:
Exposing public `virtual` functions directly in C++ base classes creates fragile APIs. Client code can override virtual methods while bypassing class invariants, pre-condition checks, or synchronization locks.

To eliminate this architectural risk, modern C++ leverages the **Non-Virtual Interface (NVI) Pattern** (a concrete realization of the Template Method Pattern). Under NVI, public interface methods are strictly **non-virtual**, while customization hooks are declared as `private` or `protected` **virtual** methods.

Furthermore, understanding the underlying **Virtual Table (`vtable`)** and **Virtual Pointer (`vptr`)** layout explains why calling virtual methods incurs runtime pointer indirections and disables compiler inline optimizations.

**The Code Snippet**:
```cpp
#include <iostream>
#include <memory>
#include <chrono>

// NON-VIRTUAL INTERFACE (NVI) PATTERN CLASS
class DatabaseConnection {
public:
    virtual ~DatabaseConnection() = default;

    // Public Non-Virtual Interface method enforcing invariants & metrics logging
    void executeQuery(const std::string& query) {
        // Step 1: Pre-condition invariant check / locking
        std::cout << "[NVI Core] Validating query connection & starting transaction...\n";
        auto start = std::chrono::high_resolution_clock::now();

        // Step 2: Delegate customization behavior to private virtual hook
        doExecuteQuery(query);

        // Step 3: Post-condition cleanup / telemetry
        auto end = std::chrono::high_resolution_clock::now();
        std::cout << "[NVI Core] Transaction committed cleanly.\n";
    }

private:
    // Private Virtual Customization Hook
    virtual void doExecuteQuery(const std::string& query) = 0;
};

class PostgresConnection : public DatabaseConnection {
private:
    void doExecuteQuery(const std::string& query) override {
        std::cout << "  [PostgresConnection] Executing SQL via libpq: " << query << "\n";
    }
};

int main() {
    std::unique_ptr<DatabaseConnection> db = std::make_unique<PostgresConnection>();

    // Client invokes public non-virtual interface method
    db->executeQuery("SELECT * FROM audit_logs;");

    // Memory Layout Inspection:
    // sizeof(DatabaseConnection) includes 8 bytes for vptr (on 64-bit systems)
    std::cout << "\nSize of DatabaseConnection instance: " << sizeof(*db) << " bytes (includes vptr)\n";

    return 0;
}
```

**Under the Hood / Why It Happens**:
1. **Virtual Table Layout (`vtable` & `vptr`)**:
   When a class declares or inherits at least one `virtual` function:
   - The C++ compiler generates a static array of function pointers called the **vtable** for that class.
   - The compiler secretly inserts a hidden pointer field—the **`vptr`**—at byte offset 0 of the object layout.

2. **Virtual Call Mechanics**:
   Executing `obj->virtualFunc()` requires two runtime memory dereferences:
   - Read object memory address to locate `vptr` pointer (`vptr = obj->vptr`).
   - Look up the function pointer index inside `vtable` (`func_ptr = vptr[index]`).
   - Execute call to `func_ptr`.

3. **Why NVI Improves Architecture & Performance**:
   - In standard public virtual classes, invariant checking must be repeated inside *every derived class override*. If a derived class developer forgets to log metrics or acquire a mutex, invariants fail silently.
   - Under NVI, pre/post checks reside once in the public non-virtual method. Because the public entry point is non-virtual, calling code executes the invariant checks inline, while calling private virtual hooks only for derived custom steps.

**Key Takeaway / Safe Pattern**:
- Prefer Non-Virtual Interface (NVI) design: keep base class public methods **non-virtual**, and declare customization hooks as **`private` or `protected` virtual** functions.
- Declare base class destructors as `public virtual` (or `protected non-virtual`) to guarantee proper object destruction when deleting derived pointers.
- Be mindful of `vptr` memory padding overhead when defining millions of small polymorphic objects in memory-constrained environments.
