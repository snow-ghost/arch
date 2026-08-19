from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "arch"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"{path} does not start with YAML frontmatter")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError(f"{path} has no closing frontmatter delimiter") from exc
    values: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip():
            continue
        if ":" not in line:
            raise AssertionError(f"unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values, "\n".join(lines[closing + 1 :])


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_is_portable_and_specific(self) -> None:
        values, _ = frontmatter(SKILL_FILE)
        self.assertEqual(set(values), {"name", "description"})
        self.assertEqual(values["name"], SKILL_DIR.name)
        self.assertRegex(values["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(values["name"]), 64)
        self.assertTrue(1 <= len(values["description"]) <= 1024)
        for trigger in (
            "software",
            "deprecated",
            "regex",
            "compare commits",
            "architectural evolution",
            "Do not use",
        ):
            self.assertIn(trigger, values["description"])

    def test_main_skill_is_compact_and_has_required_workflow(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        required = (
            "## Establish authority and scope",
            "## Map before changing",
            "## Render architecture views when useful",
            "## Compare architecture across snapshots",
            "## Apply the reuse ladder",
            "## Diagnose with evidence",
            "## Choose the smallest fitting design",
            "## Check dependencies and APIs",
            "## Use metrics as signals",
            "## Respect language semantics",
            "## Verify proportionally",
            "## Enforce guardrails",
        )
        for heading in required:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_main_skill_relative_links_exist(self) -> None:
        _, body = frontmatter(SKILL_FILE)
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)
        self.assertGreaterEqual(len(links), 10)
        for target in links:
            with self.subTest(target=target):
                self.assertFalse(target.startswith(("http://", "https://", "#")))
                self.assertTrue((SKILL_DIR / target).is_file())

    def test_references_cover_language_and_counterexample_routes(self) -> None:
        references = SKILL_DIR / "references"
        for path in references.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if len(text.splitlines()) > 100:
                with self.subTest(contents=path.name):
                    self.assertIn("## Contents", text)

        tooling = (references / "language-tooling.md").read_text("utf-8")
        for ecosystem in (
            "## Python",
            "## JavaScript and TypeScript",
            "## Go",
            "## Rust",
            "## JVM",
            "## .NET",
            "## C and C++",
        ):
            with self.subTest(ecosystem=ecosystem):
                self.assertIn(ecosystem, tooling)
        examples = (SKILL_DIR / "references" / "examples.md").read_text("utf-8")
        for route in ("Intervene:", "Accept:", "Investigate:", "Reject:"):
            self.assertIn(route, examples)

    def test_architecture_views_define_evidence_backed_zoom(self) -> None:
        text = (SKILL_DIR / "references" / "architecture-views.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "sequenceDiagram",
            "stateDiagram-v2",
            "Data-flow diagram",
            "IDEF0",
            "Observed:",
            "Inferred:",
            "Proposed:",
            "Unknown:",
            "as-is",
            "to-be",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_architecture_comparison_defines_aligned_evidence_model(self) -> None:
        text = (
            SKILL_DIR / "references" / "architecture-comparison.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "endpoint-to-endpoint",
            "stable logical IDs",
            "node churn",
            "relation churn",
            "**None:**",
            "**Local:**",
            "**Material:**",
            "**Systemic:**",
            "**Unknown:**",
            "**Not assessed:**",
            "**Demonstrated regression:**",
            "allowed-but-absent",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn("git-scm.com/docs/git-diff", text)
        self.assertIn("doi.org/10.1145/222132.222136", text)

    def test_sources_state_empirical_limits(self) -> None:
        text = (SKILL_DIR / "references" / "sources.md").read_text("utf-8")
        self.assertGreaterEqual(text.count("https://"), 20)
        self.assertIn("preprint", text.lower())
        self.assertIn("Limit", text)
        self.assertIn("Package hallucinations", text)
        for source in (
            "c4model.com",
            "owasp.org",
            "mermaid.js.org",
            "nist.gov",
            "doi.org",
            "git-scm.com",
        ):
            self.assertIn(source, text.lower())

    def test_openai_metadata_has_explicit_invocation(self) -> None:
        text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Architecture Guard"', text)
        self.assertIn("$arch", text)
        self.assertNotRegex(text, r"(?i)\b(?:todo|fixme|tbd)\b")


class PackagingTests(unittest.TestCase):
    MANIFESTS = (
        ROOT / ".codex-plugin" / "plugin.json",
        ROOT / ".claude-plugin" / "plugin.json",
        ROOT / ".cursor-plugin" / "plugin.json",
    )

    def test_manifests_are_thin_and_consistent(self) -> None:
        documents = []
        for path in self.MANIFESTS:
            with self.subTest(path=path):
                document = json.loads(path.read_text(encoding="utf-8"))
                documents.append(document)
                self.assertEqual(document["name"], "arch")
                self.assertEqual(document["skills"], "./skills/")
                self.assertEqual(document["license"], "MIT")
                self.assertNotIn("hooks", document)
                self.assertNotIn("mcpServers", document)
        self.assertEqual({document["version"] for document in documents}, {"0.1.0"})
        self.assertEqual(len({document["description"] for document in documents}), 1)
        self.assertIn("architecture", documents[0]["description"].lower())

    def test_repository_documents_supported_agents(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for product in ("Codex", "Claude Code", "Cursor", "OpenCode"):
            with self.subTest(product=product):
                self.assertIn(product, readme)
        self.assertIn("npx skills add snow-ghost/arch", readme)
        self.assertTrue((ROOT / "LICENSE").is_file())


class EvaluationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = json.loads((ROOT / "evals" / "cases.json").read_text("utf-8"))

    def test_cases_are_unique_and_cover_all_routes(self) -> None:
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 12)
        routes = [case["applicability"] for case in self.cases]
        for route in ("apply", "skip", "clarify"):
            with self.subTest(route=route):
                self.assertGreaterEqual(routes.count(route), 3)
        languages = {case["language"] for case in self.cases}
        self.assertGreaterEqual(len(languages), 8)

    def test_architecture_view_cases_cover_routes_and_notations(self) -> None:
        view_cases = [
            case for case in self.cases if "architecture-view" in case["tags"]
        ]
        self.assertEqual(len(view_cases), 4)
        self.assertEqual(
            {case["applicability"] for case in view_cases},
            {"apply", "skip", "clarify"},
        )
        joined_tags = {tag for case in view_cases for tag in case["tags"]}
        for tag in ("component-graph", "sequence", "dfd", "dynamic-dispatch"):
            self.assertIn(tag, joined_tags)

    def test_architecture_comparison_cases_cover_routes_and_risks(self) -> None:
        comparison_cases = [
            case
            for case in self.cases
            if "architecture-comparison" in case["tags"]
        ]
        self.assertEqual(len(comparison_cases), 3)
        self.assertEqual(
            {case["applicability"] for case in comparison_cases},
            {"apply", "skip", "clarify"},
        )
        joined_tags = {tag for case in comparison_cases for tag in case["tags"]}
        for tag in ("conformance", "rename", "dynamic-dispatch"):
            self.assertIn(tag, joined_tags)

    def test_cases_have_actionable_oracles(self) -> None:
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertRegex(case["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertGreater(len(case["prompt"]), 100)
                self.assertIn(case["applicability"], {"apply", "skip", "clarify"})
                expected = case["expected"]
                self.assertGreaterEqual(len(expected["must_address"]), 4)
                self.assertGreaterEqual(len(expected["failure_modes"]), 4)

    def test_eval_scripts_and_rubric_exist(self) -> None:
        for relative in (
            "evals/run_eval.py",
            "evals/build_blind_pairs.py",
            "evals/run_judge.py",
            "evals/score_judgments.py",
            "evals/rubric.md",
            "evals/README.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())
        rubric = (ROOT / "evals" / "rubric.md").read_text(encoding="utf-8")
        self.assertIn("architecture_theater", rubric)
        self.assertIn("architecture_view_accuracy", rubric)
        self.assertIn("Critical Errors", rubric)
        self.assertIn("stable logical IDs", rubric)
        self.assertIn("structural delta", rubric)
        self.assertIn("degradation percentage", rubric)


if __name__ == "__main__":
    unittest.main()
