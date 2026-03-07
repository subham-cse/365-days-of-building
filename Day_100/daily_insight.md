# Day 100: Type Juggling Anomalies and Truthy/Falsy Pitfalls
- **Language / Domain**: PHP
- **The Core Concept / "Did You Know?"**: PHP performs implicit type casting (type juggling) when evaluating loose equality (`==`) or implicit boolean checks. One of the most famous PHP anomalies is how the string `"0"` behaves compared to `0`, `false`, and empty arrays.

Specifically:
- `"0"` is considered **falsy** in boolean contexts (e.g. `if ("0")` evaluates to `false`).
- `"0.0"` is considered **truthy** in boolean contexts (e.g. `if ("0.0")` evaluates to `true`).
- In PHP 8.0+, numeric string comparisons were revised, but legacy loose comparisons still produce surprising results across mixed types!

- **The Code Snippet**:
```php
<?php

$values = [
    "0",
    "0.0",
    "00",
    "",
    null,
    false,
    []
];

foreach ($values as $val) {
    echo "Value: " . var_export($val, true) . "\n";
    echo "  Boolean check: " . ($val ? "TRUTHY" : "FALSY") . "\n";
    echo "  Loose check == 0: " . ($val == 0 ? "TRUE" : "FALSE") . "\n";
    echo "  Strict check === 0: " . ($val === 0 ? "TRUE" : "FALSE") . "\n";
    echo "---------------------------\n";
}
```

- **Under the Hood / Why It Happens**:
PHP's Zend Engine converts variables to `zend_bool` during conditional branch evaluation via `zend_is_true()`. 

The C implementation of `zend_is_true` handles `IS_STRING` by checking both string length and value: if string length is 1 and the single character is `'0'`, it evaluates to `0` (false). Any other string (including `"0.0"` or `"00"`) has a length greater than 1, so `zend_is_true` returns `1` (true)!

- **Key Takeaway / Safe Pattern**:
Always use strict equality comparison operator `===` instead of `==`. When validating user input strings (like form submission zeros or query parameters), use explicit string length checks or `strlen($str) === 0` rather than loose truthy checks:

```php
<?php

function isInputProvided(?string $input): bool {
    // Safe: handles "0" correctly without treating it as empty/missing
    return $input !== null && strlen(trim($input)) > 0;
}
```
