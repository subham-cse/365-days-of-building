# Day 035: Microtasks vs Macrotasks in JavaScript Event Loop

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript's concurrency model relies on an event loop managing two distinct task queues: the Microtask Queue (Promises, `queueMicrotask`, `MutationObserver`) and the Macrotask Queue (`setTimeout`, `setInterval`, `setImmediate`, I/O). The event loop guarantees that the Microtask Queue is completely drained after the execution of any synchronous script or macrotask, BEFORE rendering updates or picking the next macrotask.

This means recursive or heavily chained microtasks can starve the event loop, freezing UI renders and delaying timer callbacks infinitely, despite `setTimeout(..., 0)` appearing to run immediately.

**The Code Snippet**:
```javascript
function demonstrateTaskExecutionOrder() {
    console.log("1. Synchronous script start");

    setTimeout(() => {
        console.log("5. Macrotask 1 (setTimeout 0ms)");
        
        Promise.resolve().then(() => {
            console.log("6. Microtask nested inside Macrotask 1");
        });
    }, 0);

    Promise.resolve().then(() => {
        console.log("3. Microtask 1 (Promise.then)");
    }).then(() => {
        console.log("4. Microtask 2 (Chained Promise)");
    });

    queueMicrotask(() => {
        console.log("3b. Microtask explicit (queueMicrotask)");
    });

    console.log("2. Synchronous script end");
}

demonstrateTaskExecutionOrder();

/* Expected Execution Order Output:
 1. Synchronous script start
 2. Synchronous script end
 3. Microtask 1 (Promise.then)
 3b. Microtask explicit (queueMicrotask)
 4. Microtask 2 (Chained Promise)
 5. Macrotask 1 (setTimeout 0ms)
 6. Microtask nested inside Macrotask 1
*/
```

**Under the Hood / Why It Happens**:
The V8 / ECMAScript runtime specification outlines a strict processing sequence:
1. Execute the main call stack to completion.
2. Check the Microtask Queue. Run and pop tasks one by one until the queue length is zero. If a microtask enqueues another microtask, it runs in the current loop tick.
3. Perform DOM layout and repaint (browser engine dependent).
4. Select the oldest pending task from the Macrotask Queue, execute it, and return to step 2.

Because step 2 loops until the microtask queue is entirely empty, scheduling continuous microtasks keeps control inside the microtask drain phase, starving macrotasks and rendering frames.

**Key Takeaway / Safe Pattern**:
Use `Promise` / `queueMicrotask` for immediate state consistency and lightweight async scheduling. If performing heavy background work that shouldn't block UI renders or timers, chunk the execution using macrotasks like `setTimeout(fn, 0)` or `requestIdleCallback`.
