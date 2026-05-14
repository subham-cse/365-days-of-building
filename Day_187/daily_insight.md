# Day 187: Elixir BEAM Mailbox Growth and Selective Receive Bottlenecks

**Language / Domain**: Elixir / Erlang

**The Core Concept / "Did You Know?"**:
In the Erlang VM (BEAM), processes communicate exclusively via message passing. Every process maintains its own private queue called a **mailbox**. Messages sent to a process land in its mailbox in the exact order they arrive.

When a process executes a `receive do ... end` block with pattern matching, BEAM performs a **selective receive**. It scans the mailbox from oldest to newest message until it finds one that matches the pattern. If unmatched messages accumulate in the process mailbox, every subsequent `receive` call must traverse all pending unmatched messages before finding a matching candidate. This converts message evaluation complexity from \(O(1)\) to \(O(N)\), creating severe performance degradation and eventual out-of-memory crashes.

**The Code Snippet**:
```elixir
defmodule SelectiveReceiveWorker do
  def loop do
    receive do
      # Only matches messages tagged with :priority
      {:priority, msg} ->
        IO.puts("Processed priority message: #{msg}")
        loop()
    end
  end

  def run_demo do
    pid = spawn(&loop/0)

    # Flooding the mailbox with standard messages that DO NOT match :priority
    for i <- 1..50_000 do
      send(pid, {:standard, "Standard payload ##{i}"})
    end

    # Send one priority message at the end
    send(pid, {:priority, "Urgent task!"})

    # The receive loop must now scan through 50,000 unmatched messages first!
  end
end
```

**Under the Hood / Why It Happens**:
The BEAM process struct maintains two internal pointers for message queues: `msg_in` (newly received messages) and `msg_save` (messages skipped during selective receive). 

When executing `receive`, BEAM scans the process message queue starting from `save_queue`. If a message does not match any guard or clause in `receive`, it is moved to `save_queue`, and the pointer advances to the next message. If thousands of unmatched messages sit in `save_queue`, every pattern evaluation involves a full linear scan of thousands of heap allocations, consuming CPU cycles and inflating memory consumption.

**Key Takeaway / Safe Pattern**:
Always consume unmatched messages using a catch-all fallback clause or handle messages sequentially using `GenServer` behavior modules. If selective processing is required, maintain separate dedicated queues in process state or use discrete worker processes.

```elixir
defmodule SafeWorker do
  def loop do
    receive do
      {:priority, msg} ->
        IO.puts("Priority: #{msg}")
        loop()
      
      # Catch-all clause prevents mailbox bloat and quadratic scan degradation
      other ->
        IO.puts("Unhandled message ignored: #{inspect(other)}")
        loop()
    end
  end
end
```
