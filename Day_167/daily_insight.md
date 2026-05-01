# Day 167: Goroutine Leaks via Unbuffered Channel Deadlocks

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
Goroutines in Go are lightweight, managed by the Go runtime scheduler, and cost only ~2KB of initial stack memory. However, goroutines are not garbage collected automatically when they go out of scope. If a goroutine gets blocked indefinitely waiting to send or receive on a channel, it leaks permanently for the lifetime of the application.

A common concurrency mistake occurs when launching a background worker with an unbuffered channel and returning early (e.g., due to a timeout or context cancellation). The worker goroutine tries to send its result to the channel, but because no reader is listening anymore, it blocks forever.

**The Code Snippet**:

```go
package main

import (
	"context"
	"fmt"
	"runtime"
	"time"
)

func queryDatabase() string {
	time.Sleep(200 * time.Millisecond) // Simulate slow query
	return "db_result"
}

// BUGGY: Leaks goroutine on timeout
func fetchWithTimeoutBuggy() (string, error) {
	// Unbuffered channel
	ch := make(chan string)

	go func() {
		res := queryDatabase()
		// If context times out, caller exits and no one reads from `ch`.
		// This line BLOCKS FOREVER, leaking this goroutine!
		ch <- res 
	}()

	select {
	case res := <-ch:
		return res, nil
	case <-time.After(50 * time.Millisecond):
		return "", fmt.Errorf("timeout")
	}
}

// SAFE: Buffered channel allows non-blocking send even if caller leaves
func fetchWithTimeoutSafe() (string, error) {
	// Capacity of 1 prevents goroutine blocking on send
	ch := make(chan string, 1)

	go func() {
		res := queryDatabase()
		ch <- res // Never blocks because buffer size is 1!
	}()

	select {
	case res := <-ch:
		return res, nil
	case <-time.After(50 * time.Millisecond):
		return "", fmt.Errorf("timeout")
	}
}

main() {
	startingGoroutines := runtime.NumGoroutine()

	fetchWithTimeoutBuggy()
	time.Sleep(300 * time.Millisecond) // Wait for worker to finish sleep

	fmt.Printf("Goroutines before: %d, after buggy call: %d (Leaked 1!)\n", 
		startingGoroutines, runtime.NumGoroutine())

	fetchWithTimeoutSafe()
	time.Sleep(300 * time.Millisecond)
	fmt.Printf("Goroutines after safe call: %d (No leak!)\n", runtime.NumGoroutine())
}
```

**Under the Hood / Why It Happens**:
In Go's channel implementation (`runtime/chan.go`), sending to an unbuffered channel (`ch <- val`) requires a receiver goroutine to be actively waiting in the channel's wait queue (`recvq`).

If no receiver is waiting when the send executes:
1. The sending goroutine allocates a wait entry (`sudog`).
2. It enqueues `sudog` into the channel's `sendq` list.
3. It calls `gopark()`, transitioning the goroutine state from `_Grunning` to `_Gwaiting`.

Because the caller function has already returned and discarded the channel handle, no code will ever call `<-ch`. The parked goroutine stays in `_Gwaiting` state indefinitely, retaining its stack memory and captured variables.

**Key Takeaway / Safe Pattern**:
When launching a goroutine that writes a result back to a channel while the parent context may timeout or exit early:
1. Always use a buffered channel of capacity 1 (`make(chan T, 1)`).
2. Or use a `select` block inside the goroutine with `context.Done()` to abort the channel write if the operation was cancelled.
