# Day 220: TypeScript Template Literal Types & Tail-Call Recursive Inference Limits

**Language / Domain**: TypeScript / Type System Compiler Internals

**The Core Concept / "Did You Know?"**:
TypeScript's type system is Turing complete. With the introduction of **Template Literal Types** and **Conditional Type Inference (`infer`)**, developers can build type-level parsers, string formatters, and compile-time router validators directly in TypeScript type signatures.

However, TypeScript enforces strict compiler stack depth limits on type recursion (typically 50 to 1000 stack frames). Naive recursive type aliases quickly hit `Type instantiation is excessively deep and possibly infinite. (ts2589)` errors. To circumvent this compiler limit, TypeScript 4.5 introduced **Tail-Call Optimization (TCO) for Conditional Types**, allowing accumulator-style recursive types to exceed standard stack depth limits.

**The Code Snippet**:
```typescript
// --- TRAP: Non-Tail-Call Recursive String Parser (Fails on long strings) ---
type NaiveSplit<S extends string, Sep extends string> =
  S extends `${infer Head}${Sep}${infer Tail}`
    ? [Head, ...NaiveSplit<Tail, Sep>] // Recursive call is NOT in tail position due to tuple spread!
    : [S];

// --- SAFE PATTERN: Tail-Call Optimized (TCO) Recursive String Parser ---
type SplitTCO<
  S extends string,
  Sep extends string,
  Acc extends string[] = [] // Accumulator parameter
> = S extends `${infer Head}${Sep}${infer Tail}`
  ? SplitTCO<Tail, Sep, [...Acc, Head]> // Pure recursive call in tail position!
  : [...Acc, S];

// Compile-Time Route Parameter Extractor using TCO Template Literals
type ExtractRouteParams<
  Path extends string,
  Acc extends string = never
> = Path extends `${string}:${infer Param}/${infer Rest}`
  ? ExtractRouteParams<Rest, Acc | Param>
  : Path extends `${string}:${infer Param}`
  ? Acc | Param
  : Acc;

// Usage Examples:
type Route = "/api/v1/users/:userId/posts/:postId/comments/:commentId";
type Params = ExtractRouteParams<Route>;
// Result Type: "userId" | "postId" | "commentId"

type LongCSV = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z";
type ParsedCSV = SplitTCO<LongCSV, ",">;
// Result Type: ["a", "b", ..., "z"] cleanly resolved without compile error!
```

**Under the Hood / Why It Happens**:
When the TypeScript type checker evaluates a conditional type:
1. In `NaiveSplit`: The result expression `[Head, ...NaiveSplit<Tail, Sep>]` requires the compiler to pause resolution of `NaiveSplit`, deferring stack frames while evaluating nested calls. This consumes memory on the compiler's call stack proportional to string length \(O(N)\).
2. In `SplitTCO`: The recursive invocation `SplitTCO<Tail, Sep, [...Acc, Head]>` returns the result of the recursive type direct without pending outer operations.

The TypeScript compiler recognizes when a conditional type evaluates directly to another instance of itself in the dynamic branch. When this condition is met, the compiler applies internal tail-call elimination: it reuses the evaluation loop frame without pushing a new stack frame onto the engine's internal call stack, elevating structural recursion limits from ~50 frames to thousands of iterations.

**Key Takeaway / Safe Pattern**:
- When writing type-level string parsers, mappers, or math accumulating types in TypeScript, always pass an `Acc` (accumulator) generic parameter.
- Ensure the recursive type call is the outermost expression in the conditional branch—avoid wrapping recursive type calls inside tuples, mapped types, or object unions (`[...Acc, RecursiveCall<...>]` breaks TCO; `RecursiveCall<..., [...Acc, Item]>` preserves TCO).
