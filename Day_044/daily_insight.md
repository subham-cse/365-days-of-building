# Day 044: PHP Type Juggling Anomalies and Loose Comparisons

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP is dynamically and weakly typed, performing automatic type juggling (coercion) when operators encounter mismatched types. Loose equality (`==`) applies complex, non-transitive coercion rules that can cause surprising security vulnerabilities (e.g., bypass checks when comparing hash strings starting with `0e`).

Furthermore, in PHP versions prior to PHP 8.0, comparing a string to an integer converted the string to a number, causing `"000123"` and `"123"` or `"0abc"` and `0` to evaluate as equal.

**The Code Snippet**:
```php
<?php

function demonstrateTypeJuggling() {
    // 1. Loose Equality Trap: Magic Hash vulnerability
    // Strings starting with '0e' followed only by numbers evaluate as 0 in scientific notation
    $hash1 = "0e123456789012345678901234567890";
    $hash2 = "0e987654321098765432109876543210";

    echo "Loose Comparison ('0e' hashes):\n";
    var_dump($hash1 == $hash2); // bool(true) !

    echo "Strict Comparison ('0e' hashes):\n";
    var_dump($hash1 === $hash2); // bool(false)

    // 2. String-to-Int Comparison (Legacy PHP vs PHP 8 behavior)
    echo "\nString vs Zero Comparison:\n";
    var_dump("foo" == 0);  // true in PHP < 8.0, false in PHP 8.0+

    // 3. In_array Loose Checking Risk
    $untrustedInput = "0";
    $allowedStatuses = [true, "active", "pending"];

    echo "\nUnsafe in_array check (loose default):\n";
    // "0" == true evaluates to true!
    var_dump(in_array($untrustedInput, $allowedStatuses)); // bool(true) !

    echo "Safe in_array check (strict mode):\n";
    var_dump(in_array($untrustedInput, $allowedStatuses, true)); // bool(false)
}

demonstrateTypeJuggling();
```

**Under the Hood / Why It Happens**:
When loose equality (`==`) evaluates two string operands, PHP checks if both strings match the format of a valid numeric literal (including scientific notation exponent form `0e...`). If both qualify, PHP converts both strings to double-precision floats (`0.0 * 10^123` = `0.0`), rendering them equal.

For comparisons between string and int in PHP 7, PHP cast the string to int using `(int) $string` (which parses leading numeric digits and truncates the rest to `0`). PHP 8 revised type juggling rules so that comparing numbers to non-numeric strings converts the number to a string instead.

**Key Takeaway / Safe Pattern**:
Always use strict comparison operators (`===` and `!==`) instead of loose operators (`==` and `!=`). Always set the 3rd parameter `$strict` to `true` when using array functions like `in_array()` or `array_search()`. Enable `declare(strict_types=1);` at the top of PHP files.
