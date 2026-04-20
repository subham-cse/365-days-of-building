# Day 152: TypeScript `any` vs `unknown` & Type Safety Contagion

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
In TypeScript, `any` and `unknown` are both top types capable of holding values of any arbitrary type. However, they exhibit fundamentally opposite type-checking semantics!

`any` completely turns off TypeScript's static type checker. It is **contagious**: passing an `any` variable into functions or operations suppresses type checking across dependent variables down the call stack. Conversely, `unknown` is **type-safe**. TypeScript allows you to assign any value to an `unknown` variable, but forbids you from calling methods, accessing properties, or passing `unknown` into typed functions without performing explicit **Type Narrowing** checks first!

**The Code Snippet**:
```typescript
// DANGEROUS: Using 'any' turns off type checker completely
function parseApiResponseUnsafe(jsonString: string): any {
  return JSON.parse(jsonString);
}

// SAFE: Using 'unknown' enforces type narrowing before property access
function parseApiResponseSafe(jsonString: string): unknown {
  return JSON.parse(jsonString);
}

// --- Execution Demonstration ---
const rawData = '{"userId": 42, "role": "admin"}';

const unsafeUser = parseApiResponseUnsafe(rawData);
// No compile errors! Fails silently at runtime if method doesn't exist
console.log(unsafeUser.nonExistentMethod()); // RUNTIME ERROR: unsafeUser.nonExistentMethod is not a function

const safeUser = parseApiResponseSafe(rawData);

// COMPILER ERROR: Object is of type 'unknown'.
// console.log(safeUser.userId);

// SAFE PATTERN: Type Narrowing / Type Guard validation
interface User {
  userId: number;
  role: string;
}

function isUser(obj: any): obj is User {
  return typeof obj === 'object' && obj !== null && typeof obj.userId === 'number';
}

if (isUser(safeUser)) {
  // TypeScript safely narrows safeUser to 'User' interface!
  console.log(`Validated User ID: ${safeUser.userId}`);
}
```

**Under the Hood / Why It Happens**:
Inside the TypeScript Compiler (`checker.ts`):
1. **`any` Type Assignment**: Assigning `any` to a target variable `T` causes `isTypeAssignableTo(source, target)` to immediately return `true` without checking property schemas. The compiler skips type-checking instructions, emitting raw JavaScript output without safety checks.
2. **`unknown` Type Assignment**: `unknown` represents an un-narrowed top type. When property access (`safeUser.userId`) is encountered, the type checker verifies if `unknown` contains the member key. Because `unknown` explicitly declares zero properties, the compiler triggers error code `TS2339: Property 'x' does not exist on type 'unknown'`.

Only when custom Type Predicates (`obj is User`) or runtime `typeof`/`instanceof` guards evaluate to `true` does the compiler narrow the flow-analyzed type set from `unknown` to `User`.

**Key Takeaway / Safe Pattern**:
Never use `any` for untrusted external inputs (API payloads, user inputs, third-party libraries). Use `unknown` alongside Type Guard predicates (`obj is T`) or runtime schema validation libraries (such as Zod) to enforce type safety at boundary interfaces.
