# Day 147: Racket Hygienic Macros & Variable Capture Traps

**Language / Domain**: Elixir / Erlang / Racket

**The Core Concept / "Did You Know?"**:
Racket and Scheme feature **homoiconicity**—code is represented directly as data structures (syntax objects). Unlike C preprocessor `#define` macros which perform naive string expansion, Racket's macro system uses **hygienic macros** (`define-syntax-rule` / `syntax-parse`).

Hygienic macros ensure that temporary local variables introduced inside a macro expansion do NOT accidentally shadow or capture variables in the macro caller's surrounding lexical scope! Understanding how Racket maintains variable binding hygiene prevents subtle bugs when generating code programmatically.

**The Code Snippet**:
```racket
#lang racket

;; Define a hygienic swap macro
(define-syntax-rule (swap! a b)
  (let ([temp a])
    (set! a b)
    (set! b temp)))

;; Demonstration of Hygiene Preservation
(define (test-hygiene)
  (define temp 999) ; Variable named 'temp' in caller scope
  (define x 10)
  (define y 20)

  (displayln (format "Before swap: x=~a, y=~a, temp=~a" x y temp))
  
  ;; Expanding (swap! x y) introduces an internal 'temp' variable!
  ;; In non-hygienic languages (like C macros), 'temp' would collide with caller's 'temp'.
  (swap! x y)

  (displayln (format "After swap:  x=~a, y=~a, temp=~a" x y temp)))

(test-hygiene)
;; Output:
;; Before swap: x=10, y=20, temp=999
;; After swap:  x=20, y=10, temp=999  (Caller 'temp' remains untouched!)
```

**Under the Hood / Why It Happens**:
In unhygienic macro expansion (e.g. C `#define SWAP(a,b) int temp = a; a = b; b = temp;`), macro expansion blindly overwrites text identifiers. If the caller scope already declared `int temp`, the macro accidentally mutates or shadows `temp`.

In Racket's macro expander (`syntax/stx.rkt`):
1. Every syntax transformer operates on **Syntax Objects** containing syntax tree structure along with **Lexical Context Stamps** (scopes).
2. When `define-syntax-rule` expands `(let ([temp a]) ...)`, the expander generates a fresh internal identifier symbol tagged with a unique scope mark (similar to `gensym`).
3. The identifier `temp` inside the macro body is recognized as distinct from the caller's `temp` variable in the AST, preserving lexical binding scope across transformations automatically.

If a developer explicitly *wants* to introduce variables into the caller's scope (unhygienic macro), Racket requires explicitly constructing syntax objects using `datum->syntax`.

**Key Takeaway / Safe Pattern**:
Racket's `define-syntax-rule` and `syntax-parse` protect macro expansions from variable capture by default. Rely on hygienic syntax transformations to write safe code generators without worrying about symbol collisions in caller environments.
