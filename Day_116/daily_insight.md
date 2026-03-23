# Day 116: OPcache Bytecode Caching and Copy-on-Write Array Semantics
- **Language / Domain**: PHP
- **The Core Concept / "Did You Know?"**: In PHP, arrays are value types managed via **Copy-on-Write (COW)** semantics. Assigning an array to another variable or passing it to a function does *not* immediately duplicate the array in memory—both variables share the same underlying hashtable payload until one of them modifies it.

Additionally, PHP's **OPcache** extension caches compiled Zend VM bytecodes and immutable literal arrays directly in shared system memory (SHM), eliminating script parsing overhead across HTTP requests.

- **The Code Snippet**:
```php
<?php

function inspectMemory(string $label) {
    echo sprintf("%-20s: %d bytes\n", $label, memory_get_usage());
}

inspectMemory("Initial Memory");

// Create a large array
$array1 = range(1, 100000);
inspectMemory("After Array 1 Created");

// Copy array (COW Optimization: shares internal zend_array structure!)
$array2 = $array1;
inspectMemory("After Array 2 Assigned"); // Memory usage remains virtually unchanged!

// Mutate array2 (Triggers actual memory duplication!)
$array2[0] = 999999;
inspectMemory("After Array 2 Mutated"); // Memory usage jumps by size of array!
```

- **Under the Hood / Why It Happens**:
Inside the Zend Engine, variables are represented by `zval` structures pointing to a `zend_array` (hashtable).

The `zend_array` contains a reference count field (`GC_REFCOUNT`). 
1. When `$array2 = $array1` executes, Zend increments `GC_REFCOUNT` on the `zend_array` pointer and assigns `$array2` to point to the exact same hash structure.
2. When `$array2[0] = 999999` is executed, Zend checks `GC_REFCOUNT`. Because it is greater than `1`, Zend allocates a new `zend_array` structure, deep-copies the hash elements, decrements the original array's refcount, and mutates the newly allocated copy.

- **Key Takeaway / Safe Pattern**:
Pass arrays directly into functions without fear of performance penalties; PHP's Copy-on-Write guarantees zero copy overhead unless element modifications occur inside the function.
