# Day 128: PHP Copy-on-Write Arrays & Memory Multiplication Traps

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP arrays use a Copy-on-Write (CoW) memory model. When you assign an array variable to another variable or pass it to a function by value, PHP does not copy the array buffer in memory immediately. Both variables share the exact same internal `zend_array` structure.

However, the moment any modification (such as adding an element or altering a key) occurs on either copy, PHP is forced to duplicate the entire array data structure in memory! A subtle trap occurs when iterating over large arrays using `foreach ($array as &$item)` or when passing arrays to functions that inadvertently trigger internal reference allocations.

**The Code Snippet**:
```php
<?php

$startMemory = memory_get_usage();

// Create a large array of 100,000 integers
$largeArray = range(1, 100000);

echo "Initial Array Memory: " . round((memory_get_usage() - $startMemory) / 1024 / 1024, 2) . " MB\n";

// Assignment by value (CoW - no memory increase yet)
$copyArray = $largeArray;

echo "After Copy Assignment Memory: " . round((memory_get_usage() - $startMemory) / 1024 / 1024, 2) . " MB\n";

// Modifying single element forces PHP Zend Engine to clone the entire 100,000 element array
$copyArray[0] = 999;

echo "After Single Index Mutation Memory: " . round((memory_get_usage() - $startMemory) / 1024 / 1024, 2) . " MB\n";

// TRAP: Foreach by reference leaves reference dangling
foreach ($largeArray as &$ref) {
    // modifying via reference
}
unset($ref); // Critical! Without unset, subsequent loops corrupt $largeArray
```

**Under the Hood / Why It Happens**:
In the Zend Engine (PHP 7+ / 8+), arrays are represented by `zend_array` structs containing reference-counted `zval` elements. When array assignment `$b = $a` occurs, Zend increments the `refcount` of the `zend_array` pointer.

When `$b[0] = 999` is evaluated:
1. The engine checks the array's refcount.
2. Because `refcount > 1`, the array is shared between multiple zval containers.
3. To uphold value semantics, Zend executes `zend_array_dup()`, allocating a fresh hash table, copying all key-value entries, and decrementing the original array's refcount.
If arrays are large (megabytes in size), innocent-looking mutations inside processing pipelines cause severe memory spikes and latency penalties.

**Key Takeaway / Safe Pattern**:
For large dataset transformations, avoid mutating intermediate array copies. Utilize PHP `Generator`s (`yield`) or object wrappers (`SplFixedArray`) to stream data without duplicating memory tables. Always `unset()` reference iteration variables immediately after `foreach ($arr as &$v)` loops.
