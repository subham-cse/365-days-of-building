# Day 179: Prototype Pollution Vulnerabilities and Prevention

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript objects inherit properties through a prototype chain linked via `Object.prototype`. **Prototype Pollution** is a critical security vulnerability that occurs when an attacker trick an application into mutating `Object.prototype` via properties like `__proto__`, `constructor.prototype`, or recursive deep merge utilities.

Because almost all standard JavaScript objects inherit from `Object.prototype`, polluting `Object.prototype` injects arbitrary properties into *every single object* across the entire JavaScript runtime! This can lead to Remote Code Execution (RCE), authentication bypasses, or denial of service.

**The Code Snippet**:

```javascript
// Vulnerable Deep Merge Function
function unsafeMerge(target, source) {
  for (let key in source) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) target[key] = {};
      unsafeMerge(target[key], source[key]); // Recursive merge
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// Simulated Malicious JSON payload
const maliciousPayload = JSON.parse('{"__proto__": {"isAdmin": true}}');

// Target object before merge
const config = {};
console.log("Before pollution - Standard object isAdmin:", {}.isAdmin); // undefined

// Merge payload into target
unsafeMerge(config, maliciousPayload);

// IMPACT: Object.prototype has been corrupted!
console.log("After pollution - Standard object isAdmin:", {}.isAdmin); // TRUE!
console.log("Any new object now inherits polluted state:", ({}).isAdmin); // TRUE!

// SAFE PATTERN 1: Object with NO prototype
const cleanMap = Object.create(null);
console.log("Clean map has no prototype chain:", cleanMap.__proto__); // undefined

// SAFE PATTERN 2: Defend merge function against key pollution
function safeMerge(target, source) {
  for (let key in source) {
    // Block dangerous keys
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      if (typeof source[key] === 'object' && source[key] !== null) {
        if (!target[key]) target[key] = {};
        safeMerge(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
  }
  return target;
}
```

**Under the Hood / Why It Happens**:
In V8/JavaScript runtime semantics, accessing `obj.__proto__` invokes the getter/setter defined on `Object.prototype.__proto__`.

When `unsafeMerge` iterates over `key = "__proto__"`:
1. `target["__proto__"]` resolves to `Object.prototype`.
2. Setting `target["__proto__"]["isAdmin"] = true` mutates `Object.prototype.isAdmin`.
3. Subsequent property lookups on *any* object perform prototype chain traversal. When `({}).isAdmin` is evaluated, the engine checks the instance (not found), then checks `Object.prototype`, finding `isAdmin = true`.

**Key Takeaway / Safe Pattern**:
1. Filter out `__proto__`, `constructor`, and `prototype` keys in custom recursive object assign/merge utilities.
2. For dictionary map lookups, use `Map` or objects created with `Object.create(null)`.
3. Freeze prototype objects in high-security environments using `Object.freeze(Object.prototype)`.
