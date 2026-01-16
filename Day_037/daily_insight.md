# Day 037: C# LINQ Deferred Execution and Double Enumeration

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
LINQ queries operating on `IEnumerable<T>` evaluate lazily using deferred execution. The query itself is just an execution plan; no underlying filtering or projection occurs until the query is iterated over (e.g., via `foreach`, `.ToList()`, or `.Any()`).

A major performance trap arises when an `IEnumerable<T>` query variable is iterated over multiple times. Each iteration re-executes the entire LINQ chain from scratch, causing unnecessary database queries, redundant allocations, or side-effect duplication.

**The Code Snippet**:
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class DeferredExecutionDemo
{
    private static int _evalCount = 0;

    public static IEnumerable<int> FetchActiveIds()
    {
        Console.WriteLine("Executing database pipeline scan...");
        for (int i = 1; i <= 3; i++)
        {
            _evalCount++;
            yield return i;
        }
    }

    public static void Main()
    {
        // Query defined - NOT executed yet
        IEnumerable<int> query = FetchActiveIds().Where(id => id > 0);

        Console.WriteLine("--- First Iteration (.Any) ---");
        // Traverses element 1 to check condition
        bool hasElements = query.Any(); 

        Console.WriteLine("\n--- Second Iteration (.Count) ---");
        // Re-executes FetchActiveIds() from scratch to count elements!
        int totalCount = query.Count(); 

        Console.WriteLine($"\nTotal Evaluations triggered: {_evalCount}"); // Prints 4 (1 from Any + 3 from Count)

        Console.WriteLine("\n--- Materialized Execution (.ToList) ---");
        _evalCount = 0;
        // Materializes sequence into concrete list in memory
        List<int> materializedList = FetchActiveIds().Where(id => id > 0).ToList();

        bool countCheck = materializedList.Any();
        int finalCount = materializedList.Count;

        Console.WriteLine($"Materialized Evaluations triggered: {_evalCount}"); // Prints 3 (evaluated only once!)
    }
}
```

**Under the Hood / Why It Happens**:
LINQ operator methods (`Where`, `Select`) return iterator state machines compiled from standard `yield return` blocks or custom `IEnumerable<T>` implementations.

When `.Any()` is invoked, it calls `.GetEnumerator()` on the query object, fetches the first element via `.MoveNext()`, and disposes the enumerator. Later, when `.Count()` is invoked, it calls `.GetEnumerator()` again, generating an entirely new state machine that runs the upstream data generator from the beginning. If the data source is an `IQueryable<T>` backed by Entity Framework, double enumeration triggers duplicate SQL queries to the database server.

**Key Takeaway / Safe Pattern**:
If you need to evaluate an `IEnumerable<T>` multiple times (e.g., checking `.Any()` before running a `.Count()` or `.ToList()`), explicitly materialize the sequence into memory using `.ToList()` or `.ToArray()` beforehand. Use static analyzers like ReSharper or Roslyn analyzers to catch "Possible multiple enumeration" warnings.
