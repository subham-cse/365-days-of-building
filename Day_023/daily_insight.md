# Day 023: Prototype Mutation, Variable Hoisting, and Scope Leakage
**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript utilizes prototype-based inheritance. Mutating an object's prototype (`Object.prototype` or `Array.prototype`) at runtime alters behavior globally for **all** objects across the application, introducing severe security vulnerabilities like **Prototype Pollution**.

Furthermore, variables declared with `var` are **hoisted** to the top of their enclosing function scope and initialized to `undefined`, whereas function declarations are hoisted along with their full implementations. Declaring variables with `var` inside loops leaks the variable state into the outer scope.

**The Code Snippet**:
```javascript
// Trap 1: Prototype Pollution Vulnerability
function mergeUnsafe(target, source) {
    for (let key in source) {
        if (typeof target[key] === 'object' && typeof source[key] === 'object') {
            mergeUnsafe(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

const maliciousPayload = JSON.parse('{"__proto__": {"admin": true}}');
mergeUnsafe({}, maliciousPayload);

const user = {};
console.log("Is user admin?", user.admin); 
// Output: true! Globally mutated Object.prototype!

// Trap 2: Variable Hoisting and Scope Leakage
function hoistingTrap() {
    console.log("Value of x before declaration:", x); // Output: undefined (NOT ReferenceError!)
    
    var x = 10;

    for (var i = 0; i < 3; i++) {
        // `i` is hoisted to function scope!
    }

    console.log("Value of i outside loop:", i); // Output: 3 (Leaked to function!)
}

hoistingTrap();
```

**Under the Hood / Why It Happens**:
During V8 compilation phase, code execution takes place in two passes:
1. **Creation/Parsing Phase**: The JavaScript engine allocates memory space for function declarations and variables. Variables declared with `var` are assigned `undefined` in the Execution Context's Variable Environment. Variables declared with `let` and `const` are created in a **Temporal Dead Zone (TDZ)** and remain uninitialized until execution reaches their declaration statement.
2. **Execution Phase**: Code executes line by line.

For prototype inheritance, every JavaScript object has an internal `[[Prototype]]` link. Accessing a property (`user.admin`) triggers a lookup chain: if missing on `user`, V8 follows `user.__proto__` to `Object.prototype`. Merging malicious `__proto__` properties assigns properties directly to `Object.prototype`, affecting all downstream object lookups.

**Key Takeaway / Safe Pattern**:
Never use `var`; always declare variables using `const` or `let` to enforce block scoping. Protect objects from prototype pollution by using `Object.create(null)` for map dictionaries or checking `Object.hasOwn(obj, key)`.

```javascript
// SAFE: Creating dictionary with NO prototype chain
const safeMap = Object.create(null);
safeMap["key"] = "value";
console.log(safeMap.__proto__); // undefined! Prototype pollution impossible!

// SAFE: Block scoping with let/const
function safeScope() {
    for (let j = 0; j < 3; j++) {
        // `j` strictly scoped to block
    }
    // console.log(j); // ReferenceError: j is not defined!
}
```
