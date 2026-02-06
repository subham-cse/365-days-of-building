# Day 065: Deferred Execution Traps and Variable Capture in C# LINQ

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
LINQ queries in C# use deferred execution by default. Constructing a LINQ query using `Where`, `Select`, or similar extension methods does not immediately process the underlying collection; instead, it builds an execution tree or delegate chain that is evaluated only when the query is iterated (e.g., via `foreach`, `ToList()`, `First()`, or `Count()`).

A classic production bug arises when LINQ queries capture outer loop variables or rely on mutable state before iteration occurs. Because C# lambdas capture variable references rather than values, any modification to the captured variable between query construction and query enumeration will change the query's behavior—often leading to duplicated filtering conditions, incorrect computations, or modified collection errors.

**The Code Snippet**:
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class Program
{
    public static void Main()
    {
        var numbers = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
        
        // --- TRAP: Variable capture in deferred LINQ execution ---
        var filters = new List<Func<int, bool>>();
        var targetValues = new List<int> { 2, 5, 8 };

        // Misleading code: capturing loop variable by reference
        IEnumerable<int> query = numbers;
        foreach (var val in targetValues)
        {
            // BAD: 'val' is captured by reference (in older C# versions or outer scopes)
            // or mutating shared state across evaluation loops
            query = query.Where(x => x != val);
        }

        // At this point, no filtering has actually executed!
        
        // Mutating source collection before iteration
        var sourceList = new List<int> { 10, 20, 30 };
        var delayedQuery = sourceList.Where(n => n > 15);
        
        sourceList.Add(40); // Mutates source after query definition
        
        Console.WriteLine($"Delayed query count: {delayedQuery.Count()}"); 
        // Prints 3 (includes 40!), NOT 2.

        // --- SAFE PATTERN: Eager evaluation & lexical scoping ---
        var safeSource = new List<int> { 10, 20, 30 };
        // Materialize query immediately into memory to capture current state
        var eagerResult = safeSource.Where(n => n > 15).ToList();
        
        safeSource.Add(40);
        Console.WriteLine($"Eager result count: {eagerResult.Count}"); 
        // Prints 2, isolated from future source mutations.
    }
}
```

**Under the Hood / Why It Happens**:
LINQ query methods return instances of compiler-generated classes implementing `IEnumerable<T>` (such as `WhereEnumerableIterator<TSource>`). When a lambda expression accesses a variable defined outside its scope, the C# compiler generates a dynamic closure class (hoisting the variable into a field on that closure class).

Because the iterator defers calling `MoveNext()` on the underlying enumerator until iteration starts, the delegate bound inside the iterator reads the closure field's *current value at execution time*, rather than its *value at definition time*. If the source data or reference fields change between declaration and iteration, execution reflects the modified state.

**Key Takeaway / Safe Pattern**:
When a LINQ query depends on mutable state or variables that change in subsequent lines of code, materialize the query immediately using `.ToList()` or `.ToArray()`. Alternatively, bind values to local immutably scoped variables inside loops prior to closure capture.
