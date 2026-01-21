# Day 047: Elixir BEAM Process Mailboxes and Selective Receive Bottlenecks

**Language / Domain**: Elixir / BEAM

**The Core Concept / "Did You Know?"**:
In Elixir and Erlang running on the BEAM virtual machine, lightweight processes communicate exclusively via message passing. Each process owns a private sequential message queue called a **Mailbox**.

When a process uses pattern matching inside a `receive` block, BEAM performs **selective receive**: it scans the mailbox sequentially until it finds a message that matches the given clause pattern. Unmatched messages remain in the mailbox. If unhandled messages accumulate over time, scanning the mailbox degrades process performance from $O(1)$ to $O(N)$ for every subsequent incoming message.

**The Code Snippet**:
```elixir
defmodule MailboxDemo do
  def run do
    target_pid = self()

    # Simulate accumulation of unmatched messages in the mailbox
    for i <- 1..10_000 do
      send(target_pid, {:unmatched_junk, i})
    end

    # Send target priority message at the end
    send(target_pid, {:priority_target, "MATCH_ME"})

    # Benchmark selective receive with 10,000 unmatched items clogging the mailbox
    {time_us, result} = :timer.tc(fn ->
      receive do
        # Selective receive scans past all 10,000 junk messages to find priority_target!
        {:priority_target, payload} -> payload
      end
    end)

    IO.puts("Matched payload: #{result}")
    IO.puts("Selective receive execution time: #{time_us} microseconds")

    # Clear mailbox with a catch-all guard pattern
    drain_mailbox()
  end

  defp drain_mailbox do
    receive do
      _other -> drain_mailbox()
    after
      0 -> :ok
    end
  end
end

MailboxDemo.run()
```

**Under the Hood / Why It Happens**:
BEAM maintains two pointers for each process mailbox:
1. `save_queue`: Unmatched messages passed over during the current `receive` iteration.
2. `msg_q`: Incoming messages yet to be evaluated.

When executing `receive`, BEAM pops the top message from `msg_q` and tests it against the pattern clauses. If no pattern matches, BEAM moves that message to `save_queue` and checks the next message. If a process receives millions of unmatched messages, BEAM must iterate through millions of memory elements on every single `receive` call, leading to extreme CPU usage and memory pressure.

**Key Takeaway / Safe Pattern**:
Always include a generic catch-all match clause (`_other -> ...`) or construct dedicated state machine behaviors (such as `:gen_statem` or `GenServer`) to prevent unhandled messages from cluttering BEAM process mailboxes. Flush unused process mailboxes periodically.
