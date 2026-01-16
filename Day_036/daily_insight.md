# Day 036: TypeScript `any` vs `unknown` and Type Widening

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
In TypeScript, `any` and `unknown` both represent a value of any type, but they are fundamentally opposite in terms of type safety. `any` disables all static type checking, making TypeScript operate like dynamically typed JavaScript. Conversely, `unknown` is the type-safe top type: it accepts any value, but TypeScript forbids performing arbitrary operations, property access, or function invocations on an `unknown` variable without explicit type narrowing.

Overusing `any` introduces invisible runtime bugs by propagating type loss across dependent function signatures.

**The Code Snippet**:
```typescript
interface UserProfile {
    id: string;
    displayName: string;
}

// Dangerous pattern using `any`
function parseUnsafeApiResponse(jsonString: string): any {
    return JSON.parse(jsonString);
}

// Safe pattern using `unknown` with runtime type guard narrowing
function parseSafeApiResponse(jsonString: string): unknown {
    return JSON.parse(jsonString);
}

function isUserProfile(obj: unknown): obj is UserProfile {
    return (
        typeof obj === "object" &&
        obj !== null &&
        "id" in obj &&
        typeof (obj as UserProfile).id === "string" &&
        "displayName" in obj &&
        typeof (obj as UserProfile).displayName === "string"
    );
}

// Usage demonstration
const jsonPayload = '{"id": "usr_100", "displayName": "Alice"}';

const unsafeUser = parseUnsafeApiResponse(jsonPayload);
// Compiles fine, but runtime crash if nonExistentMethod does not exist!
// unsafeUser.nonExistentMethod(); 

const safeUser = parseSafeApiResponse(jsonPayload);
// safeUser.displayName; // Compile Error: Object is of type 'unknown'.

if (isUserProfile(safeUser)) {
    // Narrowed safely to UserProfile!
    console.log(`User validated: ${safeUser.displayName} (${safeUser.id})`);
} else {
    console.error("Payload did not conform to UserProfile schema");
}
```

**Under the Hood / Why It Happens**:
`any` acts as a hole in the type graph. Assigning `any` to another variable turns off type checking downstream because the compiler assigns `any` to both top and bottom positions in type compatibility checks.

`unknown` acts as a top type in TypeScript's set-theoretic type system. Every type is a subtype of `unknown`, but `unknown` is not a subtype of anything except `any` and `unknown`. Therefore, the compiler enforces a mandatory narrowing check (via `typeof`, `instanceof`, or custom type predicate functions (`is`)) before allowing member access or arithmetic operations.

**Key Takeaway / Safe Pattern**:
Avoid `any` when handling untrusted dynamic data (such as API payloads or local storage parsing). Prefer `unknown` combined with custom type guard predicates (`x is T`) or schema validation libraries (such as Zod) to enforce runtime boundary checks safely.
