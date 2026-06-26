# Day 231: BEAM Process Mailbox Pattern Matching Guards & Message Queue Bottlenecks

**Language / Domain**: Elixir / Erlang BEAM Concurrency

**The Core Concept / "Did You Know?"**:
On the BEAM Virtual Machine, processes process incoming messages from their mailbox using pattern matching. A common optimization misconception is that complex guard clauses (`when is_integer(x) and x > 100`) inside a `receive` loop help filter out irrelevant messages quickly.

In reality, if a message matches the structural signature of a `receive` clause but fails the **guard evaluation**, BEAM skips that message, leaving it sitting in the process mailbox. The skipped message is placed into the process's internal `save_queue`, forcing every subsequent `receive` iteration to scan past it. Using restrictive guards without handling unmatched cases creates silent CPU bottlenecks and memory leaks in high-throughput OTP applications.

**The Code Snippet**:
```elixir
defmodule MailboxGuardDemo do
  # TRAP: Restrictive guard leaves non-matching payloads in the mailbox!
  def restrictive_receiver(processed_count) do
    receive do
      {:data, id, val} when is_integer(val) and val > 50 ->
        # Only processes values > 50!
        # If val <= 50, the message stays in the mailbox forever!
        restrictive_receiver(processed_count + 1)
    after
      100 ->
        {:message_queue_len, len} = Process.info(self(), :message_queue_len)
        IO.puts("[Restrictive] Mailbox len after timeout: #{len}, Processed: #{processed_count}")
    end
  end

  # SAFE PATTERN: Match structure broadly, handle logic conditionally or drain invalid messages
  def safe_receiver(processed_count) do
    receive do
      {:data, _id, val} ->
        if is_integer(val) and val > 50 do
          # Process valid payload
          safe_receiver(processed_count + 1)
        else
          # Explicitly discard or log invalid payload to clear mailbox!
          safe_receiver(processed_count)
        end
    after
      100 ->
        {:message_queue_len, len} = Process.info(self(), :message_queue_len)
        IO.puts("[Safe] Mailbox len after timeout: #{len}, Processed: #{processed_count}")
    end
  end

  def run do
    # Test Restrictive Receiver
    pid1 = spawn(fn -> restrictive_receiver(0) end)
    for i <- 1..1000 do
      send(pid1, {:data, i, 10}) # Sending values <= 50
    end

    # Test Safe Receiver
    pid2 = spawn(fn -> safe_receiver(0) end)
    for i <- 1..1000 do
      send(pid2, {:data, i, 10}) # Sending values <= 50
    end

    Process.sleep(300)
  end
end
```

**Under the Hood / Why It Happens**:
BEAM process mailbox evaluation operates in distinct runtime phases:

1. The process checks the head of its message queue.
2. If the message matches the clause pattern `{:data, id, val}`, BEAM evaluates the guard expression `when is_integer(val) and val > 50`.
3. If the guard evaluates to `false`, BEAM determines that the clause did **not** match.
4. Because no other `receive` clauses exist in the `restrictive_receiver` block, BEAM moves the message off the main queue into the process `save_queue`.
5. When the next message arrives, BEAM scans past all messages parked in `save_queue` before inspecting new arrivals.

When 1,000 low-value messages arrive, `restrictive_receiver` parks all 1,000 messages in `save_queue`. Every future valid message must iterate through all 1,000 skipped items, degrading lookup speed from \(O(1)\) to \(O(N)\). In contrast, `safe_receiver` pattern-matches the tuple unconditionally, consumes it from the mailbox, and drops invalid items instantly.

**Key Takeaway / Safe Pattern**:
- Avoid using restrictive guard clauses in `receive` blocks to drop unwanted messages.
- Always match message structures broadly and discard or route invalid payloads inside the execution block (`if`, `case`, or separate handler functions).
- Regularly monitor process mailbox lengths using `:erlang.process_info(pid, :message_queue_len)` in production systems to catch mailbox leaks early.
