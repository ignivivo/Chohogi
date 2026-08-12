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
DOCTOR = ROOT / "tooling" / "doctor.sh"
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

    def test_doctor_reports_registry_state_without_running_audit(self) -> None:
        doctor_source = DOCTOR.read_text(encoding="utf-8")
        self.assertNotIn("Deprecated", doctor_source)
        self.assertNotIn("graft-compatibility", doctor_source)
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
                ["bash", str(DOCTOR), "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = __import__("json").loads(result.stdout)
        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["installed"]["layoutVersion"], 2)
        self.assertTrue(report["registry"]["digestMatches"])
        self.assertEqual(report["components"]["missingActive"], [])
        self.assertEqual(report["components"]["unexpectedRetired"], [])
        self.assertNotIn("audit", result.stdout.lower())

    def test_doctor_reports_missing_active_component(self) -> None:
        self.build_genome_map()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_home = Path(temporary_directory)
            subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT, text=True, capture_output=True, check=True,
            )
            (target_home / ".agents" / "skills" / "performance").rename(
                target_home / ".agents" / "skills" / "performance-missing"
            )
            result = subprocess.run(
                ["bash", str(DOCTOR), "--home", str(target_home)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
        self.assertEqual(result.returncode, 1)
        report = __import__("json").loads(result.stdout)
        self.assertEqual(report["status"], "drift")
        self.assertIn(".agents/skills/performance", report["components"]["missingActive"])

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

    def test_installer_retires_every_manifest_declared_owned_skill(self) -> None:
        self.build_genome_map()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_home = Path(temporary_directory)
            retired = [
                target_home / ".agents" / "skills" / "frontend-surface",
                target_home / ".agents" / "skills" / "react-async-state-safety",
            ]
            for skill in retired:
                skill.mkdir(parents=True)
                (skill / ".chohogi-owner.json").write_text('{"package":"chohogi"}\n', encoding="utf-8")
                (skill / "SKILL.md").write_text("legacy\n", encoding="utf-8")
            install = subprocess.run(
                ["bash", "tooling/install.sh", "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            self.assertTrue(all(not skill.exists() for skill in retired))
            audit = subprocess.run(
                ["bash", str(AUDIT), "--home", str(target_home)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(audit.returncode, 0, audit.stderr)


if __name__ == "__main__":
    unittest.main()
