# Day 104: Object Slicing in Virtual Function Hierarchies
- **Language / Domain**: C++
- **The Core Concept / "Did You Know?"**: In C++, pass-by-value of derived objects into functions expecting a base type causes **Object Slicing**. When a derived class instance is assigned or passed by value to a base class object, the compiler copies only the base portion of the object, stripping away the derived members and resetting the virtual method table (vptr) to point to the base class!

As a result, runtime polymorphism is lost entirely, and calls to virtual functions resolve strictly to the base class implementation.

- **The Code Snippet**:
```cpp
#include <iostream>
#include <memory>

class Base {
public:
    virtual void speak() const {
        std::cout << "Base animal sound\n";
    }
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    void speak() const override {
        std::cout << "Derived dog bark!\n";
    }
};

// TRAP: Passed by value causes object slicing!
void make_it_speak_sliced(Base b) {
    b.speak(); // Always calls Base::speak()
}

// SAFE: Passed by reference preserves polymorphism
void make_it_speak_ref(const Base& b) {
    b.speak(); // Polymorphic: calls Derived::speak()
}

int main() {
    Derived d;
    
    std::cout << "--- Passed by Value (Sliced) ---\n";
    make_it_speak_sliced(d); // Output: Base animal sound

    std::cout << "--- Passed by Reference ---\n";
    make_it_speak_ref(d); // Output: Derived dog bark!

    return 0;
}
```

- **Under the Hood / Why It Happens**:
Every polymorphic C++ object contains a hidden pointer `vptr` pointing to its class `vtable`. 

When `make_it_speak_sliced(Base b)` is invoked, `Base`'s copy constructor is executed: `Base::Base(const Base&)`. This constructor initializes `b` as a pure `Base` instance, setting its `vptr` to `Base::vtable`. The additional memory occupied by `Derived`'s fields is sliced off during stack frame layout allocation for the function parameter.

- **Key Takeaway / Safe Pattern**:
To retain polymorphic behavior, always pass polymorphic class instances by reference (`const Base&`) or smart pointers (`std::shared_ptr<Base>`, `std::unique_ptr<Base>`). Mark base class copy constructors deleted or protected if slicing should be strictly prevented at compile-time.
