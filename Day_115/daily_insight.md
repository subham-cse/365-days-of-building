# Day 115: Method Lookup Chain and Open Class Monkey Patching Hazards
- **Language / Domain**: Ruby
- **The Core Concept / "Did You Know?"**: Ruby's class model allows **Open Classes** (monkey patching): any built-in or third-party class can be reopened and modified at runtime. 

When a method is called on an object, Ruby searches for the method by traversing a strict **Method Lookup Chain** (Ancestors array). If a monkey patch introduces or overrides a method higher in the lookup chain, it globally alters behavior for all callers across the entire Ruby process!

- **The Code Snippet**:
```ruby
class String
  # DANGEROUS MONKEY PATCH: Globally overwriting core String method
  def blank?
    strip.empty?
  end
end

module CustomLogger
  def log(msg)
    "LOG: #{msg}"
  end
end

class Application
  include CustomLogger
end

# Inspecting the Method Lookup Chain (Ancestors)
puts "Application Ancestors Chain:"
puts Application.ancestors.inspect
# Output: [Application, CustomLogger, Object, Kernel, BasicObject]

# Demonstrating Monkey Patching Effect
p "   ".blank? # true

# Hazard: Library A patches String#blank?, Library B patches String#blank? differently.
# Last loaded code silently overrides previous implementations globally!
```

- **Under the Hood / Why It Happens**:
Every Ruby object has a class pointer (`RClass`). When `obj.method_name()` is executed, the YARV interpreter starts at `obj`'s singleton class (if present), then moves to its class, followed by included modules (prepended modules are inserted before the class), parent superclasses, `Object`, `Kernel`, and finally `BasicObject`.

Because class definitions are dynamic mutating structures, adding a method to `String` writes directly to `String`'s method table dictionary. Every string in memory instantly resolves method calls through the modified lookup table.

- **Key Takeaway / Safe Pattern**:
Avoid global monkey patching. Instead, use Ruby **Refinements** (`refine` and `using`), which lexically scope class modifications strictly to the module or file where they are activated:

```ruby
module StringExtensions
  refine String do
    def custom_blank?
      strip.empty?
    end
  end
end

class SafeService
  using StringExtensions # Activated ONLY within this class scope!

  def process(input)
    input.custom_blank?
  end
end
```
