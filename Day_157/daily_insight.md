# Day 157: Microtask Queue Starvation of the Event Loop

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart executes single-threaded code on an isolate powered by an event loop. The event loop maintains two distinct internal processing queues: the **Microtask Queue** and the **Event Queue**.

Microtasks are short asynchronous tasks intended to run immediately after the current stack frame finishes, but *before* control yields back to the main event queue (which handles I/O, timers, user input, and UI repaints). Because the Dart event loop drains the *entire* Microtask Queue before picking up a single item from the Event Queue, recursively scheduling microtasks will completely starve the Event Queue, causing freeze-ups and UI hangs.

**The Code Snippet**:

```dart
import 'dart:async';

void main() {
  print('1. Main sync start');

  // Schedule an event on the main Event Queue
  Timer.run(() {
    print('4. Event Queue Callback Executed (Timer)');
  });

  // Starve the Event Queue by recursively populating the Microtask Queue
  scheduleInfiniteMicrotasks(1);

  print('2. Main sync end');
}

void scheduleInfiniteMicrotasks(int count) {
  if (count > 5) return; // Guard for demo, remove guard to freeze event loop permanently

  scheduleMicrotask(() {
    print('3. Microtask #$count executed');
    scheduleInfiniteMicrotasks(count + 1);
  });
}
```

**Under the Hood / Why It Happens**:
The Dart runtime loop algorithm follows strict pseudo-code logic:
```
while (isolateIsRunning) {
  while (microtaskQueue.isNotEmpty) {
    runNextMicrotask();
  }
  if (eventQueue.isNotEmpty) {
    runNextEvent();
  }
}
```
`Future.microtask()` or `scheduleMicrotask()` inject tasks directly into `microtaskQueue`. If microtasks continually enqueue further microtasks, the outer `while (microtaskQueue.isNotEmpty)` condition never evaluates to false. Consequently, standard asynchronous events scheduled via `Future.delayed()`, `Timer.run()`, or UI rendering frame ticks are completely blocked from executing.

**Key Takeaway / Safe Pattern**:
Use `scheduleMicrotask()` sparingly and strictly for brief state reconciliations that must happen synchronously before control returns to the event loop. For general asynchronous operations or repeated iterations, use standard `Future()` or `Timer.run()` to allow the event loop to service I/O and user events between iterations.
