# Day 059: Ruby Blocks vs Procs vs Lambdas

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, closures exist in three primary forms: **Blocks**, **Procs**, and **Lambdas**. While all three encapsulate executable code blocks and capture surrounding lexical scope, Procs and Lambdas differ fundamentally in two key aspects: argument checking strictness and `return` control flow semantics.

Calling `return` inside a Proc exits the *enclosing method* that created the Proc, whereas calling `return` inside a Lambda exits *only the Lambda itself*, returning control to the caller.

**The Code Snippet**:
```ruby
def demonstrate_proc_return
  puts "1. Entering demonstrate_proc_return"
  
  bad_proc = Proc.new { return "EARLY RETURN FROM PROC" }
  bad_proc.call # Immediately exits demonstrate_proc_return!
  
  puts "2. This line will NEVER be reached!"
end

def demonstrate_lambda_return
  puts "1. Entering demonstrate_lambda_return"
  
  good_lambda = lambda { return "LAMBDA RETURN VALUE" }
  result = good_lambda.call # Returns string to caller, execution continues!
  
  puts "2. Lambda returned: '#{result}'"
  puts "3. Exiting demonstrate_lambda_return cleanly"
end

def demonstrate_argument_checking
  sample_proc = Proc.new { |a, b| "Proc args: a=#{a.inspect}, b=#{b.inspect}" }
  sample_lambda = ->(a, b) { "Lambda args: a=#{a.inspect}, b=#{b.inspect}" }

  # Proc silently ignores missing arguments or truncates extra arguments
  puts sample_proc.call(10) # a=10, b=nil

  # Lambda enforces strict arity checking!
  begin
    sample_lambda.call(10)
  rescue ArgumentError => e
    puts "Lambda caught expected error: #{e.message}"
  end
end

puts "--- Proc Return Semantics ---"
puts "Result: #{demonstrate_proc_return}"

puts "\n--- Lambda Return Semantics ---"
demonstrate_lambda_return

puts "\n--- Argument Checking ---"
demonstrate_argument_checking
```

**Under the Hood / Why It Happens**:
In YARV (Yet Another Ruby VM), both Procs and Lambdas are instances of the `Proc` class, but Lambdas have an internal flag set (`IS_LAMBDA_P(proc) == true`).

When YARV executes a `leave` byte instruction inside a Proc, it looks up the call frame stack pointer of the *scope where the Proc was instantiated* and unwinds the stack to that frame. If that frame has already returned, calling the Proc raises a `LocalJumpError`.

In contrast, a Lambda frame is treated like an isolated method call: its `return` instruction simply pops the current frame off YARV's execution stack and returns execution to the instruction immediately following `.call`.

**Key Takeaway / Safe Pattern**:
Prefer Lambdas (`->(x) { ... }` or `lambda { ... }`) over raw `Proc.new` for anonymous functions and callbacks. Lambdas provide predictable method-like argument checking and safe `return` semantics. Reserve Procs for DSL blocks where early method unwinding is explicitly intended.
