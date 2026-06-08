# Day 215: BEAM Selective Receive & Process Mailbox Memory Leaks

**Language / Domain**: Elixir / BEAM

**The Core Concept / "Did You Know?"**:
In Erlang and Elixir's BEAM virtual machine, processes communicate by sending immutable messages to process mailboxes. A key feature of BEAM is **Selective Receive**: a `receive` block can match against specific message structures, leaving unmatched messages sitting in the process mailbox to be processed later.

While selective receive allows flexible message handling, it poses a severe hidden performance trap: if a process regularly receives messages that never match any active `receive` clauses, those unmatched messages remain in the mailbox indefinitely. Over time, every subsequent `receive` scan must traverse an ever-growing list of stale messages, causing message lookup latency to degrade from \(O(1)\) to \(O(N)\), leading to CPU spikes and memory exhaustion.

**The Code Snippet**:
```elixir
defmodule MailboxLeak do
  def worker_loop(state) do
    receive do
      {:priority_task, payload} ->
        # Process high priority message
        IO.puts("Processed priority: #{inspect(payload)}")
        worker_loop(state + 1)

      {:standard_task, payload} ->
        # Process standard message
        IO.puts("Processed standard: #{inspect(payload)}")
        worker_loop(state + 1)
      # MISSING: catch-all clause for unexpected or telemetry messages!
    end
  end

  def run_leak_demo do
    pid = spawn(fn -> worker_loop(0) end)

    # Simulate unexpected system logs or external messages flooding the process
    for i <- 1..100_000 do
      send(pid, {:telemetry_event, i, "metrics_data"})
    end

    # Send a single priority task
    t1 = System.monotonic_time(:microsecond)
    send(pid, {:priority_task, "Urgent Job"})
    
    # Wait brief moment for processing
    Process.sleep(50)
    t2 = System.monotonic_time(:microsecond)

    {:message_queue_len, len} = Process.info(pid, :message_queue_len)
    IO.puts("Mailbox backlog length: #{len}")
    IO.puts("Time elapsed for matching: #{t2 - t1} microseconds")
  end
end
```

**Under the Hood / Why It Happens**:
BEAM manages a process mailbox using two pointers:
1. `save_queue`: Contains messages that were already scanned during the current `receive` operation but failed to match.
2. `msg_q`: Points to new incoming messages appended by other processes.

When a `receive` block executes:
1. BEAM begins scanning from the top of `save_queue`.
2. If a message matches a pattern, it is consumed, and all messages currently in `save_queue` are prepended back into the main message queue for future scans.
3. If NO message in `save_queue` or `msg_q` matches, the process suspends, keeping all unmatched messages in `save_queue`.

If 100,000 telemetry messages enter a process whose `receive` block only matches `{:priority_task, _}` or `{:standard_task, _}`, every single priority task arrival requires BEAM to iterate over all 100,000 unmatched tuple pointers in memory before finding the matching message at the tail.

**Key Takeaway / Safe Pattern**:
To prevent unbounded mailbox growth and latency degradation in BEAM applications:
- Always include a fallback catch-all pattern (`other -> log_unhandled(other)`) in processes that execute selective receives, or ensure stale messages are explicitly discarded.
- Monitor `:message_queue_len` via `:erlang.process_info(pid, :message_queue_len)` or telemetry metrics in production.
- Use OTP abstractions like `GenServer`, which structure message loops cleanly, and handle unexpected messages inside `handle_info/2`.
