---
name: arch
description: Review, plan, implement, or visualize software changes with evidence-first architectural oversight. Use when generated or existing code may duplicate repository behavior, reinvent a standard or maintained library, depend on stale or deprecated APIs, cross architectural boundaries, accumulate cycles or concentrated complexity, parse structured data with brittle regexes, grow conditionals or switches, introduce unnecessary abstractions, or require a cleaner language-idiomatic design. Also use for dependency modernization, architecture reviews, refactoring plans, maintainability audits, and repository-grounded architecture maps, dependency graphs, process or sequence views, data-flow diagrams, state views, ownership trees, or current-versus-proposed diagrams. Do not use to demand patterns, diagrams, or low metric scores without a demonstrated maintenance, correctness, security, or evolution need.
---

# Architecture Guard

Keep code changes small, repository-aware, current for the project's supported versions, and easy to evolve. Treat architecture as a set of verified constraints and change costs, not a preference for more layers.

## Start with concrete requests

- "Before adding this parser, find an existing repository or standard-library implementation."
- "Review this diff for duplicated behavior, deprecated APIs, boundary violations, and accidental complexity."
- "Replace this giant conditional only if a simpler data model or fitting pattern reduces a real change cost."
- "Modernize these dependencies without exceeding the repository's runtime and compatibility targets."
- "Check whether this regex is a bounded recognizer or an unsafe substitute for a structured parser."
- "Audit this generated module, but keep an exhaustive match if it is the clearest closed-world design."
- "Map the affected checkout architecture at component level and show the payment sequence with repository evidence."

## Establish authority and scope

1. Read repository instructions, manifests, lockfiles, build configuration, tests, and nearby code before proposing a design.
2. Determine the requested mode: review, implementation, modernization, or architecture planning.
3. Record supported runtimes, frameworks, compatibility promises, public APIs, generated-code boundaries, and allowed scope. Treat repository configuration as authoritative until the user says otherwise.
4. Ask only when a missing choice changes behavior, compatibility, dependency policy, or public architecture. Otherwise make a reversible assumption and label it.
5. Read [review-method.md](references/review-method.md) before a substantive audit or implementation.

## Map before changing

Build the smallest useful map of the affected path:

1. Locate callers, implementations, tests, configuration, data ownership, and error handling.
2. Search the repository for names, literals, schemas, protocols, and equivalent behavior—not only identical text.
3. Trace imports and dependency direction across the touched boundary.
4. Inspect history or blame only when it can explain a compatibility workaround or coupled change.
5. Run repository-native checks first. Do not install a new analyzer merely to complete an ordinary review.

State what was searched. Absence of evidence is not proof that no reusable implementation exists.

## Render architecture views when useful

1. Draw only when a relationship is materially easier to verify visually or the user requests a view.
2. State the question, snapshot, affected scope, viewpoint, and whether the view is observed as-is or proposed to-be.
3. Select the fitting view: context or component graph, dependency graph, sequence, data flow, process flow, state, ownership tree, deployment, or IDEF0 when explicitly required.
4. Aggregate files and symbols into nodes with demonstrated responsibility, ownership, runtime, data, external, trust, or public-contract boundaries.
5. Give material nodes and edges stable IDs and map them to paths, symbols, configuration, tests, or runtime evidence.
6. Distinguish observed, inferred, proposed, and unknown relationships. Never fill a dynamic edge merely to complete the picture.
7. Keep observed and proposed architecture in separate views. Skip a diagram when a compact text map is clearer.
8. Use the repository's established format first; otherwise prefer portable Mermaid flowchart, sequence, or state syntax without adding a dependency.

Read [architecture-views.md](references/architecture-views.md) before producing a diagram or broad architecture map. Follow its zoom, evidence, notation, and IDEF0 constraints.

## Apply the reuse ladder

Prefer the first option that is semantically correct and cheaper to own:

1. Reuse or extend an existing repository abstraction.
2. Use the language or framework standard library.
3. Use an already-approved direct dependency.
4. Add a maintained external dependency after verifying its real package identity, support status, license, security posture, runtime compatibility, transitive cost, and API fit.
5. Write a focused local implementation when the behavior is trivial, domain-specific, performance-sensitive, security-sensitive, or cheaper than a dependency.

Do not count line deletion alone as value. Compare total ownership cost, behavior, failure modes, and migration risk. Never install a model-suggested package before confirming it in the official registry and upstream repository.

## Diagnose with evidence

Classify a suspected problem, then prove its mechanism:

- **Duplicate or reinvention:** show the equivalent behavior and the maintenance divergence it can cause.
- **Dependency or API obsolescence:** show the project's target version and an official deprecation, support, vulnerability, or migration source.
- **Boundary or coupling failure:** show the dependency edge, cycle, unstable direction, hidden side effect, or coupled change.
- **Concentrated complexity:** identify the decision density, mixed responsibilities, or hard-to-test paths—not just a threshold violation.
- **Brittle parsing or workaround:** identify the valid input grammar, adversarial case, platform assumption, or bypassed API.
- **Unjustified abstraction:** identify layers, indirection, extension points, or dependencies that do not serve a current variation or boundary.

For every finding provide location, evidence, harm mechanism, smallest fitting correction, and verification. If one is missing, report an observation or question rather than a defect. Follow the severity model in [review-method.md](references/review-method.md).

