# Day 060: PHP Opcache Behavior and Copy-on-Write Array Semantics

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP arrays implement Copy-on-Write (CoW) semantics. Assigning an array to a new variable or passing an array into a function does NOT copy the array contents immediately in memory. Both variables point to a single shared array structure until one variable attempts to mutate elements.

When combined with **OPcache** (Zend OPcache), precompiled PHP bytecode and immutable literal arrays are stored directly in shared memory (`SHM`). Mutating a large array forces PHP to perform a full deep heap copy of the array dataset.

**The Code Snippet**:
```php
<?php

function demonstrateCopyOnWrite() {
    // Large array creation
    $original = range(1, 100000);
    $initialMemory = memory_get_usage();

    // Copying array to new variable - Shared reference memory!
    $copy = $original;
    $afterCopyMemory = memory_get_usage();

    echo "Memory delta after array assignment: " . ($afterCopyMemory - $initialMemory) . " bytes\n";
    // Delta is virtually 0 bytes because underlying array reference is shared!

    // Mutating single element in copy array triggers CoW deep allocation
    $copy[0] = 999999;
    $afterMutationMemory = memory_get_usage();

    echo "Memory delta after modifying \$copy[0]: " . ($afterMutationMemory - $afterCopyMemory) . " bytes\n";
    // Significant memory allocation occurs here as PHP clones entire 100k element array!
}

function demonstrateReferencePassing(array &$data) {
    // Passing by reference avoids Copy-on-Write deep copy during mutation
    $data[0] = 42;
}

demonstrateCopyOnWrite();

$myArray = [1, 2, 3, 4, 5];
demonstrateReferencePassing($myArray);
echo "Mutated via reference: " . $myArray[0] . "\n";
```

**Under the Hood / Why It Happens**:
In PHP's Zend Engine, arrays are stored as `zend_array` hash table structures wrapped inside `zval` containers. Every `zval` contains a reference count header `refcount` and flags.

When `$copy = $original` executes:
1. Zend Engine increments `$original`'s `zval.u1.v.refcount`.
2. Both `$original` and `$copy` point to the identical `zend_array` memory address.

When `$copy[0] = 999999` executes, Zend Engine checks if `refcount > 1`. Detecting shared ownership, it invokes `zend_array_dup()`, allocating a separate `zend_array` block on the system heap, copying all key-value entries, decrementing the original `refcount`, and mutating the duplicate.

**Key Takeaway / Safe Pattern**:
Be mindful of array mutation inside loops or data transformation pipelines processing large datasets. When passing large arrays to functions that modify elements, pass by reference (`array &$data`) or use `Generator` yields to stream elements without triggering CoW deep cloning overhead.
