# Day 071: Method Lookup Chain & Monkey Patching Hazards in Ruby

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
Ruby's object model is dynamically open: any class, including built-in core classes like `Array`, `String`, or `Hash`, can be modified at runtime (a technique known as **Monkey Patching**).

While monkey patching allows elegant domain-specific languages (DSLs) and rapid monkey-fix extensions, it creates severe side effects across large applications or third-party gems. Because Ruby resolves method calls by traversing a single linear **Method Lookup Chain**, patching or overriding a core method changes that method globally for *all* code running in the Ruby virtual machine (MRI), leading to obscure bugs, infinite recursion traps, and hard-to-trace bugs.

**The Code Snippet**:
```ruby
# TRAP: Global Monkey Patching Core Class
class String
  # Overriding built-in method or adding global method
  def blank?
    strip.empty?
  end

  # DANGEROUS: Overriding core method with unexpected side effect
  def +(other)
    # Accidentally changing fundamental string concatenation!
    puts "[LOG]: Concatenating '#{self}' with '#{other}'"
    super(other)
  end
end

puts "hello ".blank? # Output: false
puts "abc" + "def"    # Output: [LOG] ... "abcdef"

# --- SAFE PATTERN: Using Refinements for Scoped Changes ---
module StringExtensions
  refine String do
    def custom_transform
      upcase.reverse
    end
  end
end

class IsolatedService
  # Refinement is scoped EXCLUSIVELY to this class file context
  using StringExtensions

  def process(input)
    # Works here
    input.custom_transform 
  end
end

class StandardService
  def process(input)
    # Raised NoMethodError! Standard string remains unpolluted globally!
    # input.custom_transform 
  end
end

puts IsolatedService.new.process("ruby") # Output: YBUR
```

**Under the Hood / Why It Happens**:
In YARV (Yet Another Ruby VM), an object's class reference points to an `RClass` struct. When a method is called (`obj.foo`), Ruby searches for the method dynamic table in the following exact hierarchy (Method Lookup Chain):
1. Singleton Class (Eigenclass) of `obj`
2. Prepended Modules (in reverse order of `prepend`)
3. Class of `obj` (`obj.class`)
4. Included Modules (in reverse order of `include`)
5. Superclass $\rightarrow$ Superclass's Included Modules $\rightarrow ...$ up to `Object` $\rightarrow$ `Kernel` $\rightarrow$ `BasicObject`.

When a developer re-opens `class String` and defines a method, Ruby writes directly into `String`'s method table. Every gem, library, or core function executing in the VM that calls that string method now routes through the patched implementation. 

`Refinements` (`refine`) solve this by creating localized method table overlays that are active only in lexical scopes where `using` is explicitly declared.

**Key Takeaway / Safe Pattern**:
Avoid monkey patching core Ruby standard library classes globally. Prefer **Refinements** (`refine` / `using`) for lexically scoped changes, or use standard wrapper pattern/utility modules instead of modifying global class prototypes.
