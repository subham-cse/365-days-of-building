# Day 236: TypeScript Distributive Conditional Types & Naked Type Parameter Expansion

**Language / Domain**: TypeScript / Advanced Type System & Generics

**The Core Concept / "Did You Know?"**:
In TypeScript, when a conditional type acts on a **naked type parameter** (e.g., `T extends U ? X : Y`), the conditional type automatically becomes **distributive** over union types. When a union type like `string | number` is passed for `T`, TypeScript unrolls the union, applying the conditional type to each constituent type individually: `(string extends U ? X : Y) | (number extends U ? X : Y)`.

While distributive behavior is essential for utility types like `Exclude<T, U>` and `Extract<T, U>`, it can trigger unexpected compiler bugs when working with `never`, tuple types, or checking type equality. Passing `never` to a naked distributive type results in `never` immediately, completely skipping the conditional logic!

**The Code Snippet**:
```typescript
// --- DISTRIBUTIVE TYPE BEHAVIOR ---
type ToArrayNaked<T> = T extends any ? T[] : never;

// Union type is unrolled: (string extends any ? string[] : never) | (number extends any ? number[] : never)
type UnrolledResult = ToArrayNaked<string | number>;
// Result: string[] | number[]

// --- TRAP 1: Naked never handling ---
type IsNeverNaked<T> = T extends never ? true : false;

type TestNever1 = IsNeverNaked<never>;
// Result: never! (NOT true! Because union of zero types distributes to nothing)

// --- TRAP 2: Unintentional Union Splitting during Array Wrapping ---
type WrapInTuple<T> = T extends any ? [T] : never;
type TupleResult = WrapInTuple<string | number>;
// Result: [string] | [number] (NOT [string | number]!)

// --- SAFE PATTERN: Disabling Distribution via Square Bracket Wrapping `[T]` ---
type IsNeverNonDistributive<T> = [T] extends [never] ? true : false;
type ToArrayNonDistributive<T> = [T] extends [any] ? T[] : never;
type WrapInTupleNonDistributive<T> = [T] extends [any] ? [T] : never;

type TestNever2 = IsNeverNonDistributive<never>;
// Result: true! (Correctly evaluates!)

type SingleTupleResult = WrapInTupleNonDistributive<string | number>;
// Result: [string | number] (Preserves original union without unrolling!)
```

**Under the Hood / Why It Happens**:
1. **Distributive Trigger Rule**:
   TypeScript's distributive conditional type rule applies if and only if:
   - The type being checked (`T`) is a bare/naked type parameter (not wrapped inside a tuple, array, object, or function).
   - `T` is instantiated with a union type or `never`.

2. **Why `IsNeverNaked<never>` evaluates to `never`**:
   In TypeScript's type system, `never` is represented as the **empty union** (an empty set of types). When distributing over a union of $N$ types, TypeScript evaluates the conditional $N$ times and unions the results. Distributing over an empty union ($N=0$) executes 0 times, returning the empty union (`never`).

3. **Disabling Distribution with `[T]`**:
   Wrapping `T` in a tuple syntax (`[T] extends [never]`) removes the "naked" status of `T`. TypeScript treats `[T]` as a single compound data type, preventing union unrolling and preserving exact type equality logic.

**Key Takeaway / Safe Pattern**:
- **Leverage distribution** when filtering union types (e.g., `type NonNullable<T> = T extends null | undefined ? never : T`).
- **Disable distribution** using tuple wrapping `[T] extends [U]` when checking for `never`, `any`, or when preserving composite union types intact without splitting.
