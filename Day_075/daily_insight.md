# Day 075: BEAM Process Mailboxes and Unmatched Pattern Traps in Elixir

**Language / Domain**: Elixir / Erlang (BEAM)

**The Core Concept / "Did You Know?"**:
Elixir and Erlang execute on the BEAM virtual machine using lightweight processes communicating strictly via asynchronous message passing. Each BEAM process has a sequential **Mailbox**.

When a process executes a `receive` block, BEAM checks messages in the process mailbox sequentially from top to bottom, matching them against pattern clauses defined inside `receive`. However, if messages arrive that do NOT match any pattern in the `receive` block, **they are not discarded—they remain in the mailbox indefinitely!** 

Accumulating unmatched messages causes a invisible memory leak known as mailbox bloat, severely degrading message lookup performance and increasing garbage collection overhead.

**The Code Snippet**:
```elixir
defmodule MailboxDemo do
  # TRAP: Selective receive with missing wildcard guard clause
  def receive_selective_unsafe do
    receive do
      {:priority, msg} ->
        IO.puts("Processed priority message: #{msg}")
        # Message is removed from mailbox, but unmatched {:standard, _} messages remain!
    after
      100 -> :timeout
    end
  end

  # SAFE PATTERN: Flushes or logs unexpected/unmatched messages
  def receive_safe do
    receive do
      {:priority, msg} ->
        IO.puts("Processed priority message: #{msg}")

      {:standard, msg} ->
        IO.puts("Processed standard message: #{msg}")

      # Catch-all guard clause prevents mailbox accumulation!
      other ->
        IO.puts("WARNING: Received unexpected message: #{inspect(other)}")
    end
  end

  def run do
    pid = self()

    # Send a mix of unexpected and priority messages
    send(pid, {:standard, "Routine maintenance"})
    send(pid, {:unmatched_junk, 12345})
    send(pid, {:priority, "CRITICAL ALERT"})

    IO.puts("Mailbox message count before receive: #{Process.info(pid, :message_queue_len) |> elem(1)}")

    # Unsafe selective receive only handles {:priority, _}
    receive_selective_unsafe()

    # The mailbox STILL contains {:standard, _} and {:unmatched_junk, _}!
    IO.puts("Mailbox message count AFTER unsafe receive: #{Process.info(pid, :message_queue_len) |> elem(1)}")
  end
end

MailboxDemo.run()
```

**Under the Hood / Why It Happens**:
BEAM maintains two pointers for each process mailbox:
1. `save_queue`: The start of the message queue.
2. `msg_q`: The current message being evaluated against pattern guards.

When evaluating `receive`, BEAM scans down `msg_q`. If a pattern matches, the message is unlinked from the queue and garbage collected. If a pattern fails to match, BEAM advances `msg_q` to the next message while leaving the skipped message intact.

If skipped messages accumulate to thousands or millions of elements, every subsequent `receive` operation must traverse the entire linked list of skipped messages before reaching new arrivals ($O(N)$ traversal overhead per message).

**Key Takeaway / Safe Pattern**:
Always include a catch-all wildcard clause (`other -> ...`) or handle expected message variants when writing `receive` loops in GenServers and raw BEAM processes. Regularly monitor `:message_queue_len` in telemetry to detect mailbox leaks in production.
