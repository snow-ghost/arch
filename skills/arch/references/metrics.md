# Maintainability metrics as diagnostic signals

Metrics help locate review targets and compare a change with its baseline. They do not produce an objective cleanliness score.

## Contents

- [Principles](#principles)
- [Useful signals](#useful-signals)
- [Cross-version structural churn](#cross-version-structural-churn)
- [Structural erosion indicator](#structural-erosion-indicator)
- [Verbosity indicator](#verbosity-indicator)
- [Recommended review table](#recommended-review-table)
- [Quality gates](#quality-gates)
- [Anti-gaming checks](#anti-gaming-checks)

## Principles

- Prefer repository-local trends and before/after deltas.
- Measure the affected path, then widen only when comparison requires it.
- Combine a structural signal with code reading, tests, and change history.
- Keep generated, vendored, test, migration, and configuration code distinguishable.
- Record tool, version, configuration, exclusions, and baseline.
- Do not turn a research threshold into a universal gate.
- Reject improvements that only redistribute complexity.

## Useful signals

### Size and churn

Track total and changed lines, function or method size, public surface, number of files, and dependency count. Combine size with churn or ownership: large stable tables differ from frequently edited policy code.

A growing diff can indicate scope expansion. It can also reflect tests, types, or explicit error handling. Inspect composition before judging it.

### Cyclomatic complexity

Cyclomatic complexity approximates the number of independent control-flow paths. Use it to identify functions that may need focused tests or decomposition.

Do not assume every branch is equally difficult. A flat exhaustive match can be easier to reason about than implicit dispatch across many classes.

### Cognitive complexity

Cognitive-complexity tools approximate nesting and human control-flow burden. Values depend on tool rules and language. Use one configured implementation consistently; do not compare raw scores across tools as if equivalent.

### Duplication

Token- or AST-based clone tools find candidate blocks. Review semantic ownership and co-change. Many clones are harmless or intentionally isolated; extraction can create coupling.

Report clone location and the policy that might diverge. Do not report a percentage alone.

### Dependency graph

Inspect cycles, forbidden direction, fan-in, fan-out, unstable dependencies, and public boundary leakage. High fan-in can indicate a stable core; high fan-out can be normal orchestration. A cycle is most important when it impedes ownership, build, test, initialization, or deployment.

### Change coupling and hotspots

Version history can reveal files that change together and combine high churn with complexity. Use sufficient history and account for bulk formatting, generated changes, renames, and repository age.

Change coupling supports a maintenance claim more directly than static similarity, but it remains observational.

### API and dependency surface

Count direct and transitive dependencies, exposed types from external packages, public entry points, and supported runtime combinations. Smaller is not automatically better; one well-maintained standards implementation can replace risky local code.

### Testability signals

Inspect branch coverage, mutation results, flaky tests, fixture setup, hidden global state, and time or network dependence. Coverage shows execution, not assertion quality. Mutation testing can be expensive and language support varies.

## Cross-version structural churn

Build aligned architecture models before calculating a graph delta. Use the same scope, viewpoint, zoom, node identity, relation semantics, exclusions, and analyzer configuration for both snapshots. Map moves and renames by demonstrated responsibility and contract continuity, not path equality.

When mappings are stable, optional set-based indicators are:

    node churn = |N_base symmetric_difference N_target| / |N_base union N_target|
    relation churn = |E_base symmetric_difference E_target| / |E_base union E_target|

Define empty-set handling and exclude unresolved mappings or report a bounded range. These indicators measure structural difference. They do not measure degradation, rationale, runtime semantics, risk, or value.

Prefer a per-axis delta profile and gates on new forbidden edges, cycles, or contract breaks. Require repository-owned axes, weights, tool versions, baseline, and ratcheting policy before emitting one composite CI score. See [architecture-comparison.md](architecture-comparison.md) for the full comparison contract.

## Structural erosion indicator

For longitudinal agent runs, one research metric defines complexity mass per function as:

    mass = cyclomatic_complexity * sqrt(source_lines)

Structural erosion is the share of total mass contributed by functions whose cyclomatic complexity exceeds 10.

This combines size and complexity and can expose concentration that tests miss. The threshold and formula came from a particular Python benchmark; use them for comparison or research replication, not as a language-neutral release gate.

## Verbosity indicator

One research benchmark estimates verbosity as the union of:

- lines matched by a catalog of structural anti-pattern queries; and
- lines belonging to detected clone blocks;

divided by source lines.

This can track iterative drift under one fixed detector configuration. It is sensitive to query coverage, clone thresholds, generated code, comments, and language grammar. Inspect every flagged category before acting.

## Recommended review table

For a material refactor, capture only relevant metrics:

| Signal | Baseline | Candidate | Interpretation |
| --- | ---: | ---: | --- |
| Behavior tests | result | result | Compatibility evidence |
| Changed lines | value | value | Scope and migration cost |
| Concentrated paths | value | value | Decision distribution |
| Duplicate semantic policies | value | value | Sources of truth |
| Boundary violations or cycles | value | value | Dependency direction |
| Direct/transitive dependencies | value | value | Ownership and supply chain |
| Public API changes | value | value | Consumer migration |

Explain why each delta matters. Omit rows that do not answer the decision.

## Quality gates

Introduce a gate only when:

1. the measured failure matters to this repository;
2. the tool is reproducible in CI;
3. exclusions and ownership are defined;
4. current baseline and ratcheting policy are explicit;
5. developers can diagnose and correct failures;
6. the gate cannot be passed by moving complexity elsewhere;
7. false positives have an appeal or suppression path.

Prefer ratcheting new or changed code to immediately failing an inherited codebase. Review the gate after tool or language upgrades.

## Anti-gaming checks

After an apparent metric improvement, ask:

- Did the branch count move into dispatch tables, decorators, generated classes, or callbacks?
- Did the file count and navigation cost increase?
- Did the public or dependency surface grow?
- Did tests become less direct?
- Did one source of truth become several registrations?
- Did performance, allocations, or error semantics change?
- Can a new maintainer still trace one request end to end?

Report a neutral result when the metric improves but total design cost does not.