## Choose the smallest fitting design

Keep a branch, switch, match, regex, duplicate block, or old dependency when it is the clearest compatible choice and its risks are controlled.

When change is justified:

- replace static value selection with data only when behavior is truly data-driven;
- extract a function when it creates one responsibility or reusable semantic operation;
- use a strategy when behavior varies independently and new variants are expected;
- use a state machine when legal transitions and temporal state are the problem;
- use an adapter at a real external boundary;
- use a pipeline when stable stages need independent composition;
- use polymorphism only when variant-owned behavior is more stable than centralized logic.

Read [design-decisions.md](references/design-decisions.md) before recommending a named pattern or broad structural rewrite. Describe the variation, ownership boundary, and simpler rejected alternative. A pattern name is not evidence.

## Check dependencies and APIs

1. Read the manifest and lockfile together; distinguish declared, resolved, direct, transitive, runtime, development, and optional dependencies.
2. Determine the repository's supported runtime before calling a version old.
3. Verify current status in official documentation, release notes, registry metadata, security advisories, and the upstream repository. Browse when status could have changed.
4. Inspect replacement signatures and semantics. A deprecation rename can still change arguments, return values, errors, or performance.
5. Prefer incremental updates and preserve lockfile determinism. Use tests plus static analysis; passing tests alone do not establish upgrade safety.
6. Read the relevant ecosystem section in [language-tooling.md](references/language-tooling.md).

## Use metrics as signals

Prefer before/after deltas in the touched area over universal scores. Useful signals include changed lines, function size, cyclomatic or cognitive complexity, duplicated blocks, dependency cycles, fan-in/fan-out, public surface, and change coupling.

Do not fail a change solely because a metric crosses a generic threshold. Do not lower a score by moving branches into more files or adding layers. Read [metrics.md](references/metrics.md) before introducing a threshold, dashboard, or quality gate.

## Respect language semantics

Apply ecosystem conventions instead of translating one architecture style everywhere:

- Prefer exhaustive matches for closed variants in languages that verify exhaustiveness.
- Prefer small explicit interfaces and straightforward control flow in Go; avoid Java-shaped interface hierarchies.
- Use type-aware deprecation checks in dynamic ecosystems when available.
- Account for ABI, compiler, build-matrix, and platform constraints in C and C++ upgrades.
- Use JVM or .NET architecture tests for important existing boundaries, not to justify a new layer by themselves.

Use [language-tooling.md](references/language-tooling.md) for current command examples, then confirm them against repository versions.

## Verify proportionally

After an authorized change:

1. Run the narrowest relevant tests, type checks, linters, build, and security or dependency checks already configured.
2. Add a focused regression test for the demonstrated failure mode.
3. Compare behavior and structural signals before and after.
4. Check public API, serialization, error, concurrency, performance, and migration effects where relevant.
5. Report commands and outcomes exactly. Separate checks not run from checks that passed.

For review-only requests, do not edit. For implementation requests, keep the diff inside the demonstrated problem and preserve unrelated user changes.

## Report decisions

Lead with the result.

For a review, list findings by severity. Each finding must include:

- location;
- evidence and confidence;
- concrete failure or maintenance mechanism;
- smallest correction;
- verification plan.

Then list accepted choices that may look suspicious but are justified, followed by open questions and checks not run. Say explicitly when no actionable architectural defect was found.

For an implementation, report:

- reuse and dependency decision;
- changed behavior and files;
- verification results;
- residual risk or compatibility constraint.

See [examples.md](references/examples.md) when deciding whether to intervene, accept, or investigate.

For an architecture view, report its question and scope, the diagram or reason for skipping it, an evidence index, inferred edges and unknowns, and findings supported by the view.

## Enforce guardrails

- Do not perform speculative rewrites or widen scope to unrelated architecture.
- Do not ban regex, switches, conditionals, duplication, dependencies, or old versions categorically.
- Do not label a project unmaintained from age or release cadence alone.
- Do not introduce a library for a trivial stable operation without an ownership advantage.
- Do not hide behavior changes behind a cleanup label.
- Do not invent packages, APIs, repository conventions, tool output, benchmark results, or migration guarantees.
- Do not claim cleaner architecture when complexity merely moved.
- Do not treat generated or vendored code as hand-maintained code without checking its source of truth.
- Do not treat a diagram as proof without repository evidence or turn every file, class, or function into an architectural node.
- Do not mix observed and proposed edges or present inferred runtime wiring as verified.

## Load references selectively

- Always use [review-method.md](references/review-method.md) for substantive work.
- Use [design-decisions.md](references/design-decisions.md) for conditionals, abstraction, patterns, or boundary redesign.
- Use [language-tooling.md](references/language-tooling.md) for ecosystem tools, dependencies, deprecations, and language idioms.
- Use [metrics.md](references/metrics.md) for measurement and quality gates.
- Use [examples.md](references/examples.md) for ambiguous intervention decisions.
- Use [sources.md](references/sources.md) when explaining the empirical basis or updating this skill.
- Use [architecture-views.md](references/architecture-views.md) for architecture maps, dependency graphs, sequence, process, data-flow, state, ownership, deployment, or IDEF0 views.
