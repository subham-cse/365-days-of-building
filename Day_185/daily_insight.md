# Day 185: Dart Microtask Queue Priority and Event Loop Starvation

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart's single-threaded asynchronous execution model operates using two distinct FIFO queues inside each Isolate: the **Event Queue** and the **Microtask Queue**. 

While standard async I/O events, timers (`Future.delayed`, `Timer`), and user interaction inputs enter the Event Queue, microtasks (`scheduleMicrotask`, `Future.microtask`, internal `Future` completions) enter the Microtask Queue. Crucially, Dart's event loop prioritizes the Microtask Queue over the Event Queue. The event loop will continuously drain the Microtask Queue until it is completely empty before processing a single event from the Event Queue. If microtasks continuously schedule more microtasks, the Event Queue will experience total starvation, freezing I/O processing and UI rendering.

**The Code Snippet**:
```dart
import 'dart:async';

void main() {
  print('1. Start main script');

  // Scheduled in the Event Queue
  Timer.run(() {
    print('4. Event Queue: Timer callback executed');
  });

  // Scheduled in the Microtask Queue
  scheduleMicrotask(() {
    print('2. Microtask Queue: First microtask');
    
    // Recursive microtask scheduling causes event starvation
    scheduleMicrotask(() {
      print('3. Microtask Queue: Chained nested microtask');
    });
  });

  print('5. End main script execution');
}
```

**Under the Hood / Why It Happens**:
Dart's event loop structure can be represented logically as:

```
while (isolateIsAlive) {
  while (microtaskQueue.isNotEmpty) {
    processNextMicrotask();
  }
  if (eventQueue.isNotEmpty) {
    processNextEvent();
  }
}
```

Because `scheduleMicrotask` or immediate `Future.then` chains append tasks directly to `microtaskQueue`, any recursive or heavy processing inside microtasks blocks `processNextEvent()`. Standard timers or UI frame rendering callbacks waiting in `eventQueue` are never reached until the microtask queue clears completely.

**Key Takeaway / Safe Pattern**:
Avoid heavy recursive computations or long task chains inside `scheduleMicrotask`. For heavy background computations or deferred task execution that allows UI frames and I/O to process, use `Future.delayed(Duration.zero, ...)` or offload the workload to a separate `Isolate`.

```dart
// Safe Pattern: Yield control back to the Event Queue
void processChunks(List<int> items) {
  if (items.isEmpty) return;
  
  // Do batch work...
  
  // Schedule remaining work in Event Queue, allowing UI/IO events to run
  Future.delayed(Duration.zero, () => processChunks(items.sublist(100)));
}
```
