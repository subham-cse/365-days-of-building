# Day 159: BEAM Process Mailbox Leak via Selective Receive

**Language / Domain**: Elixir / Erlang

**The Core Concept / "Did You Know?"**:
In Erlang and Elixir's BEAM virtual machine, every process has an isolated internal memory space and a single incoming message buffer called the **Mailbox**. Messages sent to a process are appended to the end of its mailbox.

When using pattern matching in a `receive` block, BEAM performs **selective receive**: it iterates through the mailbox from oldest to newest until it finds a message matching one of the pattern clauses. If unhandled or unexpected messages arrive in the mailbox, they are *not* discarded. Instead, they remain in the process mailbox indefinitely, growing RAM usage and slowing down every subsequent `receive` operation.

**The Code Snippet**:

```elixir
defmodule MailboxLeakDemo do
  def worker_loop do
    receive do
      {:process_task, data} ->
        IO.puts("Processed task: #{data}")
        worker_loop()
      # BUG: No catch-all fallback pattern matching!
      # Unmatched messages like {:telemetry, ...} stay in the process mailbox forever.
    end
  end

  def run do
    pid = spawn(&worker_loop/0)

    # Send 100,000 unmatched noise messages
    for i <- 1..100_000 do
      send(pid, {:unmatched_event, i})
    end

    # Send a valid message
    send(pid, {:process_task, "Important Job"})
    
    # Process mailbox inspect
    {:message_queue_len, len} = Process.info(pid, :message_queue_len)
    IO.puts("Unhandled Mailbox Queue Size: #{len}") # Outputs: 100000
  end
end
```

**Under the Hood / Why It Happens**:
BEAM process mailboxes are backed by linked lists. When a `receive` statement is reached:
1. The VM sets a pointer to the head of the mailbox list.
2. It tests the current message against all `receive` pattern guards.
3. If no match is found, the VM increments the pointer to the next message in the list and repeats the check.
4. If a match is found, the message is unlinked from the mailbox and consumed.

When thousands of unmatched messages accumulate, every new `receive` block must traverse thousands of dead messages before finding a valid match. This transforms $O(1)$ message retrievals into $O(N)$ linear scans and eventually triggers BEAM Out-Of-Memory (OOM) crashes.

**Key Takeaway / Safe Pattern**:
Always include a fallback match clause `_ ->` with logging/discarding in custom `receive` loops, or use high-level abstractions like `GenServer`. `GenServer` handles unexpected messages via `handle_info/2` callbacks, ensuring unhandled messages don't leak inside process mailboxes.
