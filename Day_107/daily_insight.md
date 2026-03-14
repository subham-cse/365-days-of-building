# Day 107: Event Loop Microtask vs Macrotask Execution Order
- **Language / Domain**: JavaScript
- **The Core Concept / "Did You Know?"**: JavaScript executes asynchronous callbacks via an event loop operating with two queue levels: **Macrotasks** (or Tasks: `setTimeout`, `setInterval`, `setImmediate`, I/O) and **Microtasks** (`Promise` callbacks, `queueMicrotask`, `MutationObserver`).

At the end of every task execution turn, the JavaScript runtime MUST completely drain the **entire** Microtask Queue before yielding to render frames or processing the next Macrotask from the Macrotask Queue.

- **The Code Snippet**:
```javascript
console.log("1. Synchronous Start");

setTimeout(() => {
  console.log("4. Macrotask: setTimeout 1");
  
  Promise.resolve().then(() => {
    console.log("5. Microtask inside setTimeout");
  });
}, 0);

Promise.resolve().then(() => {
  console.log("3. Microtask: Promise 1");
});

queueMicrotask(() => {
  console.log("3b. Microtask: queueMicrotask");
});

console.log("2. Synchronous End");

/*
Execution Output:
1. Synchronous Start
2. Synchronous End
3. Microtask: Promise 1
3b. Microtask: queueMicrotask
4. Macrotask: setTimeout 1
5. Microtask inside setTimeout
*/
```

- **Under the Hood / Why It Happens**:
The V8 JavaScript engine processes execution in turns:
1. Execute call stack to completion (synchronous script execution).
2. Check Microtask Queue. If microtasks exist, pop and execute microtasks until the queue is completely empty (including microtasks scheduled by microtasks).
3. Perform render updates (in browser environments).
4. Take the single oldest task from the Macrotask Queue and push it onto the call stack.
5. Repeat steps 2–4.

- **Key Takeaway / Safe Pattern**:
Be careful with recursive Promise/microtask chains; they will lock up the main thread and prevent user interface rendering, DOM updates, and `setTimeout` executions from ever occurring.
