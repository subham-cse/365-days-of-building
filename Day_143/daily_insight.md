# Day 143: Ruby Method Lookup Chain & Prepended Module Overrides

**Language / Domain**: Ruby

**The Core Concept / "Did You Know?"**:
When you call a method on a Ruby object, the Ruby Virtual Machine searches for the method implementation by traversing the **Ancestors Chain** (`klass.ancestors`). While standard module `include` inserts modules *above* the class in the lookup hierarchy, Ruby 2.0 introduced `prepend`, which inserts modules *below* the class in the ancestors chain!

Because `prepend` places module methods in front of the class's own method definitions, calling `super` inside a prepended module delegates execution down to the class's original method definition. This makes `prepend` the preferred mechanism for cleanly wrapping class behavior without resorting to risky method alias monkey-patching (`alias_method`).

**The Code Snippet**:
```ruby
module AuditLogger
  def calculate_tax(amount)
    puts "[AuditLogger] Intercepted tax calculation for amount: $#{amount}"
    result = super # Calls the class's original method!
    puts "[AuditLogger] Calculated final tax: $#{result}"
    result
  end
end

class TaxCalculator
  # Using 'include' would place AuditLogger ABOVE TaxCalculator in ancestors chain,
  # meaning TaxCalculator#calculate_tax would override AuditLogger!
  # Using 'prepend' places AuditLogger BEFORE TaxCalculator in ancestors chain!
  prepend AuditLogger

  def calculate_tax(amount)
    amount * 0.20
  end
end

# Execution Demonstration
calc = TaxCalculator.new
total_tax = calc.calculate_tax(100)

puts "\nMethod Lookup Ancestors Order:"
puts TaxCalculator.ancestors.join(" -> ")
# Output: AuditLogger -> TaxCalculator -> Object -> Kernel -> BasicObject
```

**Under the Hood / Why It Happens**:
Every class in Ruby is an instance of `RClass` in C internals. An object's class contains a pointer (`super`) to its parent class or included module wrappers.

When `include ModuleA` is executed:
- Ruby inserts an `iclass` (include class) proxy node between `TaxCalculator` and its superclass `Object`:
  `TaxCalculator -> iclass(ModuleA) -> Object`.

When `prepend ModuleB` is executed:
- Ruby creates an `iclass` wrapper for `TaxCalculator`'s original methods and updates `TaxCalculator`'s method table to point to `ModuleB` first:
  `TaxCalculator (points to ModuleB) -> iclass(TaxCalculator) -> Object`.

Thus, `TaxCalculator.ancestors` evaluates to `[AuditLogger, TaxCalculator, Object, Kernel, BasicObject]`. Invoking `calc.calculate_tax` hits `AuditLogger#calculate_tax` first, and calling `super` descends into `TaxCalculator#calculate_tax`.

**Key Takeaway / Safe Pattern**:
Use `prepend` instead of `alias_method` or standard `include` when designing decorators, logging layers, or tracing wrappers in Ruby classes. It provides clean wrapper invocation via `super` without corrupting class method signatures.
