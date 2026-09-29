#!/usr/bin/env python3
"""Behavior tests for active-skill resource integrity."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tooling" / "verify-skills.py"


class SkillResourceIntegrityTests(unittest.TestCase):
    def run_verifier(self, skill_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--skill-root", str(skill_root)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_skill(self, root: Path, name: str, body: str = "") -> Path:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory\n---\n{body}\n",
            encoding="utf-8",
        )
        return skill

    def test_rejects_a_broken_local_resource_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_skill(root, "sample", "[missing](references/missing.md)")
            self.make_skill(root, "adaptive-sample", "method")
            result = self.run_verifier(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing local reference", result.stdout)
        self.assertIn("sample", result.stdout)

    def test_accepts_a_reachable_local_resource_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sample = self.make_skill(root, "sample", "[guide](references/guide.md)")
            (sample / "references").mkdir()
            (sample / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            self.make_skill(root, "adaptive-sample", "method")
            result = self.run_verifier(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_long_skill_emits_a_review_signal_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body = "\n".join("instruction" for _ in range(501))
            self.make_skill(root, "long-sample", body)
            self.make_skill(root, "adaptive-sample", "method")
            result = self.run_verifier(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("review signal", result.stdout)
        self.assertIn("long-sample", result.stdout)


if __name__ == "__main__":
    unittest.main()
