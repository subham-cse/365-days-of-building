# Day 099: Blocks vs Procs vs Lambdas Mechanics and Return Traps
- **Language / Domain**: Ruby
- **The Core Concept / "Did You Know?"**: In Ruby, closures exist in three primary forms: blocks, `Proc` objects, and `lambda`s. While they look similar, they handle parameter counts (arity) and the `return` statement in fundamentally different ways.

An explicit `return` inside a `Proc` will return **from the enclosing scope (method)** where the `Proc` was defined, potentially throwing a `LocalJumpError` if that scope has already exited. In contrast, an explicit `return` inside a `lambda` returns only from the `lambda` itself back to the caller.

- **The Code Snippet**:
```ruby
def proc_return_test
  my_proc = Proc.new { return "Returned from Proc (exits method!)" }
  my_proc.call
  "This code in method will NEVER be executed"
end

def lambda_return_test
  my_lambda = -> { return "Returned from Lambda" }
  result = my_lambda.call
  "Method continues! Lambda returned: #{result}"
end

puts proc_return_test
# Output: Returned from Proc (exits method!)

puts lambda_return_test
# Output: Method continues! Lambda returned: Returned from Lambda

# Proc Arity vs Lambda Arity
p_proc = Proc.new { |a, b| "a: #{a.inspect}, b: #{b.inspect}" }
l_lambda = ->(a, b) { "a: #{a.inspect}, b: #{b.inspect}" }

puts p_proc.call(1) # Flexible arity: missing args become nil ("a: 1, b: nil")
# puts l_lambda.call(1) # Strict arity: raises ArgumentError (wrong number of arguments)
```

- **Under the Hood / Why It Happens**:
Ruby's YARV virtual machine marks call frames differently for `Proc` vs `lambda`. 
- `Proc` blocks share the control frame of their defining lexical scope. A `return` opcode (`opt_send_without_block` / `leave`) unwinds the VM stack all the way to the parent method frame.
- `lambda` creates a isolated stack frame with the `VM_FRAME_FLAG_LAMBDA` flag set. The YARV engine inspects this flag during return execution; if set, it unwinds only the current lambda frame.

- **Key Takeaway / Safe Pattern**:
Use `lambda` (or `->(...) {}`) when you need function-like behavior with strict argument checking and localized `return` semantics. Use `Proc` (or blocks) when writing iterator/control-structure DSLs designed to break or return directly from the caller.
