# Day 108: Structural vs Nominal Typing and Conditional Type Inference
- **Language / Domain**: TypeScript
- **The Core Concept / "Did You Know?"**: TypeScript uses a **structural type system** ("duck typing"): two types are considered identical if they share the same shape, regardless of their declared names or class structures.

This can lead to type safety issues where unrelated objects are accepted interchangeably. To enforce strict type safety (known as **nominal typing**), TypeScript developers use *branding* or *tagging* techniques combined with conditional types (`infer`).

- **The Code Snippet**:
```typescript
// Structural Typing Problem
interface UserIDStructural { id: string }
interface PostIDStructural { id: string }

function fetchPost(postId: PostIDStructural) {
  console.log("Fetching post:", postId.id);
}

const userId: UserIDStructural = { id: "user_123" };
fetchPost(userId); // Compiles with NO errors despite passing UserID to PostID!

// Solution: Nominal Typing via Nominal Branding
declare const __brand: unique symbol;

type Brand<T, B> = T & { readonly [__brand]: B };

type UserId = Brand<string, "UserId">;
type PostId = Brand<string, "PostId">;

function makeUserId(id: string): UserId { return id as UserId; }
function makePostId(id: string): PostId { return id as PostId; }

function fetchPostNominal(postId: PostId) {
  console.log("Fetching post:", postId);
}

const safeUserId = makeUserId("user_123");
const safePostId = makePostId("post_456");

fetchPostNominal(safePostId); // OK
// fetchPostNominal(safeUserId); // Type Error: Type '"UserId"' is not assignable to type '"PostId"'

// Conditional Type Inference with infer
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;
type ResolvedNumber = UnpackPromise<Promise<number>>; // number
```

- **Under the Hood / Why It Happens**:
TypeScript's type checker (`tsc`) erases all types during compilation to JavaScript. During static analysis, `tsc` compares type shapes by recursively matching property keys and value types (`TypeCompatibility`). 

By adding an unassignable unique symbol brand (`readonly [__brand]: B`), we force the type checker's structural compatibility matrix to fail unless the exact brand is present.

- **Key Takeaway / Safe Pattern**:
Use branded types (`Brand<Primitive, Tag>`) when creating IDs, currency units (e.g. `USD` vs `EUR`), or sanitized strings to prevent domain logic bugs caused by structural type matching.
