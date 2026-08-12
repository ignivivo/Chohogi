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
    def run_verifier(self, reusable_root: Path, adaptive_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--reusable-root",
                str(reusable_root),
                "--adaptive-root",
                str(adaptive_root),
            ],
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
            base = Path(temporary)
            reusable = base / "reusable"
            adaptive = base / "adaptive"
            self.make_skill(reusable, "sample", "[missing](references/missing.md)")
            self.make_skill(adaptive, "adaptive-sample", "method")
            result = self.run_verifier(reusable, adaptive)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing local reference", result.stdout)
        self.assertIn("sample", result.stdout)

    def test_accepts_a_reachable_local_resource_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            reusable = base / "reusable"
            adaptive = base / "adaptive"
            sample = self.make_skill(reusable, "sample", "[guide](references/guide.md)")
            (sample / "references").mkdir()
            (sample / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            self.make_skill(adaptive, "adaptive-sample", "method")
            result = self.run_verifier(reusable, adaptive)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
