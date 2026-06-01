# Day 208: TypeScript Distributive Conditional Types and `never` Filtering

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript supports **Conditional Types** formatted as `T extends U ? X : Y`. When a conditional type acts on a naked generic type parameter `T` passed as a **union type** (e.g. `string | number | boolean`), the conditional type automatically becomes **distributive**.

Distributive conditional types automatically map across each member of the union independently: `(A | B) extends U ? X : Y` evaluates as `(A extends U ? X : Y) | (B extends U ? X : Y)`.

When combined with `never`, distributive conditional types provide a powerful type-level filtering mechanism. Because `never` represents the empty set in TypeScript's type system, returning `never` from a branch silently eliminates that member from the resulting output union!

**The Code Snippet**:
```typescript
// Filtering Union Types using Distributive Conditional Types
type FilterType<T, Target> = T extends Target ? T : never;

type MixedUnion = string | number | boolean | string[] | (() => void);

// Extract only string and string[] from union
type StringsOnly = FilterType<MixedUnion, string | string[]>;
// Evaluates as:
// (string extends string | string[] ? string : never) |
// (number extends string | string[] ? number : never) |
// (boolean extends string | string[] ? boolean : never) | ...
// Result: string | string[] (never types are filtered out!)


// TRAP: Preventing Distributivity using Tuple Wrapper [T]
type NonDistributiveFilter<T, Target> = [T] extends [Target] ? T : never;

// Passing union to NonDistributiveFilter evaluates [string | number] extends [string]
type TestDistributive = NonDistributiveFilter<string | number, string>;
// Result: never (Union is evaluated as a whole tuple, NOT distributed per member!)
```

**Under the Hood / Why It Happens**:
The TypeScript compiler handles type evaluation in `checker.ts`:

1. When evaluating `T extends U ? X : Y`, the compiler checks if `T` is a generic type parameter and if `T` is "naked" (not enclosed inside a tuple `[T]`, array `T[]`, or interface wrapper `{ key: T }`).
2. If `T` is a union type (e.g., `UnionType` with components \(C_1, C_2, \dots, C_n\)), `getConditionalType()` splits the union into individual member components.
3. It evaluates `instantiateType()` on each component type individually.
4. If a component evaluates to `never`, TypeScript's union constructor `getUnionType([X, never])` simplifies the set: \(X \cup \emptyset = X\). `never` is eliminated from the returned composite type.

**Key Takeaway / Safe Pattern**:
Leverage distributive conditional types to build custom utility types (like built-in `Extract<T, U>` and `Exclude<T, U>`). If you need to check if an entire union type as a whole satisfies a condition without distributing across individual members, wrap generic parameters in tuples `[T] extends [U]`.

```typescript
// Built-in Utility Implementation using Distributive Conditional Types:
type MyExclude<T, U> = T extends U ? never : T;
type MyExtract<T, U> = T extends U ? T : never;

// Prevents distributivity when checking if T strictly includes boolean
type IsStrictlyBoolean<T> = [T] extends [boolean] ? true : false;
```
