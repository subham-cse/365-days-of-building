# Day 207: JavaScript Prototype Mutation and Hidden Class De-optimization

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
In JavaScript engines like V8 (Chrome, Node.js), property access is optimized using **Hidden Classes** (also called **Shapes** or **Maps**) and Inline Caching (IC). When JavaScript code accesses properties on an object (`obj.x`), V8 uses fast offset lookups based on the object's hidden class structure rather than expensive hash table searches.

Mutating an object's prototype chain dynamically at runtime using `Object.setPrototypeOf()` or `obj.__proto__ = ...` is one of the most severe performance anti-patterns in JavaScript. Mutating a prototype invalidates inline caches across **all** objects that share that prototype chain, forcing V8 to drop optimized machine code and drop back to slow generic dictionary lookups.

**The Code Snippet**:
```javascript
function Point(x, y) {
  this.x = x;
  this.y = y;
}

const p1 = new Point(10, 20);
const p2 = new Point(30, 40);

const customProto = {
  getSum() {
    return this.x + this.y;
  }
};

console.time('Fast inline cache property access');
let total1 = 0;
for (let i = 0; i < 1000000; i++) {
  total1 += p1.x + p1.y;
}
console.timeEnd('Fast inline cache property access');

// TRAP: Dynamic prototype mutation breaks V8 hidden class chain!
Object.setPrototypeOf(p1, customProto); // De-optimizes p1 and breaks Inline Caches!

console.time('De-optimized property access');
let total2 = 0;
for (let i = 0; i < 1000000; i++) {
  total2 += p1.x + p1.y;
}
console.timeEnd('De-optimized property access');
```

**Under the Hood / Why It Happens**:
V8 uses **Shape Chains** for prototype property lookup:

1. Every object maintains a pointer to its `Map` (Shape) and its Prototype.
2. V8 compiles JIT machine code using Inline Caches (IC). When it sees `p1.x`, the JIT stub checks `if (object.map == CachedMap) return object.inline_slot[0]`.
3. When `Object.setPrototypeOf(p1, customProto)` executes, V8 mutates `p1`'s map and marks `p1`'s prototype cell as modified.
4. V8 invalidates all JIT compiled IC stubs dependent on `Point.prototype` and sets the type feedback vector status to **Megamorphic**.
5. Subsequent property accesses bypass JIT inline slot offsets and execute full hash table dynamic lookups in C++ runtime code.

**Key Takeaway / Safe Pattern**:
Never mutate an object's prototype after instantiation. Define prototype methods on class declarations or use `Object.create(proto)` at instantiation time to set prototypes immutably.

```javascript
// Safe Pattern: Create object with prototype immutably at allocation time
const customProto = {
  getSum() { return this.x + this.y; }
};

// Prototype set cleanly during allocation; V8 builds stable Shape/Map upfront
const pSafe = Object.create(customProto);
pSafe.x = 10;
pSafe.y = 20;
```
