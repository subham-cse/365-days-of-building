# Day 015: Method Lookup Chains, Open Class Monkey Patching, and Block vs Proc vs Lambda Semantics
**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, every object lookup traverses a strict **Method Lookup Chain**: `Singleton Class (Eigenclass) -> Modules (in reverse include order) -> Superclass -> Object -> Kernel -> BasicObject`. Modifying core classes at runtime (Monkey Patching) affects all instances globally across the application, introducing mysterious bugs when third-party gems patch overlapping methods.

Furthermore, Ruby distinguishes between **Blocks**, **Procs**, and **Lambdas**. A `Proc` handles argument count loosely and performs a **top-level method return** (exiting the enclosing method immediately), whereas a `Lambda` checks argument arity strictly and returns control back to the caller.

**The Code Snippet**:
```ruby
# Trap 1: Monkey Patching Global Core Classes
class String
  def blank?
    self.strip.empty?
  end
end

# Third-party library monkey-patches String differently elsewhere!
class String
  def blank?
    # Overwrites previous definition globally!
    self.nil? || self.strip.length == 0
  end
end

# Trap 2: Return Semantics in Proc vs Lambda
def proc_return_trap
  bad_proc = Proc.new { return "Returned from Proc!" }
  bad_proc.call # Immediately exits proc_return_trap method!
  
  "This code will NEVER be reached!"
end

def lambda_return_safe
  good_lambda = -> { return "Returned from Lambda!" }
  result = good_lambda.call # Returns string to caller, execution continues!
  
  "Method execution finished successfully. Lambda got: #{result}"
end

puts proc_return_trap   # Output: "Returned from Proc!"
puts lambda_return_safe # Output: "Method execution finished successfully..."
```

**Under the Hood / Why It Happens**:
Ruby's object model represents classes as instances of `Class`. When a class is re-opened (`class String`), Ruby doesn't create a new class; it modifies the existing `RClass` struct in memory, inserting or overwriting method entries in its internal method table (`m_tbl`).

For return semantics, `Proc.new` creates a closure bound to its surrounding lexical execution context (`rb_control_frame_t`). Executing `return` inside a `Proc` issues a return instruction targeting the frame of the **enclosing method** where the `Proc` was defined. If that enclosing frame has already popped off the call stack, Ruby raises a `LocalJumpError: unexpected return`. A `Lambda` behaves like an anonymous method: its `return` pops only the lambda's execution frame.

**Key Takeaway / Safe Pattern**:
Avoid global class monkey patching. Use Ruby **Refinements** (`using MyRefinement`) to restrict monkey patches strictly to the current file or module scope. Favor `lambdas` (`-> {}`) over `Proc.new` when storing reusable callables to ensure clean return control flow.

```ruby
# SAFE Pattern: Ruby Refinements scope monkey-patches safely
module StringExtensions
  refine String do
    def safe_blank?
      strip.empty?
    end
  end
end

class UserPresenter
  using StringExtensions # Refinement enabled ONLY within this class scope!

  def initialize(name)
    @name = name
  end

  def valid?
    !@name.safe_blank?
  end
end

# Outside UserPresenter, String#safe_blank? is completely undefined!
```
