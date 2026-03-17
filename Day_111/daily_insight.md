# Day 111: Goroutine Leaks and Unbuffered Channel Deadlocks
- **Language / Domain**: Go
- **The Core Concept / "Did You Know?"**: In Go, goroutines are lightweight, but they are not automatically garbage collected when they fall out of scope. If a goroutine is blocked forever waiting to send or receive on a channel, it will remain in memory indefinitely—causing a **Goroutine Leak**.

Goroutine leaks silently consume stack memory and retain open heap references, leading to gradual memory degradation in long-running services.

- **The Code Snippet**:
```go
package main

import (
	"fmt"
	"runtime"
	"time"
)

// LEAK BUG: Unbuffered channel send blocks if receiver leaves early
func fetchDataWithTimeout() string {
	ch := make(chan string) // Unbuffered channel!

	go func() {
		time.Sleep(100 * time.Millisecond) // Simulating slow API call
		ch <- "Data Payload"               // BLOCKS FOREVER if main function timed out!
		fmt.Println("Goroutine finished") // Will NEVER print on timeout!
	}()

	select {
	case res := <-ch:
		return res
	case <-time.After(20 * time.Millisecond): // Timeout triggers early return
		return "Timeout"
	}
}

func main() {
	fmt.Println("Starting Goroutines:", runtime.NumGoroutine())
	
	for i := 0; i < 5; i++ {
		fetchDataWithTimeout()
	}

	time.Sleep(200 * time.Millisecond)
	// Goroutines are leaked and still alive in runtime!
	fmt.Println("Leaked Goroutines Count:", runtime.NumGoroutine())
}
```

- **Under the Hood / Why It Happens**:
An unbuffered Go channel (`make(chan T)`) requires a synchronous handoff: a sender `gopark`s (suspends) its execution state in the runtime until a receiver is ready to read from the channel queue `hchan.waitq`.

If the receiving context exits via a `select` timeout, no process will ever read from `ch`. The background goroutine's stack frame remains parked in `gopark` state inside the Go runtime scheduler, unreachable by code but anchored in memory.

- **Key Takeaway / Safe Pattern**:
To prevent goroutine leaks on channel writes, use a buffered channel of size 1 (`make(chan string, 1)`) so the sender can complete its write and exit even if the receiver abandons the read context. Alternatively, pass a `context.Context` to handle explicit cancellation.
