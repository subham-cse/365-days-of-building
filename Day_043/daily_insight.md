# Day 043: Ruby Method Lookup Chain and Open Class Monkey Patching

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
In Ruby, method invocations follow a strict, predictable ancestor lookup path: `Singleton Class (Eigenclass)` -> `Prepended Modules` -> `Class` -> `Included Modules` -> `Superclass` -> `Object` -> `Kernel` -> `BasicObject`.

Because Ruby classes are "open", any class definition can be reopened anywhere in the codebase to add or override methods. However, monkey patching global classes directly (like `String` or `Array`) globally mutates method behavior, creating silent, hard-to-debug library conflicts.

**The Code Snippet**:
```ruby
module CodeSanitizer
  def sanitize
    "[Sanitized]: #{to_s.strip}"
  end
end

class String
  # Dangerous Monkey Patch: Reopens String globally!
  def sanitize
    "GLOBAL MONKEY PATCH: #{self}"
  end
end

class Document
  include CodeSanitizer
end

class PrioritizedDocument < Document
  # Prepended modules sit BEFORE the class in method lookup order
  prepend CodeSanitizer
  
  def sanitize
    "Original Class Method: #{to_s}"
  end
end

doc = PrioritizedDocument.new

# Inspect ancestral method lookup chain
puts "Ancestors lookup order:"
puts PrioritizedDocument.ancestors.inspect
# Output: [CodeSanitizer, PrioritizedDocument, Document, Object, Kernel, BasicObject]

puts "\nMethod call result:"
puts doc.sanitize 
# Executes CodeSanitizer#sanitize due to `prepend` standing prior to PrioritizedDocument!

puts "\nGlobal String Monkey Patch:"
puts "   hello world   ".sanitize
```

**Under the Hood / Why It Happens**:
Every object in Ruby has an associated hierarchy of class objects. When a message (method name) is dispatched via `send`, Ruby traverses the `RClass` structure's `super` pointer pointers:
1. `prepend Module`: Ruby inserts an anonymous include class *above* the target class in the inheritance chain.
2. `include Module`: Ruby inserts an anonymous include class *below* the target class, between it and its superclass.
3. Class reopening alters the internal `m_tbl` (method table) of the existing target class directly in memory.

If two gems reopen `String#sanitize`, the last evaluated method definition overwrites `String`'s method table entry globally.

**Key Takeaway / Safe Pattern**:
Avoid monkey patching core standard classes directly. Instead, use Ruby **Refinements** (`using MyRefinement`) to limit class modifications to specific file scopes, or use `Module#prepend` to cleanly wrap existing methods while retaining access to `super`.
