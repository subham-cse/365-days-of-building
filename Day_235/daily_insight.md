# Day 235: JavaScript Event Loop Microtask Starvation via Promise Chains

**Language / Domain**: JavaScript / Browser & Node.js Runtime Mechanics

**The Core Concept / "Did You Know?"**:
The JavaScript engine operates an Event Loop managing two main execution queues:
1. **Macrotask Queue (Task Queue)**: `setTimeout`, `setInterval`, `setImmediate` (Node.js), I/O events, UI rendering callbacks.
2. **Microtask Queue**: Resolved `Promise` callbacks (`.then()`, `.catch()`, `.finally()`), `queueMicrotask()`, `process.nextTick()` (Node.js).

Just like Dart, JavaScript prioritizes the **Microtask Queue**. After the current call stack clears, the V8 engine drains the entire Microtask Queue before yielding execution to the Macrotask Queue or performing UI layout repaints. Continuously enqueuing microtasks inside resolved Promise chains starves timers, rendering engines, and I/O handlers indefinitely.

**The Code Snippet**:
```javascript
function runMicrotaskStarvationDemo() {
  console.log("1. Starting Execution");

  // Scheduled on Macrotask Queue
  setTimeout(() => {
    console.log("MACROTASK: setTimeout executed! (Should run after 0ms)");
  }, 0);

  // Microtask Starvation Generator
  let count = 0;
  function recursiveMicrotask() {
    count++;
    if (count <= 100_000) {
      // Re-enqueueing microtask continuously onto Microtask Queue
      Promise.resolve().then(recursiveMicrotask);
    } else {
      console.log(`2. Microtask recursion complete after ${count} iterations.`);
    }
  }

  // Kick off microtask queue flooding
  Promise.resolve().then(recursiveMicrotask);

  console.log("3. Synchronous main call stack finished.");
}

runMicrotaskStarvationDemo();

/* Output Sequence:
1. Starting Execution
3. Synchronous main call stack finished.
2. Microtask recursion complete after 100001 iterations.
MACROTASK: setTimeout executed! (Should run after 0ms)
*/
```

**Under the Hood / Why It Happens**:
The V8 Event Loop processing algorithm executes steps in the following strict order:

```
1. Run synchronous JavaScript code until Call Stack is empty.
2. While (MicrotaskQueue is NOT empty):
     a. Dequeue microtask.
     b. Push microtask onto Call Stack and execute.
     c. (If microtask enqueues a new microtask, it gets added to the back of MicrotaskQueue!)
3. Perform browser UI style recalculation, layout, and repaint (if frame deadline reached).
4. Dequeue and execute ONE Macrotask from MacrotaskQueue.
5. Loop back to Step 2.
```

In the code snippet:
- `setTimeout` places its callback into the Macrotask Queue.
- `Promise.resolve().then(...)` places its callback into the Microtask Queue.
- When `recursiveMicrotask` runs, it calls `Promise.resolve().then(...)` before finishing, appending a new item to `MicrotaskQueue` while `MicrotaskQueue` is still being drained.
- Step 2 loops 100,000 times. During these 100,000 iterations, the event loop **never reaches Step 3 or Step 4**.
- In browser environments, an infinite microtask chain completely freezes the web page UI, making buttons unclickable and blocking DOM updates.

**Key Takeaway / Safe Pattern**:
- Avoid recursive `Promise.resolve().then()` or `queueMicrotask()` loops for heavy batch operations.
- For long-running asynchronous background processing, yield to the Macrotask Queue periodically using `setTimeout(fn, 0)` or `scheduler.yield()` (modern browsers) to allow UI rendering and timer updates:
  ```javascript
  async function yieldToMacrotaskQueue() {
    return new Promise(resolve => setTimeout(resolve, 0));
  }
  ```
- Use Web Workers or Node.js Worker Threads for CPU-bound computation tasks to preserve event loop responsiveness.
