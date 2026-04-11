# Day 144: PHP Loose Type Juggling & Strict Equality Traps

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP's loose comparison operator (`==`) performs automatic type coercion (type juggling) before performing value comparisons. While loose typing attempts to offer convenience, it produces bizarre, non-transitive comparison anomalies that frequently introduce security vulnerabilities (such as authentication bypasses via hash collision signatures).

In PHP 8.0+, string-to-number comparison rules were overhauled, but loose comparisons involving strings, booleans, and `null` still yield dangerous false-positive equality matches.

**The Code Snippet**:
```php
<?php

function checkLooseEquality($a, $b) {
    $result = ($a == $b) ? 'TRUE' : 'FALSE';
    echo var_export($a, true) . " == " . var_export($b, true) . " => " . $result . "\n";
}

echo "--- Loose Equality (==) Traps ---\n";
checkLooseEquality("0", false);       // TRUE!
checkLooseEquality("0000", 0);        // TRUE!
checkLooseEquality("0e12345", "0e99999"); // TRUE! (Both coerced to float 0.0!)
checkLooseEquality(null, "");         // TRUE!
checkLooseEquality(0, "foo");         // FALSE in PHP 8+, TRUE in PHP 7!

echo "\n--- Strict Equality (===) Fix ---\n";
// Strict equality checks BOTH value AND type without coercion
var_dump("0e12345" === "0e99999"); // bool(false)
var_dump("0" === false);           // bool(false)

// SECURITY TRAP: Loose comparison in password hash check
$userProvidedHash = "0e830400451993494058024219903391"; // Magic hash
$databaseHash     = "0e100000000000000000000000000000";

if ($userProvidedHash == $databaseHash) {
    echo "\nCRITICAL VULNERABILITY: Loose comparison authenticated magic hash!\n";
}
```

**Under the Hood / Why It Happens**:
When evaluating `$a == $b`:
1. **Scientific Notation Strings**: Strings matching the regex `/^0e\d+$/` are recognized as floating-point numbers in scientific notation ($0 \times 10^x = 0$). When comparing `"0e12345"` and `"0e99999"`, PHP converts both strings to `float(0.0)`. Since `0.0 == 0.0`, the loose comparison evaluates to `true`!
2. **Boolean Coercion**: Comparing any non-boolean type to a boolean (`$a == false`) converts `$a` into a boolean first using `(bool)$a`. Since `"0"`, `0`, `null`, and `[]` convert to `false`, loose equality returns `true`.

In PHP 8.0, comparing a string to a number converts the number to a string if the string is non-numeric, fixing the `0 == "foo"` anomaly, but scientific notation string-to-string comparisons still juggled values in loose mode.

**Key Takeaway / Safe Pattern**:
Always use strict comparison operators (`===` and `!==`) across all PHP codebases. Enable strict type checking globally by declaring `declare(strict_types=1);` at the top of every PHP file. For hash comparisons, use `hash_equals()`.
