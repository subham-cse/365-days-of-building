# Day 200: PHP Loose Comparison Type Juggling and `in_array` Security Traps

**Language / Domain**: PHP

**The Core Concept / "Did You Know?"**:
PHP is a dynamically typed language that aggressively performs automatic type conversion, known as **Type Juggling**. When using loose equality operators (`==`, `!=`) or default array searching functions like `in_array($needle, $haystack)`, PHP attempts to convert operands to comparable types before evaluation.

This coercion behavior leads to shocking logical anomalies: non-numeric strings can equal `0`, string prefixes like `"0e12345"` (hex/scientific format) can evaluate as equal to `"0e67890"` because both parse as float `0.0`, and boolean `true` loosely matches *any* truthy string or non-zero integer. In security contexts (such as password hash comparisons, API token validation, or access control lists), loose comparisons can bypass authentication entirely.

**The Code Snippet**:
```php
<?php

// Trap 1: String-to-Integer Type Coercion
$adminToken = "secret_admin_token_abc";

// Loose comparison converts string to int 0!
if ($adminToken == 0) {
    echo "Bypassed auth! String == 0 evaluates to TRUE in PHP < 8.0!\n";
}

// Trap 2: Default in_array() loose checking
$allowedRoles = ['admin', 'super_user', 'manager'];
$userRole = 0; // Integer zero passed from unvalidated input

// Default 3rd parameter $strict is false!
if (in_array($userRole, $allowedRoles)) {
    // 0 == 'admin' -> true in PHP loose comparison!
    echo "Access granted! Integer 0 matched 'admin' in allowed roles!\n";
}

// Trap 3: Hash collision loose comparison ("Magic Hashes")
$hash1 = "0e123456789012345678901234567890";
$hash2 = "0e987654321098765432109876543210";

if ($hash1 == $hash2) {
    echo "Magic hashes match! Both coerced to float 0e0 = 0.0\n";
}
```

**Under the Hood / Why It Happens**:
In PHP's Zend Engine, loose comparison `==` follows type promotion tables:
1. When comparing an integer `$i$` and a string `$s$`, PHP attempts to convert `$s$` to an integer/float via `zend_string_to_double()`. In PHP versions prior to 8.0, non-numeric strings like `"admin"` converted to numeric `0`, making `0 == 0` evaluate to `true`.
2. When comparing two strings matching scientific notation regex (`0e[0-9]+`), PHP converts both strings to floating-point numbers (`0 * 10^x = 0.0`). Comparing `0.0 == 0.0` evaluates to `true`.
3. `in_array($needle, $haystack)` defaults to `$strict = false`, calling `is_equal_function()` on every element in the array.

**Key Takeaway / Safe Pattern**:
Always use strict equality operators (`===`, `!==`) and always pass `true` as the third parameter to array functions like `in_array($needle, $haystack, true)`. For cryptographic hash comparisons, use `hash_equals()`.

```php
<?php

// Safe Pattern 1: Strict equality and strict in_array
if (in_array($userRole, $allowedRoles, true)) {
    // Requires exact type and value match
}

// Safe Pattern 2: Timing-attack safe strict hash comparison
if (hash_equals($knownHash, $userSuppliedHash)) {
    // Safe timing and type verification
}
```
