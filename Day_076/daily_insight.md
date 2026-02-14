# Day 076: Object Slicing and Virtual Destructor Traps in C++

**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, polymorphism only works when accessing derived objects through references (`Derived&`) or pointers (`Derived*`). Assigning a derived class object to a base class value object results in **Object Slicing**: the derived part of the object is discarded ("sliced off"), leaving only the base subobject.

A related memory safety trap involves polymorphic base classes lacking virtual destructors. If you delete a derived object through a base class pointer (`Base* b = new Derived()`), and `Base` does not declare a `virtual ~Base()`, C++ triggers **Undefined Behavior**. The derived class constructor runs, but its destructor is never invoked, leaking resources and skipping memory cleanup.

**The Code Snippet**:
```cpp
#include <iostream>
#include <memory>
#include <string>

class BaseSensor {
public:
    std::string name;
    
    BaseSensor(std::string n) : name(std::move(n)) {}
    
    // TRAP 1: Non-virtual destructor in polymorphic base class!
    // SHOULD BE: virtual ~BaseSensor() = default;
    ~BaseSensor() {
        std::cout << "~BaseSensor destructor called for " << name << "\n";
    }

    virtual void measure() const {
        std::cout << "Base sensor measuring...\n";
    }
};

class TemperatureSensor : public BaseSensor {
public:
    double* buffer;

    TemperatureSensor(std::string n) : BaseSensor(std::move(n)) {
        buffer = new double[100]; // Heap allocation
    }

    ~TemperatureSensor() {
        std::cout << "~TemperatureSensor cleanup: freeing double buffer\n";
        delete[] buffer;
    }

    void measure() const override {
        std::cout << "Measuring ambient temperature: 24.5C\n";
    }
};

int main() {
    std::cout << "--- TRAP 1: Object Slicing ---\n";
    TemperatureSensor tempSensor("Sensor_A");
    
    // Slicing occurs here! Pass by value slices off Derived data & vtable!
    BaseSensor slicedSensor = tempSensor; 
    slicedSensor.measure(); // Output: Base sensor measuring... (Polymorphism LOST!)

    std::cout << "\n--- TRAP 2: Undefined Behavior via Non-Virtual Destructor ---\n";
    BaseSensor* polySensor = new TemperatureSensor("Sensor_B");
    polySensor->measure(); // Output: Measuring ambient temperature...
    
    // UNDEFINED BEHAVIOR: ~TemperatureSensor() is NEVER CALLED! Buffer leaks!
    delete polySensor; 

    return 0;
}
```

**Under the Hood / Why It Happens**:
In C++, an object's vtable pointer (`vptr`) is stored at offset 0 of the object layout. 

When object slicing occurs (`BaseSensor slicedSensor = tempSensor`), the C++ compiler invokes `BaseSensor`'s copy constructor, copying only the `name` member field into a newly allocated stack location sized strictly for `sizeof(BaseSensor)`. The `TemperatureSensor` fields (`buffer`) and its derived vtable pointer are completely omitted.

When invoking `delete polySensor`, the compiler checks `BaseSensor`'s vtable for destructor offset. Since `~BaseSensor()` is non-virtual, the compiler performs static dispatch, directly invoking `BaseSensor::~BaseSensor()` while bypassing `TemperatureSensor::~TemperatureSensor()`. Memory allocated inside `TemperatureSensor` is leaked permanently.

**Key Takeaway / Safe Pattern**:
Always declare base class destructors `virtual` (e.g., `virtual ~BaseClass() = default;`) if any method in the class is `virtual`. To prevent object slicing, pass polymorphic objects exclusively via references (`const Base&`) or smart pointers (`std::unique_ptr<Base>`). Mark base copy constructors `delete` if instantiation by value should be prevented.
