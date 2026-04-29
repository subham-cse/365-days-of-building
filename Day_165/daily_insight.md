# Day 165: LINQ Deferred Execution and Variable Capture Traps

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
LINQ queries in C# (such as `.Where()`, `.Select()`) utilize **deferred execution**. Defining a LINQ query does *not* execute the query or create a snapshot of the data. Instead, execution is deferred until the query is actually iterated over (e.g., via `foreach`, `.ToList()`, or `.First()`).

Combining deferred execution with lambda expressions that capture loop variables leads to a famous concurrency and iteration bug: the closure captures a *reference* to the variable, not its *value* at the moment the LINQ query was declared.

**The Code Snippet**:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class LinqDeferredExecution
{
    public static void Main()
    {
        var numbers = new List<int> { 1, 2, 3, 4, 5 };
        var actions = new List<Func<int>>();

        // BUG: In C# 4.0 and earlier (or when capturing outer scope variables),
        // closing over `factor` captures the variable reference, not its value snapshot!
        int factor = 2;
        var query = numbers.Select(n => n * factor);

        // Mutate the captured variable BEFORE iterating the query
        factor = 10;

        // Iteration happens NOW (Deferred Execution)
        Console.WriteLine("Query results after mutating factor:");
        foreach (var val in query)
        {
            // Prints 10, 20, 30, 40, 50 instead of 2, 4, 6, 8, 10!
            Console.Write($"{val} ");
        }
        Console.WriteLine();

        // Safe Pattern: Force immediate execution via ToList()
        factor = 2;
        var immediateQuery = numbers.Select(n => n * factor).ToList();
        factor = 10;

        Console.WriteLine("Immediate execution results:");
        foreach (var val in immediateQuery)
        {
            // Prints 2, 4, 6, 8, 10 as expected
            Console.Write($"{val} ");
        }
    }
}
```

**Under the Hood / Why It Happens**:
When C# compiles a closure that references a local variable (`factor`), the compiler generates a hidden display class behind the scenes:
```csharp
[CompilerGenerated]
private sealed class <>c__DisplayClass0_0
{
    public int factor;
    public int <Main>b__0(int n) => n * this.factor;
}
```
Instead of allocating `factor` on the stack, the variable `factor` is hoisted to a field inside an instance of `<>c__DisplayClass0_0` allocated on the heap.

When `factor = 10;` executes, it mutates `<>c__DisplayClass0_0.factor` directly. When LINQ iterates over the query via `IEnumerable<T>.GetEnumerator()`, the yield return iterator evaluates the lambda function, reading the *current* mutated value of `<>c__DisplayClass0_0.factor` (which is 10).

**Key Takeaway / Safe Pattern**:
Be mindful of deferred execution in LINQ. If a query depends on local variables or underlying collections that may change before iteration, force immediate materialization by calling `.ToList()` or `.ToArray()`.
