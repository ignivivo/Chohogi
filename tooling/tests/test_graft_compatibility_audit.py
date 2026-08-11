#!/usr/bin/env python3
"""Behavior tests for the post-install graft compatibility audit commands."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "tooling" / "graft-compatibility_install-audit.sh"
LEGACY = ROOT / "tooling" / "doctor.sh"
GENOME_MAP = ROOT / "tooling" / "genome_map.py"


class GraftCompatibilityAuditTests(unittest.TestCase):
    def build_genome_map(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GENOME_MAP), "build"], cwd=ROOT, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_canonical_audit_accepts_a_clean_installation(self) -> None:
        self.build_genome_map()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_home = Path(temporary_directory)
            install = subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            result = subprocess.run(
                ["bash", str(AUDIT), "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Graft compatibility installation audit: PASS", result.stdout)

    def test_legacy_doctor_wrapper_warns_and_preserves_audit_result(self) -> None:
        self.build_genome_map()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_home = Path(temporary_directory)
            subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            result = subprocess.run(
                ["bash", str(LEGACY), "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("deprecated", result.stderr.lower())
        self.assertIn("Graft compatibility installation audit: PASS", result.stdout)

    def test_v1_migration_preserves_owned_tree_and_retires_grill_me(self) -> None:
        self.build_genome_map()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_home = Path(temporary_directory)
            old_root = target_home / ".agents" / "chohogi"
            old_root.mkdir(parents=True)
            (old_root / ".chohogi-owner.json").write_text('{"package":"chohogi"}\n', encoding="utf-8")
            (old_root / "legacy-proof.txt").write_text("v1\n", encoding="utf-8")
            grill = target_home / ".agents" / "skills" / "grill-me"
            grill.mkdir(parents=True)
            (grill / ".chohogi-owner.json").write_text('{"package":"chohogi"}\n', encoding="utf-8")
            (grill / "SKILL.md").write_text("legacy\n", encoding="utf-8")
            install = subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            backups = list((target_home / ".agents" / "chohogi-backups").glob("layout-v1-*"))
            self.assertEqual(len(backups), 1)
            self.assertTrue((backups[0] / "chohogi" / "legacy-proof.txt").is_file())
            self.assertTrue((backups[0] / "skills" / "grill-me" / "SKILL.md").is_file())
            self.assertFalse(grill.exists())
            audit = subprocess.run(
                ["bash", str(AUDIT), "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(audit.returncode, 0, audit.stderr)
            reinstall = subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(reinstall.returncode, 0, reinstall.stderr)
            self.assertEqual(len(list((target_home / ".agents" / "chohogi-backups").glob("layout-v1-*"))), 1)


if __name__ == "__main__":
    unittest.main()
