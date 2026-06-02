# Day 209: C# `ref struct`, Stack Allocation, and `Span<T>` Safety

**Language / Domain**: C#

**The Core Concept / "Did You Know?"**:
In C#, `class` instances are reference types allocated on the managed garbage collector (GC) heap, whereas standard `struct` instances are value types allocated inline on the stack or inside their containing object.

To enable ultra-high performance zero-allocation memory parsing, modern C# (.NET Core 2.1+) introduced `Span<T>` and `ref struct`. A `ref struct` is guaranteed to be allocated **strictly on the execution stack**. It can **never** be allocated on the heap under any circumstances. 

Because a `ref struct` lives exclusively on the stack frame, C# compiler safety rules strictly forbid `ref struct` types from being boxed, implemented by interfaces, captured in async state machines (`async`/`await`), captured inside lambda closures, or used as fields inside standard heap-allocated classes.

**The Code Snippet**:
```csharp
using System;

public ref struct StackOnlyBuffer
{
    public Span<byte> Data;

    public StackOnlyBuffer(Span<byte> initialBuffer)
    {
        Data = initialBuffer;
    }
}

public class MemoryParsingDemo
{
    public static void ProcessStringData(string rawInput)
    {
        // Zero-allocation stack slicing via ReadOnlySpan<char>
        ReadOnlySpan<char> inputSpan = rawInput.AsSpan();
        ReadOnlySpan<char> header = inputSpan.Slice(0, 4);

        Console.WriteLine($"Extracted Header: {header.ToString()}");
    }

    // TRAP 1: Cannot use ref struct inside async methods!
    /*
    public static async Task ProcessAsync(StackOnlyBuffer buf)
    {
        await Task.Delay(100); // Error: Cannot yield inside method with ref struct!
    }
    */

    // TRAP 2: Cannot box or assign to object/interface!
    /*
    public static void BoxTrap(StackOnlyBuffer buf)
    {
        object boxed = buf; // Error: Cannot convert 'StackOnlyBuffer' to 'object'!
    }
    */

    public static void Main()
    {
        byte[] rawBytes = new byte[100];
        Span<byte> stackBuffer = rawBytes.AsSpan();
        
        StackOnlyBuffer bufferWrapper = new StackOnlyBuffer(stackBuffer);
        ProcessStringData("HTTP/1.1 200 OK");
    }
}
```

**Under the Hood / Why It Happens**:
The .NET CLR runtime guarantees stack safety for `ref struct` types through compile-time escape analysis (`System.Runtime.CompilerServices.IsByRefLikeAttribute`):

1. **Async State Machines**: When an `async` method encounters an `await` expression, the C# compiler generates a hidden state machine class implementing `IAsyncStateMachine`. Any local variables in scope across `await` points are promoted to fields inside this state machine class on the heap. Because a `ref struct` cannot exist on the heap, holding a `ref struct` across an `await` boundary is prohibited.
2. **GC Pointer Safety**: A `ref struct` may contain `ref` fields (interior pointers into GC heap memory or native stack frames). Allowing interior pointers on the managed heap would severely complicate GC stack/heap pointer scanning algorithms and risk dangling pointers.

**Key Takeaway / Safe Pattern**:
Use `Span<T>`, `ReadOnlySpan<T>`, and `ref struct` for hot-path buffer slicing, string parsing, and binary serialization to achieve zero GC allocation overhead. When buffer data must cross `async`/`await` boundaries, use `Memory<T>` or `ReadOnlyMemory<T>` instead.

```csharp
// Safe Pattern: Use Memory<T> for heap-compatible async buffer handling
public static async Task ProcessAsyncMemory(ReadOnlyMemory<char> buffer)
{
    await Task.Delay(100);
    ReadOnlySpan<char> span = buffer.Span; // Slice span locally after await completes!
    Console.WriteLine($"Processed: {span.Length} chars");
}
```
