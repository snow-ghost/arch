# Design decisions without pattern theater

Use this reference when control flow, layering, or abstraction is under review. Start from the variation and ownership problem. Select a pattern only after the direct design stops being the clearest option.

## Contents

- [Decision sequence](#decision-sequence)
- [Conditional and switch choices](#conditional-and-switch-choices)
- [State and workflow choices](#state-and-workflow-choices)
- [Boundary choices](#boundary-choices)
- [Duplicate-code choices](#duplicate-code-choices)
- [Regex and parsing choices](#regex-and-parsing-choices)
- [Dependency versus local code](#dependency-versus-local-code)
- [Architecture decision note](#architecture-decision-note)

## Decision sequence

1. Name the behavior that changes.
2. Name who owns that behavior.
3. Decide whether the set of variants is closed or expected to grow.
4. Decide whether variation is data, behavior, temporal state, or an external protocol.
5. Check whether one direct function remains easy to test and read.
6. Compare the smallest direct design with one fitting abstraction.
7. Choose the option with lower total change cost, not more pattern vocabulary.

## Conditional and switch choices

### Keep direct conditionals

Keep an if/else chain when there are few branches, each condition is local, the set is stable, and a reader can see the policy in one place. Extract named predicates if conditions are hard to understand.

### Keep an exhaustive match or switch

Keep it when the language verifies exhaustiveness, the variant set is closed, and centralized handling is the intended ownership model. This is often strong for algebraic data types, enums, protocol messages, compiler phases, and serialization.

Do not replace compiler-checked exhaustiveness with runtime registration unless independent extension is a real requirement.

### Use a lookup table

Use a map or table when input selects static values or simple callables and missing-key behavior is explicit. Avoid it when conditions overlap, depend on ordered context, or need rich error handling hidden by lambdas.

### Use strategy

Use a strategy when behavior varies independently, variants have meaningful implementations, and callers should depend on one stable contract. Avoid one-class-per-branch when variants are tiny, fixed, and only used in one location.

### Use polymorphism

Move behavior to variants when those variants own the behavior and are more stable than a central dispatcher. Check serialization, visitor needs, cross-cutting operations, and discoverability. Adding many new operations to the same variants can make centralized functions clearer.

### Use chain of responsibility

Use a chain for independently composable handlers with clear ordering and stop/continue semantics. Do not hide a fixed business decision tree in a dynamic chain.

### Use a rules engine

Require externally managed or frequently changing rules, auditability, and a well-defined rule language. A rules engine is usually excessive for a stable handful of conditions.

## State and workflow choices

### Use explicit state with direct transitions

Use an enum plus one transition function for a small closed lifecycle. Validate illegal transitions and make effects explicit.

### Use a state machine

Use a state machine when legal transitions, events, guards, retries, or temporal behavior are the main source of defects. Define transition tables, invariants, and tests. Do not split a two-state flag into a framework.

### Use a pipeline

Use a pipeline when ordered stages are stable concepts that need independent composition, instrumentation, failure policy, or testing. Preserve cancellation, resource cleanup, and error semantics.

### Use events

Use events when producers should not know consumers and delayed or multi-consumer behavior is intentional. Account for delivery guarantees, ordering, idempotency, retries, observability, and schema evolution. Do not use events to avoid a straightforward in-process call.

## Boundary choices

### Use an adapter

Use one at a real external boundary: SDK, database, message broker, filesystem, operating system, clock, or unstable third-party API. Keep the adapter contract in the owning layer and translate errors and models deliberately.

Avoid wrapping a stable library one-for-one across the entire API. That creates a second API without isolation.

### Use a facade

Use a facade to expose a cohesive, smaller operation over a complex subsystem. Do not mirror every method.

### Use dependency inversion

Place the contract with the policy that needs it when this reverses an unwanted dependency or isolates a testable external effect. Do not create an interface solely because a concrete type exists.

### Split modules

Split when responsibilities have distinct reasons to change, ownership, lifecycle, security boundary, or deployment needs. File size alone is insufficient. Check whether the split introduces cycles or forces callers to orchestrate internals.

## Duplicate-code choices

Extract shared code when sites implement the same policy and should evolve together. Name the shared semantic operation, keep dependencies in the right direction, and preserve meaningful differences as parameters only when they represent stable variation.

Keep duplication when:

- examples or tests benefit from local readability;
- code belongs to independent bounded contexts;
- generated or vendored sources have different ownership;
- two similar implementations are already diverging for valid reasons;
- abstraction would need boolean flags, mode strings, or callbacks that recreate both originals.

Use clone detection to find candidates. Confirm change coupling before consolidation.

## Regex and parsing choices

Regex is a good fit for bounded lexical recognition, token extraction, local validation, and substitutions with a specified input language.

Prefer a parser, tokenizer, standard library, or protocol implementation when handling:

- nesting or recursive structure;
- escaping and quoting rules;
- URLs, email, dates, source code, or markup with a maintained standard parser;
- multiple encodings or Unicode normalization;
- adversarial untrusted input with backtracking risk;
- a grammar expected to evolve.

If regex remains, anchor intended full matches, bound input size, avoid catastrophic constructions, document the accepted language, and test near-misses and adversarial cases.

## Dependency versus local code

Add a dependency when it implements a nontrivial evolving standard or security-sensitive primitive better than the project can own, fits supported targets, and has acceptable maintenance, license, supply-chain, transitive, binary, and operational costs.

Keep local code when the operation is trivial and stable, domain-specific, or requires semantics a dependency would obscure. Never implement cryptography, complex protocol parsing, or security token validation casually.

## Architecture decision note

For material choices, record:

- context and current constraint;
- observed variation or boundary;
- direct option;
- abstraction or dependency option;
- evidence and trade-offs;
- decision and scope;
- verification and reversal path.

Avoid claiming future extensibility without a concrete expected change.
