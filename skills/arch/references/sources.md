# Empirical and primary sources

This bibliography records the evidence behind the workflow. It is not a universal scorecard. Results depend on model, date, language, prompt, repository, task, tool configuration, and evaluation design.

## Contents

- [Generated-code structure and maintainability](#generated-code-structure-and-maintainability)
- [Repository and documentation grounding](#repository-and-documentation-grounding)
- [Dependencies, APIs, and package identity](#dependencies-apis-and-package-identity)
- [Security evidence is context-dependent](#security-evidence-is-context-dependent)
- [Duplication and code smells](#duplication-and-code-smells)
- [Patterns and architectural complexity](#patterns-and-architectural-complexity)
- [Regex and parser safety](#regex-and-parser-safety)
- [Skill effectiveness](#skill-effectiveness)
- [Official tool references](#official-tool-references)
- [Architecture views and notation](#architecture-views-and-notation)

## Generated-code structure and maintainability

### SlopCodeBench

SlopCodeBench studies long-horizon Python repository generation with 36 problems, 15 agents, and 196 checkpoints. No evaluated agent solved an entire problem under its strict criterion. Structural erosion increased in 77 percent of trajectories and measured verbosity increased in 75.5 percent. The paper reports agent code as 2.3 times more verbose and 2.0 times more structurally eroded than its 473-project open-source comparison set. Quality-focused prompting reduced initial issues but did not stop longitudinal degradation and added cost.

Use: inspect checkpoints and before/after structure rather than trusting final tests alone.

Limit: 2026 preprint, Python-focused benchmark, study-specific detectors and thresholds.

- Paper: https://arxiv.org/abs/2603.24755
- HTML: https://arxiv.org/html/2603.24755v2

### AI-generated architectural smells

A 2026 preprint reports method bloat, God classes, redundant implementation, and coupling in a small MetaGPT study. It found a strong size-to-smell correlation in that setting and no clear improvement from more detailed prompts.

Use: treat size and smell growth as review signals.

Limit: small sample, one agent system and task construction; do not generalize its correlation as a universal law.

- Paper: https://arxiv.org/abs/2605.02741

### Static-analysis feedback

A study of 4,066 Java and Python snippets generated in an older ChatGPT setting found 1,930 snippets with maintainability or style issues reported by static analyzers. Issue distributions differed by language and tools had non-overlapping findings. Static and runtime feedback repaired a subset.

Use: combine language-specific linters and runtime verification; do not rely on one analyzer.

Limit: snippet and LeetCode setting, older model generation, tool warnings are not all architectural defects.

- Paper: https://arxiv.org/abs/2307.12596

## Repository and documentation grounding

RepoCoder retrieves repository-level context iteratively and reports more than a ten-percent improvement over in-file completion in its evaluated settings. De-Hallucinator retrieves project API references and reports substantial correct-API recall improvements. DocPrompting retrieves documentation before generation and improves results in its evaluated tasks.

Use: search repository APIs, manifests, tests, and current documentation before generating local replacements.

- RepoCoder: https://arxiv.org/abs/2303.12570
- De-Hallucinator: https://arxiv.org/abs/2401.01701
- DocPrompting: https://arxiv.org/abs/2207.05987

## Dependencies, APIs, and package identity

### Deprecated API use

An ICSE 2025 study evaluated seven language models across 145 deprecated-to-current mappings in eight Python libraries and 28,125 prompts. Among plausible completions, deprecated API usage remained substantial and varied by context and model.

Use: detect deprecations against the project's exact targets and verify replacement semantics.

- Paper: https://arxiv.org/abs/2406.09834

A newer 2026 preprint evaluates evolving Python APIs and reports that structured documentation improves executable migration results, while stale learned knowledge still interferes.

Use: retrieve targeted current documentation rather than asking for ungrounded self-reflection.

Limit: preprint and current-model snapshot.

- Paper: https://arxiv.org/abs/2604.09515

### Package hallucinations

A USENIX Security 2025 distinguished paper generated 576,000 Python and JavaScript samples from 16 models. It reports nonzero hallucinated-package rates across model groups and 205,474 unique hallucinated package names.

Use: verify package existence and identity in the official registry and upstream repository before installation.

- Paper page: https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen

### Dependency updates and tests

A study injecting faults into dependency updates in 262 Java projects found that test suites detected an average of 47 percent of injected faults in direct dependencies and 35 percent in transitive dependencies.

Use: combine tests with static analysis, API inspection, and change-impact reasoning.

Limit: injected-fault methodology and Java project sample.

- Paper: https://arxiv.org/abs/2109.11921

## Security evidence is context-dependent

An early GitHub Copilot study generated 1,689 programs over 89 security scenarios and found about 40 percent vulnerable. A controlled user study found less secure results and overconfidence among participants using an AI assistant. A separate USENIX Security 2023 C study with 58 participants did not find a large increase in critical security bugs for its task.

Use: require threat-model and task-specific verification. Do not assert that every AI-generated change is insecure.

- Copilot scenarios: https://arxiv.org/abs/2108.09293
- User study: https://arxiv.org/abs/2211.03622
- C user study: https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval

## Duplication and code smells

A study across eight systems reports that 61 to 84.7 percent of detected clones were not harmful under its consistent-maintenance measure.

Use: clone detection is triage; verify shared ownership and change coupling before extraction.

- Study record: https://ink.library.smu.edu.sg/sis_research/6193/
- PMD CPD documentation: https://pmd.github.io/pmd/pmd_userdocs_cpd.html

Systematic reviews find associations between some code smells, faults, and maintainability but also heterogeneous definitions, detectors, thresholds, and evidence.

Use: describe a concrete mechanism rather than treating a smell label as proof.

- Review: https://www.mdpi.com/2078-2489/9/11/273
- Review: https://arxiv.org/abs/2004.10777

## Patterns and architectural complexity

Pattern use can reduce selected control-flow measures while increasing classes and source size. Other studies emphasize context in resolving dependency cycles and developer-perceived architecture burden.

Use: compare patterns against direct designs and require a current variation or boundary.

- Pattern metrics study: https://doaj.org/article/a4555bd1dbac445ca13360fbbb2a8420
- Object-oriented overkill study: https://scholars.duke.edu/publication/758386
- Dependency-cycle untangling: https://arxiv.org/abs/2306.10599
- Architectural complexity at Google: https://research.google/pubs/understanding-architectural-complexity-maintenance-burden-and-developer-sentiment-a-large-scale-study/
- Refactoring catalog example: https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html

## Regex and parser safety

OWASP and MITRE document regular-expression denial of service from excessive backtracking. Standard parser documentation also records format-specific parsing and validation caveats.

Use: define grammar and exposure, bound inputs, test adversarial cases, and prefer maintained specification-aware parsers for structured formats.

- OWASP ReDoS: https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
- MITRE CWE-1333: https://cwe.mitre.org/data/definitions/1333.html
- Python URL parsing: https://docs.python.org/3/library/urllib.parse.html
- WHATWG standards: https://spec.whatwg.org/

## Skill effectiveness

SkillsBench reports an average improvement from curated skills across its tasks, with smaller gains in software engineering and negative effects from some skills. A 2026 SWE-Skills-Bench preprint reports small average gains across public software-engineering skills and degradation from some version-mismatched guidance.

Use: keep the operational core focused, retrieve current documentation, include counterexamples, and evaluate against a no-skill baseline.

Limits: benchmark tasks, agents, skill implementations, and preprint status constrain generalization.

- SkillsBench: https://arxiv.org/abs/2602.12670
- SWE-Skills-Bench: https://arxiv.org/abs/2603.15401
- Agent Skills specification: https://github.com/agentskills/agentskills

## Official tool references

Confirm versions and configuration in the target repository.

- Ruff complexity and deprecated imports: https://docs.astral.sh/ruff/rules/complex-structure/ and https://docs.astral.sh/ruff/rules/deprecated-import/
- pip-audit: https://github.com/pypa/pip-audit
- typescript-eslint deprecations: https://typescript-eslint.io/rules/no-deprecated/
- npm outdated and audit: https://docs.npmjs.com/cli/v11/commands/npm-outdated/ and https://docs.npmjs.com/cli/v11/commands/npm-audit/
- Staticcheck SA1019: https://staticcheck.dev/docs/checks/#SA1019
- govulncheck: https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
- Rust Clippy: https://doc.rust-lang.org/clippy/
- Java deprecation warnings: https://docs.oracle.com/en/java/javase/25/core/notifications-and-warnings.html
- .NET package status: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-package-list
- clang-tidy: https://clang.llvm.org/extra/clang-tidy/
- ArchUnit: https://www.archunit.org/userguide/html/000_Index.html
- Import Linter: https://import-linter.readthedocs.io/en/stable/
- dependency-cruiser: https://github.com/sverweij/dependency-cruiser
- NetArchTest: https://github.com/BenMorris/NetArchTest
- cargo-deny: https://embarkstudios.github.io/cargo-deny/
- golangci-lint depguard: https://golangci-lint.run/docs/linters/configuration/#depguard

## Architecture views and notation

The C4 model defines software system, container, component, and code abstractions and allows teams to use only the diagram levels that add value.

Use: choose the smallest zoom that answers the review question and aggregate repository symbols into demonstrated boundaries.

Limit: C4 vocabulary does not prove that a node, edge, or boundary exists in the target repository.

- Abstractions: https://c4model.com/abstractions
- Diagrams: https://c4model.com/diagrams

OWASP's threat-modeling guidance uses data-flow diagrams with external entities, processes, data stores, data flows, and trust boundaries.

Use: represent security-relevant data movement and boundary crossings; name the data on important flows.

Limit: a DFD is an input to threat analysis, not a complete threat model or proof of security.

- Threat Modeling Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

Mermaid documents flowchart, sequence, and state syntax. Its native C4 syntax is explicitly experimental.

Use: prefer the repository's established renderer; otherwise emit portable Mermaid flowchart, sequence, or state text and verify syntax against the repository's pinned renderer when one exists.

Limit: do not assume experimental C4 syntax is supported by every Markdown host or Mermaid version.

- Flowchart: https://mermaid.js.org/syntax/flowchart.html
- Sequence: https://mermaid.js.org/syntax/sequenceDiagram.html
- State: https://mermaid.js.org/syntax/stateDiagram.html
- Experimental C4: https://mermaid.js.org/syntax/c4.html

FIPS PUB 183 standardized IDEF0 in 1993. NIST lists FIPS 183 as withdrawn on 2 September 2008.

Use: provide IDEF0-style input, control, output, and mechanism views only when a stakeholder or existing artifact requires that legacy notation.

Limit: label Mermaid approximations as non-normative and make no current FIPS-conformance claim.

- FIPS PUB 183: https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub183.pdf
- NIST withdrawn FIPS index: https://www.nist.gov/system/files/documents/2016/12/15/withdrawn_fips_by_numerical_order_index.pdf
