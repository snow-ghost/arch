# Architecture Guard paired-evaluation rubric

Score each anonymous response independently. Use the case's expected properties as task-specific evidence, not as phrases that must appear verbatim.

Each dimension receives 0, 1, or 2 points.

## Dimensions

### evidence_and_repository_grounding

- **0:** Invents facts, ignores supplied repository evidence, treats mutable or unresolved versions as fixed, or makes a decision from style alone.
- **1:** Uses some evidence but leaves important searches, contracts, snapshot identities, or assumptions unstated.
- **2:** Grounds the decision in repository facts, exact targets and snapshots when applicable, behavior, and clearly labeled uncertainty.

### reuse_and_dependency_accuracy

- **0:** Reinvents known behavior, proposes an unverified package, or misstates dependency status.
- **1:** Notices reuse or dependency issues but incompletely checks semantic fit and ownership cost.
- **2:** Searches the reuse ladder, verifies identity and status, and selects the lowest-cost fitting source.

### architectural_fit

- **0:** Chooses the wrong intervention route or introduces a design that worsens ownership or coupling.
- **1:** Direction is plausible but boundary, variation, or migration reasoning is incomplete.
- **2:** Applies, accepts, or investigates appropriately and ties the design to a demonstrated boundary or variation.

### architecture_view_accuracy

- **0:** Invents or mislabels relationships, uses the wrong zoom or notation, mixes as-is with to-be, compares unaligned snapshots, or treats structural change as drift without declared intent.
- **1:** Selects a useful view or comparison but incompletely records evidence, stable identity, status, unknowns, aggregation, or the comparison contract.
- **2:** Selects or skips a view appropriately, uses fitting typed relationships and evidence, and separates observed, inferred, proposed, and unknown facts. For comparisons, aligns stable logical IDs at the same scope, viewpoint, and zoom and separates structural delta from conformance change.

### simplicity_and_maintainability

- **0:** Adds speculative layers, factories, registries, patterns, or rewrites without removing a real mechanism.
- **1:** Avoids major overengineering but leaves unnecessary scope or vague cleanup.
- **2:** Chooses the smallest clear design and explains why more elaborate alternatives are not warranted.

### language_and_api_accuracy

- **0:** Contradicts supplied language semantics, target versions, deprecation facts, or API behavior.
- **1:** Mostly idiomatic but misses a relevant ecosystem constraint.
- **2:** Uses language-specific strengths and verifies APIs and migrations against exact project targets.

### verification_and_migration_safety

- **0:** Omits verification or proposes a change likely to break behavior, security, or compatibility.
- **1:** Gives generic tests but misses an important failure mode or migration risk.
- **2:** Names focused checks tied to the mechanism and reports residual risks or missing evidence.

### clarity_and_actionability

- **0:** Is primarily slogans, pattern names, or an internal-method transcript.
- **1:** Understandable but verbose, indirect, or missing an executable next step.
- **2:** Leads with the decision, separates fact from inference, and gives concise actionable next steps.

Maximum raw score: 16.

## architecture_theater penalty

Subtract an additional 0 to 3 points:

- **0:** No unnecessary architecture performance.
- **1:** Some excess terminology or generic checklist content, but the decision remains direct.
- **2:** Patterns, layers, unnecessary diagrams, metric narration, or process dominate the concrete problem.
- **3:** The response substantially replaces engineering work with architecture or diagram theater, false visual precision, or metric gaming.

Do not penalize a named pattern when the response identifies its current variation, ownership boundary, and verification.

## Critical Errors

List each critical error separately. Examples include:

- installing or endorsing a package whose identity has not been verified;
- inventing repository contents, official status, tool output, or benchmark results;
- ignoring a supplied runtime, ABI, security, compatibility, or public-contract constraint;
- presenting an inferred or unknown architecture relationship as observed;
- mixing proposed architecture into an as-is view or claiming strict notation conformance without support;
- comparing unresolved or mutable refs as fixed snapshots, or silently changing scope, zoom, relation semantics, exclusions, or analyzer configuration between versions;
- calling an implementation difference architectural drift without declared intent, or deriving a degradation percentage from file or line churn;
- changing behavior under a cleanup label without migration handling;
- introducing a security bypass or unsafe parser policy;
- recommending a broad rewrite that does not address the demonstrated mechanism;
- declaring code defective solely from a regex, switch, clone, age, or metric threshold;
- missing an explicit case fact that reverses the correct intervention decision.

A critical error can justify preferring the lower-scoring response when its practical risk is materially smaller. Explain this in the judge reason.

## Winner

Choose A, B, or tie after scoring and critical-error review. Prefer the response that would lead to the safer, smaller, better-evidenced engineering decision. Do not infer which condition used the skill from writing style.
