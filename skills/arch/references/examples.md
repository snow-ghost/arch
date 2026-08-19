# Intervention examples

These examples calibrate decisions. Match the evidence pattern, not the surface syntax.

## Contents

- [Intervene: repository duplicate](#intervene-repository-duplicate)
- [Accept: similar boundary code](#accept-similar-boundary-code)
- [Intervene: structured data parsed by regex](#intervene-structured-data-parsed-by-regex)
- [Accept: bounded regex](#accept-bounded-regex)
- [Intervene: open behavior switch](#intervene-open-behavior-switch)
- [Accept: closed exhaustive match](#accept-closed-exhaustive-match)
- [Intervene: stale API on supported target](#intervene-stale-api-on-supported-target)
- [Investigate: old pinned dependency](#investigate-old-pinned-dependency)
- [Reject: hallucinated package](#reject-hallucinated-package)
- [Reject: metric gaming](#reject-metric-gaming)
- [Intervene: forbidden dependency direction](#intervene-forbidden-dependency-direction)
- [Accept: small explicit Go switch](#accept-small-explicit-go-switch)
- [Investigate: proposed external retry library](#investigate-proposed-external-retry-library)
- [Example review finding](#example-review-finding)
- [Example accepted choice](#example-accepted-choice)
- [Example insufficient claim](#example-insufficient-claim)
- [Render: cross-boundary checkout flow](#render-cross-boundary-checkout-flow)
- [Investigate: reflective handler wiring](#investigate-reflective-handler-wiring)
- [Skip: diagram for a local helper](#skip-diagram-for-a-local-helper)

## Intervene: repository duplicate

A generated handler validates a customer identifier with new local logic. Repository search finds a domain validator used by imports and batch jobs. The two implementations disagree on Unicode normalization.

Decision: use or extend the domain validator. The demonstrated problem is two sources of truth with existing semantic divergence. Add a handler-level regression test for the normalized form.

## Accept: similar boundary code

Two service adapters translate nearly identical response fields from different vendors. They belong to independent integration packages, have different error semantics, and do not change together.

Decision: keep the local duplication. A shared mapper would couple independent boundaries and hide vendor-specific policy. A clone detector result is only an observation.

## Intervene: structured data parsed by regex

A URL allowlist splits and matches hostnames with one regex. It mishandles user information, encoded delimiters, IPv6 literals, and default ports. The supported standard library has a URL parser.

Decision: parse with the standard library, normalize the relevant components, then apply an explicit policy. Test adversarial and near-match URLs. The reason is grammar and security behavior, not a blanket regex ban.

## Accept: bounded regex

A command validates an ASCII build tag defined by the repository as one to twelve lowercase letters, digits, or hyphens. The regex is anchored, the input length is bounded, and tests cover valid and invalid cases.

Decision: keep it. A parser abstraction or dependency would add cost without solving a failure.

## Intervene: open behavior switch

Several modules switch on a payment provider. Adding a provider requires editing five dispatchers, and provider-specific retry and signing behavior is mixed into each.

Decision: define one provider contract owned by the payment boundary and implement provider strategies. Migrate one dispatcher at a time with contract tests. The variation and coupled change justify the abstraction.

## Accept: closed exhaustive match

A Rust reducer matches every variant of a closed domain enum, and the compiler rejects a missing variant. All transitions are visible in one pure function.

Decision: keep the match. Replacing it with trait objects would lose exhaustiveness and scatter a stable state transition.

## Intervene: stale API on supported target

The manifest targets a runtime where an API carries an official deprecation and the replacement is available. Static analysis identifies reachable calls, and official migration notes show an error-semantic change.

Decision: migrate deliberately, translate the changed error behavior, and run compatibility tests. Do not perform a name-only replacement.

## Investigate: old pinned dependency

A lockfile contains a package released several years ago. The project supports an old runtime, applies vendor patches, and has no stated update policy.

Decision: do not label it obsolete yet. Determine declared constraints, support policy, upstream status, known vulnerabilities, and why the patch exists. Age alone is insufficient.

## Reject: hallucinated package

An agent proposes installing a plausible package name that is absent from the official registry and has no upstream repository.

Decision: do not install it. Search repository, standard library, and verified packages again. Treat the name as untrusted generated text.

## Reject: metric gaming

A function exceeds a complexity threshold. A proposed change moves each branch into a class and factory, increasing files and registrations while preserving the same decision structure.

Decision: reject the change unless responsibilities or test isolation improve. The score moved; the complexity mechanism did not.

## Intervene: forbidden dependency direction

A domain pricing module imports an HTTP request type for headers. Existing architecture rules require transport independence, and unit tests now need a web framework fixture.

Decision: translate headers at the transport adapter into a domain request value. Add an import-boundary check. The correction restores ownership and test isolation.

## Accept: small explicit Go switch

A Go function maps three stable wire values to internal constants, returns an error for unknown input, and has table-driven tests.

Decision: keep the switch. A registry and interfaces would obscure a closed conversion without reducing risk.

## Investigate: proposed external retry library

The repository has one local retry loop, but requirements for jitter, cancellation, idempotency, and server hints are unclear.

Decision: establish semantics and search existing helpers first. Compare the standard library, approved dependencies, and one verified package. Do not recommend a dependency until behavior and ownership costs are known.

## Example review finding

### Medium: duplicate normalization can diverge

- Location: application/import_customer.py, normalize_id.
- Evidence: domain/customer_id.py already defines normalization; the new function differs for Unicode composed forms.
- Mechanism: imports and API writes can persist different identifiers for the same customer.
- Correction: call the domain constructor from both paths and remove the local copy.
- Verification: add one composed/decomposed Unicode regression case to both entry-point tests.
- Confidence: high.

## Example accepted choice

Accepted: the exhaustive status match remains. The enum is closed, the compiler checks new variants, and the reducer is pure and covered by transition tests. No registry or state-pattern layer is warranted.

## Example insufficient claim

Insufficient: "This file has 400 lines and violates clean architecture."

Required next evidence: responsibilities, change history, dependency direction, hard-to-test behavior, or a reproducible failure. Size alone does not establish a defect.

## Render: cross-boundary checkout flow

Repository evidence shows an HTTP adapter calling one checkout application service, which owns the transaction, invokes a payment-port adapter, and persists through an order repository. A component graph answers ownership and dependency direction; a separate sequence view answers payment ordering and failure handling.

Decision: aggregate by those responsibilities, label dependency and call edges, and attach evidence IDs to the route, service, port binding, repository, and tests. Keep the observed flow separate from any proposed outbox or retry design.

## Investigate: reflective handler wiring

Static code shows a controller calling a handler registry, but handlers are selected from generated configuration through reflection. The generated registry and runtime trace are unavailable.

Decision: draw the verified controller-to-registry slice, mark the dispatch edge unknown, and request the generated artifact or trace. Do not invent handlers to make the graph look complete.

## Skip: diagram for a local helper

A private pure helper has one caller, no external interaction, no state, and no architectural boundary. A manager requests C4, DFD, and a sequence diagram for it.

Decision: skip the diagrams and provide a one-sentence text map. Visual notation would add ceremony without making a material relationship easier to verify.
