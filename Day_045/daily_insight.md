# Day 045: Dart Event Loop Queues and Microtask Scheduling

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart applications execute inside single-threaded Isolates, powered by an event loop driven by two queues: the **Microtask Queue** and the **Event Queue**. The Microtask Queue handles internal state transitions, `scheduleMicrotask()`, and immediate asynchronous callbacks, while the Event Queue handles external events like I/O, timers, user interactions, and `Future.delayed()`.

Just as in JavaScript, the Dart event loop completely drains the Microtask Queue before popping the next item from the Event Queue. Inserting recursive microtasks starves event handling, freezing UI animations and delaying Flutter frame rendering.

**The Code Snippet**:
```dart
import 'dart:async';

void main() {
  print('1. Main synchronous start');

  // Scheduled in Event Queue (Timer)
  Future.delayed(Duration.zero, () {
    print('5. Event Queue task: Future.delayed');
  });

  // Scheduled in Event Queue (Standard Future constructor)
  Future(() {
    print('4. Event Queue task: Standard Future');
  });

  // Scheduled in Microtask Queue
  scheduleMicrotask(() {
    print('3. Microtask Queue task: scheduleMicrotask');
  });

  // Scheduled in Microtask Queue via Future.value/then
  Future.value(100).then((_) {
    print('3b. Microtask Queue task: Future.then callback');
  });

  print('2. Main synchronous end');
}

/* Expected Terminal Output:
 1. Main synchronous start
 2. Main synchronous end
 3. Microtask Queue task: scheduleMicrotask
 3b. Microtask Queue task: Future.then callback
 4. Event Queue task: Standard Future
 5. Event Queue task: Future.delayed
*/
```

**Under the Hood / Why It Happens**:
The Dart event loop architecture follows a strict processing priority:
```
void mainEventLoop() {
  while (hasTasksToRun) {
    if (microtaskQueue.isNotEmpty) {
      microtaskQueue.removeFirst().run();
    } else if (eventQueue.isNotEmpty) {
      eventQueue.removeFirst().run();
    }
  }
}
```
Every time synchronous execution finishes or an event handler completes, the event loop enters a loop checking `microtaskQueue.isNotEmpty`. As long as microtasks remain queued, `eventQueue` tasks—such as Flutter UI touch events, networking responses, or frame draw triggers—are paused.

**Key Takeaway / Safe Pattern**:
Use standard `Future` constructors or `async`/`await` for standard asynchronous operations so tasks yield control to the main Event Queue. Use `scheduleMicrotask()` only for brief internal state updates that must complete before handing control back to the UI framework.
