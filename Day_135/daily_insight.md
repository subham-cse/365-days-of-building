# Day 135: JavaScript Event Loop Microtasks vs Macrotasks Execution Order

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript operates on a single-threaded event loop, but task scheduling is split into two distinct queues: the **Microtask Queue** (Promises, `queueMicrotask`, `process.nextTick` in Node) and the **Macrotask Queue** (Task Queue: `setTimeout`, `setInterval`, `setImmediate`, I/O operations).

Before processing **a single** new task from the Macrotask queue, the engine must completely drain the entire Microtask queue! If microtasks continuously spawn new microtasks, the event loop will starve macrotasks and render UI thread updates or timer callbacks completely frozen.

**The Code Snippet**:
```javascript
console.log('1. Script start (Synchronous)');

setTimeout(() => {
  console.log('5. Macrotask 1: setTimeout 0ms');
}, 0);

Promise.resolve()
  .then(() => {
    console.log('3. Microtask 1: Promise.then');
    return Promise.resolve();
  })
  .then(() => {
    console.log('4. Microtask 2: Chained Promise.then');
  });

queueMicrotask(() => {
  console.log('3b. Microtask 3: queueMicrotask');
});

console.log('2. Script end (Synchronous)');

/*
  OUTPUT EXECUTION ORDER:
  1. Script start (Synchronous)
  2. Script end (Synchronous)
  3. Microtask 1: Promise.then
  3b. Microtask 3: queueMicrotask
  4. Microtask 2: Chained Promise.then
  5. Macrotask 1: setTimeout 0ms
*/
```

**Under the Hood / Why It Happens**:
The V8 / JavaScript engine execution cycle follows this exact sequence:
1. Execute the main call stack synchronously until empty.
2. Check the **Microtask Queue**:
   - Dequeue and execute microtasks one by one.
   - If a microtask enqueues another microtask, add it to the tail of the Microtask Queue and keep executing until the queue length reaches zero.
3. Perform DOM rendering / layout updates (in browser environments).
4. Pop **one single** task from the **Macrotask Queue** and run it.
5. Loop back to Step 2 (drain Microtasks again).

Because step 2 requires *complete exhaustion* of microtasks, Promises and `queueMicrotask` take absolute scheduling precedence over `setTimeout(..., 0)`.

**Key Takeaway / Safe Pattern**:
Do not use recursive `Promise` chains or recursive `queueMicrotask()` for heavy background processing. Use `setTimeout(..., 0)` or `requestIdleCallback()` to break up intensive CPU work and permit the event loop to repaint and process I/O events.
