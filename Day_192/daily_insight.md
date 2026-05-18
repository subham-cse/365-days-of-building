# Day 192: TypeScript Structural Typing and Branded Nominal Types

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
Unlike languages like Java or C++ which use **nominal typing** (types are compatible only if explicitly declared in an inheritance hierarchy), TypeScript uses a **structural typing system** ("duck typing"). If two interfaces or classes share the same shape (names and types of properties), TypeScript considers them completely assignable to one another, regardless of their class hierarchy or constructor identity.

This structural soundness model can lead to domain errors—such as accidentally passing a `UserId` string where an `OrderId` string is expected, or passing an empty object `{}` when an object type with optional parameters is expected.

**The Code Snippet**:
```typescript
interface User {
  id: string;
  name: string;
}

interface Product {
  id: string;
  name: string;
}

function deleteUser(user: User) {
  console.log(`Deleting user: ${user.name}`);
}

const item: Product = { id: "p_100", name: "Wireless Mouse" };

// Structurally valid! Product has same shape as User
deleteUser(item); // Compiles without error despite semantic type mismatch!


// Advanced Trap: Excessive Property Checks only apply to direct object literals
function logCoordinates(point: { x: number; y: number }) {
  console.log(`${point.x}, ${point.y}`);
}

const extraProp = { x: 10, y: 20, z: 30 };
logCoordinates(extraProp); // Allowed structurally!
// logCoordinates({ x: 10, y: 20, z: 30 }); // Error: Direct literal triggers excess property check
```

**Under the Hood / Why It Happens**:
TypeScript's type checker verifies compatibility by shape evaluation. When checking if type `T` is assignable to type `U`:
1. The compiler iterates through every required member property of `U`.
2. It checks if `T` possesses a property with identical key name and a subtype-compatible type.
3. If all members of `U` exist in `T`, assignability succeeds (`T <: U`).

Because runtime metadata does not maintain type names, type identity exists only at compile time. Direct object literals enforce "excess property checks", but indirect variable assignments bypass this check due to structural subtyping rules.

**Key Takeaway / Safe Pattern**:
To prevent domain type confusion in TypeScript, use **Branded Types** (also called Nominal Flavoring) by combining primitive types with unique tag symbols.

```typescript
// Safe Pattern: Nominal Branded Types
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };

function makeUserId(id: string): UserId { return id as UserId; }
function makeOrderId(id: string): OrderId { return id as OrderId; }

function processUser(userId: UserId) { /* ... */ }

const uid = makeUserId("usr_123");
const oid = makeOrderId("ord_999");

processUser(uid); // OK
// processUser(oid); // Compile Error: Type 'OrderId' is not assignable to type 'UserId'
```
