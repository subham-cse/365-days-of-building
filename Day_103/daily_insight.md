# Day 103: BEAM Process Mailboxes and Unbounded Queue Overflow
- **Language / Domain**: Elixir / Erlang / Racket
- **The Core Concept / "Did You Know?"**: In Erlang/Elixir on the BEAM virtual machine, every process has an isolated internal message queue known as its **mailbox**. Mailbox sizes are unbounded by default. 

When a process receives messages using selective pattern matching (`receive do ... end`), any message that does **not** match the specified patterns is left behind in the mailbox! Over time, unmatched messages accumulate, turning pattern matching into an $O(N)$ linear search through thousands of dead messages and causing massive garbage collection overhead or OOM crashes.

- **The Code Snippet**:
```elixir
defmodule MailboxLeakDemo do
  def worker do
    receive do
      {:process_task, id} ->
        IO.puts("Processed task #{id}")
        worker()
      # CRITICAL BUG: No catch-all fallback clause!
      # Unrecognized messages (e.g. {:heartbeat}, {:telemetry, data}) stay in mailbox forever!
    end
  end

  def safe_worker do
    receive do
      {:process_task, id} ->
        IO.puts("Processed task #{id}")
        safe_worker()

      unknown_message ->
        IO.puts("Discarding unknown message: #{inspect(unknown_message)}")
        safe_worker()
    end
  end
end
```

- **Under the Hood / Why It Happens**:
The BEAM VM maintains a pointer (`save_mark`) into the message queue for selective receive operations. 

When `receive` is evaluated, BEAM scans from `save_mark` through the entire queue looking for a pattern match. If a match is found, the message is unlinked and extracted. If no match is found, the message is skipped and left in memory, forcing every subsequent `receive` call to iterate over every accumulated skipped message from the beginning.

- **Key Takeaway / Safe Pattern**:
Always include a catch-all pattern matching clause (`other -> ...`) or use standard OTP abstractions (`GenServer`), which log and discard unhandled calls/casts by default.
