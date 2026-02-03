# Day 063: Elixir Pattern Matching Guards and Homoiconicity Macros

**Language / Domain**: Elixir / Erlang / Racket

**The Core Concept / "Did You Know?"**:
Elixir is homoiconic: Elixir code is represented internally as Elixir data structures (specifically, 3-element AST tuples). This property enables Elixir's powerful metaprogramming macro system, allowing developers to extend the language syntax at compile time.

Additionally, Elixir functions rely on pattern matching and **Guard Clauses** (`when`). Guards allow function dispatch based on runtime type assertions and expressions, but they strictly forbid side-effecting operations (like I/O or external function calls) to ensure pure, deterministic pattern matching during BEAM process execution.

**The Code Snippet**:
```elixir
defmodule CustomControlFlow do
  # Custom macro extending Elixir syntax at compile time: `unless_null`
  defmacro unless_null(val, do: block) do
    quote do
      case unquote(val) do
        nil -> :ok
        _val -> unquote(block)
      end
    end
  end
end

defmodule PatternGuardDemo do
  import CustomControlFlow

  # Pattern matching with type guard clause `is_integer/1` and constraint check
  def process_transaction(amount) when is_integer(amount) and amount > 0 do
    {:ok, "Processed positive integer deposit: $#{amount}"}
  end

  def process_transaction(amount) when is_binary(amount) do
    {:error, "String amounts not accepted! Expected integer representation."}
  end

  # Catch-all fallback match for invalid amounts (negative ints, floats, etc.)
  def process_transaction(_invalid_amount) do
    {:error, "Invalid transaction payload"}
  end

  def run do
    IO.inspect(process_transaction(500))
    IO.inspect(process_transaction("500"))
    IO.inspect(process_transaction(-50))

    # Using custom compile-time macro
    user_name = "Alice"
    unless_null user_name do
      IO.puts("Macro evaluated successfully for non-null user: #{user_name}")
    end
  end
end

PatternGuardDemo.run()
```

**Under the Hood / Why It Happens**:
Metaprogramming in Elixir operates directly on the Abstract Syntax Tree (AST):
- `quote` converts raw Elixir code blocks into AST tuples of the form `{function_name, metadata, arguments}`.
- `unquote` injects outside values or AST fragments into a quoted expression.

During compilation, BEAM expands macros into raw AST prior to bytecode generation.

Guard clauses (`when is_integer(x) and x > 0`) are restricted by the BEAM compiler to a predefined subset of safe BIFs (Built-in Functions). User-defined functions cannot be used inside guard clauses because BEAM pattern matching must be side-effect-free, exception-safe, and capable of evaluating in constant time $O(1)$ without crashing the process mailbox evaluator.

**Key Takeaway / Safe Pattern**:
Use pattern matching and guard clauses (`is_map/1`, `is_binary/1`, `when elem > 0`) instead of imperative `if/else` checks to construct clean, declarative function signatures. Use macros sparingly and only when plain functions or protocols cannot achieve the desired abstractions, as macros obscure stack traces and increase compile-time complexity.
