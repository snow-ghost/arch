# Compare architecture across versions

Use this reference to compare two releases, tags, commits, branches, working-tree snapshots, or supplied source trees. Compare architecture at one declared viewpoint and zoom. Do not substitute file churn for architectural change.

## Contents

- [Distinguish change from drift](#distinguish-change-from-drift)
- [Establish the comparison contract](#establish-the-comparison-contract)
- [Resolve immutable inputs](#resolve-immutable-inputs)
- [Build aligned architecture models](#build-aligned-architecture-models)
- [Compare decision-relevant axes](#compare-decision-relevant-axes)
- [Measure without false precision](#measure-without-false-precision)
- [Classify scale and conformance](#classify-scale-and-conformance)
- [Render a delta view](#render-a-delta-view)
- [Verify both snapshots](#verify-both-snapshots)
- [Report the comparison](#report-the-comparison)
- [Enforce comparison guardrails](#enforce-comparison-guardrails)
- [Primary sources](#primary-sources)

## Distinguish change from drift

Use three separate concepts:

- **Architecture change:** an observed difference between two implementation snapshots at the same abstraction level.
- **Conformance change:** a difference in how either snapshot satisfies a declared architecture rule, required relation, ownership policy, or accepted model.
- **Drift finding:** a new or worsened mismatch with that declared intent, supported by a concrete maintenance, correctness, security, compatibility, or evolution mechanism.

Do not call every changed node or edge drift. A large intentional migration can preserve architectural integrity. A one-line import can create a material conformance regression.

When no intended architecture is available, report an implementation change profile and mark conformance as **not assessed**. Do not reconstruct intent from directory names or personal preference.

## Establish the comparison contract

Record these inputs before inspecting deltas:

| Field | Required evidence |
|---|---|
| Baseline | immutable commit, tag resolved to a commit, or content-addressed snapshot |
| Target | immutable commit, tag resolved to a commit, or content-addressed snapshot |
| Range semantics | endpoint-to-endpoint or merge-base-to-target |
| Scope | system, service, package, scenario, and explicit exclusions |
| Viewpoint | component, dependency, runtime, data, state, deployment, ownership, or public contract |
| Zoom | identical aggregation rule for both snapshots |
| Runtime targets | language, framework, platform, deployment, and compatibility targets for each snapshot |
| Architecture authority | ADRs, architecture docs, dependency rules, CODEOWNERS, schemas, tests, or approved exceptions |
| Tool contract | tool and version, configuration, path rules, generated-code policy, and commands |

Stop and ask when the two refs, range semantics, or requested scope are ambiguous. Continue with labeled assumptions when the missing detail only limits confidence.

Treat a runtime, framework, deployment, or analyzer change as part of the result. Do not silently normalize it away.

## Resolve immutable inputs

For Git inputs, resolve refs before comparing:

~~~sh
git rev-parse --verify --end-of-options '<baseline>^{commit}'
git rev-parse --verify --end-of-options '<target>^{commit}'
~~~

Use the resulting commit IDs in subsequent commands. Record tag-to-commit resolution. Distinguish these comparisons:

- **git diff base target** compares two endpoints;
- **git diff base...target** compares the merge base with the target.

Use endpoint comparison for two releases unless the user asks what one branch introduced since divergence.

Start with a rename-aware inventory:

~~~sh
git diff --find-renames --name-status <base-sha> <target-sha> -- <scope>
git diff --find-renames --stat <base-sha> <target-sha> -- <scope>
git log --oneline --no-merges <base-sha>..<target-sha> -- <scope>
~~~

Treat rename detection as evidence of file continuity, not proof that architectural responsibility stayed the same. Inspect contracts, owners, callers, and dependencies before mapping a moved file to the same component.

For two directories, record their origin and content digest and use **git diff --no-index** only as a change inventory. Its exit status is nonzero when differences exist. Do not present a mutable working tree as a reproducible release snapshot without recording its status and patch digest.

Prefer tree-level Git inspection when possible. When an analyzer or build requires checked-out files, create separate detached temporary worktrees without disturbing the user's current tree:

~~~sh
git worktree add --detach <temp-base> <base-sha>
git worktree add --detach <temp-target> <target-sha>
~~~

Use explicit temporary paths. Remove only worktrees created for the comparison with **git worktree remove** after preserving required reports. Do not reuse build outputs, dependency directories, caches, or generated artifacts across snapshots when they could affect results.

## Build aligned architecture models

Build the baseline and target models independently before calculating a delta:

1. Apply the same scope, viewpoint, zoom, evidence rules, and exclusions.
2. Use repository-native architecture or dependency reports when both snapshots support the same configuration.
3. Aggregate code by demonstrated responsibility, ownership, runtime, data, trust, external, or public-contract boundary.
4. Assign stable logical IDs to material nodes and typed relations.
5. Map renamed or moved elements across versions only when responsibility and contract continuity are evidenced.
6. Mark split, merge, redirect, and unresolved mappings explicitly.
7. Record dynamic, generated, reflective, plugin, and configuration-driven edges as inferred or unknown unless runtime or generated evidence resolves them.

Use a mapping table:

| Logical ID | Baseline evidence | Target evidence | Mapping basis | Status |
|---|---|---|---|---|
| N1 | path, symbol, config | path, symbol, config | same public contract | unchanged |
| N2 | old path and owner | new path and owner | verified rename | moved |
| N3 | one component | two components | responsibility split | split |
| E1 | typed relation | typed relation | same endpoints and semantics | unchanged |
| E2 | absent | target import and call | new relation | added |

Keep unknown mappings out of numeric distance calculations or report a bounded range. Do not force a one-to-one mapping to make graphs comparable.

## Compare decision-relevant axes

Inspect only axes that answer the user's question:

| Axis | Compare |
|---|---|
| Components | added, removed, moved, split, merged, or responsibility changes |
| Relations | added, removed, redirected, or retyped imports, calls, events, and data flows |
| Boundaries | new crossings of module, team, trust, process, deployment, or external-system boundaries |
| Ownership and state | owner changes, multiple writers, persistence movement, transaction ownership |
| Runtime scenarios | ordering, retries, cancellation, errors, compensation, dynamic dispatch |
| Public contracts | APIs, schemas, protocols, serialization, compatibility promises |
| Dependencies and targets | direct and transitive packages, runtimes, platforms, build or deployment topology |
| Conformance controls | forbidden or required edges, architecture tests, waivers, and ADR changes |

Separate source topology from runtime behavior. An import delta does not prove a runtime call; a passing behavior test does not prove dependency conformance.

Record material deltas as **added**, **removed**, **redirected**, **moved**, **split**, **merged**, **semantics changed**, **unchanged**, or **unknown**.

## Measure without false precision

Prefer a profile of relevant deltas:

- material nodes and relations added, removed, or redirected;
- boundary crossings and dependency cycles introduced or removed;
- public contracts, data owners, processes, stores, and external systems changed;
- conformance regressions, resolved violations, and accepted exceptions;
- exact before/after values from one reproducible repository-native analyzer.

When stable mapping exists, optionally report set-based structural churn:

    node churn = |N_base symmetric_difference N_target| / |N_base union N_target|
    relation churn = |E_base symmetric_difference E_target| / |E_base union E_target|

Define node identity, relation type, exclusions, empty-set handling, and unknown mappings. Call these values node or relation churn, not “percent architecture degradation.” They measure graph difference and ignore rationale, runtime semantics, risk, and change value.

Do not emit a built-in weighted architecture score. If the repository requires one CI value, require explicit axes, weights, baseline, ratcheting policy, tool versions, suppressions, and ownership. Prefer gates on new forbidden edges, cycles, or contract breaks over a universal distance threshold.

## Classify scale and conformance

Assign one change scale at the selected viewpoint:

- **None:** no semantic implementation difference relevant to the selected viewpoint remains after mapping and exclusions; only unchanged, renamed, reformatted, generated, or otherwise excluded physical churn remains.
- **Local:** a semantic implementation change remains inside one existing node while its responsibility, material external relations, boundaries, state ownership, and contracts stay stable.
- **Material:** at least one component responsibility, typed relation, boundary, state owner, runtime scenario, public contract, or deployment element changed.
- **Systemic:** the change spans several independently owned or deployed boundaries, rewrites an end-to-end flow, or changes multiple public or data contracts.
- **Unknown:** evidence or cross-version mapping is insufficient.

Treat scale as breadth, not severity or quality. Report severity separately for demonstrated findings.

Assign one conformance status:

- **Not assessed:** no authoritative intent or enforceable rule was available.
- **No demonstrated regression:** checked constraints show no new or worsened mismatch in scope.
- **Candidate regression:** a mismatch is plausible, but mapping, dynamic evidence, or intent is incomplete.
- **Demonstrated regression:** target adds or worsens a forbidden relation, removes a required relation, or violates another explicit constraint with a harm mechanism.
- **Intentional evolution:** approved architecture authority changes with the implementation and migration evidence supports the new model.
- **Accepted exception:** a documented waiver covers the mismatch with owner, scope, and expiry or review condition.

For reflexion-style conformance, distinguish:

- **convergent:** implementation relation matches declared intent;
- **divergent:** implementation contains a relation forbidden or not represented by the intended model;
- **absent-required:** a required relation is missing;
- **allowed-but-absent:** a permitted relation is unused and is not a violation.

Do not label every absent permitted edge a defect.

## Render a delta view

Draw only the material changed slice. Preserve the same logical IDs and layout where practical. Encode status in text, not color alone:

~~~mermaid
flowchart LR
    API["N1 API [=]"] -->|"E1 calls [=]"| APP["N2 Application [=]"]
    API -->|"E2 imports [+, divergent]"| DB["N3 Persistence [=]"]
    APP -.->|"E3 calls [-]"| PORT["N4 Repository port [-]"]
~~~

Use **[+]**, **[-]**, **[~]**, and **[=]** for added, removed, changed, and unchanged. A removed element belongs to the comparison view, not the target as-is model; label it accordingly.

When one delta view becomes ambiguous, render separate baseline and target views with identical zoom and a compact delta table. Do not combine unrelated component, sequence, deployment, and data-flow changes in one graph.

## Verify both snapshots

Run checks under comparable conditions:

1. Use exact runtime, dependency, analyzer, and configuration versions for each snapshot.
2. Run the same repository-native graph or architecture command on both when compatible.
3. Record configuration changes that prevent direct numeric comparison.
4. Run focused behavior, contract, and architecture tests tied to material relations.
5. Resolve dynamic edges with generated artifacts, deployment configuration, or representative traces when the decision depends on them.
6. Inspect renames, generated sources, vendored code, submodules, and lockfiles according to each snapshot's source-of-truth policy.
7. Report command failures, skipped checks, and non-comparable results.

Do not install a new analyzer merely to obtain a score. Propose a reproducible extractor only when the comparison will recur and the rule matters to the repository.

## Report the comparison

Lead with:

- resolved baseline and target IDs;
- scope, viewpoint, and range semantics;
- change scale;
- conformance status;
- one-sentence decision.

Then provide:

1. a snapshot and tool contract;
2. a material delta table with stable IDs and evidence from both versions;
3. one delta view or a reason for skipping it;
4. metric deltas with exact commands and limitations;
5. conformance findings with severity and harm mechanism;
6. intentional or accepted changes that should not be called drift;
7. unknown mappings, checks not run, and the minimum evidence needed next.

Say **no demonstrated architectural drift in the inspected scope** rather than **architecture is unchanged** when evidence is limited.

## Enforce comparison guardrails

- Do not infer architectural distance from changed files, lines, directories, or release-number size alone.
- Do not compare different scopes, zooms, relation types, exclusions, or analyzer configurations as one trend.
- Do not call an implementation difference drift without declared intent and a mismatch.
- Do not treat every new dependency edge, component, queue, or service as degradation.
- Do not let rename, code movement, generated output, formatting, or vendored updates inflate logical-node churn.
- Do not hide a public contract, runtime target, state-owner, trust-boundary, or deployment change inside a “minor version” label.
- Do not mark missing permitted relations as violations.
- Do not turn an optional graph distance into a universal quality score.
- Do not modify the user's current worktree merely to inspect another ref.
- Do not claim a clean comparison when tools, builds, or dynamic evidence differ materially.

## Primary sources

Software reflexion models compare a high-level model, an extracted source model, and an explicit mapping. They classify matching, divergent, and absent relations. Structural-distance research demonstrates that connectivity changes between version endpoints can be measured, while also identifying abstraction and entity mapping as central validity problems. Architecture-erosion research covers structural, violation, quality, and evolution symptoms and does not reduce erosion to one metric.

- Perry and Wolf, *Foundations for the Study of Software Architecture*: https://www.cs.unibo.it/~cianca/wwwpages/readings/perrywolf.pdf
- Murphy, Notkin, and Sullivan, *Software Reflexion Models*: https://doi.org/10.1145/222132.222136
- Nakamura and Basili, *Metrics of Software Architecture Changes Based on Structural Distance*: https://doi.org/10.1109/METRICS.2005.35
- Terra et al., *Static Architecture-Conformance Checking: An Illustrative Overview*: https://homepages.dcc.ufmg.br/~mtov/pub/2010_ieeesw.pdf
- Li et al., *Understanding Software Architecture Erosion: A Systematic Mapping Study*: https://doi.org/10.1002/smr.2423
- Git diff documentation: https://git-scm.com/docs/git-diff
- Git rev-parse documentation: https://git-scm.com/docs/git-rev-parse
- Git worktree documentation: https://git-scm.com/docs/git-worktree
