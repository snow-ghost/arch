#!/usr/bin/env python3
"""Blind baseline/Architecture Guard response pairs and prepare judging prompts."""

from __future__ import annotations

import argparse
import json
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "evidence_and_repository_grounding",
    "reuse_and_dependency_accuracy",
    "architectural_fit",
    "simplicity_and_maintainability",
    "language_and_api_accuracy",
    "verification_and_migration_safety",
    "clarity_and_actionability",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--cases", type=Path, default=ROOT / "evals" / "cases.json")
    parser.add_argument("--rubric", type=Path, default=ROOT / "evals" / "rubric.md")
    parser.add_argument("--seed", type=int, default=9173)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing blind directory.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def response_path(run_dir: Path, case_id: str, run_name: str, condition: str) -> Path:
    return run_dir / "cases" / case_id / run_name / condition / "response.md"


def judge_prompt(
    *,
    case: dict[str, Any],
    rubric: str,
    response_a: str,
    response_b: str,
) -> str:
    output_example = {
        "scores": {
            "A": {name: 0 for name in DIMENSIONS},
            "B": {name: 0 for name in DIMENSIONS},
        },
        "architecture_theater": {"A": 0, "B": 0},
        "critical_errors": {"A": [], "B": []},
        "winner": "A|B|tie",
        "reason": "two to five sentences",
    }
    return (
        "Evaluate the two anonymous responses independently using the rubric. "
        "Do not infer their condition from style. Return only one JSON object with "
        "the exact shape shown at the end. Use integer dimension scores 0..2 and "
        "integer architecture_theater penalties 0..3.\n\n"
        f"# Task\n\n{case['prompt']}\n\n"
        "# Expected properties\n\n"
        f"{json.dumps(case['expected'], indent=2, ensure_ascii=False)}\n\n"
        f"{rubric.strip()}\n\n"
        f"# Response A\n\n{response_a.strip()}\n\n"
        f"# Response B\n\n{response_b.strip()}\n\n"
        "# Required JSON shape\n\n"
        f"{json.dumps(output_example, indent=2)}\n"
    )


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    output_dir = (args.output_dir or run_dir / "blind").resolve()
    if output_dir.exists():
        if not args.force:
            raise SystemExit(f"output already exists: {output_dir}; use --force")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    cases = load_json(args.cases.resolve())
    by_id = {case["id"]: case for case in cases}
    rubric = args.rubric.resolve().read_text(encoding="utf-8")
    manifest = load_json(run_dir / "manifest.json")
    randomizer = random.Random(args.seed)
    mappings: dict[str, dict[str, str]] = {}
    judgments: dict[str, Any] = {}

    for case_id in manifest["case_ids"]:
        case_root = run_dir / "cases" / case_id
        if not case_root.is_dir():
            raise SystemExit(f"missing case artifacts: {case_root}")
        if case_id not in by_id:
            raise SystemExit(f"case {case_id} not found in {args.cases}")
        for run_path in sorted(path for path in case_root.iterdir() if path.is_dir()):
            baseline = response_path(run_dir, case_id, run_path.name, "baseline")
            arch = response_path(run_dir, case_id, run_path.name, "arch")
            if not baseline.is_file() or not arch.is_file():
                raise SystemExit(
                    f"paired responses required for {case_id}/{run_path.name}"
                )
            pair_id = f"{case_id}--{run_path.name}"
            order = ["baseline", "arch"]
            randomizer.shuffle(order)
            mapping = {"A": order[0], "B": order[1]}
            mappings[pair_id] = mapping
            contents = {
                "baseline": baseline.read_text(encoding="utf-8"),
                "arch": arch.read_text(encoding="utf-8"),
            }
            pair_dir = output_dir / "pairs" / pair_id
            pair_dir.mkdir(parents=True)
            (pair_dir / "A.md").write_text(contents[mapping["A"]], encoding="utf-8")
            (pair_dir / "B.md").write_text(contents[mapping["B"]], encoding="utf-8")
            (pair_dir / "judge-prompt.md").write_text(
                judge_prompt(
                    case=by_id[case_id],
                    rubric=rubric,
                    response_a=contents[mapping["A"]],
                    response_b=contents[mapping["B"]],
                ),
                encoding="utf-8",
            )
            judgments[pair_id] = {
                "scores": {
                    "A": {name: None for name in DIMENSIONS},
                    "B": {name: None for name in DIMENSIONS},
                },
                "architecture_theater": {"A": None, "B": None},
                "critical_errors": {"A": [], "B": []},
                "winner": None,
                "reason": "",
            }

    key = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_run": str(run_dir),
        "seed": args.seed,
        "mappings": mappings,
    }
    (output_dir / "key.json").write_text(
        json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    template = {
        "schema_version": 1,
        "dimensions": DIMENSIONS,
        "judgments": judgments,
    }
    (output_dir / "judgments-template.json").write_text(
        json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Blind pairs: {len(mappings)}")
    print(f"Judge prompts: {output_dir / 'pairs'}")
    print(f"Copy judgments-template.json to judgments.json and fill it before scoring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
