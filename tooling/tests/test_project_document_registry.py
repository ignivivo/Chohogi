from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/verify-project-document-registry.py"


class ProjectDocumentRegistryTests(unittest.TestCase):
    def run_registry(self, registry: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "plan.md").write_text("active\n", encoding="utf-8")
            (project / "history.md").write_text("history\n", encoding="utf-8")
            path = project / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOL), "--root", str(project), "--registry", str(path)], text=True, capture_output=True, check=False)

    def test_single_active_plan_and_superseded_target_pass(self) -> None:
        result = self.run_registry({"schemaVersion": 1, "activeExecutionPlan": "plan.md", "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active"},
            {"path": "history.md", "role": "history", "authority": "evidence", "state": "historical", "supersededBy": "plan.md"},
        ]})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_superseded_target_must_be_active_plan(self) -> None:
        result = self.run_registry({"schemaVersion": 1, "activeExecutionPlan": "plan.md", "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active"},
            {"path": "history.md", "role": "history", "authority": "evidence", "state": "historical", "supersededBy": "missing.md"},
        ]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supersededBy", result.stdout)

    def run_with_record(self, registry: dict[str, object], verification: dict[str, object] | None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "plan.md").write_text("active\n", encoding="utf-8")
            (project / "history.md").write_text("history\n", encoding="utf-8")
            record = project / "records/WORK-1"
            record.mkdir(parents=True)
            if verification is not None:
                (record / "verification.json").write_text(json.dumps(verification), encoding="utf-8")
            path = project / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOL), "--root", str(project), "--registry", str(path)], text=True, capture_output=True, check=False)

    def test_no_active_plan_can_be_declared_explicitly(self) -> None:
        result = self.run_registry({"schemaVersion": 1, "activeExecutionPlan": None, "documents": [
            {"path": "plan.md", "role": "history", "authority": "evidence", "state": "historical"},
            {"path": "history.md", "role": "history", "authority": "evidence", "state": "historical", "supersededBy": "plan.md"},
        ]})
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_active_plan_key_is_still_required(self) -> None:
        result = self.run_registry({"schemaVersion": 1, "documents": [
            {"path": "plan.md", "role": "history", "authority": "evidence", "state": "historical"},
        ]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("activeExecutionPlan", result.stdout)

    def test_null_active_plan_rejects_an_active_plan_entry(self) -> None:
        result = self.run_registry({"schemaVersion": 1, "activeExecutionPlan": None, "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active"},
        ]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("activeExecutionPlan", result.stdout)

    def test_active_plan_with_finalized_record_fails(self) -> None:
        result = self.run_with_record({"schemaVersion": 1, "activeExecutionPlan": "plan.md", "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active", "executionRecord": "records/WORK-1"},
            {"path": "records/WORK-1", "role": "execution-record", "authority": "evidence", "state": "historical"},
        ]}, {"status": "pass"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("finalized", result.stdout)

    def test_active_plan_with_open_record_passes(self) -> None:
        result = self.run_with_record({"schemaVersion": 1, "activeExecutionPlan": "plan.md", "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active", "executionRecord": "records/WORK-1"},
            {"path": "records/WORK-1", "role": "execution-record", "authority": "evidence", "state": "active"},
        ]}, None)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_active_plan_execution_record_must_be_declared(self) -> None:
        result = self.run_with_record({"schemaVersion": 1, "activeExecutionPlan": "plan.md", "documents": [
            {"path": "plan.md", "role": "active-plan", "authority": "execution-queue", "state": "active", "executionRecord": "records/WORK-1"},
        ]}, None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("executionRecord", result.stdout)

    def test_active_execution_record_entry_that_is_finalized_fails(self) -> None:
        result = self.run_with_record({"schemaVersion": 1, "activeExecutionPlan": None, "documents": [
            {"path": "plan.md", "role": "history", "authority": "evidence", "state": "historical"},
            {"path": "records/WORK-1", "role": "execution-record", "authority": "evidence", "state": "active"},
        ]}, {"status": "pass"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("finalized", result.stdout)

    def test_nested_project_plan_directories_are_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            plans = project / "docs/chohogi/plans"
            plans.mkdir(parents=True)
            (plans / "active.md").write_text("active\n", encoding="utf-8")
            (plans / "unregistered.md").write_text("unregistered\n", encoding="utf-8")
            registry = project / "registry.json"
            registry.write_text(json.dumps({"schemaVersion": 1, "activeExecutionPlan": "docs/chohogi/plans/active.md", "documents": [
                {"path": "docs/chohogi/plans/active.md", "role": "active-plan", "authority": "execution-queue", "state": "active"},
            ]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(TOOL), "--root", str(project), "--registry", str(registry)], text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/chohogi/plans/unregistered.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
