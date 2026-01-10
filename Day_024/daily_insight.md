# Day 024: Conditional Types, Infer Keyword Magic, and Type Narrowing Limits
**Language / Domain**: TypeScript

**The Core Concept / "Did You Know?"**:
TypeScript's type system is Turing-complete, featuring **Conditional Types** (`T extends U ? X : Y`) and the powerful `infer` keyword. `infer` allows extracting and introducing template type variables dynamically inside generic type declarations.

However, when conditional types act on generic type parameters, they become **Distributive Conditional Types** over union types. This causes unexpected union distributions when passed types like `T | null` or `never`, leading to hard-to-debug type transformation bugs.

**The Code Snippet**:
```typescript
// Advanced Metaprogramming with `infer`
// Extract return type of a Promise or Function automatically
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;

type A = UnpackPromise<Promise<string>>; // Type A is `string`
type B = UnpackPromise<number>;          // Type B is `number`

// Distributive Conditional Type Trap
type ToArray<T> = T extends any ? T[] : never;

type UnionResult = ToArray<string | number>; 
// Expected: (string | number)[]
// Actual Type: string[] | number[] ! (Distributed across union elements!)

// Non-distributive Conditional Type Fix
type ToArrayNonDistributive<T> = [T] extends [any] ? T[] : never;

type CorrectUnionResult = ToArrayNonDistributive<string | number>; 
// Type is correctly: (string | number)[]

// Type Narrowing Limitation Trap with Array methods
function processItems(items: (string | null)[]) {
    // Filter out nulls
    const filtered = items.filter(item => item !== null);
    
    // TRAP: TypeScript still thinks `filtered` is (string | null)[]!
    // filtered.forEach(item => item.toUpperCase()); // Compiler Error!
}
```

**Under the Hood / Why It Happens**:
When a conditional type `T extends U ? X : Y` operates on a bare generic parameter `T`, and `T` is instantiated with a union type $A \mid B$, TypeScript distributes the evaluation across each member of the union:
$$\text{ToArray}<A \mid B> \implies \text{ToArray}<A> \mid \text{ToArray}<B> \implies A[] \mid B[]$$

To disable distribution, the type parameter `T` must be wrapped in a tuple `[T]`, breaking the distributive trigger rule in the compiler's type relation solver.

For array operations like `.filter()`, TypeScript's standard declaration for `Array.prototype.filter` returns `T[]` unless a custom **Type Predicate** (`item is string`) is explicitly supplied to the callback function.

**Key Takeaway / Safe Pattern**:
Wrap conditional type parameters in tuples `[T]` when distributor behavior is unwanted. Use explicit Type Predicate functions (`x is T`) to narrow array filter results accurately.

```typescript
// SAFE: Array filter with custom Type Predicate
function isNotNull<T>(val: T | null | undefined): val is T {
    return val !== null && val !== undefined;
}

function processItemsSafe(items: (string | null)[]) {
    // TypeScript correctly narrows return type to string[]!
    const filtered: string[] = items.filter(isNotNull);
    
    filtered.forEach(item => console.log(item.toUpperCase())); // SAFE!
}
```
