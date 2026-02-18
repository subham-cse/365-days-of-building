# Day 080: Structural vs Nominal Typing & Template Type Inflation in TypeScript

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript's type system is **structural** (duck-typed), not nominal. Unlike languages like Java or C# where two types are incompatible unless one explicitly inherits from the other, TypeScript considers two types compatible if they share the same shape (matching property names and signatures), regardless of how or where they were declared!

While structural typing provides flexibility, it can lead to subtle bugs where two domain-distinct entities (such as `UserId` and `OrderId`, both defined as `string`) can be passed interchangeably without type compiler errors.

To enforce compile-time type safety for domain primitives, TypeScript developers use **Nominal Tagging / Branding**.

**The Code Snippet**:
```typescript
// --- TRAP: Structural Typing accepts distinct domain entities ---
type UnsafeUserId = string;
type UnsafeOrderId = string;

function cancelOrderUnsafe(orderId: UnsafeOrderId, userId: UnsafeUserId) {
    console.log(`Cancelling order ${orderId} for user ${userId}`);
}

const userId: UnsafeUserId = "USR_1001";
const orderId: UnsafeOrderId = "ORD_9999";

// BUG: Arguments swapped! TypeScript compiler allows this cleanly!
cancelOrderUnsafe(userId, orderId); 


// --- SAFE PATTERN: Nominal Branding / Tagged Types ---
declare const __brand: unique symbol;

// Branded type helper
export type Brand<T, B> = T & { readonly [__brand]: B };

export type UserId = Brand<string, "UserId">;
export type OrderId = Brand<string, "OrderId">;

// Constructor helper functions
export function makeUserId(id: string): UserId {
    return id as UserId;
}

export function makeOrderId(id: string): OrderId {
    return id as OrderId;
}

function cancelOrderSafe(orderId: OrderId, userId: UserId) {
    console.log(`Safely cancelling order ${orderId} for user ${userId}`);
}

const safeUserId = makeUserId("USR_1001");
const safeOrderId = makeOrderId("ORD_9999");

// SAFE: Swapping arguments now causes explicit COMPILER ERROR!
// cancelOrderSafe(safeUserId, safeOrderId); 
// Error: Argument of type 'UserId' is not assignable to parameter of type 'OrderId'.

cancelOrderSafe(safeOrderId, safeUserId); // Works!
```

**Under the Hood / Why It Happens**:
TypeScript's type checker (`checker.ts`) evaluates type compatibility by comparing object structure using recursive property member checks (`isTypeRelatedTo`). If two interface declarations share identical field names and types, TypeScript treats them as mutually assignable.

By adding a phantom branded field containing a `unique symbol` tag (`readonly [__brand]: B`), the compiler assigns a unique structural signature to `UserId` that does not match standard `string` or `OrderId`. Because `unique symbol` signatures cannot be produced accidentally, attempting to pass a plain `string` or an `OrderId` where a `UserId` is expected fails structural type validation.

**Key Takeaway / Safe Pattern**:
Use nominal branding (`T & { readonly [__brand]: B }`) for critical domain entities (such as primary keys, currency amounts, validated email strings, or sanitized HTML) to prevent accidental argument swapping and structural collision across API boundaries.
