# Day 180: Distributive Conditional Types and `infer` Keyword Type Inference

**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript's type system is Turing-complete. Among its most powerful metaprogramming tools are **Conditional Types** (`T extends U ? X : Y`) and the **`infer`** keyword, which allows extracting sub-types dynamically from complex signatures (such as promise returns, function arguments, or array elements).

However, conditional types exhibit a counterintuitive behavior called **Distributive Conditional Types**: when given a generic union type (`T = A | B`), a conditional type automatically distributes across each member of the union! If distribution is not intended, developers must wrap the type check in tuple brackets (`[T] extends [U]`).

**The Code Snippet**:

```typescript
// 1. Unpack Return Type using `infer`
type UnpackPromise<T> = T extends Promise<infer R> ? R : T;

type StringPromise = Promise<string>;
type ExtractedString = UnpackPromise<StringPromise>; // string
type NonPromise = UnpackPromise<number>;            // number

// 2. Distributive Conditional Type Trap
type ToArrayDistributive<T> = T extends any ? T[] : never;

// Generic union type input: `string | number`
type DistributedResult = ToArrayDistributive<string | number>;
// EXPECTED (by beginners): (string | number)[]
// ACTUAL OUTPUT: string[] | number[]  (Distributed over union members!)

// 3. Preventing Distribution using Tuple Wrapping `[T]`
type ToArrayNonDistributive<T> = [T] extends [any] ? T[] : never;

type NonDistributedResult = ToArrayNonDistributive<string | number>;
// ACTUAL OUTPUT: (string | number)[]  (Preserved intact union array!)

// Practical Usage: Flatten nested function parameters
type FirstArgument<T> = T extends (first: infer A, ...args: any[]) => any ? A : never;

function calculateScore(userId: string, multiplier: number): number {
  return 100 * multiplier;
}

type UserParam = FirstArgument<typeof calculateScore>; // string
```

**Under the Hood / Why It Happens**:
In TypeScript compiler (`checker.ts`), when evaluating `T extends U ? X : Y`:
1. If `T` is a bare type parameter (a raw generic placeholder without surrounding modifiers) and `T` is instantiated with a union type `A | B`:
2. The compiler expands the expression into `(A extends U ? X : Y) | (B extends U ? X : Y)`.

This distribution mechanism powers built-in utility types like `Exclude<T, U>` (`T extends U ? never : T`).
Wrapping `[T] extends [U]` prevents `T` from being treated as a bare type parameter, suppressing distribution and forcing the type checker to evaluate the union as a single unified entity.

**Key Takeaway / Safe Pattern**:
Use conditional types with `infer` to build robust dynamic type utilities. Always remember that bare generic types in conditional clauses distribute over unions; wrap types in tuple syntax `[T] extends [U]` whenever you want to evaluate a union type holistically without distribution.
