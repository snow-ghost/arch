# Repository instructions

## Purpose

This repository contains one portable Agent Skill, arch. Keep the canonical skill implementation in skills/arch. Product manifests must remain thin and point to ./skills/.

## Change rules

- Preserve frontmatter with only name and description.
- Keep SKILL.md below 500 lines and put detailed material in references.
- Use imperative operational language in the skill.
- Require repository evidence and exact runtime targets before findings.
- Keep counterexamples: regex, switches, duplication, and older versions are not defects by syntax or age alone.
- Never add a dependency, API, benchmark number, or maintenance claim without a verifiable source.
- Prefer current official documentation for volatile tool and package facts.
- Identify preprints and narrow empirical settings in research documents.
- Keep Codex, Claude Code, Cursor, and OpenCode manifests consistent at version 0.1.0.
- Update eval cases and rubric when a workflow change alters expected behavior.
- Do not commit generated evals/runs artifacts.

## Required checks

Run from the repository root:

    python3 -m unittest discover -s tests -v
    python3 evals/run_eval.py --dry-run
    python3 -m compileall -q evals tests

Also run the Agent Skill and Codex plugin validators when their development packages are available.

## Evaluation claims

A harness dry run is not a behavioral result. Any quality claim must name the model, exact command, commit and skill digest, cases, repeats, judge, preference counts, paired score delta, critical errors, and isolation limitations.
