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

    def test_components_declare_a_real_plugin_slot_for_active_managed_assets(self) -> None:
        result = self.run_resolver("components", "--ownership", "managed")
        self.assertEqual(result.returncode, 0, result.stderr)
        components = {item["id"]: item for item in json.loads(result.stdout)["components"]}
        self.assertEqual(components["chohogi-organs"]["pluginSlot"], "policy")
        self.assertEqual(components["critical-reviewer-role"]["pluginSlot"], "agents")
        self.assertEqual(components["reusable-methods"]["pluginSlot"], "skills")
        self.assertEqual(components["reusable-methods"]["source"], "skills")

    def test_validate_rejects_duplicate_component_id(self) -> None:
        document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        duplicate = dict(document["components"][0])
        document["components"].append(duplicate)
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = Path(temporary_directory) / "manifest.json"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_resolver("validate", manifest=manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate component id", result.stderr)

    def test_validate_rejects_source_outside_repository_root(self) -> None:
        document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        document["components"][0]["source"] = "../outside.md"
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = Path(temporary_directory) / "manifest.json"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_resolver("validate", manifest=manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source escapes repository root", result.stderr)

    def test_validate_rejects_a_retired_component_with_a_missing_source(self) -> None:
        document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        retired = next(item for item in document["components"] if item["ownership"] == "retired")
        retired["source"] = "assets/missing-retired-source"
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = Path(temporary_directory) / "manifest.json"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_resolver("validate", manifest=manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retired source does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
