# Day 131: Elixir BEAM Process Mailbox Bottlenecks & Selective Receive Traps

**Language / Domain**: Elixir / Erlang

**The Core Concept / "Did You Know?"**:
In Elixir and the Erlang BEAM virtual machine, processes communicate via asynchronous message passing into a process **Mailbox**. When a process evaluates a `receive` block with pattern matching, BEAM searches the mailbox sequentially from oldest to newest message until it finds one matching the pattern.

However, if unmatched messages enter the mailbox, they are NOT discarded—they remain queued in the process mailbox indefinitely! A common performance anti-pattern occurs when using selective `receive` without a fallback catch-all guard. As unmatched messages accumulate, every subsequent `receive` operation must traverse thousands of stale messages, causing message lookup latency to degrade from $O(1)$ to $O(N)$.

**The Code Snippet**:
```elixir
defmodule MailboxDemo do
  def worker do
    receive do
      {:action, data} ->
        IO.puts("Processed action: #{data}")
        worker()
      # TRAP: If unhandled messages arrive, mailbox grows endlessly!
      # FIX: Include a catch-all or periodic flush mechanism
      other ->
        IO.puts("Warning: Flushed unexpected message: #{inspect(other)}")
        worker()
    after
      5000 ->
        IO.puts("Timeout waiting for messages")
    end
  end

  def run do
    pid = spawn(&worker/0)

    # Send 10,000 unmatched messages
    for i <- 1..10000 do
      send(pid, {:unmatched_tag, i})
    end

    # Send 1 valid action message
    send(pid, {:action, "Success!"})
  end
end
```

**Under the Hood / Why It Happens**:
Each BEAM process has an associated control block containing two message pointers:
1. `msg_q`: Points to the head of the incoming mailbox queue.
2. `save_queue`: Stores messages that were evaluated by `receive` but failed to match any pattern in the current `receive` block.

When selective matching occurs:
- BEAM iterates through `msg_q`.
- If a message matches, it is removed and processed.
- If a message does NOT match, BEAM moves it into `save_queue` and checks the next message.
- When the `receive` block exits, `save_queue` contents are prepended back onto `msg_q`.

If a process receives high volumes of unmatched messages, `save_queue` scanning consumes massive CPU cycles during every pattern match check, leading to process memory leaks and CPU exhaustion.

**Key Takeaway / Safe Pattern**:
Always match expected messages promptly or handle unhandled messages with catch-all clauses (`other -> ...`) or `GenServer` handles. Monitor mailbox depth in production using `Process.info(pid, :message_queue_len)`.
