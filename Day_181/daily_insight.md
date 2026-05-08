# Day 181: Memory Slicing and Allocation Elimination with Span<T>

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
In traditional C# performance-critical code, parsing substrings (`string.Substring()`) or slicing arrays (`array.Skip().Take()`) creates new object allocations on the Managed Heap. In high-throughput network services or serializers, this causes heavy Garbage Collection (GC) pressure and latency spikes.

Introduced in .NET Core 2.1, **`Span<T>`** and **`ReadOnlySpan<T>`** provide a unified, type-safe representation of contiguous memory regardless of whether that memory is allocated on the Managed Heap, Stack, or Unmanaged Native Memory. Crucially, slicing a `Span<T>` operates with zero allocations and zero memory copies.

**The Code Snippet**:

```csharp
using System;
using System.Text;

public class SpanBenchmark
{
    public static void Main()
    {
        string rawHeader = "Authorization: Bearer secret_token_value_12345";

        // 1. Traditional Allocating Approach (Creates multiple string heap allocations)
        string token1 = ParseTokenLegacy(rawHeader);
        Console.WriteLine($"Parsed Legacy Token: {token1}");

        // 2. High-Performance Span Approach (ZERO Heap Allocations)
        ReadOnlySpan<char> headerSpan = rawHeader.AsSpan();
        ReadOnlySpan<char> token2 = ParseTokenSpan(headerSpan);
        Console.WriteLine($"Parsed Span Token: {token2.ToString()}");

        // 3. Stack-Allocated Memory Slicing with Span
        Span<byte> stackBuffer = stackalloc byte[128];
        for (int i = 0; i < stackBuffer.Length; i++)
        {
            stackBuffer[i] = (byte)i;
        }

        Span<byte> slice = stackBuffer.Slice(10, 5); // Zero copy slice!
        Console.WriteLine($"Slice length: {slice.Length}, First elem: {slice[0]}");
    }

    public static string ParseTokenLegacy(string header)
    {
        // Creates new string allocation for Split, and another for Substring!
        int bearerIndex = header.IndexOf("Bearer ");
        if (bearerIndex != -1)
        {
            return header.Substring(bearerIndex + 7);
        }
        return string.Empty;
    }

    public static ReadOnlySpan<char> ParseTokenSpan(ReadOnlySpan<char> headerSpan)
    {
        int bearerIndex = headerSpan.IndexOf("Bearer ".AsSpan());
        if (bearerIndex != -1)
        {
            // Slice() returns a new ReadOnlySpan pointing directly to original memory window!
            return headerSpan.Slice(bearerIndex + 7);
        }
        return ReadOnlySpan<char>.Empty;
    }
}
```

**Under the Hood / Why It Happens**:
`Span<T>` is defined as a `ref struct`, meaning it can only reside on the execution stack, never on the managed heap.

Under the hood, `Span<T>` is a **byref-like type** containing two fields:
1. `ref T _pointer`: A managed pointer pointing directly to the starting memory address.
2. `int _length`: The length of the memory segment.

Because `Span<T>` contains a interior managed pointer (`ref T`), the .NET CLR GC tracks it dynamically if it points into a heap array, ensuring GC compaction updates the pointer safely. Calling `.Slice(start, length)` simply updates `_pointer = _pointer + start` and adjusts `_length`, performing an $O(1)$ constant-time calculation with zero memory allocations.

**Key Takeaway / Safe Pattern**:
Use `ReadOnlySpan<char>` for string parsing, `Span<byte>` for network socket stream processing, and `Memory<T>` when asynchronous context boundaries (`async/await`) prevent using `ref struct` `Span<T>`.
