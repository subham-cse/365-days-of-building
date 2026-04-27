# Day 160: Polymorphic Object Slicing in Pass-By-Value Assignments

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, when a derived class instance is assigned or passed by value to a variable or parameter of a base class type, only the base portion of the object is copied. The derived class fields, custom state, and virtual method implementations are discarded—a silent memory issue called **Object Slicing**.

Object slicing strips away polymorphism completely: the resulting object is stripped down to an instance of the base class, and its vtable pointer (`vptr`) is updated to point to the base class vtable.

**The Code Snippet**:

```cpp
#include <iostream>
#include <memory>
#include <string>

class Base {
public:
    std::string name;
    Base(std::string n) : name(std::move(n)) {}
    virtual void describe() const {
        std::cout << "[Base] Name: " << name << std::endl;
    }
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    int extra_data;
    Derived(std::string n, int data) : Base(std::move(n)), extra_data(data) {}
    void describe() const override {
        std::cout << "[Derived] Name: " << name << " | Extra: " << extra_data << std::endl;
    }
};

// BUG: Parameter passed by value causes object slicing!
void print_sliced(Base b) {
    b.describe(); // Calls Base::describe(), NOT Derived::describe()!
}

// SAFE: Parameter passed by reference preserves polymorphic vtable dispatch
void print_safe(const Base& b) {
    b.describe(); // Calls Derived::describe() as expected!
}

int main() {
    Derived d("PolymorphicObj", 42);
    
    std::cout << "--- Passed by Value (Sliced) ---" << std::endl;
    print_sliced(d); 

    std::cout << "--- Passed by Reference (Preserved) ---" << std::endl;
    print_safe(d);
    
    return 0;
}
```

**Under the Hood / Why It Happens**:
In C++'s object memory layout, a `Derived` instance consists of the `Base` layout (vptr + `Base` fields) followed immediately by `Derived` fields in contiguous memory.

When `Base b = d;` or `void print_sliced(Base b)` is invoked, C++ calls `Base`'s copy constructor `Base::Base(const Base&)`. The copy constructor allocates stack space sized strictly to `sizeof(Base)` (ignoring the larger `sizeof(Derived)`). It copies only `Base`'s member fields and initializes `b`'s vptr to point to `Base::vtable`. The memory range corresponding to `extra_data` is left behind and sliced off.

**Key Takeaway / Safe Pattern**:
To prevent object slicing in C++:
1. Pass polymorphic objects using references (`const Base&`) or pointers (`std::shared_ptr<Base>` / `std::unique_ptr<Base>`).
2. Mark base class copy constructors and copy assignment operators as `protected` or `delete` to prevent value copies at compile time.
