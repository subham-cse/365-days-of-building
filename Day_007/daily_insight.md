# Day 007: Event Loop Microtask Starvation and Automatic Type Coercion
**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript's single-threaded event loop processes tasks in strict priority queues: the **Microtask Queue** (`Promise.then`, `queueMicrotask`, `process.nextTick`) and the **Macrotask Queue** (`setTimeout`, `setInterval`, `setImmediate`, I/O events). 

Because the runtime drains the entire microtask queue completely before rendering frames or yielding to the next macrotask, recursively scheduling microtasks will completely starve the macrotask queue, freezing UI rendering, I/O operations, and timer handlers indefinitely.

JavaScript also features counterintuitive dynamic typing quirks such as `[] + {}` evaluating to `"[object Object]"`, while `{}` + `[]` evaluates to `0` in browser console contexts due to block scope parsing.

**The Code Snippet**:
```javascript
// Trap 1: Microtask Queue Starvation
function starveEventLoop() {
    console.log("Starving event loop...");
    
    // Macrotask: Will NEVER run!
    setTimeout(() => {
        console.log("Macrotask executed!");
    }, 0);

    function recursiveMicrotask() {
        Promise.resolve().then(() => {
            // Infinite microtask chain blocks macrotasks and UI frame updates
            recursiveMicrotask();
        });
    }

    recursiveMicrotask();
}

// Trap 2: Coercion & Array/Object Operator Expressions
console.log([] + {});        // "[object Object]"
console.log({} + []);        // 0 (when parsed as block statement + +[])
console.log([] == ![]);      // true
console.log([1, 2] + [3, 4]); // "1,23,4"
```

**Under the Hood / Why It Happens**:
The V8 JavaScript Engine event loop runs in distinct phases:
1. Execute synchronous script execution.
2. Process all tasks in the Microtask Queue until empty.
3. Perform UI render steps (if running in browser engine).
4. Pick ONE macrotask from the Macrotask Queue and execute.
5. Repeat from Step 2.

When a microtask creates another microtask via `Promise.resolve().then(...)`, the new microtask is appended to the current Microtask Queue being drained. The loop will not proceed to Step 3 or Step 4 until the queue size reaches zero.

For type coercions like `[] + {}`, the binary `+` operator calls `ToPrimitive()` on both operands. For arrays, `[].toString()` produces `""`. For objects, `{}.toString()` produces `"[object Object]"`. String concatenation yields `"" + "[object Object]"` = `"[object Object]"`. For `[] == ![]`, `![]` evaluates to `false`. `[] == false` converts both to numbers: `Number([])` becomes `0`, and `Number(false)` becomes `0`, evaluating `0 == 0` as `true`.

**Key Takeaway / Safe Pattern**:
Avoid unbounded microtask recursive loops. If executing continuous long-running background tasks, chunk execution across macrotasks using `setTimeout(fn, 0)` or `scheduler.yield()` in modern web browsers to grant the engine time to process user inputs and DOM updates.

```javascript
// SAFE: Yielding to Macrotask Queue to prevent UI/IO freezing
function ProcessLargeDataset(items) {
    let index = 0;

    function processBatch() {
        const start = performance.now();
        while (index < items.length && performance.now() - start < 10) {
            // Process item for up to 10ms
            index++;
        }

        if (index < items.length) {
            // Yield control back to Event Loop Macrotask Queue
            setTimeout(processBatch, 0);
        } else {
            console.log("Processing complete.");
        }
    }

    processBatch();
}
```
