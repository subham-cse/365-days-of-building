# Day 032: Generator Yield Behavior, Fiber Coroutines, and Large Memory Streams
**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP **Generators** (`yield`) provide a memory-efficient way to process large datasets without loading entire collections into memory at once. A generator function returns an instance of the internal `Generator` class, executing code lazily on demand.

However, once a PHP `Generator` has been iterated through (e.g. via `foreach`), it **cannot be rewound or re-iterated**. Attempting to iterate an exhausted generator a second time throws an uncatchable `Exception: Cannot traverse an already closed generator`.

Furthermore, PHP 8.1 introduced **Fibers** (full asymmetric coroutines), allowing non-blocking concurrency within a single thread.

**The Code Snippet**:
```php
<?php

// Memory Efficient Generator Function
function getLargeDataset(): Generator {
    for ($i = 1; $i <= 5; $i++) {
        yield $i => "Record #{$i}";
    }
}

function generatorExhaustionTrap() {
    $generator = getLargeDataset();

    echo "First Pass Iteration:\n";
    foreach ($generator as $key => $val) {
        echo "{$key} => {$val}\n";
    }

    echo "\nSecond Pass Iteration (TRAP!):\n";
    try {
        // TRAP: Generator is already closed/exhausted!
        foreach ($generator as $key => $val) {
            echo "{$key} => {$val}\n";
        }
    } catch (Throwable $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }
}

// Memory Comparison: Array vs Generator
function compareMemory() {
    $startMem = memory_get_usage();

    // Standard Array: Allocates 1,000,000 integers in RAM (~30MB)
    // $largeArray = range(1, 1000000); 

    // Generator: Allocates zero extra array memory (~1KB)
    $largeGen = (function() {
        for ($i = 0; $i < 1000000; $i++) yield $i;
    })();

    echo "Memory used by generator: " . (memory_get_usage() - $startMem) . " bytes\n";
}

generatorExhaustionTrap();
compareMemory();
```

**Under the Hood / Why It Happens**:
When the Zend Engine executes a function containing the `yield` keyword, it wraps the function execution context inside a `zend_generator` heap structure. The function does not execute immediately; it returns an iterator implementation.

When `.next()` or `foreach` executes:
1. Zend VM resumes execution at the saved opcode instruction pointer (`IP`).
2. When execution hits `yield`, Zend saves the local variable stack frame pointers and yields the value back to the caller.
3. Once the generator function reaches the end or executes `return`, the Zend Engine flags the `zend_generator` state as `CLOSED` and frees its stack frame memory.

Because the execution frame is destroyed when closed, attempting to rewind an exhausted generator fails because its internal opcode state pointers no longer exist.

**Key Takeaway / Safe Pattern**:
Do not pass raw generators to functions that require multiple iteration passes over the same dataset. If re-iteration is required, wrap the generator in a caching iterator (`NoRewindIterator` or custom buffer array) or call the generator factory function again to instantiate a fresh generator.

```php
<?php

// SAFE: Re-instantiating fresh generator for multiple passes
function processDataset(callable $generatorFactory) {
    // Pass 1:
    foreach ($generatorFactory() as $item) {
        // Process pass 1
    }

    // Pass 2: Invoke factory again to get fresh unexhausted generator!
    foreach ($generatorFactory() as $item) {
        // Process pass 2 safely
    }
}

processDataset(fn() => getLargeDataset());
```
