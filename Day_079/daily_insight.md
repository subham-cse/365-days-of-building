# Day 079: Event Loop Microtask vs Macrotask Execution Order in JavaScript

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript operates on a single-threaded Event Loop architecture. Asynchronous execution is divided into two distinct queues: the **Macrotask Queue** (Task Queue) and the **Microtask Queue**.

Macrotasks include operations like `setTimeout`, `setInterval`, `setImmediate`, and I/O handlers. Microtasks include `Promise` resolution callbacks (`.then`, `.catch`, `finally`), `queueMicrotask()`, `async/await` continuation steps, and `MutationObserver`.

The fundamental event loop rule is: **After completing the synchronous call stack, the runtime flushes the ENTIRE Microtask Queue to completion BEFORE picking up the next Macrotask from the Task Queue.**

**The Code Snippet**:
```javascript
console.log("1. Synchronous Start");

// Macrotask 1
setTimeout(() => {
    console.log("2. Macrotask 1 (setTimeout)");
    
    // Microtask nested inside Macrotask 1
    Promise.resolve().then(() => {
        console.log("3. Microtask nested inside Macrotask 1");
    });
}, 0);

// Microtask 1
Promise.resolve().then(() => {
    console.log("4. Microtask 1 (Promise.then)");
});

// Microtask 2 using queueMicrotask
queueMicrotask(() => {
    console.log("5. Microtask 2 (queueMicrotask)");
});

// Macrotask 2
setTimeout(() => {
    console.log("6. Macrotask 2 (setTimeout)");
}, 0);

console.log("7. Synchronous End");

/*
EXPECTED EXECUTION OUTPUT:
1. Synchronous Start
7. Synchronous End
4. Microtask 1 (Promise.then)
5. Microtask 2 (queueMicrotask)
2. Macrotask 1 (setTimeout)
3. Microtask nested inside Macrotask 1
6. Macrotask 2 (setTimeout)
*/
```

**Under the Hood / Why It Happens**:
The V8 / JavaScript engine processes event loop iterations (ticks) according to the HTML5 event loop specification:
1. Execute the main synchronous call stack until empty.
2. **Flush Microtasks**: Check the Microtask Queue. Execute tasks one by one until the queue length is strictly `0`. If running a microtask adds *another* microtask to the queue, that new microtask executes immediately within the *same* flush cycle!
3. Render UI updates (in browser context).
4. **Execute ONE Macrotask**: Pull the oldest macrotask from the Macrotask Queue and execute it.
5. Return to step 2 (Flush Microtasks completely again).

Because microtasks continuously drain until empty, an infinite loop created via recursive Promises (`function loop() { Promise.resolve().then(loop); }`) will completely freeze the event loop and browser UI, preventing any macrotask (`setTimeout`) or user click event from ever executing!

**Key Takeaway / Safe Pattern**:
Use microtasks (`queueMicrotask` / `Promise`) when state changes must be processed immediately before UI rendering or subsequent I/O. Use macrotasks (`setTimeout(..., 0)`) when yielding execution back to the browser or Node.js engine to allow other I/O events and render frames to process.
