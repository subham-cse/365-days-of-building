# Day 191: JavaScript Microtasks vs Macrotasks Execution Order

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
In JavaScript's event loop runtime, asynchronous operations are split into two distinct execution queues: **Microtask Queue** (`Promise.then`, `queueMicrotask`, `MutationObserver`) and **Macrotask / Task Queue** (`setTimeout`, `setInterval`, `setImmediate`, I/O callbacks).

The event loop processes exactly **one** macrotask from the task queue, and then immediately drains the **entire** microtask queue before yielding control back to the rendering engine or picking the next macrotask. As a result, microtasks spawned inside microtasks will execute before any pending `setTimeout(..., 0)` callbacks, potentially delaying timers indefinitely.

**The Code Snippet**:
```javascript
console.log('1. Script start');

setTimeout(() => {
  console.log('5. Macrotask: setTimeout 0ms');
}, 0);

Promise.resolve().then(() => {
  console.log('3. Microtask 1: Promise.then');
  queueMicrotask(() => {
    console.log('4. Microtask 2: Chained queueMicrotask');
  });
});

console.log('2. Script end');

// Output order:
// 1. Script start
// 2. Script end
// 3. Microtask 1: Promise.then
// 4. Microtask 2: Chained queueMicrotask
// 5. Macrotask: setTimeout 0ms
```

**Under the Hood / Why It Happens**:
The V8 / browser event loop follows a strict processing lifecycle:

1. Execute synchronous call stack script.
2. When call stack clears, check **Microtask Queue**.
3. Continuously pop and execute microtasks until `Microtask Queue.length === 0`.
4. Render UI frame updates (in browser context).
5. Pop **one** task from **Macrotask Queue** (`setTimeout`), push to call stack, and execute.
6. Repeat step 2.

Because step 3 drains the entire microtask queue synchronously before moving to step 4 or 5, promises always starve timers if scheduled in rapid succession.

**Key Takeaway / Safe Pattern**:
Use microtasks (`Promise.then`, `queueMicrotask`) for light asynchronous state updates that must resolve prior to UI re-renders. Use `setTimeout` or `requestAnimationFrame` when yielding execution to allow browser rendering or user I/O processing between computational batches.

```javascript
// Safe Pattern: Break long microtask loops into macrotasks to preserve responsiveness
function processBatch(items) {
  if (items.length === 0) return;
  
  // Process current slice...
  const chunk = items.splice(0, 100);
  
  // Defer next iteration to macrotask queue
  setTimeout(() => processBatch(items), 0);
}
```
