# Day 155: Proc vs Lambda Return Jump Semantics

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, blocks, `Proc` objects, and `lambda`s all encapsulate deferred execution logic, but they exhibit fundamentally different behaviors when handling the `return` keyword. A `return` executed inside a `lambda` exits only the lambda itself and returns control to the enclosing caller function. In stark contrast, a `return` executed inside a standard `Proc` (or block) attempts to return directly from the lexical scope (enclosing method) where the `Proc` was defined.

If the enclosing method has already finished executing and exited its stack frame when the `Proc` is invoked, calling `Proc#call` will trigger a fatal `LocalJumpError: unexpected return`.

**The Code Snippet**:

```ruby
def create_proc
  Proc.new { return "Returned from Proc" }
end

def create_lambda
  -> { return "Returned from Lambda" }
end

def test_lambda_behavior
  lam = create_lambda
  result = lam.call
  "Lambda execution success: #{result}"
end

def test_proc_behavior
  prc = create_proc
  # Calling prc here attempts to return from `create_proc`, 
  # which has already returned!
  prc.call
rescue LocalJumpError => e
  "Caught Expected Error: #{e.message}"
end

puts test_lambda_behavior
# Output: Lambda execution success: Returned from Lambda

puts test_proc_behavior
# Output: Caught Expected Error: unexpected return
```

**Under the Hood / Why It Happens**:
Ruby's runtime engine (YARV) tracks control flow instructions using execution frame flags. A `lambda` is created with a `VM_FRAME_FLAG_LAMBDA` frame flag, treating its code block as an isolated function frame. Executing `return` within a lambda performs a standard method return (`opt_send_without_block` / `leave` instructions).

Conversely, a standard `Proc` binds directly to the stack frame (`rb_control_frame_t`) of its lexically enclosing method. When `return` occurs inside a Proc, YARV unwinds the call stack up to the frame of that enclosing method. If that method is no longer present in the VM stack (because execution already exited `create_proc`), YARV raises a `LocalJumpError` because the target destination frame no longer exists.

**Key Takeaway / Safe Pattern**:
Use `lambda` (or `->(...) {}`) whenever creating standalone anonymous function objects intended to return values. Reserve standard `Proc` objects or blocks for inline control abstractions (like custom iteration blocks) where non-local returns from the surrounding method are explicitly desired.
