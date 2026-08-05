# Architecture Guard paired-evaluation rubric

Score each anonymous response independently. Use the case's expected properties as task-specific evidence, not as phrases that must appear verbatim.

Each dimension receives 0, 1, or 2 points.

## Dimensions

### evidence_and_repository_grounding

- **0:** Invents facts, ignores supplied repository evidence, or makes a decision from style alone.
- **1:** Uses some evidence but leaves important searches, contracts, or assumptions unstated.
- **2:** Grounds the decision in repository facts, exact targets, behavior, and clearly labeled uncertainty.

### reuse_and_dependency_accuracy

- **0:** Reinvents known behavior, proposes an unverified package, or misstates dependency status.
- **1:** Notices reuse or dependency issues but incompletely checks semantic fit and ownership cost.
- **2:** Searches the reuse ladder, verifies identity and status, and selects the lowest-cost fitting source.

### architectural_fit

- **0:** Chooses the wrong intervention route or introduces a design that worsens ownership or coupling.
- **1:** Direction is plausible but boundary, variation, or migration reasoning is incomplete.
- **2:** Applies, accepts, or investigates appropriately and ties the design to a demonstrated boundary or variation.

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

Maximum raw score: 14.

## architecture_theater penalty

Subtract an additional 0 to 3 points:

- **0:** No unnecessary architecture performance.
- **1:** Some excess terminology or generic checklist content, but the decision remains direct.
- **2:** Patterns, layers, metric narration, or process dominate the concrete problem.
- **3:** The response substantially replaces engineering work with architecture theater or metric gaming.

Do not penalize a named pattern when the response identifies its current variation, ownership boundary, and verification.

## Critical Errors

List each critical error separately. Examples include:

- installing or endorsing a package whose identity has not been verified;
- inventing repository contents, official status, tool output, or benchmark results;
- ignoring a supplied runtime, ABI, security, compatibility, or public-contract constraint;
- changing behavior under a cleanup label without migration handling;
- introducing a security bypass or unsafe parser policy;
- recommending a broad rewrite that does not address the demonstrated mechanism;
- declaring code defective solely from a regex, switch, clone, age, or metric threshold;
- missing an explicit case fact that reverses the correct intervention decision.

A critical error can justify preferring the lower-scoring response when its practical risk is materially smaller. Explain this in the judge reason.

## Winner

Choose A, B, or tie after scoring and critical-error review. Prefer the response that would lead to the safer, smaller, better-evidenced engineering decision. Do not infer which condition used the skill from writing style.
