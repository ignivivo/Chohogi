#!/usr/bin/env python3
"""Behavioral regression tests for project-owned security gates and skill intake."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tooling/run-security-gate.py"
INTAKE = ROOT / "tooling/scan-skill-intake.py"
BOUNDARY = ROOT / "tooling/verify-security-boundary.py"
CLASSIFIER = ROOT / "tooling/classify-security-boundary.py"


class SecurityGateTests(unittest.TestCase):
    def write_plan(self, directory: Path, checks: list[dict[str, object]]) -> Path:
        plan = directory / "security-gate.json"
        plan.write_text(json.dumps({"schemaVersion": 1, "checks": checks}), encoding="utf-8")
        return plan

    def run_gate(self, project: Path, plan: Path, output: Path, execute: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(GATE), "--project", str(project), "--plan", str(plan), "--output", str(output)]
        if execute:
            command.append("--execute")
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_gate_records_a_real_passing_check_and_required_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            plan = self.write_plan(project, [{
                "id": "secret-scan",
                "kind": "secret-scan",
                "command": [sys.executable, "-c", "from pathlib import Path; Path('secret-report.json').write_text('{}')"],
                "requiredArtifacts": ["secret-report.json"],
            }])
            output = project / "security-observation.json"
            result = self.run_gate(project, plan, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            observation = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(observation["status"], "pass")
            self.assertEqual(observation["checks"][0]["status"], "pass")

    def test_gate_fails_when_scanner_fails_even_if_a_report_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            plan = self.write_plan(project, [{
                "id": "sast",
                "kind": "sast",
                "command": [sys.executable, "-c", "from pathlib import Path; Path('sast.json').write_text('{}'); raise SystemExit(7)"],
                "requiredArtifacts": ["sast.json"],
            }])
            output = project / "security-observation.json"
            result = self.run_gate(project, plan, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["checks"][0]["status"], "fail")

    def test_gate_fails_when_a_passing_command_omits_its_required_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            plan = self.write_plan(project, [{
                "id": "dependency-scan",
                "kind": "dependency-scan",
                "command": [sys.executable, "-c", "raise SystemExit(0)"],
                "requiredArtifacts": ["dependency-report.json"],
            }])
            output = project / "security-observation.json"
            result = self.run_gate(project, plan, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missingArtifacts", json.loads(output.read_text(encoding="utf-8"))["checks"][0])

    def test_gate_never_executes_a_project_plan_without_explicit_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            plan = self.write_plan(project, [{
                "id": "secret-scan",
                "kind": "secret-scan",
                "command": [sys.executable, "-c", "raise SystemExit(0)"],
                "requiredArtifacts": [],
            }])
            result = self.run_gate(project, plan, project / "security-observation.json", execute=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--execute", result.stderr)

    def test_intake_inventories_scripts_and_resources_and_rejects_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "skill"
            (root / "scripts").mkdir(parents=True)
            (root / "references").mkdir()
            (root / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n[guide](references/guide.md)\n", encoding="utf-8")
            (root / "scripts/check.py").write_text("print('scan me')\n", encoding="utf-8")
            (root / "references/guide.md").write_text("https://example.com/reference\n", encoding="utf-8")
            output = root / "intake.json"
            result = subprocess.run([sys.executable, str(INTAKE), str(root), "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("scripts/check.py", [item["path"] for item in report["files"]])
            self.assertIn("https://example.com/reference", report["externalReferences"])
            (root / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n[missing](references/missing.md)\n", encoding="utf-8")
            failed = subprocess.run([sys.executable, str(INTAKE), str(root), "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("missing local references", failed.stderr)

    def test_intake_can_inventory_a_full_repository_with_a_selected_entry_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            entry = root / "nested/SKILL.md"
            entry.parent.mkdir()
            (entry.parent / "references").mkdir()
            (entry.parent / "scripts").mkdir()
            entry.write_text(
                "---\nname: nested\ndescription: nested\n---\n"
                "[reference directory](references/)\n"
                "[guide](references/guide.md)\n",
                encoding="utf-8",
            )
            (entry.parent / "references/guide.md").write_text("guide\n", encoding="utf-8")
            (entry.parent / "scripts/check.js").write_text("console.log('scan me');\n", encoding="utf-8")
            (root / "shared-play.md").write_text("shared resource\n", encoding="utf-8")
            output = root / "intake.json"
            result = subprocess.run([sys.executable, str(INTAKE), str(root), "--entry", "nested/SKILL.md", "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["entry"], "nested/SKILL.md")
            self.assertIn("shared-play.md", [item["path"] for item in report["files"]])
            self.assertEqual(report["directoryReferences"], [{"source": "nested/SKILL.md", "target": "nested/references"}])
            self.assertTrue(report["coverage"]["containsReferences"])
            self.assertTrue(report["coverage"]["containsScripts"])
            self.assertEqual(report["coverage"]["executableFileCount"], 1)

    def test_intake_attributes_an_escaping_reference_to_its_actual_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            entry = root / "nested/SKILL.md"
            entry.parent.mkdir()
            entry.write_text("---\nname: nested\ndescription: nested\n---\n[escape](../../outside.md)\n", encoding="utf-8")
            output = root / "intake.json"
            result = subprocess.run([sys.executable, str(INTAKE), str(root), "--entry", "nested/SKILL.md", "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reference escapes intake root: nested/SKILL.md -> ../../outside.md", result.stderr)

    def test_intake_accepts_and_records_an_internal_symlinked_resource(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n", encoding="utf-8")
            (root / "real.md").write_text("resource\n", encoding="utf-8")
            os.symlink(root / "real.md", root / "references.md")
            output = root / "intake.json"
            result = subprocess.run([sys.executable, str(INTAKE), str(root), "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["symlinks"][0]["path"], "references.md")
            self.assertEqual(report["symlinks"][0]["target"], "real.md")
            self.assertEqual(report["symlinks"][0]["kind"], "internal")
            self.assertIn("targetSha256", report["symlinks"][0])

    def test_intake_rejects_a_symlink_outside_the_payload_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            (root / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n", encoding="utf-8")
            target = Path(outside) / "outside.md"
            target.write_text("outside\n", encoding="utf-8")
            os.symlink(target, root / "escape.md")
            output = root / "intake.json"
            result = subprocess.run([sys.executable, str(INTAKE), str(root), "--output", str(output)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink escapes intake root", result.stderr)

    def test_security_boundary_rejects_a_risk_fixture_without_pre_code_disposition(self) -> None:
        fixtures = ROOT / "assets/agents/security_immune_system/boundary-fixtures.json"
        document = json.loads(fixtures.read_text(encoding="utf-8"))
        target = next(item for item in document["fixtures"] if item["id"] == "agent-tool-change")
        target["expectedDisposition"] = "no-special-security-boundary"
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "security-boundary.json"
            mutated.write_text(json.dumps(document), encoding="utf-8")
            result = subprocess.run([sys.executable, str(BOUNDARY), "--fixtures", str(mutated)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must require pre-code security acceptance", result.stderr)

    def test_classifier_requires_pre_code_acceptance_for_agent_tool_risk(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "profile.json"
            profile.write_text(json.dumps({"riskSignals": ["agent-tool", "external-fetch"]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(CLASSIFIER), str(profile)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            observation = json.loads(result.stdout)
            self.assertEqual(observation["disposition"], "pre-code-security-acceptance")
            self.assertIn("prompt-injection-tests", observation["requirements"])
            self.assertIn("ssrf-controls", observation["requirements"])

    def test_classifier_rejects_an_unknown_risk_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "profile.json"
            profile.write_text(json.dumps({"riskSignals": ["imaginary-risk"]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(CLASSIFIER), str(profile)], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown risk signals", result.stderr)


if __name__ == "__main__":
    unittest.main()
