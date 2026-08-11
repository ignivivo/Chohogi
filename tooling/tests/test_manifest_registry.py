#!/usr/bin/env python3
"""Behavior tests for the Chohogi manifest registry resolver."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESOLVER = ROOT / "tooling" / "manifest_registry.py"


class ManifestRegistryTests(unittest.TestCase):
    def run_resolver(self, *arguments: str, manifest: Path | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(RESOLVER)]
        if manifest is not None:
            command.extend(("--manifest", str(manifest)))
        command.extend(arguments)
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_validate_accepts_the_repository_manifest(self) -> None:
        result = self.run_resolver("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "valid")

    def test_active_components_exclude_retired_component(self) -> None:
        result = self.run_resolver("components", "--ownership", "managed")
        self.assertEqual(result.returncode, 0, result.stderr)
        component_ids = {item["id"] for item in json.loads(result.stdout)["components"]}
        self.assertIn("chohogi-organs", component_ids)
        self.assertNotIn("grill-me", component_ids)

    def test_install_plan_expands_only_active_managed_assets(self) -> None:
        result = self.run_resolver("install-plan")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)["actions"]
        destinations = {item["destination"] for item in plan}
        self.assertIn(".agents/chohogi", destinations)
        self.assertIn(".agents/skills/accessibility", destinations)
        self.assertIn(".agents/skills/homeostasis", destinations)
        self.assertNotIn(".agents/skills/grill-me", destinations)

    def test_validate_rejects_duplicate_active_destination(self) -> None:
        document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        duplicate = dict(document["components"][0])
        duplicate["id"] = "duplicate-global-guidance"
        document["components"].append(duplicate)
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = Path(temporary_directory) / "manifest.json"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_resolver("validate", manifest=manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate active destination", result.stderr)

    def test_validate_rejects_source_outside_repository_root(self) -> None:
        document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        document["components"][0]["source"] = "../outside.md"
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = Path(temporary_directory) / "manifest.json"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_resolver("validate", manifest=manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source escapes repository root", result.stderr)


if __name__ == "__main__":
    unittest.main()
