# Day 229: Dart Event Loop Queues & Microtask vs Event Queue Priority

**Language / Domain**: Dart / Asynchronous Execution & Flutter Architecture

**The Core Concept / "Did You Know?"**:
Dart executes code within single-threaded **Isolates**. An isolate runs a single event loop powered by two internal task queues:
1. **Microtask Queue**: For brief internal state updates, reactive signals, and `scheduleMicrotask()` callbacks.
2. **Event Queue**: For external asynchronous events (I/O, timers, UI draw frames, HTTP requests, port messages).

The Dart event loop prioritizes the Microtask Queue over the Event Queue. Before processing the next item from the Event Queue, Dart **must drain the Microtask Queue completely**. Scheduling infinite microtasks or recursive `Future.microtask()` callbacks completely starves the Event Queue, causing Flutter UI rendering freezes, dropped touches, and silent application lockups.

**The Code Snippet**:
```dart
import 'dart:async';

void main() {
  print('1. Main execution started');

  // Scheduled on standard Event Queue
  Future(() {
    print('5. Event Queue Task 1 executed');
  });

  // Scheduled on standard Event Queue with 0ms delay
  Future.delayed(Duration.zero, () {
    print('6. Event Queue Delayed Task executed');
  });

  // Scheduled on Microtask Queue
  scheduleMicrotask(() {
    print('3. Microtask 1 executed');
  });

  // Future.microtask schedules directly onto Microtask Queue
  Future.microtask(() {
    print('4. Microtask 2 executed');
  });

  print('2. Main execution finished');

  // UNHANDLED MICROTASK STARVATION TRAP (Do NOT un-comment in production!):
  // void starveEventLoop() {
  //   scheduleMicrotask(() => starveEventLoop()); // Complete UI / Event Freeze!
  // }
  // starveEventLoop();
}

/* Expected Execution Output:
1. Main execution started
2. Main execution finished
3. Microtask 1 executed
4. Microtask 2 executed
5. Event Queue Task 1 executed
6. Event Queue Delayed Task executed
*/
```

**Under the Hood / Why It Happens**:
The Dart isolate event loop algorithm operates strictly as follows:

```
while (isolateIsRunning) {
    while (microtaskQueue.isNotEmpty) {
        processNextMicrotask();
    }
    if (eventQueue.isNotEmpty) {
        processNextEvent();
    }
}
```

1. Sync code runs to completion.
2. `scheduleMicrotask()` pushes closures into `microtaskQueue`.
3. Standard `Future()` or `Timer()` pushes closures into `eventQueue`.
4. After sync code yields, Dart enters the outer loop. It checks `microtaskQueue`. If populated, it pops and executes microtasks until `microtaskQueue` is completely empty.
5. Only when `microtaskQueue` length reaches `0` does Dart process *a single item* from `eventQueue`.
6. After processing one event item, the event loop loops back and checks `microtaskQueue` again!

If microtasks continuously re-enqueue new microtasks, the inner loop never exits, and the event loop never processes pending frame redraw requests or I/O events sitting in the `eventQueue`.

**Key Takeaway / Safe Pattern**:
- Use standard `Future()` or `Timer.run()` for asynchronous work unless immediate synchronous-like state resolution is required before UI repainting.
- Avoid recursive `scheduleMicrotask()` or chaining unbounded `Future.microtask()` calls.
- In Flutter, offload heavy computation tasks to separate background isolates using `Isolate.run()` to prevent blocking both the main isolate event queue and microtask queue.
