#!/usr/bin/env python3
"""Regression tests for project-attached external capability contracts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "tooling" / "verify-external-capability-contract.py"
RETIREMENT = ROOT / "tooling" / "verify-retired-capability.py"


class ExternalCapabilityContractTests(unittest.TestCase):
    def write_contract(self, project: Path, conflicts: list[dict[str, str]]) -> None:
        directory = project / ".agents"
        directory.mkdir(parents=True)
        (directory / "chohogi-external-capabilities.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "capabilities": [
                        {
                            "id": "external-review",
                            "provider": "third-party-review",
                            "state": "attach-specialist",
                            "purpose": "Independent static analysis for this project.",
                            "trigger": "A selected review needs this provider's analysis.",
                            "nonTrigger": "It does not select workflow or completion.",
                            "allowedActions": ["read repository", "return findings"],
                            "prohibitedControllerClaims": ["artifact-path", "commit", "workflow", "completion"],
                            "conflicts": conflicts,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_attached_capability_reports_declared_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_contract(project, [{"externalRequirement": "writes its own report", "chohogiResolution": "use project work log", "userReport": "Report before use."}])
            result = subprocess.run([sys.executable, str(CONTRACT), "--project", str(project)], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("USER-REPORT", result.stdout)

    def test_attached_capability_rejects_controller_claim_not_declared_prohibited(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            self.write_contract(project, [])
            path = project / ".agents" / "chohogi-external-capabilities.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["capabilities"][0]["prohibitedControllerClaims"].remove("commit")
            path.write_text(json.dumps(document), encoding="utf-8")
            result = subprocess.run([sys.executable, str(CONTRACT), "--project", str(project)], text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing prohibited controller claims", result.stderr)

    def test_retirement_scan_covers_hidden_document_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            path = project / ".hidden" / "docs" / "retired-provider.txt"
            path.parent.mkdir(parents=True)
            path.write_text("Retired-Provider output\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(RETIREMENT), "--root", str(project), "--forbid", "retired-provider"], text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".hidden/docs/retired-provider.txt", result.stderr)


if __name__ == "__main__":
    unittest.main()
