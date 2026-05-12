# Day 184: PHP Copy-on-Write (CoW) Array Mutation and Memory Spikes

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
In PHP, arrays are passed by value syntactically, but managed via Copy-on-Write (CoW) under the hood. When you pass a massive array into a function or assign it to a new variable, PHP does not immediately duplicate the memory payload. Instead, both variables point to the same underlying reference-counted zval memory structure.

However, the moment any modification occurs to either variable—such as inserting an element, modifying a key, or passing the array by value into a loop that implicitly modifies internal iteration pointers—PHP is forced to perform a full deep clone of the array data payload in memory. If your codebase operates on large dataset arrays (e.g., 100,000 items), minor array mutations can cause sudden, massive RAM usage spikes and severe garbage collection overhead.

**The Code Snippet**:
```php
<?php

function processLargeDataset(array $dataset): array
{
    // Modifying a single element triggers a full deep-copy of $dataset zval
    $dataset[0]['processed_at'] = microtime(true);
    
    return $dataset;
}

$largeArray = [];
for ($i = 0; $i < 100000; $i++) {
    $largeArray[] = ['id' => $i, 'payload' => str_repeat('A', 100)];
}

$startMemory = memory_get_usage();

// Call function passing array by value
$result = processLargeDataset($largeArray);

$peakMemory = memory_get_peak_usage();
echo "Memory before mutation write: " . round($startMemory / 1024 / 1024, 2) . " MB\n";
echo "Peak memory usage after mutation: " . round($peakMemory / 1024 / 1024, 2) . " MB\n";
```

**Under the Hood / Why It Happens**:
PHP's Zend Engine manages variables using `zval` structures and reference counting (`zend_refcounted`). Array data structures are backed by Zend HashTable implementations. When `$result = processLargeDataset($largeArray)` is evaluated, `$dataset` increments the refcount of `$largeArray`'s underlying HashTable without allocating new heap memory.

When `$dataset[0]['processed_at'] = ...` executes, Zend checks `GC_REFCOUNT(ht) > 1`. Detecting multiple references, it invokes `zend_array_dup()`. This allocates a completely separate HashTable, deep-copying all 100,000 keys and values. Memory usage doubles instantaneously for a single key assignment.

**Key Takeaway / Safe Pattern**:
To prevent unwanted memory duplications when mutating large datasets, pass arrays by reference (`array &$dataset`), or use Generator streams (`yield`) and immutable Object Iterators instead of holding raw giant arrays in memory.

```php
<?php

// Passing by reference avoids CoW cloning penalty
function processLargeDatasetInPlace(array &$dataset): void
{
    $dataset[0]['processed_at'] = microtime(true);
}

processLargeDatasetInPlace($largeArray);
```
