# Day 051: JavaScript Prototype Mutation and Unexpected Inheritance

**Language / Domain**: JavaScript

**The Core Concept / "Did You Know?"**:
JavaScript utilizes prototype-based inheritance. Every object maintains an internal link (`[[Prototype]]`, accessible via `Object.getPrototypeOf()` or `__proto__`) to another object. If a property or method is not found on the object instance, JavaScript recursively traverses up the prototype chain.

Mutating an object's prototype at runtime or assigning shared objects to `Constructor.prototype` affects ALL existing and future instances derived from that prototype, causing hard-to-track side-effects across detached codebase modules.

**The Code Snippet**:
```javascript
function UserAccount(username) {
    this.username = username;
}

// Anti-pattern: Assigning mutable reference array directly to constructor prototype
UserAccount.prototype.permissions = ["READ_POSTS"];

const userAlice = new UserAccount("Alice");
const userBob = new UserAccount("Bob");

console.log("Alice permissions initial:", userAlice.permissions); // ['READ_POSTS']
console.log("Bob permissions initial:", userBob.permissions);     // ['READ_POSTS']

// Alice mutates the shared prototype array reference!
userAlice.permissions.push("ADMIN_DELETE");

console.log("\nAfter Alice modifies permissions array:");
console.log("Alice permissions:", userAlice.permissions); // ['READ_POSTS', 'ADMIN_DELETE']
console.log("Bob permissions:", userBob.permissions);     // ['READ_POSTS', 'ADMIN_DELETE'] -> Bob got escalated!

// Safe Pattern: Defining instance-specific properties in constructor
function SafeUserAccount(username) {
    this.username = username;
    // Each instance gets its own isolated Array memory reference
    this.permissions = ["READ_POSTS"]; 
}

// Methods remain shared on prototype (stateless functions)
SafeUserAccount.prototype.addPermission = function(perm) {
    this.permissions.push(perm);
};

const safeAlice = new SafeUserAccount("SafeAlice");
const safeBob = new SafeUserAccount("SafeBob");

safeAlice.addPermission("ADMIN_DELETE");
console.log("\nSafe Pattern Result:");
console.log("Safe Alice:", safeAlice.permissions); // ['READ_POSTS', 'ADMIN_DELETE']
console.log("Safe Bob:", safeBob.permissions);     // ['READ_POSTS']
```

**Under the Hood / Why It Happens**:
When `userAlice.permissions.push(...)` executes, JavaScript first resolves `userAlice.permissions`. Finding no `permissions` key on `userAlice`'s own property descriptor map, the engine looks up `UserAccount.prototype.permissions`, returning the single Array object reference stored on the prototype object. 

Calling `.push()` on that reference mutates the underlying Array object in heap memory. Because `userBob` shares the exact same prototype reference link, `userBob.permissions` evaluates to the modified array.

**Key Takeaway / Safe Pattern**:
Only attach stateless functions/methods to constructor function prototypes or class definitions. Keep mutable state data (arrays, objects) strictly within instance constructors using `this.propertyName = ...` or standard ES6 `class` fields.
