# Day 164: Structural Typing Weaknesses and Index Signature Excess Property Checks

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript uses a **structural type system** (duck typing): type compatibility is determined entirely by an object's structure (its properties and methods), rather than explicit class declarations or nominal inheritance.

However, structural typing presents surprising quirks when dealing with **Excess Property Checks** and index signatures (`[key: string]: any`). Direct object literals undergo strict excess property validation, whereas passing the exact same object via an intermediate variable bypasses the check completely!

**The Code Snippet**:

```typescript
interface UserProfile {
  username: string;
  email: string;
}

function updateProfile(profile: UserProfile): void {
  console.log(`Updating ${profile.username} <${profile.email}>`);
}

// Scenario 1: Object Literal directly passed -> Trigger Excess Property Check
// COMPILER ERROR: Object literal may only specify known properties, and 'extraField' does not exist in type 'UserProfile'.
/*
updateProfile({
  username: "alice",
  email: "alice@example.com",
  extraField: "surprise!" 
});
*/

// Scenario 2: Passed via intermediate variable -> Bypasses Excess Property Check!
const rawData = {
  username: "bob",
  email: "bob@example.com",
  extraField: "bypassed property check"
};

// COMPILER PERMITS THIS! `rawData` has all required fields of `UserProfile`
updateProfile(rawData);

// Index Signature Trap
interface StringMap {
  [key: string]: string;
}

const map: StringMap = {};
// TypeScript assumes map["non_existent_key"] is a valid `string` at compile-time!
// But at runtime, it evaluates to `undefined`, risking runtime crashes!
const value: string = map["missing_key"];
console.log(value.toUpperCase()); // TypeError: Cannot read properties of undefined
```

**Under the Hood / Why It Happens**:
TypeScript's excess property checking is a pragmatic design choice built into the compiler (`checker.ts`) specifically to catch typos in object literals (e.g., passing `{ userame: "alice" }`). Since inline object literals are created specifically for the function call, any unexpected property is almost certainly a bug.

However, when an object is assigned to an intermediate variable (`rawData`), TypeScript falls back to standard structural subtyping rules. As long as `rawData` contains the required properties (`username`, `email`), the extra properties are ignored for subtyping purposes.

Regarding index signatures: TypeScript assumes index signatures return the declared type without automatically forcing `undefined` unless `noUncheckedIndexedAccess` is explicitly enabled in `tsconfig.json`.

**Key Takeaway / Safe Pattern**:
1. Enable `noUncheckedIndexedAccess: true` in your `tsconfig.json` so indexing objects (`map[key]`) forces the compiler to include `| undefined` in the return type.
2. Use nominal type patterns (tagged unions or branded types) when strict object shape guarantees are needed across boundaries.
