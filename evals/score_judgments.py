#!/usr/bin/env python3
"""Unblind completed judgments and summarize paired scores."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ("apply", "skip", "clarify")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blind_dir", type=Path)
    parser.add_argument("--judgments", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cases", type=Path, default=ROOT / "evals" / "cases.json")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def checked_score(value: Any, *, pair_id: str, label: str, dimension: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value not in {0, 1, 2}:
        raise SystemExit(
            f"{pair_id}: {label}.{dimension} must be an integer from 0 to 2"
        )
    return value


def case_route(pair_id: str, cases: dict[str, str]) -> str:
    matches = [
        route for case_id, route in cases.items() if pair_id.startswith(f"{case_id}--")
    ]
    if len(matches) != 1:
        raise SystemExit(f"{pair_id}: cannot resolve exactly one case route")
    return matches[0]


def main() -> int:
    args = parse_args()
    blind_dir = args.blind_dir.resolve()
    judgments_path = (args.judgments or blind_dir / "judgments.json").resolve()
    output_path = (args.output or blind_dir / "summary.md").resolve()
    if not judgments_path.is_file():
        raise SystemExit(
            f"missing {judgments_path}; copy judgments-template.json and complete it"
        )
    key = load_json(blind_dir / "key.json")
    document = load_json(judgments_path)
    cases_document = load_json(args.cases.resolve())
    cases = {
        case["id"]: case["applicability"]
        for case in cases_document
        if isinstance(case, dict)
        and isinstance(case.get("id"), str)
        and case.get("applicability") in ROUTES
    }
    if not cases:
        raise SystemExit("cases file has no valid applicability routes")

    dimensions = document.get("dimensions")
    judgments = document.get("judgments")
    if not isinstance(dimensions, list) or not dimensions:
        raise SystemExit("judgments file has no dimensions")
    if not isinstance(judgments, dict):
        raise SystemExit("judgments file has no judgments object")

    rows: list[dict[str, Any]] = []
    condition_wins = {"baseline": 0, "arch": 0, "tie": 0}
    scores_by_condition: dict[str, list[int]] = {"baseline": [], "arch": []}
    critical_by_condition = {"baseline": 0, "arch": 0}
    theater_by_condition = {"baseline": 0, "arch": 0}
    dimension_by_condition = {
        condition: {dimension: [] for dimension in dimensions}
        for condition in ("baseline", "arch")
    }

    for pair_id, mapping in key["mappings"].items():
        if pair_id not in judgments:
            raise SystemExit(f"missing judgment for {pair_id}")
        judgment = judgments[pair_id]
        adjusted: dict[str, int] = {}
        for label in ("A", "B"):
            values = judgment.get("scores", {}).get(label, {})
            dimension_values = {
                dimension: checked_score(
                    values.get(dimension),
                    pair_id=pair_id,
                    label=label,
                    dimension=dimension,
                )
                for dimension in dimensions
            }
            raw = sum(dimension_values.values())
            penalty = judgment.get("architecture_theater", {}).get(label)
            if (
                not isinstance(penalty, int)
                or isinstance(penalty, bool)
                or penalty not in {0, 1, 2, 3}
            ):
                raise SystemExit(f"{pair_id}: {label} architecture_theater must be 0..3")
            adjusted[label] = raw - penalty
            condition = mapping[label]
            scores_by_condition[condition].append(adjusted[label])
            theater_by_condition[condition] += penalty
            for dimension, score in dimension_values.items():
                dimension_by_condition[condition][dimension].append(score)
            errors = judgment.get("critical_errors", {}).get(label, [])
            if not isinstance(errors, list):
                raise SystemExit(f"{pair_id}: {label} critical_errors must be an array")
            critical_by_condition[condition] += len(errors)

        winner = judgment.get("winner")
        if winner not in {"A", "B", "tie"}:
            raise SystemExit(f"{pair_id}: winner must be A, B, or tie")
        winner_condition = "tie" if winner == "tie" else mapping[winner]
        condition_wins[winner_condition] += 1
        by_condition = {mapping[label]: adjusted[label] for label in ("A", "B")}
        rows.append(
            {
                "pair_id": pair_id,
                "route": case_route(pair_id, cases),
                "baseline": by_condition["baseline"],
                "arch": by_condition["arch"],
                "delta": by_condition["arch"] - by_condition["baseline"],
                "winner": winner_condition,
                "reason": str(judgment.get("reason", "")).strip(),
            }
        )

    deltas = [row["delta"] for row in rows]
    lines = [
        "# Blind Paired Evaluation Summary",
        "",
        f"Pairs: {len(rows)}",
        "",
        "| Metric | Baseline | Architecture Guard |",
        "|---|---:|---:|",
        (
            f"| Mean adjusted score (max {2 * len(dimensions)}) | "
            f"{statistics.fmean(scores_by_condition['baseline']):.2f} | "
            f"{statistics.fmean(scores_by_condition['arch']):.2f} |"
        ),
        f"| Preference wins | {condition_wins['baseline']} | {condition_wins['arch']} |",
        f"| Critical errors | {critical_by_condition['baseline']} | {critical_by_condition['arch']} |",
        f"| Architecture-theater penalties | {theater_by_condition['baseline']} | {theater_by_condition['arch']} |",
        "",
        f"Ties: {condition_wins['tie']}. Mean paired Architecture Guard - baseline delta: {statistics.fmean(deltas):+.2f}.",
        "",
        "## Scores by route",
        "",
        "| Route | Pairs | Baseline mean | Architecture Guard mean | Delta | Baseline wins | Architecture Guard wins | Ties |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for route in ROUTES:
        selected = [row for row in rows if row["route"] == route]
        if not selected:
            continue
        route_wins = {
            condition: sum(row["winner"] == condition for row in selected)
            for condition in ("baseline", "arch", "tie")
        }
        baseline_mean = statistics.fmean(row["baseline"] for row in selected)
        arch_mean = statistics.fmean(row["arch"] for row in selected)
        lines.append(
            f"| {route} | {len(selected)} | {baseline_mean:.2f} | "
            f"{arch_mean:.2f} | {arch_mean - baseline_mean:+.2f} | "
            f"{route_wins['baseline']} | {route_wins['arch']} | "
            f"{route_wins['tie']} |"
        )

    lines.extend(
        [
            "",
            "## Dimension means",
            "",
            "| Dimension | Baseline | Architecture Guard | Delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for dimension in dimensions:
        baseline_mean = statistics.fmean(
            dimension_by_condition["baseline"][dimension]
        )
        arch_mean = statistics.fmean(dimension_by_condition["arch"][dimension])
        lines.append(
            f"| {dimension} | {baseline_mean:.2f} | {arch_mean:.2f} | "
            f"{arch_mean - baseline_mean:+.2f} |"
        )

    lines.extend(
        [
            "",
            "## Pair scores",
            "",
            "| Pair | Route | Baseline | Architecture Guard | Delta | Preferred |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['pair_id']} | {row['route']} | {row['baseline']} | "
            f"{row['arch']} | {row['delta']:+d} | {row['winner']} |"
        )
    lines.extend(["", "## Judge notes", ""])
    for row in rows:
        lines.append(f"- **{row['pair_id']}**: {row['reason'] or 'No reason supplied.'}")
    lines.extend(
        [
            "",
            "This summary reports the supplied judgments. Sample size, model, harness, "
            "global-profile isolation, judge independence, and replication determine how "
            "strongly the result can be generalized.",
            "",
        ]
    )
    report = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWritten: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
