#!/usr/bin/env python3
"""Run blind judge prompts and write validated judgments."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run every blind judge prompt through one command. The command must read "
            "the prompt from stdin and return either the rubric JSON or a JSON wrapper "
            "whose result field contains that JSON."
        )
    )
    parser.add_argument("blind_dir", type=Path)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace judgments.json and judge-run artifacts when present.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Judge argv after --; it must read the prompt from stdin.",
    )
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a judge command is required after --")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    return args


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot load JSON from {path}: {exc}") from exc


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def strip_fence(value: str) -> str:
    stripped = value.strip()
    fence = chr(96) * 3
    if not stripped.startswith(fence):
        return stripped
    lines = stripped.splitlines()
    if len(lines) >= 2 and lines[-1].strip() == fence:
        return "\n".join(lines[1:-1]).strip()
    return stripped


def parse_judgment(value: str) -> dict[str, Any]:
    parsed = json.loads(strip_fence(value))
    if not isinstance(parsed, dict):
        raise ValueError("judge output must be a JSON object")
    if "scores" in parsed:
        return parsed
    for key in ("result", "structured_output", "output"):
        nested = parsed.get(key)
        if isinstance(nested, str):
            return parse_judgment(nested)
        if isinstance(nested, dict) and "scores" in nested:
            return nested
    raise ValueError("judge JSON does not contain scores or a parseable result field")


def validate_judgment(
    value: dict[str, Any],
    *,
    pair_id: str,
    dimensions: list[str],
) -> None:
    scores = value.get("scores")
    theater = value.get("architecture_theater")
    errors = value.get("critical_errors")
    if not isinstance(scores, dict):
        raise ValueError(f"{pair_id}: scores must be an object")
    if not isinstance(theater, dict):
        raise ValueError(f"{pair_id}: architecture_theater must be an object")
    if not isinstance(errors, dict):
        raise ValueError(f"{pair_id}: critical_errors must be an object")

    for label in ("A", "B"):
        label_scores = scores.get(label)
        if not isinstance(label_scores, dict):
            raise ValueError(f"{pair_id}: scores.{label} must be an object")
        if set(label_scores) != set(dimensions):
            raise ValueError(f"{pair_id}: scores.{label} dimensions do not match")
        for dimension in dimensions:
            score = label_scores[dimension]
            if (
                not isinstance(score, int)
                or isinstance(score, bool)
                or score not in {0, 1, 2}
            ):
                raise ValueError(
                    f"{pair_id}: scores.{label}.{dimension} must be 0, 1, or 2"
                )
        penalty = theater.get(label)
        if (
            not isinstance(penalty, int)
            or isinstance(penalty, bool)
            or penalty not in {0, 1, 2, 3}
        ):
            raise ValueError(
                f"{pair_id}: architecture_theater.{label} must be 0..3"
            )
        critical = errors.get(label)
        if not isinstance(critical, list) or not all(
            isinstance(item, str) for item in critical
        ):
            raise ValueError(
                f"{pair_id}: critical_errors.{label} must be an array of strings"
            )

    if value.get("winner") not in {"A", "B", "tie"}:
        raise ValueError(f"{pair_id}: winner must be A, B, or tie")
    if not isinstance(value.get("reason"), str) or not value["reason"].strip():
        raise ValueError(f"{pair_id}: reason must be a non-empty string")


def run_judge(
    *,
    pair_id: str,
    prompt_path: Path,
    artifact_dir: Path,
    command: list[str],
    dimensions: list[str],
    timeout: float,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    prompt = prompt_path.read_text(encoding="utf-8")
    started = time.monotonic()
    result: dict[str, Any] = {
        "pair_id": pair_id,
        "status": "pending",
        "duration_seconds": 0.0,
        "exit_code": None,
    }
    environment = os.environ.copy()
    environment.setdefault("NO_COLOR", "1")
    environment.setdefault("TERM", "dumb")

    with tempfile.TemporaryDirectory(prefix="arch-judge-") as temporary:
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                cwd=temporary,
                env=environment,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except OSError as exc:
            result["duration_seconds"] = round(time.monotonic() - started, 3)
            result["status"] = "error"
            result["error"] = f"cannot execute judge command: {exc}"
            write_text(artifact_dir / "stdout.txt", "")
            write_text(artifact_dir / "stderr.txt", str(exc) + "\n")
            write_text(
                artifact_dir / "result.json",
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            )
            return result, None
        except subprocess.TimeoutExpired as exc:
            result["duration_seconds"] = round(time.monotonic() - started, 3)
            result["status"] = "timeout"
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            write_text(artifact_dir / "stdout.txt", stdout)
            write_text(artifact_dir / "stderr.txt", stderr)
            write_text(
                artifact_dir / "result.json",
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            )
            return result, None

    result["duration_seconds"] = round(time.monotonic() - started, 3)
    result["exit_code"] = completed.returncode
    write_text(artifact_dir / "stdout.txt", completed.stdout)
    write_text(artifact_dir / "stderr.txt", completed.stderr)
    if completed.returncode != 0:
        result["status"] = "error"
        write_text(
            artifact_dir / "result.json",
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        )
        return result, None

    try:
        judgment = parse_judgment(completed.stdout)
        validate_judgment(judgment, pair_id=pair_id, dimensions=dimensions)
    except (json.JSONDecodeError, ValueError) as exc:
        result["status"] = "invalid"
        result["error"] = str(exc)
        write_text(
            artifact_dir / "result.json",
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        )
        return result, None

    result["status"] = "ok"
    write_text(
        artifact_dir / "judgment.json",
        json.dumps(judgment, indent=2, ensure_ascii=False) + "\n",
    )
    write_text(
        artifact_dir / "result.json",
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
    )
    return result, judgment


def main() -> int:
    args = parse_args()
    blind_dir = args.blind_dir.resolve()
    template_path = blind_dir / "judgments-template.json"
    document = load_json(template_path)
    dimensions = document.get("dimensions")
    judgments = document.get("judgments")
    if not isinstance(dimensions, list) or not dimensions or not all(
        isinstance(item, str) for item in dimensions
    ):
        raise SystemExit("judgments template has no valid dimensions")
    if not isinstance(judgments, dict) or not judgments:
        raise SystemExit("judgments template has no judgment pairs")

    output_path = (args.output or blind_dir / "judgments.json").resolve()
    run_root = blind_dir / "judge-runs"
    if output_path.exists() and not args.force:
        raise SystemExit(f"output already exists: {output_path}; use --force")
    if run_root.exists() and any(run_root.iterdir()) and not args.force:
        raise SystemExit(f"judge artifacts already exist: {run_root}; use --force")

    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_blind_dir": str(blind_dir),
        "pair_ids": list(judgments),
        "parallel_jobs": args.jobs,
        "timeout_seconds": args.timeout,
        "command": args.command,
        "global_judge_profile_isolated": False,
        "isolation_note": (
            "Each judge call uses a fresh working directory. The caller's user-level "
            "profile remains available for authentication and must be audited."
        ),
    }
    write_text(
        blind_dir / "judge-manifest.json",
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )

    pairs = [
        (
            pair_id,
            blind_dir / "pairs" / pair_id / "judge-prompt.md",
            run_root / pair_id,
        )
        for pair_id in judgments
    ]
    for pair_id, prompt_path, _ in pairs:
        if not prompt_path.is_file():
            raise SystemExit(f"missing judge prompt for {pair_id}: {prompt_path}")

    def execute(
        item: tuple[int, tuple[str, Path, Path]],
    ) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
        index, (pair_id, prompt_path, artifact_dir) = item
        print(f"[{index}/{len(pairs)}] judge {pair_id}", flush=True)
        result, judgment = run_judge(
            pair_id=pair_id,
            prompt_path=prompt_path,
            artifact_dir=artifact_dir,
            command=args.command,
            dimensions=dimensions,
            timeout=args.timeout,
        )
        return pair_id, result, judgment

    indexed = list(enumerate(pairs, start=1))
    if args.jobs == 1:
        completed = [execute(item) for item in indexed]
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            completed = list(executor.map(execute, indexed))

    results = [result for _, result, _ in completed]
    write_text(
        blind_dir / "judge-results.json",
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
    )
    completed_judgments = dict(judgments)
    for pair_id, _, judgment in completed:
        if judgment is not None:
            completed_judgments[pair_id] = judgment
    partial = dict(document)
    partial["judgments"] = completed_judgments
    write_text(
        blind_dir / "judgments-partial.json",
        json.dumps(partial, indent=2, ensure_ascii=False) + "\n",
    )

    failures = [result for result in results if result["status"] != "ok"]
    if failures:
        print(f"Invalid, failed, or timed out judges: {len(failures)}", file=sys.stderr)
        print(f"Partial judgments: {blind_dir / 'judgments-partial.json'}")
        return 1

    write_text(
        output_path,
        json.dumps(partial, indent=2, ensure_ascii=False) + "\n",
    )
    print(f"Judgments: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
