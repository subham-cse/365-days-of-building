# Day 132: C++ Move Semantics & Use-After-Move Traps

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
C++11 introduced rvalue references (`&&`) and move semantics (`std::move`) to eliminate expensive deep copies when transferring ownership of resources (like dynamically allocated heap buffers). However, moving an object does NOT destroy it or set its pointer to `nullptr` automatically!

In the C++ Standard Library, a moved-from object is left in a **"valid but unspecified state"**. Accessing methods or dereferencing internal state on a moved-from object without re-initializing it leads to subtle runtime bugs, memory corruption, or undefined behavior depending on how the type's move constructor was implemented.

**The Code Snippet**:
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <utility>

struct BufferOwner {
    std::string name;
    std::vector<int> data;

    BufferOwner(std::string n, std::vector<int> d) 
        : name(std::move(n)), data(std::move(d)) {}
};

int main() {
    std::vector<int> numbers = {10, 20, 30, 40, 50};
    
    // Transfer ownership of 'numbers' vector into object
    BufferOwner owner("PrimaryBuffer", std::move(numbers));

    // TRAP: 'numbers' is now in a valid but unspecified state!
    std::cout << "Original vector size after move: " << numbers.size() << std::endl;

    // BAD PRACTICE: Accessing elements of moved-from container
    // Undefined behavior or exception depending on implementation!
    if (!numbers.empty()) {
        std::cout << "First element: " << numbers[0] << std::endl;
    } else {
        std::cout << "Vector was emptied by std::move!" << std::endl;
    }

    // SAFE RE-USE: Re-assigning or clearing moved object resets its state deterministically
    numbers = {1, 2, 3};
    std::cout << "Re-initialized vector size: " << numbers.size() << std::endl;

    return 0;
}
```

**Under the Hood / Why It Happens**:
`std::move(x)` is nothing more than a static cast to an rvalue reference `static_cast<T&&>(x)`. It performs zero operational execution at runtime. 

The actual work happens inside the target class's move constructor:
```cpp
vector(vector&& other) noexcept 
    : data_ptr(other.data_ptr), size_(other.size_) {
    other.data_ptr = nullptr; // Nullifies original pointer
    other.size_ = 0;
}
```
For standard library containers like `std::vector` or `std::string`, the move constructor clears internal capacity or pointer members. However, custom user-defined types might leave pointers dangling or primitive values unchanged if move constructors are defaulted or incorrectly written. Relying on any specific field value of a moved-from variable violates ISO C++ guarantees.

**Key Takeaway / Safe Pattern**:
Treat moved-from variables as uninitialized. Never read state from an object passed to `std::move()` unless you explicitly reassign a new value to it (`x = newValue`) or call a method with explicitly documented post-move guarantees (such as `std::shared_ptr::reset()`).
