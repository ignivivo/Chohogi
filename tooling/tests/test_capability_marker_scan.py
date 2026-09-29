#!/usr/bin/env python3
"""Behavior tests for the standalone absorbed-provider marker scanner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / "tooling" / "verify-installed-capability-markers.py"
MARKERS_FILE = ROOT / "tooling" / "retired-capability-markers.json"


class CapabilityMarkerScanTests(unittest.TestCase):
    def run_scanner(self, home: Path, markers_file: Path | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCANNER), "--home", str(home)]
        if markers_file is not None:
            command.extend(("--markers-file", str(markers_file)))
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_declared_markers_file_is_valid_and_nonempty(self) -> None:
        declared = json.loads(MARKERS_FILE.read_text(encoding="utf-8"))
        self.assertIsInstance(declared.get("markers"), list)
        self.assertTrue(declared["markers"])
        for entry in declared["markers"]:
            self.assertIsInstance(entry["marker"], str)
            self.assertTrue(entry["marker"].strip())

    def test_pass_when_installed_tree_has_no_marker(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            home_path = Path(home)
            installed = home_path / ".agents" / "chohogi" / "trunk_orchestration"
            installed.mkdir(parents=True)
            (installed / "conductor.md").write_text("no forbidden names here\n", encoding="utf-8")
            result = self.run_scanner(home_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_fail_when_installed_tree_contains_a_declared_marker(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            home_path = Path(home)
            installed = home_path / ".agents" / "chohogi" / "trunk_orchestration"
            installed.mkdir(parents=True)
            (installed / "document-lifecycle.md").write_text(
                "this plan absorbed patterns from Superpowers directly\n", encoding="utf-8"
            )
            result = self.run_scanner(home_path)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any("superpowers" in finding for finding in payload["findings"]))

    def test_exempt_path_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as markers_dir, tempfile.TemporaryDirectory() as home:
            markers_path = Path(markers_dir) / "retired-capability-markers.json"
            markers_path.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "markers": [
                            {"marker": "superpowers", "exemptPaths": ["trunk_orchestration/capability-selection.md"]}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            home_path = Path(home)
            installed = home_path / ".agents" / "chohogi" / "trunk_orchestration"
            installed.mkdir(parents=True)
            (installed / "capability-selection.md").write_text(
                "superpowers is named here only to deny it\n", encoding="utf-8"
            )
            result = self.run_scanner(home_path, markers_file=markers_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_current_installed_runtime_passes_if_present(self) -> None:
        runtime_home = Path.home()
        if not (runtime_home / ".agents" / "chohogi").is_dir():
            self.skipTest("no installed Chohogi runtime under the current HOME")
        result = self.run_scanner(runtime_home)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
