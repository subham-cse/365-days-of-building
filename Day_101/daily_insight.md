# Day 101: Event Loop Queues: Microtasks vs Event Tasks
- **Language / Domain**: Dart
- **The Core Concept / "Did You Know?"**: The Dart event loop manages execution using two distinct internal queues: the **Microtask Queue** and the **Event Queue**. 

Microtasks take strict priority over event queue items (such as `Future.delayed`, I/O, timer events, or UI frame redraws). If microtasks continuously schedule new microtasks via `scheduleMicrotask`, the Event Queue will completely starve, causing the UI to freeze and I/O handlers to never execute!

- **The Code Snippet**:
```dart
import 'dart:async';

void main() {
  print('1. Main start');

  // Scheduled on Event Queue
  Future.delayed(Duration(milliseconds: 0), () {
    print('5. Future.delayed (Event Queue)');
  });

  // Scheduled on Event Queue
  Future(() {
    print('4. Future standard (Event Queue)');
  });

  // Scheduled on Microtask Queue
  scheduleMicrotask(() {
    print('3. scheduleMicrotask (Microtask Queue)');
  });

  print('2. Main end');
}

/* 
Output order guaranteed:
1. Main start
2. Main end
3. scheduleMicrotask (Microtask Queue)
4. Future standard (Event Queue)
5. Future.delayed (Event Queue)
*/
```

- **Under the Hood / Why It Happens**:
Dart's single-threaded isolate execution model executes code in a continuous loop structured like this:

```
while (isolateIsAlive) {
  while (microtaskQueue.isNotEmpty) {
    runNextMicrotask();
  }
  if (eventQueue.isNotEmpty) {
    runNextEvent();
  }
}
```

Because the inner `microtaskQueue` loop must drain to zero before a single event from `eventQueue` can be processed, chaining microtasks indefinitely blocks all standard Futures, Timers, and rendering triggers.

- **Key Takeaway / Safe Pattern**:
Use standard `Future` constructors or `Future.delayed` for general asynchronous work, and reserve `scheduleMicrotask` only for brief internal state synchronizations that must complete strictly before yielding control to the next event turn.
