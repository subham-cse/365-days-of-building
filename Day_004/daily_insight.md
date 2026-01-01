# Day 004: Undefined Behavior in Constructing Objects with `this` in Initializer Lists
**Language / Domain**: C++

**The Core Concept / "Did You Know?"**:
In C++, passing `this` to another object's constructor or calling virtual functions within member initializer lists can result in subtlest forms of undefined behavior or broken invariants. While syntactically valid, the object pointed to by `this` is only partially constructed while executing its member initializer list. 

If a member initialized early in the list attempts to store or call methods on `this`, it accesses fields that have not yet been initialized. Even worse, if virtual functions are invoked through `this` before the constructor body runs, dynamic dispatch uses the class hierarchy corresponding to the currently executing constructor stage, not the ultimate derived class implementation.

**The Code Snippet**:
```cpp
#include <iostream>
#include <memory>
#include <string>

class Window;

class Observer {
public:
    virtual void onInit(Window* win) = 0;
    virtual ~Observer() = default;
};

class EventLogger : public Observer {
public:
    void onInit(Window* win) override;
};

class Window {
private:
    std::string title_;
    Observer& observer_;

public:
    Window(std::string title, Observer& obs)
        : observer_(obs),
          title_(std::move(title)) 
    {
        // RISKY: observer_.onInit(this) called during construction!
        // At this point, title_ IS initialized because title_ is listed AFTER observer_?
        // NO! Initialization order depends ONLY on member declaration order in the class!
    }

    const std::string& getTitle() const { return title_; }
};

class BuggyWindow {
private:
    Observer& observer_; // Declared FIRST!
    std::string title_;  // Declared SECOND!

public:
    BuggyWindow(std::string title, Observer& obs)
        : title_(std::move(title)),  // Written first in list, but initialized SECOND!
          observer_(obs)              // Initialized FIRST, but observer_.onInit uses title_!
    {
        observer_.onInit(this); // Pass partially initialized `this`
    }

    const std::string& getTitle() const { return title_; }
};

void EventLogger::onInit(Window* win) {
    // If called during member initialization before title_ is set: undefined behavior / crash!
    std::cout << "Window initialized with title: " << win->getTitle() << std::endl;
}

int main() {
    EventLogger logger;
    Window win("Main Dashboard", logger);
    return 0;
}
```

**Under the Hood / Why It Happens**:
In C++, members are initialized strictly in the order they are **declared in the class definition**, completely ignoring the order in which they appear in the member initializer list. 

In `BuggyWindow`, `observer_` is declared before `title_`. Therefore, `observer_`'s initializer runs first. If `observer_.onInit(this)` is called directly or indirectly inside `observer_`'s constructor, it attempts to dereference `this->title_`, which is raw uninitialized memory. Furthermore, during object construction, the vtable pointer (`vptr`) is updated sequentially as each base class and derived class constructor executes, meaning virtual calls do not resolve to derived overrides until construction completes.

**Key Takeaway / Safe Pattern**:
Never pass `this` to external observers or call member methods relying on uninitialized state inside member initializer lists. Perform registrations or callbacks inside the constructor body after all members are guaranteed to be initialized, or use a static factory method combined with a private constructor.

```cpp
class SafeWindow {
private:
    std::string title_;
    Observer& observer_;

    // Private constructor: only initializes data members
    SafeWindow(std::string title, Observer& obs)
        : title_(std::move(title)), observer_(obs) {}

public:
    static std::unique_ptr<SafeWindow> create(std::string title, Observer& obs) {
        auto win = std::unique_ptr<SafeWindow>(new SafeWindow(std::move(title), obs));
        obs.onInit(win.get()); // Safe: Object fully constructed!
        return win;
    }
};
```
