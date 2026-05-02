# Day 171: Method Lookup Chain: Prepend vs Include vs Extend

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
Ruby uses a dynamic method lookup chain (`ancestors`) to resolve method invocations. When a method is called on an object, Ruby traverses up the class and module inheritance hierarchy from left to right until it finds a matching method implementation.

Modules can be attached to classes using `include`, `prepend`, or `extend`. Understanding the difference between `include` and `prepend` is critical: `include` places the module *after* the class in the lookup chain (allowing the class to override module methods), whereas `prepend` inserts the module *before* the class in the lookup chain (allowing the module to intercept calls and invoke `super` to delegate to the class!).

**The Code Snippet**:

```ruby
module LoggerAspect
  def process(data)
    puts "[LOG] Processing started for: #{data}"
    res = super(data) # Calls the next entry in the ancestors lookup chain!
    puts "[LOG] Processing finished with result: #{res}"
    res
  end
end

module Helper
  def process(data)
    "Helper: #{data.upcase}"
  end
end

class StandardWorker
  include Helper
  def process(data)
    "StandardWorker: #{data}"
  end
end

class PrependedWorker
  prepend LoggerAspect
  def process(data)
    "PrependedWorker: #{data.downcase}"
  end
end

# 1. Standard Worker Ancestors: [StandardWorker, Helper, Object, Kernel, BasicObject]
w1 = StandardWorker.new
puts w1.process("Test") 
# Output: "StandardWorker: Test" (Class overrides included Helper module!)

# 2. Prepended Worker Ancestors: [LoggerAspect, PrependedWorker, Object, Kernel, BasicObject]
w2 = PrependedWorker.new
puts w2.process("Test")
# Output:
# [LOG] Processing started for: Test
# [LOG] Processing finished with result: PrependedWorker: test
# PrependedWorker: test
```

**Under the Hood / Why It Happens**:
Every Ruby class (`RClass` struct in C MRI) maintains an internal `super` pointer to its parent class or included module wrapper (`IClass`).

When `include ModuleA` is executed:
Ruby creates an `IClass` proxy node for `ModuleA` and inserts it between `MyClass` and `MyClass.super`.
Lookup order: `MyClass` $\rightarrow$ `ModuleA` $\rightarrow$ `SuperClass`.

When `prepend ModuleB` is executed:
Ruby inserts `ModuleB`'s `IClass` proxy node *ahead* of `MyClass` in the ancestors array.
Lookup order: `ModuleB` $\rightarrow$ `MyClass` $\rightarrow$ `SuperClass`.

This makes `prepend` a clean tool for implementing aspect-oriented programming (AOP), wrapping method calls without polluting monkey-patching patterns.

**Key Takeaway / Safe Pattern**:
Use `include` when adding reusable utility capabilities to a class. Use `prepend` when writing middleware, interceptors, or decorators that need to wrap existing class methods and call `super`.
