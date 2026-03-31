# Day 129: Dart Microtask Queue vs Event Queue Execution Order

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart's execution model is single-threaded and driven by an Event Loop. However, many developers don't realize that Dart does NOT process asynchronous tasks in a simple FIFO queue! Instead, the event loop maintains **two distinct queues**: the **Microtask Queue** and the **Event Queue**.

Microtasks always take absolute priority over standard Events. As long as there are tasks remaining in the Microtask Queue, the Event Loop will execute every single microtask before picking up the next task from the Event Queue (which includes I/O, timers, UI events, and standard `Future()` callbacks). Schedule microtasks recursively or heavily, and you will starve standard `Future.delayed` or UI rendering pipelines!

**The Code Snippet**:
```dart
import 'dart:async';

void main() {
  print('1. Main Start');

  // Scheduled in Event Queue
  Future(() {
    print('5. Standard Future (Event Queue)');
  });

  // Scheduled in Event Queue with delay
  Future.delayed(Duration.zero, () {
    print('6. Delayed Future (Event Queue)');
  });

  // Scheduled in Microtask Queue
  scheduleMicrotask(() {
    print('3. Microtask 1 (Microtask Queue)');
    scheduleMicrotask(() {
      print('4. Nested Microtask 2 (Microtask Queue - Priority!)');
    });
  });

  // Future.value triggers microtask completion
  Future.value(42).then((val) {
    print('3b. Future.value .then() callback (Microtask Queue)');
  });

  print('2. Main End');
}
```

**Under the Hood / Why It Happens**:
The Dart runtime event loop processes items according to strict queue priority:
```
while (microtaskQueue.isNotEmpty) {
  runNextMicrotask();
}
if (eventQueue.isNotEmpty) {
  runNextEvent();
}
```
1. Synchronous main code finishes (`1. Main Start`, `2. Main End`).
2. Before returning control to OS I/O or rendering frames, Dart drains `microtaskQueue`.
3. `scheduleMicrotask` and completed `Future.then()` handlers inject callbacks directly into `microtaskQueue`.
4. Standard `Future(...)` constructors schedule tasks into the `eventQueue`.

Because all microtasks are drained *to completion* before the next event from `eventQueue` is popped, enqueuing microtasks from within microtasks delays timer execution and user interface repaints indefinitely.

**Key Takeaway / Safe Pattern**:
Use standard `Future` or `async`/`await` for typical asynchronous workflows. Reserve `scheduleMicrotask()` strictly for brief internal state updates that must complete synchronously prior to yielding control back to the UI frame handler or I/O loop.
