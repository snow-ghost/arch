#!/usr/bin/env python3
"""Run paired baseline/skill evaluations in isolated project directories."""

from __future__ import annotations

import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "cases.json"
SKILL_SOURCE = ROOT / "skills" / "arch"
INSTALL_PATHS = {
    "codex": Path(".agents/skills/arch"),
    "claude": Path(".claude/skills/arch"),
    "cursor": Path(".cursor/skills/arch"),
    "opencode": Path(".opencode/skills/arch"),
}
PROMPT_POLICY_VERSION = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run identical cases with and without the local arch skill. "
            "Put the agent command after --; it must read the prompt from stdin."
        )
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument(
        "--case",
        action="append",
        dest="selected_cases",
        help="Case id to run; repeat the flag. Defaults to every case.",
    )
    parser.add_argument(
        "--condition",
        choices=("baseline", "arch", "both"),
        default="both",
    )
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Maximum concurrent agent processes. Defaults to sequential execution.",
    )
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument(
        "--agent",
        choices=tuple(INSTALL_PATHS),
        default="codex",
        help="Project-local skill path to install for the Architecture Guard condition.",
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompts and metadata without invoking an agent.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Agent argv after --, for example: codex exec --skip-git-repo-check -",
    )
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.dry_run and not args.command:
        parser.error("an agent command is required after -- unless --dry-run is used")
    return args


def load_cases(path: Path, selected: list[str] | None) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot load cases from {path}: {exc}") from exc
    if not isinstance(raw, list) or not raw:
        raise SystemExit("cases file must contain a non-empty JSON array")
    by_id: dict[str, dict[str, Any]] = {}
    for case in raw:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise SystemExit("every case must be an object with a string id")
        if case["id"] in by_id:
            raise SystemExit(f"duplicate case id: {case['id']}")
        if case.get("applicability") not in {"apply", "skip", "clarify"}:
            raise SystemExit(f"invalid applicability for {case['id']}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise SystemExit(f"missing prompt for {case['id']}")
        by_id[case["id"]] = case
    if not selected:
        return list(by_id.values())
    missing = sorted(set(selected) - set(by_id))
    if missing:
        raise SystemExit(f"unknown case id(s): {', '.join(missing)}")
    selected_set = set(selected)
    return [case for case in raw if case["id"] in selected_set]


def skill_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_prompt(case: dict[str, Any], condition: str) -> str:
    shared = (
        "Act as the engineer responsible for a decision-ready response. "
        "Use only the facts in the task, distinguish assumptions from evidence, "
        "name important residual risks, and keep the answer under 900 words. "
        "Do not claim measurements you have not run. Return a direct engineering "
        "answer without narrating internal method selection."
    )
    if condition == "arch":
        intervention = (
            "An optional project-local Agent Skill named `arch` is installed for "
            "internal reasoning. Invoke it only when its routing criteria fit. Do not "
            "mention the skill, its availability, its gate, or its workflow unless the "
            "task itself asks about the method. If it does not fit, silently use the "
            "direct debugging, standard-pattern, or measurement route."
        )
    else:
        intervention = "Choose the engineering method you consider most appropriate."
    return f"{shared}\n\n{intervention}\n\nTask:\n{case['prompt'].strip()}\n"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def run_job(
    *,
    case: dict[str, Any],
    condition: str,
    run_number: int,
    output_dir: Path,
    command: list[str],
    agent: str,
    timeout: float,
    dry_run: bool,
) -> dict[str, Any]:
    artifact_dir = (
        output_dir
        / "cases"
        / case["id"]
        / f"run-{run_number:03d}"
        / condition
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(case, condition)
    write_text(artifact_dir / "prompt.md", prompt)

    result: dict[str, Any] = {
        "case_id": case["id"],
        "condition": condition,
        "run": run_number,
        "status": "dry-run" if dry_run else "pending",
        "command": command,
        "duration_seconds": 0.0,
        "exit_code": None,
    }

    with tempfile.TemporaryDirectory(prefix="arch-eval-") as temporary:
        workspace = Path(temporary)
        if condition == "arch":
            destination = workspace / INSTALL_PATHS[agent]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(SKILL_SOURCE, destination)
            result["skill_install_path"] = str(INSTALL_PATHS[agent])

        if not dry_run:
            started = time.monotonic()
            environment = os.environ.copy()
            environment.setdefault("NO_COLOR", "1")
            environment.setdefault("TERM", "dumb")
            try:
                completed = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    cwd=workspace,
                    env=environment,
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
                result["duration_seconds"] = round(time.monotonic() - started, 3)
                result["exit_code"] = completed.returncode
                result["status"] = "ok" if completed.returncode == 0 else "error"
                write_text(artifact_dir / "response.md", completed.stdout)
                write_text(artifact_dir / "stderr.txt", completed.stderr)
            except subprocess.TimeoutExpired as exc:
                result["duration_seconds"] = round(time.monotonic() - started, 3)
                result["status"] = "timeout"
                stdout = exc.stdout or ""
                stderr = exc.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")
                write_text(artifact_dir / "response.md", stdout)
                write_text(artifact_dir / "stderr.txt", stderr)

    write_text(
        artifact_dir / "result.json",
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
    )
    return result


def main() -> int:
    args = parse_args()
    cases = load_cases(args.cases.resolve(), args.selected_cases)
    conditions = ["baseline", "arch"] if args.condition == "both" else [args.condition]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (ROOT / "evals" / "runs" / f"run-{timestamp}")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        (case, condition, run_number)
        for case in cases
        for run_number in range(1, args.runs + 1)
        for condition in conditions
    ]
    random.Random(args.seed).shuffle(jobs)
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cases_file": str(args.cases.resolve()),
        "case_ids": [case["id"] for case in cases],
        "conditions": conditions,
        "runs_per_condition": args.runs,
        "parallel_jobs": args.jobs,
        "seed": args.seed,
        "timeout_seconds": args.timeout,
        "agent": args.agent,
        "command": args.command,
        "dry_run": args.dry_run,
        "prompt_policy_version": PROMPT_POLICY_VERSION,
        "skill_sha256": skill_digest(SKILL_SOURCE),
        "global_agent_profile_isolated": False,
        "isolation_note": (
            "Each job uses a fresh project directory. The caller's user-level agent "
            "profile remains available for authentication, so globally installed skills "
            "must be audited separately."
        ),
    }
    write_text(
        output_dir / "manifest.json",
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )

    def execute_job(
        indexed_job: tuple[int, tuple[dict[str, Any], str, int]],
    ) -> dict[str, Any]:
        index, (case, condition, run_number) = indexed_job
        print(
            f"[{index}/{len(jobs)}] {case['id']} run={run_number} condition={condition}",
            flush=True,
        )
        return run_job(
            case=case,
            condition=condition,
            run_number=run_number,
            output_dir=output_dir,
            command=args.command,
            agent=args.agent,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )

    indexed_jobs = list(enumerate(jobs, start=1))
    if args.jobs == 1:
        results = [execute_job(job) for job in indexed_jobs]
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            results = list(executor.map(execute_job, indexed_jobs))

    write_text(
        output_dir / "results.json",
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
    )
    failures = [r for r in results if r["status"] not in {"ok", "dry-run"}]
    print(f"Artifacts: {output_dir}")
    if failures:
        print(f"Failed or timed out jobs: {len(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
