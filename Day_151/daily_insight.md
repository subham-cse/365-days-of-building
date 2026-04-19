# Day 151: JavaScript Prototype Pollution Vulnerabilities

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript uses prototype-based inheritance. Objects inherit properties and methods from their prototype object (`Object.prototype`). If an attacker can inject properties into `Object.prototype`, those injected properties become automatically visible on **every single object** across the entire JavaScript runtime environment!

This attack vector is known as **Prototype Pollution**. It frequently occurs when recursive object merging helpers or deep-cloning utility functions dynamically assign user-controlled JSON keys (such as `"__proto__"`, `"constructor"`, or `"prototype"`) without proper input sanitization.

**The Code Snippet**:
```javascript
// BUGGY: Unsanitized recursive object merge implementation
function unsafeMerge(target, source) {
  for (let key in source) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) target[key] = {};
      unsafeMerge(target[key], source[key]); // Recursively merges properties
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// Malicious JSON payload received from untrusted API request
const maliciousPayload = JSON.parse('{ "__proto__": { "admin": true } }');

const userProfile = {};
console.log("Before pollution - userProfile.admin:", userProfile.admin); // undefined

// Merging untrusted payload pollutes Object.prototype!
unsafeMerge({}, maliciousPayload);

// CONSEQUENCE: Every new object now inherits admin = true!
const newEmptyObject = {};
console.log("After pollution - newEmptyObject.admin:", newEmptyObject.admin); // TRUE!

if (newEmptyObject.admin) {
  console.log("SECURITY VULNERABILITY: Non-admin user granted privilege escalation!");
}

// SAFE PATTERN: Using Object.create(null) or Map for dictionary objects
const safeDictionary = Object.create(null); // No prototype chain!
console.log("safeDictionary prototype:", Object.getPrototypeOf(safeDictionary)); // null
```

**Under the Hood / Why It Happens**:
In JavaScript object semantics:
- Every object instance possesses an internal `[[Prototype]]` link accessed via the accessor property `__proto__` on `Object.prototype`.
- When `unsafeMerge` encounters key `"__proto__"`, evaluating `target["__proto__"]` does NOT set a literal key named `"__proto__"`. Instead, it invokes the property setter on `Object.prototype.__proto__`, traversing up the prototype chain and mutating `Object.prototype` directly!

Once `Object.prototype.admin = true` is set:
When V8 looks up `newEmptyObject.admin`:
1. V8 checks `newEmptyObject` own properties (not found).
2. V8 traverses the internal `[[Prototype]]` link up to `Object.prototype`.
3. V8 finds `admin: true` on `Object.prototype` and returns `true`.

**Key Takeaway / Safe Pattern**:
Sanitize JSON keys before deep merging by blocking sensitive key names (`__proto__`, `constructor`, `prototype`). Use `Object.create(null)` or `Map` for key-value dictionary stores, and freeze prototypes in sensitive application bootstrap phases using `Object.freeze(Object.prototype)`.
