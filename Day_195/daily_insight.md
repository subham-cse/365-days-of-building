# Day 195: Go Goroutine Leaks via Unbuffered Channel Blocking

**Language / Domain**: Go

**The Core Concept / "Did You Know?"**:
Goroutines in Go are lightweight (starting around 2 KB of stack space), but they are **not** garbage collected automatically when they go out of scope. If a goroutine is blocked indefinitely waiting to send to or receive from a channel that nobody is listening to, it will remain suspended in memory forever.

This pattern is a frequent source of **goroutine leaks**. A single leaked goroutine holds its stack allocation, references to any variables captured in its scope, and any associated file handles or network sockets, causing slow memory leaks and eventual system failure in long-running services.

**The Code Snippet**:
```go
package main

import (
	"context"
	"fmt"
	"runtime"
	"time"
)

func queryData(ctx context.Context) string {
	// TRAP: Unbuffered channel!
	ch := make(chan string)

	go func() {
		// Simulating slow network fetch
		time.Sleep(200 * time.Millisecond)
		// If context timed out, nobody is reading from 'ch'.
		// This send blocks FOREVER, leaking this goroutine!
		ch <- "Database Record"
		fmt.Println("Goroutine finished send") // Never executed on timeout!
	}()

	select {
	case res := <-ch:
		return res
	case <-ctx.Done():
		// Context times out quickly
		return "Timeout Fallback"
	}
}

main() {
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()

	fmt.Printf("Goroutines before: %d\n", runtime.NumGoroutine())
	_ = queryData(ctx)

	time.Sleep(300 * time.Millisecond)
	fmt.Printf("Goroutines after timeout: %d\n", runtime.NumGoroutine())
	// Output: Goroutines after timeout: 2 (Goroutine leaked!)
}
```

**Under the Hood / Why It Happens**:
In Go's runtime scheduler, channels maintain an internal wait list of blocked senders (`sudog` structs). 

When a goroutine attempts to send to an unbuffered channel (`ch <- val`), the runtime checks if a receiver is waiting on `ch.recvq`. If no receiver is present, the sending goroutine transitions its status from `_Grunning` to `_Gwaiting` and is detached from its OS thread (`M`). Because `queryData` returned due to context cancellation, `ch` is garbage collected from the calling function scope, but the background goroutine remains permanently attached to the channel's wait list inside the runtime scheduler.

**Key Takeaway / Safe Pattern**:
To prevent channel send deadlocks and goroutine leaks, use **buffered channels** sized appropriately for expected concurrency (e.g., `make(chan string, 1)`), or use non-blocking select sends paired with `ctx.Done()`.

```go
// Safe Pattern: Buffered channel allows send to complete without waiting for receiver
func queryDataSafe(ctx context.Context) string {
	// Buffer size 1 prevents sender blocking even if receiver exits early
	ch := make(chan string, 1)

	go func() {
		time.Sleep(200 * time.Millisecond)
		ch <- "Database Record" // Non-blocking write into buffer!
	}()

	select {
	case res := <-ch:
		return res
	case <-ctx.Done():
		return "Timeout Fallback"
	}
}
```
