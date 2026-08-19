# Evidence-first review method

Use this method for reviews, implementation planning, and post-generation cleanup. It separates verified defects from taste and keeps recommendations proportional to risk.

## Contents

- [1. Define the contract](#1-define-the-contract)
- [2. Build a local architecture map](#2-build-a-local-architecture-map)
- [3. Establish evidence](#3-establish-evidence)
- [4. Classify the observation](#4-classify-the-observation)
- [5. Prove the harm mechanism](#5-prove-the-harm-mechanism)
- [6. Assign severity](#6-assign-severity)
- [7. Select the correction](#7-select-the-correction)
- [8. Verify](#8-verify)
- [Finding template](#finding-template)

## 1. Define the contract

Capture before judging the code:

- requested outcome and allowed mutation scope;
- supported language, runtime, framework, and deployment targets;
- public APIs, persistence formats, wire protocols, and compatibility promises;
- repository rules, ownership boundaries, generated or vendored paths;
- performance, security, availability, and licensing constraints;
- commands the repository treats as authoritative.

If targets conflict, point to the conflicting files. Do not silently choose the newest setting.

## 2. Build a local architecture map

Trace only the affected path unless the evidence requires a wider map:

1. Entry point or caller.
2. Domain or application operation.
3. State and data ownership.
4. External boundary such as database, network, file system, clock, or process.
5. Error and cancellation path.
6. Tests and configuration.
7. Imports across architectural boundaries.

Search by behavior as well as symbol. Useful search keys include constants, protocol fields, error messages, schema names, endpoint paths, serialization keys, and test fixtures.

Record search coverage in one sentence. Example: "Searched src, tests, manifest, and lockfile for token parsing and found one canonical helper used by three callers."

Keep this map internal when prose is clearer. When the user requests a view or several boundaries, owners, states, or interactions are hard to verify linearly:

1. State the question, snapshot, scope, viewpoint, and whether the view is observed as-is or proposed to-be.
2. Choose one fitting view and zoom. Do not combine a dependency graph, sequence, data flow, and state model into one overloaded diagram.
3. Aggregate symbols by demonstrated responsibility, ownership, runtime, data, trust, external, or public-contract boundary.
4. Assign evidence IDs to material nodes and edges. Map each ID to a path, symbol, manifest, configuration entry, test, or runtime trace.
5. Mark relationships as observed, inferred, proposed, or unknown. Keep as-is and to-be views separate.

Use [architecture-views.md](architecture-views.md) for notation and rendering rules. A complete-looking diagram is not evidence that dynamic wiring, reflection, generated configuration, or runtime routing has been resolved.

## 3. Establish evidence

Prefer evidence in this order:

1. Reproducible behavior, failing test, compiler or runtime result.
2. Repository contract, manifest, lockfile, architecture rule, or supported-version declaration.
3. Existing implementation and call graph.
4. Repository-native static analysis, type checking, dependency or clone report.
5. Version history or co-change evidence.
6. Current official upstream documentation, advisory, registry, or release note.
7. A well-scoped external study.
8. An inference labeled with its assumptions.

A linter warning or metric is evidence of a signal, not automatically evidence of harm. A blog post or popularity count does not establish maintenance status.

## 4. Classify the observation

Use one primary class:

### Duplicate behavior

Confirm semantic overlap. Similar syntax can implement different policies; different syntax can duplicate the same policy.

Investigate:

- whether both sites should change for the same business event;
- whether they have already diverged;
- whether one is generated, vendored, compatibility-specific, or intentionally isolated;
- whether extracting shared code would create an incorrect dependency direction.

Refactor when one responsibility has multiple uncontrolled sources of truth. Keep duplication when independent change, isolation, or boundary ownership is more valuable.

### Reinvented capability

Compare the local implementation with:

- an existing repository abstraction;
- the supported standard library;
- an already-approved dependency;
- a verified external dependency.

Check semantic details: input grammar, Unicode, time zones, normalization, escaping, cancellation, resource limits, platform behavior, security, and error contracts. "A library exists" is not enough.

### Dependency or API status

Separate these claims:

- a newer version exists;
- the current version is outside project policy;
- the current version is unsupported;
- the package is deprecated or archived;
- an API is deprecated for the target runtime;
- a reachable vulnerability affects the project.

Each needs different evidence and urgency. Verify the declared and resolved versions. Inspect the replacement rather than performing a name-only edit.

### Boundary or coupling problem

Name the actual edge and cost:

- domain code depends on transport or persistence details;
- a cycle prevents independent build, test, or deployment;
- mutable state has multiple owners;
- a change repeatedly spans unrelated modules;
- an external API leaks throughout the core;
- hidden global behavior prevents isolation.

Do not infer a boundary violation from directory names alone.

### Concentrated complexity

Inspect decision points, nesting, state mutation, error paths, and responsibility count. Ask whether a reader can predict behavior and test branches locally. A long function that implements a linear protocol can be safer than five indirection layers.

### Brittle parser or workaround

Define the accepted input language and threat model. Regex is appropriate for many bounded regular languages. Prefer a standard or specification-aware parser for nested, escaped, recursively structured, security-sensitive, or evolving formats.

For untrusted inputs, examine catastrophic backtracking, input bounds, timeouts, Unicode and normalization, and partial-match behavior.

### Unjustified abstraction

Find the current variation or boundary served by each interface, factory, wrapper, registry, provider, or generic framework. If the only implementation and caller change together and no boundary is isolated, direct code may be clearer.

## 5. Prove the harm mechanism

Use at least one concrete mechanism:

- correctness failure or uncovered input;
- security exposure or advisory applicability;
- incompatible runtime or unsupported API;
- two sources of truth that must change together;
- dependency cycle or forbidden edge;
- hidden side effect or ambiguous ownership;
- branch or state space that resists focused tests;
- performance or resource regression;
- transitive, operational, licensing, or supply-chain burden;
- review and change cost demonstrated by history or structure.

Avoid claims such as "not clean", "not SOLID", "too old", or "spaghetti" without the mechanism.

## 6. Assign severity

Use the highest applicable level:

- **Critical:** likely exploitable security issue, data loss, severe compatibility break, or build/runtime failure on a supported target.
- **High:** reproducible correctness failure, supported-version failure, architectural dependency that blocks safe change, or reachable vulnerable/deprecated behavior with material impact.
- **Medium:** demonstrated divergence risk, difficult-to-test decision concentration, harmful coupling, or brittle handling with a plausible failure path.
- **Low:** localized maintainability cost with evidence and a small correction.
- **Observation:** signal, uncertainty, or optional improvement without enough evidence for a defect.

Severity is impact multiplied by likelihood and exposure, not file length or metric value. State confidence separately as high, medium, or low.

## 7. Select the correction

Choose the smallest option that removes the demonstrated mechanism:

1. Delete dead or redundant code.
2. Reuse an existing repository operation.
3. Replace a local implementation with the supported standard library.
4. Simplify data flow or control flow.
5. Extract a semantic function or module.
6. Put an adapter at an external boundary.
7. Introduce a pattern only for a current variation or state problem.
8. Add or upgrade a dependency after a full fit check.
9. Redesign a boundary only when local corrections cannot restore ownership.

Describe at least one simpler alternative and why it does not solve the problem before recommending a broad rewrite.

## 8. Verify

Match verification to the mechanism:

- regression test for the failing or divergent behavior;
- property or fuzz test for parsers and state transitions;
- type or compilation check for API migrations;
- architecture test or dependency graph for boundaries;
- static analysis for deprecated symbols;
- dependency audit plus reachability or usage inspection for advisories;
- benchmark or profile for performance claims;
- before/after clone, complexity, or coupling delta for structural claims.

A green test suite lowers uncertainty; it does not prove that architecture or dependency migration is safe.

## Finding template

Use this compact structure:

### [Severity] Short title

- Location: file and line or symbol.
- Evidence: reproducible fact, tool output, repository contract, or official source.
- Mechanism: how this causes correctness, security, compatibility, or change cost.
- Correction: smallest fitting change.
- Verification: exact check.
- Confidence: high, medium, or low.

When reviewing a diff, anchor findings to changed lines when possible. Do not hide material issues in a general summary.
