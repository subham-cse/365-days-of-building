# Day 052: TypeScript Conditional Types and Distributive Behavior

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
In TypeScript, conditional types follow the syntax `T extends U ? X : Y`. When `T` is a naked type parameter (an un-wrapped generic type argument like `T`), the conditional type becomes **distributive** over union types.

If `T` is a union `A | B`, evaluating `ToArray<A | B>` does not pass `A | B` as a single unit. Instead, TypeScript automatically distributes the conditional evaluation across each union constituent: `ToArray<A> | ToArray<B>`. Disabling distribution requires wrapping the type parameter in tuple syntax `[T]`.

**The Code Snippet**:
```typescript
// Distributive conditional type (naked type parameter T)
type ToArrayDistributive<T> = T extends any ? T[] : never;

// Non-distributive conditional type (wrapped type parameter [T])
type ToArrayNonDistributive<T> = [T] extends [any] ? T[] : never;

// Exclude utility implementation relying on distributive behavior
type CustomExclude<T, U> = T extends U ? never : A;

// Types demonstration
type UnionType = string | number;

// Result 1: Distributes over string | number => string[] | number[]
type DistributiveResult = ToArrayDistributive<UnionType>;

// Result 2: Evaluates whole union at once => (string | number)[]
type NonDistributiveResult = ToArrayNonDistributive<UnionType>;

// Verify behavior with compile-time assertions
const sampleDistributive: DistributiveResult = ["hello"]; // OK (string[])
// const invalidDistributive: DistributiveResult = ["hello", 42]; // Compile Error!

const sampleNonDistributive: NonDistributiveResult = ["hello", 42]; // OK ((string | number)[])

console.log("TypeScript conditional distribution verified.");
```

**Under the Hood / Why It Happens**:
The TypeScript type checker specification dictates that when a naked type parameter `T` is evaluated against a conditional `T extends U`, the compiler checks if `T` represents a union.

If `T` is `A | B | C`, the compiler transforms the type relation into:
$$\text{Conditional}(A \mid B \mid C) \implies \text{Conditional}(A) \mid \text{Conditional}(B) \mid \text{Conditional}(C)$$
This behavior enables essential utility types like `Exclude<T, U>`, `Extract<T, U>`, and `NonNullable<T>` to filter individual elements from union types. Wrapping `[T] extends [U]` prevents tuple unpacking, forcing TypeScript to process the union as an indivisible type.

**Key Takeaway / Safe Pattern**:
Leverage distributive conditional types to inspect or filter individual union variants (like `Extract` / `Exclude`). If you intend to test or wrap the union type as a whole, prevent distribution by enclosing both sides of `extends` in square brackets (`[T] extends [U]`).
