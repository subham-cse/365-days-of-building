# Day 087: Blocks vs Procs vs Lambdas in Ruby

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, executable code blocks are first-class objects, but manifest under three primary variations: **Blocks**, **Procs**, and **Lambdas**.

While Procs and Lambdas are both instances of the `Proc` class (`proc.is_a?(Proc)` evaluates to `true` for both!), they exhibit critical differences in **Argument Checking** and **Return Behavior**:

1. **Argument Strictness**: Lambdas enforce strict parameter counts (raising `ArgumentError` if arity mismatches). Procs ignore missing arguments (assigning `nil`) and silently drop extra arguments!
2. **Return Flow**: A `return` keyword inside a Lambda exits *only* the lambda itself. A `return` keyword inside a Proc attempts to return from the **enclosing method scope** where the Proc was defined! If that enclosing scope has already returned, calling the Proc raises a `LocalJumpError`.

**The Code Snippet**:
```ruby
# --- 1. Return Behavior Trap ---

def test_proc_return
  puts "Entering test_proc_return method"
  
  bad_proc = Proc.new { return "RETURN FROM PROC!" }
  bad_proc.call # Immediately exits test_proc_return!
  
  puts "THIS LINE IS NEVER REACHED!"
end

def test_lambda_return
  puts "\nEntering test_lambda_return method"
  
  good_lambda = -> { return "RETURN FROM LAMBDA!" }
  result = good_lambda.call # Returns string back to caller method
  
  puts "Lambda result: #{result}"
  puts "THIS LINE IS EXECUTED SAFELY!"
end

test_proc_return
test_lambda_return


# --- 2. Arity Strictness Comparison ---

my_proc = Proc.new { |a, b| puts "Proc args: a=#{a.inspect}, b=#{b.inspect}" }
my_lambda = ->(a, b) { puts "Lambda args: a=#{a.inspect}, b=#{b.inspect}" }

puts "\n--- Proc Arity Test ---"
my_proc.call(10) # Works! b is assigned nil

puts "\n--- Lambda Arity Test ---"
begin
  my_lambda.call(10) # Raises ArgumentError!
rescue ArgumentError => e
  puts "Caught expected ArgumentError in Lambda: #{e.message}"
end
```

**Under the Hood / Why It Happens**:
In YARV (Yet Another Ruby VM), Procs and Lambdas use internal control frame flags on `rb_block_t` structs:
- A Proc is flagged as `VM_FRAME_MAGIC_BLOCK`. When YARV encounters a `return` instruction inside a Proc, it inspects the captured stack frame pointer (`dfp`) and executes a non-local jump directly to the target method frame, bypassing intervening callers.
- A Lambda is flagged as `VM_FRAME_MAGIC_METHOD`. When a `return` instruction is encountered, YARV treats the execution frame identically to a standard method return, popping only the lambda frame from the execution stack.

Additionally, Lambdas have their internal `is_lambda` flag set to `1` on the `RData` object struct, instructing the YARV argument dispatcher to execute full arity validation checks (`rb_check_arity`).

**Key Takeaway / Safe Pattern**:
Default to using **Lambdas** (`->(args) { ... }` or `lambda { ... }`) when creating anonymous callable objects, as their strict argument checking and standard return behavior prevent non-local jump bugs. Reserve Procs for simple control-flow iteration helpers.
