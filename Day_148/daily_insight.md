# Day 148: C++ Object Slicing Traps in Polymorphic Collections

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, passing derived class objects by value to functions expecting a base class type, or storing derived instances inside a standard container of base types (e.g. `std::vector<Base>`), triggers **Object Slicing**.

When object slicing occurs, the C++ compiler copies only the base class portion of the derived object, discarding ("slicing off") all derived member variables and resetting the virtual method table pointer (`vptr`) back to the base class! Polymorphic virtual function dispatch is completely lost.

**The Code Snippet**:
```cpp
#include <iostream>
#include <vector>
#include <memory>

class Animal {
public:
    virtual void speak() const {
        std::cout << "Generic Animal sound\n";
    }
    virtual ~Animal() = default;
};

class Dog : public Animal {
public:
    void speak() const override {
        std::cout << "Woof! Woof!\n";
    }
};

// TRAP: Pass by value causes object slicing!
void makeAnimalSpeakSliced(Animal animal) {
    animal.speak(); // Always calls Animal::speak(), Dog part is sliced away!
}

// SAFE PATTERN 1: Pass by reference to base class
void makeAnimalSpeakRef(const Animal& animal) {
    animal.speak(); // Correctly calls Dog::speak() dynamically
}

int main() {
    Dog myDog;

    std::cout << "--- Pass by Value (Sliced) ---\n";
    makeAnimalSpeakSliced(myDog); // Output: Generic Animal sound

    std::cout << "\n--- Pass by Reference (Polymorphic) ---\n";
    makeAnimalSpeakRef(myDog);    // Output: Woof! Woof!

    // TRAP IN CONTAINERS: Vector of value types slices derived objects
    std::vector<Animal> slicedVector;
    slicedVector.push_back(Dog()); // Sliced on copy construction!
    slicedVector[0].speak();       // Output: Generic Animal sound

    // SAFE PATTERN 2: Vector of smart pointers preserves polymorphism
    std::vector<std::unique_ptr<Animal>> polymorphicVector;
    polymorphicVector.push_back(std::make_unique<Dog>());
    polymorphicVector[0]->speak();  // Output: Woof! Woof!

    return 0;
}
```

**Under the Hood / Why It Happens**:
In C++ memory representation:
- A `Dog` object memory footprint consists of: `[ Animal vptr | Base Fields | Dog Fields ]`.
- When `Animal animal = myDog;` is executed, the compiler invokes `Animal`'s copy constructor: `Animal::Animal(const Animal&)`.
- The copy constructor copies only `sizeof(Animal)` bytes into the new stack frame destination. The extra bytes holding `Dog` fields are truncated.
- Crucially, the CPU overwrites the virtual method table pointer (`vptr`) inside the newly constructed `Animal` object so that it points directly to `Animal`'s `vtable`, completely severing dynamic dispatch links to `Dog::speak()`.

**Key Takeaway / Safe Pattern**:
To maintain polymorphic behavior in C++, never pass derived objects by value or store them in containers of value types (`std::vector<Base>`). Always use pass-by-reference (`const Base&`) or containers of smart pointers (`std::vector<std::unique_ptr<Base>>`). Mark base class copy constructors as `protected` or `= delete` to catch slicing errors at compile time.
