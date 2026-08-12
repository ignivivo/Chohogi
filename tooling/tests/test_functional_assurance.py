#!/usr/bin/env python3
"""Behavior tests for functional claim-to-evidence assurance."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/verify-functional-assurance.py"
REGISTRY = ROOT / "assets/agents/functional_assurance/registry.json"


class FunctionalAssuranceTests(unittest.TestCase):
    def run_verifier(self, registry: Path | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(TOOL)]
        if registry is not None:
            command.extend(("--registry", str(registry)))
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_repository_registry_covers_active_organs_skills_and_tools(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deterministic_claim_without_fixture_is_rejected(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        target = next(item for item in registry["assurances"] if item["kind"] == "deterministic-check")
        target["fixtures"] = []
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "functional-assurance.json"
            mutated.write_text(json.dumps(registry), encoding="utf-8")
            result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixtures must be a non-empty list", result.stderr)

    def test_uncovered_tooling_command_is_rejected(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        tools = next(item for item in registry["assurances"] if item["id"] == "verification-and-topology-tools")
        tools["sources"].remove("tooling/verify-routes.py")
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "functional-assurance.json"
            mutated.write_text(json.dumps(registry), encoding="utf-8")
            result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("uncovered tooling commands", result.stderr)

    def test_skill_assurance_marker_must_match_its_registry_claim(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        methods = next(item for item in registry["assurances"] if item["id"] == "accessibility-method")
        methods["kind"] = "reference"
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "functional-assurance.json"
            mutated.write_text(json.dumps(registry), encoding="utf-8")
            result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("chohogi-assurance marker must match registry kind", result.stderr)

    def test_each_active_skill_requires_its_own_assurance_record(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        target = next(item for item in registry["assurances"] if item["id"] == "accessibility-method")
        target["sources"] = ["assets/agents/reusable_methods"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "functional-assurance.json"
            mutated.write_text(json.dumps(registry), encoding="utf-8")
            result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must map to exactly one assurance record", result.stderr)


if __name__ == "__main__":
    unittest.main()
