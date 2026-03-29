# Day 127: Ruby Blocks vs Procs vs Lambdas & Return Control Flow Traps

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
Ruby callable objects—Blocks, `Proc` instances, and `lambda`s—appear interchangeable at first glance, but exhibit critical differences in argument checking and execution control flow, specifically regarding the `return` keyword.

Executing a `return` inside a standard `Proc` does not just return from the `Proc` itself—it attempts to return from the **enclosing method context** in which the `Proc` was originally defined! If that enclosing scope has already returned, calling the `Proc` raises a `LocalJumpError`. Conversely, a `lambda` treats `return` like a traditional function call, returning execution flow strictly to its caller.

**The Code Snippet**:
```ruby
def proc_return_test
  my_proc = Proc.new { return "Returned from inside Proc!" }
  my_proc.call
  "This line in proc_return_test is NEVER reached"
end

def lambda_return_test
  my_lambda = -> { return "Returned from inside Lambda!" }
  result = my_lambda.call
  "Lambda result was: '#{result}'. Method finished normally!"
end

puts proc_return_test   # => "Returned from inside Proc!"
puts lambda_return_test # => "Lambda result was: 'Returned from inside Lambda!'. Method finished normally!"

# TRAP: Storing a Proc and executing it outside defining method scope
def create_proc
  Proc.new { return "Boom!" }
end

orphan_proc = create_proc
begin
  orphan_proc.call # Raises LocalJumpError: unexpected return
rescue LocalJumpError => e
  puts "Caught expected exception: #{e.message}"
end
```

**Under the Hood / Why It Happens**:
In Ruby's C VM (YARV), `Proc` objects maintain an execution frame reference bound to the environment where they were created. A `return` keyword inside a regular `Proc` emits a `YARV_INSN_RETURN` instruction targeted at the lexically enclosing stack frame. When evaluated, the VM pops stack frames up to and including that original defining method context.

A `lambda` is flagged internally with the `BUILD_LAMBDA` flag (`is_lambda = true`). Its `return` instruction is handled like a function boundary, popping only the local frame of the lambda execution itself. Additionally, `lambda` checks parameter strictness (raising `ArgumentError` on mismatched arity), whereas `Proc` silently fills missing arguments with `nil` or discards extra parameters.

**Key Takeaway / Safe Pattern**:
Use `lambda` (or `->(...) { ... }`) when you need isolated function-like callables that safely accept parameters and return values. Use blocks/`Proc` when designing DSL iterator blocks meant to act as control flow constructs within the caller's lexical scope.
