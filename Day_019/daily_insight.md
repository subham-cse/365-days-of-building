# Day 019: BEAM Process Mailbox Starvation and Pattern Matching Order
**Language / Domain**: Elixir / Erlang

**The Core Concept / "Did You Know?"**:
Elixir and Erlang run on the **BEAM Virtual Machine**, utilizing actor-model concurrency where lightweight BEAM processes communicate by sending messages to process **Mailboxes**. 

When a process executes a `receive` block, BEAM performs **Selective Receive**: it searches through the process mailbox sequentially from top to bottom until it finds a message matching the specified pattern match guards. Unmatched messages remain in the mailbox indefinitely. If a process receives many non-matching messages, its mailbox grows continuously, leading to process mailbox starvation, CPU consumption during scan iterations, and ultimate BEAM node memory exhaustion.

**The Code Snippet**:
```elixir
defmodule BEAMMailboxTrap do
  def worker do
    receive do
      # TRAP: Only matches explicit tuple {:work, data}
      {:work, data} ->
        IO.puts("Processing work: #{inspect(data)}")
        worker()
    end
  end

  def demonstrate_mailbox_starvation do
    pid = spawn(&worker/0)

    # Send 100,000 unmatched messages into worker mailbox
    for i <- 1..100_000 do
      send(pid, {:unmatched_log, "Log entry #{i}"})
    end

    # Send 1 valid message
    send(pid, {:work, "Important Job"})

    # Check process mailbox size using Process info
    {:message_queue_len, len} = Process.info(pid, :message_queue_len)
    IO.puts("Mailbox backlog size: #{len}") 
    # Output: 100001 messages! BEAM must scan 100,000 skipped items on every receive!
  end
end
```

**Under the Hood / Why It Happens**:
Every BEAM process memory layout contains a stack, a heap, and a message queue (mailbox). The mailbox is implemented as two linked lists: the *save queue* and the *msg queue*.

When a process enters a `receive` block:
1. BEAM inspects the head message of the message queue.
2. It tests pattern matching rules defined in the `receive` block.
3. If no match occurs, the message is moved out of the main queue into the save queue, and BEAM tests the next message.
4. Once a message matches, it is executed and removed, and all saved unmatched messages are dumped back into the front of the main queue!

If 100,000 unmatched messages accumulate in a mailbox, processing 1 valid message requires checking 100,000 patterns in RAM ($O(N)$ lookup per message receive).

**Key Takeaway / Safe Pattern**:
Include a fallback catch-all clause (`_other -> ...`) or handle unexpected messages in `receive` blocks to prevent mailbox buildup. Alternatively, monitor process mailbox size using telemetry metrics (`:message_queue_len`).

```elixir
defmodule BEAMMailboxSafe do
  def worker_safe do
    receive do
      {:work, data} ->
        IO.puts("Processing work safely: #{inspect(data)}")
        worker_safe()

      # SAFE: Handle or discard unmatched messages immediately!
      other ->
        IO.puts("Discarding unexpected message: #{inspect(other)}")
        worker_safe()
    after
      5000 ->
        # Timeout safety block
        IO.puts("No messages received for 5s")
        worker_safe()
    end
  end
end
```
