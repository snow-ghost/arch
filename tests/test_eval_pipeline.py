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
            template = json.loads(
                (blind_dir / "judgments-template.json").read_text("utf-8")
            )
            for judgment in template["judgments"].values():
                for label in ("A", "B"):
                    for dimension in template["dimensions"]:
                        judgment["scores"][label][dimension] = 2
                    judgment["architecture_theater"][label] = 0
                judgment["winner"] = "tie"
                judgment["reason"] = "Pipeline fixture."
            judgments = blind_dir / "judgments.json"
            judgments.write_text(
                json.dumps(template, indent=2) + "\n",
                encoding="utf-8",
            )

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
