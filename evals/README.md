# Evaluation guide

The harness measures whether the local arch skill improves architecture decisions over the same agent without the skill. It does not treat skill activation or longer answers as success.

Version 0.1 includes the harness and cases. No general quality lift is claimed until a named model, command, sample size, judge, and run artifact are published.

## What the cases test

The case set covers:

- repository reuse and semantic duplication;
- package identity and dependency modernization;
- deprecated APIs and supported runtime targets;
- dependency direction and integration boundaries;
- switches, exhaustive matches, and fitting patterns;
- safe and unsafe regex use;
- clone-detector and complexity false positives;
- uncertainty that requires investigation before change;
- Python, JavaScript or TypeScript, Go, Rust, Java, Kotlin, .NET, and C++ contexts.

Routes are balanced across:

- **apply:** evidence supports an intervention;
- **skip:** the suspicious construct is the fitting design;
- **clarify:** supplied evidence is insufficient for a safe decision.

## Generate a dry run

From the repository root:

    python3 evals/run_eval.py --dry-run

This writes prompts, result metadata, a skill digest, and a run manifest without invoking an agent.

Select cases or conditions:

    python3 evals/run_eval.py --dry-run \
      --case python-url-regex-parser \
      --case rust-exhaustive-reducer \
      --condition both

Use --output-dir to keep a named reproducible run. Generated evals/runs directories are ignored by git.

## Run paired generations

The command after -- must read the prompt from standard input and write the answer to standard output. Example with Codex:

    python3 evals/run_eval.py \
      --runs 3 \
      --jobs 2 \
      --agent codex \
      -- codex exec --sandbox read-only --skip-git-repo-check -

The runner randomizes job order. Every job gets a fresh temporary project. The arch condition receives a project-local copy of skills/arch at the selected agent path; the baseline does not. The --jobs option bounds concurrent agent processes; start with one or two to avoid rate-limit and load artifacts.

Supported install layouts are Codex, Claude Code, Cursor, and OpenCode. The harness does not hide the caller's user-level agent profile because it may contain authentication. Audit globally installed skills and instructions before interpreting results, or use a clean profile.

Use multiple runs because sampling variance can exceed the effect of a short instruction. Keep model, model version, reasoning setting, command, environment, seed, timeout, and skill commit fixed.

## Blind responses

After a paired run:

    python3 evals/build_blind_pairs.py evals/runs/RUN_ID

The command randomizes baseline and arch as A or B for every pair, writes anonymous responses and judge prompts, and creates:

- blind/key.json, which must remain hidden from the judge;
- blind/judgments-template.json;
- blind/pairs/PAIR_ID/judge-prompt.md.

Run an automated judge whose command reads stdin and returns the required JSON object. Runner options must precede blind_dir:

    python3 evals/run_judge.py \
      --jobs 2 \
      --timeout 600 \
      evals/runs/RUN_ID/blind \
      -- claude --print --model opus --effort max \
        --output-format json --no-session-persistence --disable-slash-commands

run_judge.py accepts raw rubric JSON or a JSON wrapper whose result field contains it. It writes the exact command, per-pair stdout, stderr, timing, validated judgments, and failure metadata.

For manual judging, copy and fill the template:

    cp evals/runs/RUN_ID/blind/judgments-template.json \
      evals/runs/RUN_ID/blind/judgments.json

Use a judge that has not seen key.json. Human review is preferred for ambiguous architecture trade-offs; an LLM judge should be identified, its resolved model recorded from raw metadata, and a sample of judgments spot-checked. Audit its user-level profile because run_judge.py isolates the working directory but retains authentication settings.

## Score

After all fields are complete:

    python3 evals/score_judgments.py evals/runs/RUN_ID/blind

The summary reports adjusted dimension scores, paired arch-minus-baseline deltas, preferences, critical-error counts, and judge notes.

Do not report only an aggregate mean. Include:

- every case and run count;
- model and exact command;
- commit and skill digest;
- prompt-policy version;
- judge identity and independence;
- preference counts and paired deltas;
- critical errors by condition;
- failed or timed-out jobs;
- global-profile isolation limitations;
- whether cases were selected or tuned after viewing results.

## Interpretation

A useful skill should improve decision calibration, not maximize interventions. It should win apply cases by finding concrete reuse, dependency, or boundary corrections; win skip cases by avoiding architecture theater; and win clarify cases by obtaining the minimum evidence needed before changing code.

Treat a small result as a smoke test. Do not generalize selected post-tuning cases. Publish raw artifacts or enough metadata for independent replication.
