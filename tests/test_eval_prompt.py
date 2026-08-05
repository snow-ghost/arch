from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    path = ROOT / "evals" / "run_eval.py"
    spec = importlib.util.spec_from_file_location("arch_eval_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromptPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.case = {"prompt": "Review the example engineering task."}

    def test_baseline_and_arch_share_direct_answer_policy(self) -> None:
        baseline = self.runner.build_prompt(self.case, "baseline")
        arch = self.runner.build_prompt(self.case, "arch")
        shared = "without narrating internal method selection"
        self.assertIn(shared, baseline)
        self.assertIn(shared, arch)
        self.assertNotIn("Agent Skill", baseline)

    def test_arch_condition_forbids_condition_disclosure(self) -> None:
        prompt = self.runner.build_prompt(self.case, "arch")
        self.assertIn("for internal reasoning", prompt)
        self.assertIn("Do not mention the skill", prompt)
        self.assertIn("silently use the direct", prompt)

    def test_prompt_policy_is_versioned(self) -> None:
        self.assertGreaterEqual(self.runner.PROMPT_POLICY_VERSION, 2)


if __name__ == "__main__":
    unittest.main()
