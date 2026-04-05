# Day 136: TypeScript Nominal Typing Workarounds using Branded Types

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript uses a **structural type system** (duck typing): two types are considered identical if they possess the same shape/properties, regardless of their declared name. While structural typing provides immense flexibility, it leads to dangerous bugs when domain concepts share the exact same underlying type (e.g. `UserId` vs `OrderId`, both represented as `string`).

Without type distinguishability, TypeScript will happily allow you to pass an `OrderId` to a function expecting a `UserId` without raising any compile-time errors. To achieve compile-time type safety for domain primitives, developers utilize **Branded Types** (also known as Nominal Typing flavor).

**The Code Snippet**:
```typescript
// Structural Trap: Plain type aliases permit cross-assignment
type RawUserId = string;
type RawOrderId = string;

function getRawOrderDetails(orderId: RawOrderId) {
  console.log(`Fetching order: ${orderId}`);
}

const userId: RawUserId = "usr_12345";
getRawOrderDetails(userId); // Passes compile check! (Unintended bug)

// SAFE PATTERN: Nominal Type Branding using unique tag symbols
declare const __brand: unique symbol;

type Brand<T, B> = T & { readonly [__brand]: B };

export type UserId = Brand<string, "UserId">;
export type OrderId = Brand<string, "OrderId">;

// Constructor helper functions (type casts)
export function makeUserId(id: string): UserId {
  return id as UserId;
}

export function makeOrderId(id: string): OrderId {
  return id as OrderId;
}

function getOrderDetails(orderId: OrderId) {
  console.log(`Fetching order safely: ${orderId}`);
}

const safeUserId = makeUserId("usr_999");
const safeOrderId = makeOrderId("ord_555");

getOrderDetails(safeOrderId); // OK

// getOrderDetails(safeUserId); 
// COMPILE ERROR: Argument of type 'UserId' is not assignable to parameter of type 'OrderId'.
```

**Under the Hood / Why It Happens**:
In TypeScript's type checker (`checker.ts`), type compatibility checks evaluate structural shapes via `isTypeAssignableTo(source, target)`. If both types are primitives like `string`, assignability succeeds trivially.

By defining `Brand<T, B> = T & { readonly [__brand]: B }`, we construct an intersection type containing a fake compile-time property (`[__brand]`). 
- At runtime, branded variables remain plain JavaScript strings—zero runtime overhead or allocation cost!
- At compile-time, TypeScript checks for the presence of the unique symbol key `[__brand]: "OrderId"`. Because `"UserId"` is not assignable to `"OrderId"`, the compiler blocks invalid variable assignments.

**Key Takeaway / Safe Pattern**:
Use branded types (`T & { readonly [__brand]: B }`) for domain primitives like database IDs, validated emails, currencies, and sanitised HTML strings to prevent accidental parameter misplacement while retaining zero runtime performance overhead.
