# Day 025: Span<T> and Memory<T> Allocation Patterns vs Value/Reference Types
**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
In modern high-performance .NET (C# 7.2+), `Span<T>` and `ReadOnlySpan<T>` enable contiguous memory representation across stack allocations, heap objects, and native memory buffers with **zero GC heap allocations**. 

However, because `Span<T>` is a `ref struct`, it is allocated exclusively on the CPU execution stack. `Span<T>` instances **cannot** be stored as fields inside regular classes, boxed onto the heap, captured inside lambda closures, or used across `async`/`await` state machine boundaries. Attempting to pass `Span<T>` into async methods results in compile errors.

**The Code Snippet**:
```csharp
using System;
using System.Threading.Tasks;

public class MemorySpanPerformance {

    // High performance zero-allocation string parsing using ReadOnlySpan
    public static int ParseYearFromDate(string dateString) {
        // "2026-10-07"
        ReadOnlySpan<char> span = dateString.AsSpan();
        ReadOnlySpan<char> yearSpan = span.Slice(0, 4); // Zero-allocation slice!
        return int.Parse(yearSpan);
    }

    // Ref Struct Lifetime Limitations
    public class RefStructLimits {
        // COMPILE ERROR: ref struct cannot be a field in a normal class!
        // private Span<byte> _buffer; 

        public async Task ProcessDataAsync(string input) {
            ReadOnlySpan<char> span = input.AsSpan();

            // COMPILE ERROR: Cannot use Span across await boundary!
            // await Task.Delay(100);
            // Console.WriteLine(span.Length);
        }
    }

    public static void Main() {
        string date = "2026-10-07";
        int year = ParseYearFromDate(date);
        Console.WriteLine($"Parsed Year: {year}");
    }
}
```

**Under the Hood / Why It Happens**:
At the CLR runtime layer, `Span<T>` is declared as a `ref struct` containing a **byref pointer** (`ref T`) and a length integer:
```csharp
public readonly ref struct Span<T> {
    internal readonly ref T _pointer;
    internal readonly int _length;
}
```
Because `byref` pointers reference arbitrary memory locations on the execution stack, allowing a `Span<T>` to escape to the heap (via class field storage or boxing) would lead to dangling pointer bugs if the stack frame pops while heap references persist.

When an `async` method is compiled, C# converts the method into a heap-allocated state machine struct implementing `IAsyncStateMachine`. Storing a `Span<T>` inside an `async` method would require hoisting the `Span<T>` into fields of this heap-allocated state machine struct, violating `ref struct` safety rules.

**Key Takeaway / Safe Pattern**:
Use `Span<T>` for synchronous, stack-bound, zero-allocation data processing. When data must cross `async`/`await` execution boundaries or be stored in class fields, use `Memory<T>` or `ReadOnlyMemory<T>`.

```csharp
using System;
using System.Threading.Tasks;

// SAFE: Memory<T> can be stored on heap and used across async boundaries!
public class AsyncMemoryProcessor {
    private Memory<byte> _heapBuffer;

    public async Task ProcessAsync(Memory<byte> memory) {
        _heapBuffer = memory;

        await Task.Delay(100); // SAFE across await!

        // Slice without allocation:
        Memory<byte> slice = _heapBuffer.Slice(0, 10);
        Console.WriteLine($"Sliced length: {slice.Length}");
    }
}
```
