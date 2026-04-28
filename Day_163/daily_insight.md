# Day 163: Microtask Queue Starvation and Event Loop Tick Phasing

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
The JavaScript engine (V8, JavaScriptCore, SpiderMonkey) runs on an event loop that alternates between executing task queues: **Macrotask Queue** (Timers, `setTimeout`, I/O, `setImmediate`) and **Microtask Queue** (`Promise.then`, `queueMicrotask`, `process.nextTick`).

Crucially, after the call stack empties, the JavaScript engine drains the **entire** Microtask Queue until it is completely empty before picking up the next single Macrotask. If microtasks continuously schedule additional microtasks, the Event Loop will never proceed to macrotasks, rendering DOM repaints, UI events, and timer callbacks completely frozen.

**The Code Snippet**:

```javascript
console.log('1. Script Start (Sync)');

// Schedule a Macrotask
setTimeout(() => {
  console.log('5. Macrotask Executed (setTimeout)');
}, 0);

// Schedule a Microtask that recursively schedules more microtasks
function recursiveMicrotask(count) {
  if (count > 3) return; // Guard for demo; remove guard to starve macrotasks indefinitely
  
  Promise.resolve().then(() => {
    console.log(`3. Microtask Step #${count}`);
    recursiveMicrotask(count + 1);
  });
}

// Schedule initial microtask
Promise.resolve().then(() => {
  console.log('2. First Microtask Executed');
});

recursiveMicrotask(1);

console.log('4. Script End (Sync)');
```

**Under the Hood / Why It Happens**:
The HTML Specification dictates the Event Loop processing model:
1. Select and run the oldest task from the *macrotask* queue.
2. Set the event loop's currently running task to null.
3. **Perform a microtask checkpoint**:
   - While the *microtask* queue is not empty:
     - Pop and run the oldest microtask.
4. Update rendering / browser UI repaints (if main thread browser environment).
5. Repeat from Step 1.

Because Step 3 is a loop that evaluates `microtaskQueue.length > 0`, any microtask callback that calls `Promise.resolve().then(...)` or `queueMicrotask(...)` pushes a new entry into `microtaskQueue` during the current checkpoint. Step 3 cannot exit until every microtask is resolved, effectively locking out Step 4 (rendering) and Step 1 (timers/events).

**Key Takeaway / Safe Pattern**:
Do not use `Promise` recursion or `queueMicrotask` for long-running iterative tasks. To break up heavy execution without blocking the event loop or starving UI repaints, yield control back to the macrotask queue using `await new Promise(resolve => setTimeout(resolve, 0))` or `requestIdleCallback()`.
