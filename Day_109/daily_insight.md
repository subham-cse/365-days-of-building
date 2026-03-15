# Day 109: Deferred Execution in LINQ and Capture Pitfalls
- **Language / Domain**: C#
- **The Core Concept / "Did You Know?"**: Most LINQ operators (`Where`, `Select`, `Take`) use **deferred (lazy) execution**. A LINQ query is not executed when it is defined—it executes only when the sequence is enumerated (e.g. via `foreach`, `.ToList()`, or `.First()`).

If variables captured inside a LINQ lambda are modified before enumeration occurs, the query will evaluate using the **final value** of those variables, leading to unexpected runtime results!

- **The Code Snippet**:
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

class Program
{
    static void Main()
    {
        var numbers = new List<int> { 1, 2, 3, 4, 5 };
        var actions = new List<Func<int>>();

        // Trap 1: Loop Variable Capture with Deferred Execution
        for (int i = 0; i < numbers.Count; i++)
        {
            // Bug: capturing 'i' by reference in deferred closure
            // actions.Add(() => numbers[i]); // Causes ArgumentOutOfRangeException when called later!
        }

        // Trap 2: Deferred Query Evaluation Timing
        int factor = 10;
        var query = numbers.Select(n => n * factor);

        factor = 100; // Mutation after definition, but BEFORE enumeration!

        Console.WriteLine("Query results (evaluated now):");
        foreach (var val in query)
        {
            Console.Write($"{val} "); // Output: 100 200 300 400 500 (uses factor = 100!)
        }
        Console.WriteLine();

        // Safe Pattern: Force immediate execution using .ToList()
        int factorSafe = 10;
        var safeQuery = numbers.Select(n => n * factorSafe).ToList();
        factorSafe = 100;

        Console.WriteLine("Safe results:");
        foreach (var val in safeQuery)
        {
            Console.Write($"{val} "); // Output: 10 20 30 40 50
        }
    }
}
```

- **Under the Hood / Why It Happens**:
The C# compiler converts LINQ queries containing deferred operators into compiler-generated iterator classes implementing `IEnumerable<T>` and `IEnumerator<T>`. 

When lambdas capture local variables (like `factor`), Roslyn generates a closure class holding fields for those variables. The lambda method reads directly from the closure object field during enumeration (`MoveNext()`). Because `factor` was set to `100` before `MoveNext()` was called inside the `foreach` loop, the updated value is read.

- **Key Takeaway / Safe Pattern**:
If a LINQ query depends on mutable state or external resources that may change, instantiate the results immediately using `.ToList()` or `.ToArray()`. Copy loop variables into local block scope variables inside loops when creating closures.
