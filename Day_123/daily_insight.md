# Day 123: Prototype Mutation, Hoisting, and [] + {} Type Coercion Quirks
- **Language / Domain**: JavaScript
- **The Core Concept / "Did You Know?"**: JavaScript combines **Prototype-based Inheritance**, variable **Hoisting**, and implicit type coercion rules that can lead to infamous expression evaluation quirks such as `[] + {}` returning `"[object Object]"` while `{}` + `[]` (in raw script evaluation) returns `0`.

Furthermore, modifying built-in prototypes (`Object.prototype`) introduces **Prototype Pollution** vulnerabilities, where attackers can inject properties into all objects across the application runtime!

- **The Code Snippet**:
```javascript
// Hoisting Behavior Trap
console.log("Hoisted var:", hoistedVar); // Output: undefined (declaration hoisted, assignment NOT)
// console.log(letVar); // ReferenceError: Cannot access 'letVar' before initialization (TDZ)

var hoistedVar = "I am hoisted";
let letVar = "I am in Temporal Dead Zone (TDZ)";

// Expression Coercion Quirks
console.log("[] + []:", [] + []);             // "" (empty string)
console.log("[] + {}:", [] + {});             // "[object Object]"
console.log("{} + []:", {} + []);             // "[object Object]" (in expression context)
console.log("true + false:", true + false);   // 1
console.log("'5' - 3:", '5' - 3);             // 2
console.log("'5' + 3:", '5' + 3);             // "53"

// Prototype Pollution Hazard
const user = {};
console.log("Before pollution:", user.isAdmin); // undefined

// Polluting root Object prototype
Object.prototype.isAdmin = true;

const newObj = {};
console.log("After pollution:", newObj.isAdmin); // true (Leaked globally to all objects!)
```

- **Under the Hood / Why It Happens**:
For type coercion (`[] + {}`), JavaScript evaluates the binary `+` operator using the Abstract Relational Comparison / ToPrimitive specification:
1. `[].valueOf()` returns `[]` (not primitive), so it calls `[].toString()`, producing `""`.
2. `{}.valueOf()` returns `{}` (not primitive), so it calls `{}.toString()`, producing `"[object Object]"`.
3. Concatenating `"" + "[object Object]"` yields `"[object Object]"`.

For prototype pollution, objects created via `{}` inherit from `Object.prototype`. Mutating `Object.prototype` writes properties directly to the root prototype object in V8 heap memory.

- **Key Takeaway / Safe Pattern**:
To prevent prototype pollution, instantiate dictionary objects using `Object.create(null)` (which creates an object with no prototype fallback), or use JavaScript `Map` data structures for key-value storage. Use strict equality (`===`) and avoid implicit type coercion expressions.
