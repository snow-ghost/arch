from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvaluationPipelineTests(unittest.TestCase):
    def test_dry_run_writes_paired_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="arch-pipeline-dry-") as temporary:
            output = Path(temporary) / "run"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "run_eval.py"),
                    "--dry-run",
                    "--case",
                    "go-small-wire-switch",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            manifest = json.loads((output / "manifest.json").read_text("utf-8"))
            self.assertEqual(manifest["conditions"], ["baseline", "arch"])
            self.assertEqual(manifest["case_ids"], ["go-small-wire-switch"])
            self.assertEqual(manifest["parallel_jobs"], 1)
            self.assertRegex(manifest["skill_sha256"], r"^[0-9a-f]{64}$")
            results = json.loads((output / "results.json").read_text("utf-8"))
            self.assertEqual(len(results), 2)
            self.assertEqual({item["status"] for item in results}, {"dry-run"})

    def test_generation_blinding_and_scoring_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="arch-pipeline-live-") as temporary:
            run_dir = Path(temporary) / "run"
            run = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "run_eval.py"),
                    "--case",
                    "rust-exhaustive-reducer",
                    "--output-dir",
                    str(run_dir),
                    "--",
                    sys.executable,
                    "-c",
                    "print('Keep the exhaustive match and verify transition tests.')",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)

            blind = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "build_blind_pairs.py"),
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(blind.returncode, 0, blind.stderr)
            blind_dir = run_dir / "blind"
            dimensions = [
                "evidence_and_repository_grounding",
                "reuse_and_dependency_accuracy",
                "architectural_fit",
                "simplicity_and_maintainability",
                "language_and_api_accuracy",
                "verification_and_migration_safety",
                "clarity_and_actionability",
            ]
            scores = {dimension: 2 for dimension in dimensions}
            fixture = {
                "scores": {"A": scores, "B": scores},
                "architecture_theater": {"A": 0, "B": 0},
                "critical_errors": {"A": [], "B": []},
                "winner": "tie",
                "reason": "Pipeline fixture.",
            }
            judge_program = Path(temporary) / "judge.py"
            judge_program.write_text(
                "import json\n" + f"print(json.dumps({fixture!r}))\n",
                encoding="utf-8",
            )
            judge = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "run_judge.py"),
                    "--jobs",
                    "2",
                    str(blind_dir),
                    "--",
                    sys.executable,
                    str(judge_program),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(judge.returncode, 0, judge.stderr)
            judge_manifest = json.loads(
                (blind_dir / "judge-manifest.json").read_text("utf-8")
            )
            self.assertEqual(judge_manifest["parallel_jobs"], 2)
            judge_results = json.loads(
                (blind_dir / "judge-results.json").read_text("utf-8")
            )
            self.assertEqual({item["status"] for item in judge_results}, {"ok"})

            score = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "score_judgments.py"),
                    str(blind_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(score.returncode, 0, score.stderr)
            summary = (blind_dir / "summary.md").read_text("utf-8")
            self.assertIn("Mean paired Architecture Guard - baseline delta: +0.00", summary)


if __name__ == "__main__":
    unittest.main()
