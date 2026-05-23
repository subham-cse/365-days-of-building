# Day 199: Ruby Method Lookup Chain and Eigenclass Dispatch

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, everything is an object, and method execution is conceptually "message passing". When you invoke a method on a Ruby object (`object.my_method`), Ruby traverses a precise, deterministic hierarchy called the **Method Lookup Chain**.

What surprises many developers is that methods defined on a specific instance (singleton methods or class methods) do not live directly on the object's class. Instead, Ruby dynamically inserts a hidden, anonymous class into the object's hierarchy known as the **Eigenclass** (also called the Singleton Class or Metaclass). Understanding where modules (`include` vs `prepend`) inject themselves into the Eigenclass hierarchy is critical for metaprogramming and debugging monkey-patched methods.

**The Code Snippet**:
```ruby
class Logger
  def log(msg)
    "Base Logger: #{msg}"
  end
end

module CustomPrefix
  def log(msg)
    "Prefix: #{super(msg)}"
  end
end

module TimestampWrapper
  def log(msg)
    "Timestamp: #{super(msg)}"
  end
end

class ApplicationLogger < Logger
  include CustomPrefix
  prepend TimestampWrapper

  # Singleton method defined on specific instance
end

app_log = ApplicationLogger.new

# Attach singleton method to single instance eigenclass
def app_log.log(msg)
  "Eigenclass Override: #{msg}"
end

puts app_log.log("System initialized")
# Output: Eigenclass Override: System initialized

# Inspecting the exact Ancestor Lookup Chain
puts ApplicationLogger.ancestors.inspect
# Output: [TimestampWrapper, ApplicationLogger, CustomPrefix, Logger, Object, Kernel, BasicObject]
```

**Under the Hood / Why It Happens**:
When `app_log.log(...)` is invoked, CRuby's method search algorithm executes the following sequence:

1. **Eigenclass (`#<Class:#<ApplicationLogger>>`)**: Inspects the object's hidden singleton class. If a singleton method exists, it executes immediately.
2. **Prepended Modules (`TimestampWrapper`)**: Inspects modules added via `prepend`. Prepended modules sit *before* the class itself in the lookup chain.
3. **Class (`ApplicationLogger`)**: Inspects instance methods defined inside the class definition.
4. **Included Modules (`CustomPrefix`)**: Inspects modules added via `include`. Included modules sit *after* the class but *before* its superclass.
5. **Superclass (`Logger`)**: Traverses up the inheritance tree to `Logger`, `Object`, `Kernel`, and `BasicObject`.
6. **`method_missing`**: If the method is not found in any level, Ruby restarts the lookup chain from step 1 looking for `method_missing`.

**Key Takeaway / Safe Pattern**:
Use `prepend` when you need to intercept and wrap class methods (acting as middleware before class methods run), and `include` when adding mixin capability methods meant to be overridden by the host class. Inspect method locations using `.ancestors` and `.singleton_class.ancestors`.

```ruby
# Safe Pattern: Inspecting eigenclasses and method resolution order
obj = ApplicationLogger.new
puts obj.singleton_class.ancestors.inspect
# Shows the complete lookup order including prepended modules and eigenclasses
```
