# Day 221: C# Ref Structs, `Span<T>`, & Stack-Allocation Safety Guarantees

**Language / Domain**: C# / .NET Core Memory Performance

**The Core Concept / "Did You Know?"**:
High-performance C# code relies heavily on `Span<T>` and `ReadOnlySpan<T>` to achieve zero-allocation memory slicing over arrays, stack memory, and unmanaged memory buffers. To guarantee that a `Span<T>` referencing stack memory never outlives its stack frame (which would lead to dangling pointers and memory corruption), C# introduces **`ref struct`** types.

A `ref struct` is strictly confined to the execution stack frame. The C# compiler enforces strict compile-time constraints on `ref struct` instances: they cannot be boxed to `object` or interfaces, cannot be fields in standard `class` or normal `struct` instances, cannot be captured in lambda expressions or async/await state machines, and cannot be used as type parameters in generic methods.

**The Code Snippet**:
```csharp
using System;
using System.Text;

public ref struct CustomBufferWriter
{
    private Span<byte> _buffer;
    private int _written;

    public CustomBufferWriter(Span<byte> initialBuffer)
    {
        _buffer = initialBuffer;
        _written = 0;
    }

    public void WriteInt32(int value)
    {
        if (!BitConverter.TryWriteBytes(_buffer.Slice(_written), value))
        {
            throw new InvalidOperationException("Buffer capacity exceeded");
        }
        _written += sizeof(int);
    }

    public ReadOnlySpan<byte> WrittenSpan => _buffer.Slice(0, _written);
}

public class MemoryDemo
{
    public static void ProcessStackMemory()
    {
        // Stack allocation without Heap GC overhead
        Span<byte> stackBuffer = stackalloc byte[256];
        
        var writer = new CustomBufferWriter(stackBuffer);
        writer.WriteInt32(1024);
        writer.WriteInt32(2048);

        ReadOnlySpan<byte> result = writer.WrittenSpan;
        Console.WriteLine($"Bytes Written to Stack: {result.Length} bytes.");

        // --- COMPILER ERRORS (Enforced Safety): ---
        // object boxed = writer; // ERROR: Cannot box ref struct
        // Func<int> lex = () => writer.WrittenSpan.Length; // ERROR: Cannot capture ref struct in closure
    }

    // async Task BadAsyncMethod()
    // {
    //     Span<byte> span = stackalloc byte[16];
    //     await Task.Delay(100); // ERROR: Cannot use ref struct across await points!
    //     Console.WriteLine(span.Length);
    // }
}
```

**Under the Hood / Why It Happens**:
Why are `ref struct` rules so restrictive?

1. **Stack Lifetime Invariant**:
   When stack memory is allocated via `stackalloc`, it resides in the current function call frame. If a `Span<T>` referencing this frame were copied to the heap (via boxing or escaping into a `class` field), the memory frame would be popped when the function returns. Subsequent reads/writes to that heap object would corrupt random stack memory in another function frame.

2. **Async/Await State Machines**:
   When an `async` method hits an `await` expression, the compiler transforms the method into a generated state machine class on the heap. Any local variables used across the `await` point must be stored as fields in that heap state machine. Since `ref struct` variables cannot exist as heap fields, using them in `async` methods across `await` points is prohibited by the compiler.

3. **Runtime Interior Pointers (`byref` tracking)**:
   In the CLR runtime, `Span<T>` is defined internally as:
   ```csharp
   public readonly ref struct Span<T> {
       internal readonly ref T _pointer;
       internal readonly int _length;
   }
   ```
   The `ref T` is an interior pointer tracked by the GC stack scanner. Keeping it strictly on the stack enables the GC to update pointers rapidly during stack unwinding without complex object table updates.

**Key Takeaway / Safe Pattern**:
- Use `Span<T>`, `ReadOnlySpan<T>`, and custom `ref struct` types for CPU-intensive string parsing, serialization, and packet decoding to eliminate heap allocations.
- Never hold a `Span<T>` or `ref struct` across asynchronous `await` boundaries; process stack data synchronously before entering asynchronous execution steps.
