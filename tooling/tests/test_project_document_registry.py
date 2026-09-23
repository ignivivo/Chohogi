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
