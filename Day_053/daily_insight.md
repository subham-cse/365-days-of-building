# Day 053: C# Span<T> and High-Performance Zero-Allocation Buffer Slicing

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
`Span<T>` and `ReadOnlySpan<T>` are ref struct types introduced in C# 7.2 that represent contiguous regions of arbitrary memory (managed heap arrays, stack-allocated memory, or unmanaged native memory).

Unlike traditional string slicing (`String.Substring()`) or array copying, slicing a `Span<T>` allocates zero heap memory. It provides direct, bounds-checked pointer-like access to sub-views of memory without triggering Garbage Collection pauses.

**The Code Snippet**:
```csharp
using System;
using System.Diagnostics;

public class SpanPerformanceDemo
{
    private const string Payload = "TIMESTAMP:2026-10-07;STATUS:OK;TRANSACTION_ID:9948271";

    public static string ParseTransactionIdLegacy(string data)
    {
        // Allocates multiple intermediate string instances on the heap!
        string[] parts = data.Split(';');
        string idPart = parts[2]; // "TRANSACTION_ID:9948271"
        return idPart.Substring(15); // Allocates new substring
    }

    public static ReadOnlySpan<char> ParseTransactionIdSpan(ReadOnlySpan<char> data)
    {
        // Zero-allocation slicing using ReadOnlySpan
        int lastSemicolon = data.LastIndexOf(';');
        ReadOnlySpan<char> idPart = data.Slice(lastSemicolon + 1); // "TRANSACTION_ID:9948271"
        int colonIdx = idPart.IndexOf(':');
        return idPart.Slice(colonIdx + 1); // Zero allocation slice!
    }

    public static void Main()
    {
        // 1. Stack memory allocation using Span
        Span<byte> stackBuffer = stackalloc byte[4];
        stackBuffer[0] = 0xDE;
        stackBuffer[1] = 0xAD;
        stackBuffer[2] = 0xBE;
        stackBuffer[3] = 0xEF;

        Console.WriteLine($"Stack buffer length: {stackBuffer.Length} bytes");

        // 2. String parsing demonstration
        string parsedLegacy = ParseTransactionIdLegacy(Payload);
        ReadOnlySpan<char> parsedSpan = ParseTransactionIdSpan(Payload.AsSpan());

        Console.WriteLine($"Parsed Transaction ID (Legacy): {parsedLegacy}");
        Console.WriteLine($"Parsed Transaction ID (Span):   {parsedSpan.ToString()}");
    }
}
```

**Under the Hood / Why It Happens**:
In the .NET Runtime, `Span<T>` is defined as a `byref struct` (a ref struct containing a `ref T` reference and a length integer):
```csharp
public readonly ref struct ReadOnlySpan<T>
{
    internal readonly ref T _pointer;
    internal readonly int _length;
}
```
Because ref structs must reside exclusively on the execution stack (and cannot be boxed or stored on the managed heap), the JIT compiler can generate raw pointer arithmetic operations for indexing and slicing without garbage collector tracing overhead.

**Key Takeaway / Safe Pattern**:
Use `ReadOnlySpan<char>` and `Span<byte>` in high-throughput hot paths (parsers, network protocols, JSON/CSV processing) to eliminate heap allocations. Note that `Span<T>` cannot be stored in fields of non-ref classes or used across async/await yield points; use `Memory<T>` or `ReadOnlyMemory<T>` for async heap-bound APIs.
