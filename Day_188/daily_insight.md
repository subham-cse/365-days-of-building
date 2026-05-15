# Day 188: C++ Object Slicing in Polymorphic Value Semantics

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, dynamic polymorphism relies on virtual function tables (`vtable`) accessed via pointers or references. When a derived class object is assigned to a base class object **by value** (or passed into a function taking a parameter by value), **Object Slicing** occurs.

During object slicing, the compiler copies only the base class portion of the derived object into the new base instance. All derived class member fields are completely discarded ("sliced off"), and the vtable pointer (`vptr`) is overwritten to point to the Base class vtable. As a result, virtual function calls on the sliced object resolve strictly to the Base class implementation, completely disabling polymorphic behavior.

**The Code Snippet**:
```cpp
#include <iostream>
#include <string>

class Animal {
public:
    virtual void speak() const {
        std::cout << "Generic animal sound\n";
    }
    virtual ~Animal() = default;
};

class Dog : public Animal {
private:
    std::string breed = "Golden Retriever";
public:
    void speak() const override {
        std::cout << "Woof! I am a " << breed << "\n";
    }
};

// TRAP: Parameter passed BY VALUE causes Object Slicing
void describeAnimalValue(Animal animal) {
    animal.speak(); // Invokes Animal::speak(), NOT Dog::speak()!
}

// SAFE: Parameter passed BY REFERENCE preserves Polymorphism
void describeAnimalRef(const Animal& animal) {
    animal.speak(); // Invokes Dog::speak()
}

int main() {
    Dog myDog;
    
    std::cout << "Pass by Value output: ";
    describeAnimalValue(myDog); // Output: Generic animal sound
    
    std::cout << "Pass by Reference output: ";
    describeAnimalRef(myDog);   // Output: Woof! I am a Golden Retriever
    
    return 0;
}
```

**Under the Hood / Why It Happens**:
When `describeAnimalValue(Animal animal)` is invoked with `myDog`:
1. The compiler allocates memory on the stack frame sized strictly for `sizeof(Animal)`.
2. It executes `Animal::Animal(const Animal&)` copy constructor.
3. The derived payload (`breed` std::string) exceeds `sizeof(Animal)` and cannot fit in the target stack location.
4. The internal `vptr` (virtual pointer) of the newly constructed `Animal` on the stack points directly to `Animal`'s vtable (`&Animal::vtable`).
5. Calling `animal.speak()` performs a vtable lookup on `Animal`'s vtable, invoking `Animal::speak()`.

**Key Takeaway / Safe Pattern**:
Always pass polymorphic base class parameters by reference (`const Base&`) or smart pointers (`std::shared_ptr<Base>`, `std::unique_ptr<Base>`). To prevent slicing at compile time, declare base class copy constructors as `= delete` or make base classes abstract with pure virtual functions.

```cpp
class AbstractAnimal {
public:
    virtual void speak() const = 0; // Pure virtual makes Base abstract
    AbstractAnimal() = default;
    AbstractAnimal(const AbstractAnimal&) = delete; // Prevents slicing assignment
    virtual ~AbstractAnimal() = default;
};
```
