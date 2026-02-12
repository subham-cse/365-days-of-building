# Day 073: Event Loop Queues and Const Constructor Allocation in Dart

**Language / Domain**: Dart

**The Core Concept / "Did You Know?"**:
Dart executes code in a single-threaded **Isolate** model backed by an **Event Loop**. The Event Loop processes events from two separate internal queues: the **Microtask Queue** and the **Event Queue**.

Microtasks always take absolute priority over standard events (such as I/O, timers, user interactions, or UI frame updates). Schedule continuous or recursive microtasks using `scheduleMicrotask()`, and you will completely freeze the Event Queue, causing Flutter UI frames to drop and network/timer callbacks to starve indefinitely.

On the memory optimization side, Dart provides `const` constructors. Instantiating objects with `const` canonicalizes instances at compile time, allocating a single shared memory object regardless of how many times that constructor is invoked.

**The Code Snippet**:
```dart
import 'dart:async';

class ImmutableConfig {
  final String apiEndpoint;
  final int maxRetries;

  // Const constructor enables compile-time canonicalization
  const ImmutableConfig({
    required this.apiEndpoint,
    required this.maxRetries,
  });
}

void main() {
  // 1. Const Canonicalization Demonstration
  var config1 = const ImmutableConfig(apiEndpoint: "https://api.com", maxRetries: 3);
  var config2 = const ImmutableConfig(apiEndpoint: "https://api.com", maxRetries: 3);
  
  // Identical memory address!
  print("Identical references? ${identical(config1, config2)}"); // Output: true

  // 2. Microtask Queue Starvation Trap
  print("Main start");

  // Scheduled on standard Event Queue
  Timer.run(() {
    print("Event Queue: Timer callback executed");
  });

  // Microtask 1
  scheduleMicrotask(() {
    print("Microtask 1 executed");
    
    // Recursive microtask insertion starves the event queue!
    // UNCOMMENT TO STARVE:
    // scheduleMicrotask(() => print("Infinite microtask starvation!"));
  });

  // Microtask 2
  Future.microtask(() {
    print("Microtask 2 executed");
  });

  print("Main end");
}
```

**Under the Hood / Why It Happens**:
The Dart runtime loop algorithm can be conceptualized as:
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
Because the inner microtask loop must reach zero items before `processNextEvent()` can pull from the Event Queue, microtasks registered during microtask execution immediately re-trigger the inner loop. 

Regarding `const`: Dart's compiler (dart2js / AOT compiler) evaluates `const` expressions during compilation and stores canonicalized instance tables in the executable binary's constant pool. No heap allocations occur at runtime when invoking `const` constructors.

**Key Takeaway / Safe Pattern**:
Use `const` constructors wherever possible for UI widgets and immutable configuration objects to eliminate redundant GC runtime allocations. Reserve `scheduleMicrotask()` exclusively for short, non-blocking internal state synchronizations, and never schedule asynchronous work loops inside microtasks.
