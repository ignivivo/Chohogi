#!/usr/bin/env python3
"""Regression tests for strict semantic interpretation of active declarations."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tooling" / "verify-semantic-assurance.py"
sys.path.insert(0, str(ROOT / "tooling"))
from semantic_contracts import SemanticContractError, strict_json, strict_yaml  # noqa: E402


class SemanticAssuranceTests(unittest.TestCase):
    def run_skill_check(self, reusable_root: Path, adaptive_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--skills-only",
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

    def write_skill(self, root: Path, name: str, frontmatter: str) -> None:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\nmethod\n", encoding="utf-8")

    def test_duplicate_frontmatter_key_fails_even_when_the_marker_text_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            reusable, adaptive = base / "reusable", base / "adaptive"
            self.write_skill(
                reusable,
                "sample",
                "name: sample\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory\nmetadata:\n  author: overwritten",
            )
            self.write_skill(adaptive, "adaptive-sample", "name: adaptive-sample\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory")
            result = self.run_skill_check(reusable, adaptive)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate YAML key", result.stderr)

    def test_missing_parsed_assurance_marker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            reusable, adaptive = base / "reusable", base / "adaptive"
            self.write_skill(reusable, "sample", "name: sample\ndescription: sample\nmetadata: {}")
            self.write_skill(adaptive, "adaptive-sample", "name: adaptive-sample\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory")
            result = self.run_skill_check(reusable, adaptive)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metadata.chohogi_assurance", result.stderr)

    def test_valid_frontmatter_passes_strict_interpretation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            reusable, adaptive = base / "reusable", base / "adaptive"
            self.write_skill(reusable, "sample", "name: sample\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory")
            self.write_skill(adaptive, "adaptive-sample", "name: adaptive-sample\ndescription: sample\nmetadata:\n  chohogi_assurance: advisory")
            result = self.run_skill_check(reusable, adaptive)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_keys_fail_for_json_and_nested_yaml_mappings(self) -> None:
        with self.assertRaisesRegex(SemanticContractError, "duplicate JSON key"):
            strict_json('{"contract": {"id": "first", "id": "overwritten"}}')
        with self.assertRaisesRegex(SemanticContractError, "duplicate YAML key"):
            strict_yaml("contract:\n  nested:\n    id: first\n    id: overwritten\n")

    def test_registry_cannot_drop_a_declared_surface(self) -> None:
        registry = json.loads((ROOT / "assets/agents/functional_assurance/semantic-contract-registry.json").read_text())
        target = next(item for item in registry["contracts"] if item["id"] == "active-json-declarations")
        target["roots"] = ["assets"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "semantic-contract-registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VERIFIER), "--registry", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active-json-declarations: roots", result.stderr)


if __name__ == "__main__":
    unittest.main()
