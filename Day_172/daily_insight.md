# Day 172: Implicit Array Key Type Casts and Hash Juggling Anomalies

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP arrays are actually ordered hash maps (`HashTable`). While PHP allows declaring both integers and strings as array keys, the engine automatically performs implicit **key casting** on certain string keys!

If a string key contains a valid decimal integer representation (e.g. `"8"`, `"100"`), PHP automatically converts that key to an `integer` primitive under the hood. However, float keys, boolean keys, and null keys are cast to integers or empty strings in completely different ways, causing hidden hash collisions and unexpected value overwrites.

**The Code Snippet**:

```php
<?php

$map = [];

// 1. String containing an integer is SILENTLY converted to integer key
$map["10"] = "String key 10";
$map[10] = "Integer key 10"; // Overwrites "10"!

// 2. Float key is cast to integer by truncating decimals
$map[10.99] = "Float key 10.99"; // Overwrites integer key 10!

// 3. Boolean keys cast to 1 and 0
$map[true] = "Boolean True";  // Overwrites integer key 1
$map[false] = "Boolean False"; // Overwrites integer key 0

// 4. Null key casts to empty string ""
$map[null] = "Null key";

echo "Final Array Elements Count: " . count($map) . "\n";
var_dump($map);

/*
Output Array Keys:
10 => string(15) "Float key 10.99"
1  => string(12) "Boolean True"
0  => string(13) "Boolean False"
"" => string(8) "Null key"
*/
```

**Under the Hood / Why It Happens**:
Inside the Zend Engine, when accessing array slots via `zend_hash_str_update()` or `zend_hash_index_update()`, PHP evaluates the input key type:
1. Strings are checked using `ZEND_HANDLE_NUMERIC()`: if a string satisfies `[0-9]+` and fits within integer boundaries (`PHP_INT_MIN` .. `PHP_INT_MAX`), it is cast to a `zend_ulong` index.
2. `float` values are truncated to `(zend_ulong)double_val`.
3. `bool` `true` becomes `1`, `false` becomes `0`.
4. `null` is converted to the empty string `""`.

This key coercion was originally designed to make `$arr["0"]` and `$arr[0]` interchangeable in web forms, but it introduces non-obvious bugs when processing strict JSON keys (such as `"123"` vs `123`).

**Key Takeaway / Safe Pattern**:
When maintaining strict key types or building generic caches, be aware that numeric strings like `"42"` will be stored as integer key `42`. To preserve strict types across arbitrary keys, use `SplObjectStorage` for objects or prefix string keys with non-numeric characters (e.g., `"key_10"`).
