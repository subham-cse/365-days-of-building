# Day 009: Deferred Execution in LINQ and Async State Machine Captured Variables
**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
LINQ queries in C# (`IEnumerable<T>`) utilize deferred execution. A LINQ query expression does not execute when defined; it executes when the sequence is enumerated (e.g., via `foreach`, `.ToList()`, or `.First()`). 

If a LINQ query captures local variables modified inside a loop before enumeration occurs, the query evaluates using the variable's final state. Furthermore, C# compiler transforms `async`/`await` methods into heap-allocated state machines, capturing local variables and context that can lead to memory leaks or thread context switching overhead when combined with `ConfigureAwait(false)`.

**The Code Snippet**:
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class LinqDeferredTrap {
    public static void Main() {
        var actions = new List<Func<int>>();
        var numbers = new List<int> { 1, 2, 3, 4, 5 };

        // Trap 1: Deferred Execution with Captured Scope
        var query = numbers.Where(n => n > 2);
        
        // Modify underlying source list BEFORE enumeration!
        numbers.Add(6);

        // Enumeration happens HERE!
        Console.WriteLine($"Query count: {query.Count()}"); // Output: 4 (3, 4, 5, 6)!

        // Trap 2: Deferred Lambda Capture in Loop
        var list = new List<Func<int>>();
        for (int i = 0; i < 3; i++) {
            // Evaluates captured variable `i` during invocation!
            list.Add(() => i * 10);
        }

        foreach (var func in list) {
            Console.WriteLine(func()); // Prints 30, 30, 30 (NOT 0, 10, 20)!
        }
    }
}
```

**Under the Hood / Why It Happens**:
LINQ implementations return iterator objects implementing `IEnumerable<T>`. Calling `.Where(...)` instantiates a `WhereListIterator` or `WhereEnumerableIterator` holding a delegate reference to your lambda. Evaluation only occurs when `.MoveNext()` is called during iteration.

For closures, the C# compiler generates a display class (a hidden compiler-generated class) containing the captured variable `i` as a field. The loop iteration mutates this single field on the heap-allocated display class instance. Because all delegates created inside the loop reference the same instance of this display class, invoking them reads the final value of `i` (`3`).

**Key Takeaway / Safe Pattern**:
Force immediate evaluation using `.ToList()` or `.ToArray()` if the underlying collection might be mutated or if you need snapshot isolation. To fix variable capture in loops, copy the iteration variable to a local variable scoped inside the loop body, or pass it explicitly to lambda arguments.

```csharp
// SAFE: Materializing LINQ query immediately
List<int> snapshot = numbers.Where(n => n > 2).ToList(); // Evaluates NOW

// SAFE: Local variable capture scope
var list = new List<Func<int>>();
for (int i = 0; i < 3; i++) {
    int v = i; // Local copy created inside block scope
    list.Add(() => v * 10);
}

foreach (var func in list) {
    Console.WriteLine(func()); // Outputs: 0, 10, 20
}
```
