# Day 227: Ruby Method Lookup Chain: `prepend` vs `include` vs Ancestors

**Language / Domain**: Ruby / Metaprogramming & Object Model

**The Core Concept / "Did You Know?"**:
In Ruby, classes do not simply copy methods when mixin modules are added. Instead, Ruby modifies the target class's **Ancestors Lookup Chain** (`Class.ancestors`).

Two primary module insertion methods exist: `include` and `prepend`.
- **`include Module`**: Inserts the module into the ancestor chain *directly after* (above) the class. If the class defines a method with the same name, the class's method takes precedence and executes first.
- **`prepend Module`**: Inserts the module into the ancestor chain *directly before* (below) the class. The prepended module overrides the class's own method! Calling `super` inside a prepended module delegates execution down to the class's method implementation.

**The Code Snippet**:
```ruby
module TraceInclude
  def execute(action)
    puts "[Include Module] Before action"
    res = super(action) if defined?(super)
    puts "[Include Module] After action"
    res
  end
end

module TracePrepend
  def execute(action)
    puts "[Prepend Module] Intercepted execution before Class!"
    # 'super' delegates execution down into WorkerClass#execute!
    res = super(action)
    puts "[Prepend Module] Intercepted execution after Class!"
    res
  end
end

class BaseWorker
  def execute(action)
    puts "[BaseWorker] Core implementation: #{action}"
    :base_ok
  end
end

class WorkerWithInclude < BaseWorker
  include TraceInclude

  def execute(action)
    puts "[WorkerWithInclude] Class method executing..."
    super(action)
  end
end

class WorkerWithPrepend < BaseWorker
  prepend TracePrepend

  def execute(action)
    puts "[WorkerWithPrepend] Class method executing..."
    super(action)
  end
end

puts "=== Ancestors for WorkerWithInclude ==="
puts WorkerWithInclude.ancestors.inspect
# Output: [WorkerWithInclude, TraceInclude, BaseWorker, Object, ...]

puts "\n=== Executing WorkerWithInclude ==="
WorkerWithInclude.new.execute("Data Processing")

puts "\n=== Ancestors for WorkerWithPrepend ==="
puts WorkerWithPrepend.ancestors.inspect
# Output: [TracePrepend, WorkerWithPrepend, BaseWorker, Object, ...]

puts "\n=== Executing WorkerWithPrepend ==="
WorkerWithPrepend.new.execute("Data Processing")
```

**Under the Hood / Why It Happens**:
Ruby resolves method calls by scanning the receiver's singleton class and ancestor chain sequentially from left to right:

1. **`include TraceInclude`**:
   Ruby creates an internal *Include Class* wrapper holding a reference to `TraceInclude`'s method table and inserts it right after `WorkerWithInclude`:
   `WorkerWithInclude` -> `TraceInclude` -> `BaseWorker` -> `Object` -> `Kernel` -> `BasicObject`
   When `WorkerWithInclude#execute` is invoked, Ruby finds `execute` in `WorkerWithInclude` first. `TraceInclude#execute` is never hit unless `WorkerWithInclude#execute` explicitly calls `super`.

2. **`prepend TracePrepend`**:
   Ruby places `TracePrepend` *ahead* of `WorkerWithPrepend` in the resolution chain:
   `TracePrepend` -> `WorkerWithPrepend` -> `BaseWorker` -> `Object` -> `Kernel` -> `BasicObject`
   When `execute` is invoked on an instance of `WorkerWithPrepend`, Ruby visits `TracePrepend` first. `TracePrepend#execute` fires immediately, wrapping around `WorkerWithPrepend#execute` when `super` is called.

**Key Takeaway / Safe Pattern**:
- Use `prepend` when building aspect-oriented wrappers, monkey-patching libraries, or tracing/timing decorators where you must intercept methods *before* the class's own implementation runs.
- Use `include` when adding reusable utility behaviors or default trait implementations that the host class should be able to override.
- Always inspect `Class.ancestors` when debugging unexpected method override behaviors or dynamic `alias_method` bugs in Ruby codebase frameworks.
