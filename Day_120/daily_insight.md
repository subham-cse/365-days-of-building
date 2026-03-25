# Day 120: RAII Traps and Move Semantics Pitfalls
- **Language / Domain**: C++
- **The Core Concept / "Did You Know?"**: In modern C++, **RAII (Resource Acquisition Is Initialization)** manages memory and OS handles automatically via constructors and destructors.

However, move semantics (`std::move`) can introduce subtle traps: moving an object leaves the source object in a "valid but unspecified state". If a move constructor fails to reset raw pointers in the moved-from instance to `nullptr`, the moved-from instance's destructor will execute on the original resource when it goes out of scope, causing a **double free** crash!

- **The Code Snippet**:
```cpp
#include <iostream>
#include <utility>

class Buffer {
private:
    int* data_;
    size_t size_;

public:
    Buffer(size_t size) : size_(size), data_(new int[size]) {
        std::cout << "Allocated " << size_ << " ints\n";
    }

    ~Buffer() {
        if (data_) {
            std::cout << "Freeing memory at " << data_ << "\n";
            delete[] data_;
        }
    }

    // Move Constructor - BUGGY (Missing reset of source pointer!)
    /*
    Buffer(Buffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        // BUG: did NOT set other.data_ = nullptr!
    }
    */

    // Move Constructor - SAFE
    Buffer(Buffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr; // Crucial: clear moved-from object pointer!
        other.size_ = 0;
    }

    // Disable copying for unique RAII ownership
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
};

int main() {
    Buffer b1(100);
    Buffer b2 = std::move(b1); // Move ownership from b1 to b2

    std::cout << "Move completed successfully.\n";
    return 0; // Safe destructor execution on b2, followed by no-op destructor on b1!
}
```

- **Under the Hood / Why It Happens**:
`std::move` does not move anything by itself; it is merely an unconditional static cast (`static_cast<T&&>`) converting an lvalue reference into an rvalue reference to enable move constructor resolution.

If the move constructor copies the pointer bitwise without setting `other.data_ = nullptr`, both instances end up holding duplicate address pointers to the same heap buffer. When the function scope unwinds, stack destruction unwinds in reverse order, calling `delete[]` twice on identical memory addresses.

- **Key Takeaway / Safe Pattern**:
Always set moved-from pointer resources to `nullptr` inside custom move constructors and move assignment operators, or prefer using standard RAII wrappers like `std::unique_ptr` and `std::vector` which implement move constructors correctly out of the box.
