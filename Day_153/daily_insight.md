# Day 153: C# `Span<T>` and Zero-Allocation High-Performance Memory Slicing

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
In traditional C#, slicing strings or arrays using methods like `string.Substring()` or `Array.Copy()` allocates new heap objects and copies memory buffers, creating garbage collector (GC) pressure in performance-critical applications.

Introduced in .NET Core 2.1, `Span<T>` and `ReadOnlySpan<T>` provide representation for contiguous regions of arbitrary memory (stack allocations, managed heap arrays, or native heap memory) **without allocating new heap memory or copying data**! However, because `Span<T>` is a `ref struct`, it cannot be boxed, stored in normal class fields, or captured across `async`/`await` boundaries.

**The Code Snippet**:
```csharp
using System;

public class MemorySpanDemo
{
    public static void Main()
    {
        string rawData = "ORDER_ID:994821;AMOUNT:149.99;STATUS:PAID";

        Console.WriteLine("--- Heap Allocating Substring (Legacy) ---");
        // Legacy approach: Substring allocates 3 new heap strings!
        int idIndex = rawData.IndexOf("ORDER_ID:") + 9;
        int semicolonIndex = rawData.IndexOf(';');
        string orderIdHeap = rawData.Substring(idIndex, semicolonIndex - idIndex);
        Console.WriteLine($"Extracted OrderId: {orderIdHeap}");

        Console.WriteLine("\n--- Zero-Allocation ReadOnlySpan<T> ---");
        // Modern approach: ReadOnlySpan creates a light window over existing string buffer
        ReadOnlySpan<char> span = rawData.AsSpan();

        int spanIdStart = span.IndexOf("ORDER_ID:") + 9;
        int spanIdEnd = span.IndexOf(';');

        // Slicing creates a new ReadOnlySpan pointer struct in 0 nanoseconds with 0 GC allocations!
        ReadOnlySpan<char> orderIdSpan = span.Slice(spanIdStart, spanIdEnd - spanIdStart);

        // Parsing directly from ReadOnlySpan without creating a string!
        if (int.TryParse(orderIdSpan, out int parsedOrderId))
        {
            Console.WriteLine($"Parsed OrderId cleanly: {parsedOrderId}");
        }

        // Stack-allocated memory span example
        Span<byte> stackBuffer = stackalloc byte[16];
        stackBuffer[0] = 0xFE;
        stackBuffer[1] = 0xFF;
        Console.WriteLine($"Stack buffer first byte: 0x{stackBuffer[0]:X2}");
    }
}
```

**Under the Hood / Why It Happens**:
Internally, `Span<T>` is defined as a `ref struct` containing a **by-ref pointer** and a length integer:
```csharp
public readonly ref struct Span<T>
{
    internal readonly ref T _pointer;
    internal readonly int _length;
}
```
1. When `.AsSpan().Slice(start, length)` is called, C# computes `_pointer = ref array[start]` and sets `_length = length`. No heap allocation (`newobj`) occurs; execution completes in a couple CPU clock cycles.
2. **`ref struct` Safety Restrictions**: To prevent stack pointers from outliving their stack frames, the CLR type safety verifier enforces that `ref struct` types:
   - Must reside strictly on the thread execution stack.
   - Cannot be boxed to `object` or `ValueType`.
   - Cannot be declared as fields in standard classes or non-ref structs.
   - Cannot be used inside `async` methods across `await` suspension points (because `async` state machines capture variables into heap-allocated state machine classes).

**Key Takeaway / Safe Pattern**:
Use `ReadOnlySpan<char>` and `Span<T>` for parsing text formats, network protocols, or binary streams to eliminate GC overhead. When passing memory representations across `async`/`await` boundaries, use `Memory<T>` or `ReadOnlyMemory<T>` instead of `Span<T>`.
