# Day 237: C# LINQ Deferred Execution & Expression Tree Re-Evaluation Traps

**Language / Domain**: C# / .NET Runtime & Functional Queries

**The Core Concept / "Did You Know?"**:
In C#, LINQ queries targeting `IEnumerable<T>` or `IQueryable<T>` leverage **Deferred Execution** (Lazy Evaluation). Constructing a LINQ query does not execute data processing or fetch items from memory/database immediately; it merely constructs an execution pipeline iterator or an Expression Tree.

Data evaluation occurs only when the query is enumerated (e.g. inside a `foreach` loop, or via `.ToList()`, `.ToArray()`, `.Count()`).

If a LINQ query captures mutable external variables or accesses stateful collections without materialized caching, **multiple enumerations will re-execute the entire query pipeline from scratch**, causing unexpected side effects, extra database queries, or silent data bugs.

**The Code Snippet**:
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class LinqDeferredExecutionDemo
{
    public static void Main()
    {
        var numbers = new List<int> { 1, 2, 3, 4, 5 };
        int factor = 10;

        // LINQ query construction (Deferred Execution - Nothing evaluated yet!)
        var query = numbers.Where(n => n % 2 == 0).Select(n => n * factor);

        Console.WriteLine("--- First Enumeration ---");
        foreach (var val in query)
        {
            Console.Write($"{val} "); // Outputs: 20 40
        }

        // TRAP 1: Mutating captured variable before second enumeration
        factor = 100;
        numbers.Add(6); // Mutating underlying collection

        Console.WriteLine("\n\n--- Second Enumeration (Re-evaluates with updated state!) ---");
        // Re-executes query pipeline! Factor is now 100, numbers includes 6!
        foreach (var val in query)
        {
            Console.Write($"{val} "); // Outputs: 200 400 600! (Data changed!)
        }

        // --- SAFE PATTERN: Materialize Query immediately via ToList() / ToArray() ---
        factor = 10;
        var materializedList = numbers
            .Where(n => n % 2 == 0)
            .Select(n => n * factor)
            .ToList(); // Materializes and snapshots result in memory right now!

        factor = 999;
        numbers.Clear();

        Console.WriteLine("\n\n--- Materialized List Enumeration (Stable Snapshot) ---");
        foreach (var val in materializedList)
        {
            Console.Write($"{val} "); // Outputs stable snapshot: 20 40 600
        }
        Console.WriteLine();
    }
}
```

**Under the Hood / Why It Happens**:
1. **Iterator State Machines**:
   When C# compiles a LINQ method like `.Where()` or `.Select()`, it generates an internal compiler class implementing `IEnumerable<T>` and `IEnumerator<T>`.
   The lambda expressions (`n => n * factor`) become closures holding references to local variable scope objects.

2. **Re-Evaluation Cost**:
   When `foreach (var val in query)` runs:
   - C# calls `query.GetEnumerator()`.
   - The state machine initializes state index pointer `0` and steps through `numbers`.
   - It reads `factor`'s *current value in memory* at the moment of `MoveNext()`.

If `query` is passed to multiple methods or enumerated three times in a method body, the iterator pipeline executes three separate iterations. For `IQueryable<T>` (Entity Framework Core), iterating a query 3 times issues **3 separate SQL queries** over the network to the database server.

**Key Takeaway / Safe Pattern**:
- **Materialize queries early**: Call `.ToList()` or `.ToArray()` when query results are intended to be immutable snapshots.
- Avoid modifying captured closure variables after defining a LINQ query.
- Use `IReadOnlyList<T>` or `IReadOnlyCollection<T>` for method return types instead of returning unmaterialized `IEnumerable<T>` when multiple calls by downstream consumers are anticipated.
