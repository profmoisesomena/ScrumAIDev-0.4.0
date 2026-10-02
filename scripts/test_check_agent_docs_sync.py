#!/usr/bin/env python3
"""Unit tests for check_agent_docs_sync.py.

Run with: python -m unittest scripts.test_check_agent_docs_sync -v
(from the repository root)
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_agent_docs_sync as checker  # noqa: E402


class TempRootTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".agents" / "workflows").mkdir(parents=True)
        (self.root / ".agents" / "skills").mkdir(parents=True)
        self._original_root = checker.ROOT
        checker.ROOT = self.root

    def tearDown(self) -> None:
        checker.ROOT = self._original_root
        self._tmp.cleanup()

    def make_workflow(self, name: str) -> None:
        (self.root / ".agents" / "workflows" / f"{name}.md").write_text("---\ndescription: x\n---\n")

    def make_skill(self, name: str) -> None:
        skill_dir = self.root / ".agents" / "skills" / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: x\n---\n")

    def write_docs(self, readme_text: str, agents_text: str) -> None:
        (self.root / "README.md").write_text(readme_text)
        (self.root / "AGENTS.md").write_text(agents_text)


class DocsSyncTests(TempRootTestCase):
    def test_no_workflows_or_skills_returns_zero(self) -> None:
        self.write_docs("nothing", "nothing")
        self.assertEqual(checker.main(), 0)

    def test_fully_documented_returns_zero(self) -> None:
        self.make_workflow("deploy")
        self.make_skill("architect")
        self.write_docs("Use /deploy and architect here", "Use /deploy and architect here")
        self.assertEqual(checker.main(), 0)

    def test_missing_workflow_in_readme_returns_one(self) -> None:
        self.make_workflow("deploy")
        self.write_docs("nothing here", "/deploy mentioned here")
        self.assertEqual(checker.main(), 1)

    def test_missing_skill_in_agents_returns_one(self) -> None:
        self.make_skill("architect")
        self.write_docs("architect mentioned here", "nothing here")
        self.assertEqual(checker.main(), 1)

    def test_missing_from_both_docs_returns_one(self) -> None:
        self.make_workflow("deploy")
        self.write_docs("nothing here", "nothing here either")
        self.assertEqual(checker.main(), 1)

    def test_self_clone_instruction_in_contributing_returns_one(self) -> None:
        self.write_docs("nothing here", "nothing here")
        (self.root / "CONTRIBUTING.md").write_text(
            "# Contributing\n\ngit clone https://github.com/example/scrumaidev.git meu-projeto\n"
        )
        self.assertEqual(checker.main(), 1)

    def test_self_clone_instruction_in_context_doc_returns_one(self) -> None:
        self.write_docs("nothing here", "nothing here")
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "docs" / "context.md").write_text(
            "O ScrumAIDev normalmente e instanciado via `git clone`.\n"
        )
        self.assertEqual(checker.main(), 1)

    def test_unrelated_git_clone_is_not_flagged(self) -> None:
        self.write_docs("nothing here", "nothing here")
        (self.root / "CONTRIBUTING.md").write_text(
            "# Contributing\n\ngit clone https://github.com/example/some-other-repo.git\n"
        )
        self.assertEqual(checker.main(), 0)


class FindMissingTests(unittest.TestCase):
    def test_reports_every_absent_doc(self) -> None:
        docs = {"README.md": "no mention", "AGENTS.md": "no mention"}
        missing = checker.find_missing({"/foo"}, docs)
        self.assertEqual(missing, {"/foo": ["README.md", "AGENTS.md"]})

    def test_present_in_all_docs_is_not_reported(self) -> None:
        docs = {"README.md": "/foo here", "AGENTS.md": "/foo here"}
        self.assertEqual(checker.find_missing({"/foo"}, docs), {})


class FindStaleSelfCloneInstructionsTests(unittest.TestCase):
    def test_flags_git_clone_of_own_repo(self) -> None:
        docs = {"CONTRIBUTING.md": "git clone https://github.com/example/scrumaidev.git\n"}
        findings = checker.find_stale_self_clone_instructions(docs)
        self.assertIn("CONTRIBUTING.md", findings)

    def test_flags_agileaidev_name_too(self) -> None:
        docs = {"docs/context.md": "instanciado via git clone do AgileAIDev\n"}
        findings = checker.find_stale_self_clone_instructions(docs)
        self.assertIn("docs/context.md", findings)

    def test_does_not_flag_unrelated_git_clone(self) -> None:
        docs = {"CONTRIBUTING.md": "git clone https://github.com/example/other-repo.git\n"}
        self.assertEqual(checker.find_stale_self_clone_instructions(docs), {})

    def test_does_not_flag_framework_name_without_git_clone(self) -> None:
        docs = {"README.md": "ScrumAIDev e um framework instalavel via CLI.\n"}
        self.assertEqual(checker.find_stale_self_clone_instructions(docs), {})


if __name__ == "__main__":
    unittest.main()
