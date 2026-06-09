# Day 216: C++ Object Slicing with Polymorphic Value Semantics

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, passing derived objects by value to functions expecting base type parameters causes **Object Slicing**. When a derived class instance is copied into a value parameter of a base class type, the compiler constructs a new object of the base type, retaining only the base class member variables and virtual function pointer (`vptr`). All derived class fields and dynamic polymorphism overrides are completely stripped away ("sliced off").

This leads to subtle logical bugs: dynamic dispatch is disabled, virtual method calls execute base implementations, and derived state vanishes without any compiler warning.

**The Code Snippet**:
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>

class BaseTask {
public:
    std::string task_name;
    BaseTask(std::string name) : task_name(std::move(name)) {}
    virtual ~BaseTask() = default;

    virtual void execute() const {
        std::cout << "[BaseTask] Executing basic task: " << task_name << "\n";
    }
};

class SecurityAuditTask : public BaseTask {
public:
    int clearance_level;
    SecurityAuditTask(std::string name, int clearance)
        : BaseTask(std::move(name)), clearance_level(clearance) {}

    void execute() const override {
        std::cout << "[SecurityAuditTask] Running audit for: " << task_name
                  << " with Level " << clearance_level << "\n";
    }
};

// SLICING BUG: Parameter taken by value
void dispatchTaskByValue(BaseTask task) {
    task.execute(); // Always calls BaseTask::execute!
}

// SAFE PATTERN: Parameter taken by reference to const
void dispatchTaskByRef(const BaseTask& task) {
    task.execute(); // Correctly invokes SecurityAuditTask::execute via vtable
}

int main() {
    SecurityAuditTask audit("Database Encryption Check", 5);

    std::cout << "--- Value Passing (Object Slicing) ---\n";
    dispatchTaskByValue(audit); // Slicing occurs here!

    std::cout << "\n--- Reference Passing (Polymorphic) ---\n";
    dispatchTaskByRef(audit);

    return 0;
}
```

**Under the Hood / Why It Happens**:
Memory layout explains why slicing occurs:
1. An instance of `SecurityAuditTask` contains:
   - `BaseTask::vptr` (points to `SecurityAuditTask`'s vtable)
   - `BaseTask::task_name`
   - `SecurityAuditTask::clearance_level`

2. When `dispatchTaskByValue(BaseTask task)` is invoked:
   - The compiler emits a call to `BaseTask`'s copy constructor: `BaseTask(const BaseTask&)`.
   - The copy constructor constructs a raw `BaseTask` on the function call stack.
   - The `vptr` of this new stack object is initialized to point to `BaseTask`'s vtable (not `SecurityAuditTask`'s vtable).
   - `clearance_level` cannot fit into the memory allocation of `BaseTask` and is ignored.

When `task.execute()` executes inside `dispatchTaskByValue`, the runtime inspects `task`'s `vptr`, finds `BaseTask::execute`, and calls it directly.

**Key Takeaway / Safe Pattern**:
- **Pass polymorphic parameters by reference or pointer**: Use `const BaseClass&`, `BaseClass*`, `std::unique_ptr<BaseClass>`, or `std::shared_ptr<BaseClass>`.
- **Make base classes abstract or prevent value copying**: Declare base class copy constructors and copy assignment operators as `delete` or `protected`:
  ```cpp
  class BaseTask {
  protected:
      BaseTask(const BaseTask&) = default;
      BaseTask& operator=(const BaseTask&) = default;
  public:
      virtual ~BaseTask() = default;
  };
  ```
  This causes any accidental object slicing at a callsite to trigger a compile-time error.
