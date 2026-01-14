# Day 031: Symbol Identity vs Strings and Dynamic Method Missing Tricks
**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, **Symbols** (`:my_symbol`) are immutable, canonicalized identifiers stored in an internal system symbol table. Unlike **Strings** (`"my_string"`), which allocate a new object on the heap every time a string literal is evaluated, identical symbols reuse the exact same memory address.

However, dynamically creating unlimited symbols at runtime from untrusted user input (e.g. `user_input.to_sym`) in older Ruby versions creates a severe memory leak, as symbols were historically never collected by Garbage Collection.

Furthermore, Ruby's `method_missing` mechanism allows intercepting undefined method calls dynamically, but failing to override `respond_to_missing?` breaks object reflection (`obj.respond_to?(:dynamic_method)`).

**The Code Snippet**:
```ruby
# Trap 1: Symbol Memory Allocation vs String Allocation
10.times do
  # Creates 10 DISTINCT String objects in heap memory!
  str_id = "user_name".object_id
  puts "String Object ID: #{str_id}"
end

10.times do
  # Uses the EXACT SAME Symbol instance in memory!
  sym_id = :user_name.object_id
  puts "Symbol Object ID: #{sym_id}"
end

# Trap 2: Incorrect method_missing implementation
class DynamicUser
  def initialize(attributes)
    @attributes = attributes
  end

  # Intercept undefined method calls dynamically
  def method_missing(method_name, *args, &block)
    if @attributes.key?(method_name)
      @attributes[method_name]
    else
      super
    end
  end

  # BUG: Forgot to override respond_to_missing?!
end

user = DynamicUser.new(name: "Alice", role: "Admin")
puts user.name # Output: "Alice" (via method_missing)

# REFLECTION BUG:
puts user.respond_to?(:name) # Output: false! Breaks introspection and metaprogramming!
```

**Under the Hood / Why It Happens**:
Ruby stores symbols in an internal symbol table managed by CRuby's VM kernel. When Ruby parses `:user_name`, it performs a hash lookup in this table. If present, it returns the `ID` symbol table index directly as an immediate `VALUE` pointer. Strings, conversely, instantiate an `RString` struct allocating heap memory buffers.

For dynamic methods, when Ruby fails to find a method in an object's method lookup chain, it constructs a frame and calls `method_missing(method_name, *args)`. 

However, calling `object.respond_to?(:method)` does not invoke `method_missing`. Instead, it checks the method table and calls `respond_to_missing?(method_name, include_private)`. If `respond_to_missing?` is omitted, Ruby returns `false`, causing APIs, ORMs, and serialization gems to misinterpret object capabilities.

**Key Takeaway / Safe Pattern**:
Always pair every `method_missing` definition with a corresponding `respond_to_missing?` override. Avoid converting arbitrary dynamic user inputs into symbols (`params[:key].to_sym`); keep them as strings or validate against a whitelist.

```ruby
# SAFE: Complete Dynamic Metaprogramming Pattern
class DynamicUserSafe
  def initialize(attributes)
    @attributes = attributes
  end

  def method_missing(method_name, *args, &block)
    if @attributes.key?(method_name)
      @attributes[method_name]
    else
      super
    end
  end

  # SAFE: Paired respond_to_missing? implementation
  def respond_to_missing?(method_name, include_private = false)
    @attributes.key?(method_name) || super
  end
end

user = DynamicUserSafe.new(name: "Alice")
puts user.respond_to?(:name) # Output: true! Introspection works perfectly!
```
