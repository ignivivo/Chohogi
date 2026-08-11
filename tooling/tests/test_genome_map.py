#!/usr/bin/env python3
"""Behavior tests for Chohogi's source-derived genome map."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling" / "genome_map.py"


class GenomeMapTests(unittest.TestCase):
    def run_map(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TOOL), *arguments], cwd=ROOT, text=True, capture_output=True, check=False
        )

    def test_build_emits_machine_graph_with_active_skill_and_document_edges(self) -> None:
        result = self.run_map("build", "--stdout")
        self.assertEqual(result.returncode, 0, result.stderr)
        graph = json.loads(result.stdout)
        nodes = {node["id"]: node for node in graph["nodes"]}
        self.assertIn("skill:security-and-hardening", nodes)
        self.assertIn("document:README.md", nodes)
        self.assertTrue(any(edge["relation"] == "documents" for edge in graph["edges"]))

    def test_impact_includes_documentation_and_verification_consumers(self) -> None:
        result = self.run_map("impact", "assets/agents/leaves_capabilities/security-and-hardening/SKILL.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertIn("skill:security-and-hardening", packet["affected"])
        self.assertIn("verifier:provenance", packet["verification"])
        self.assertIn("document:README.md", packet["documentation"])
        self.assertNotIn("skill:performance", packet["affected"])

    def test_repair_packet_is_inspection_only_and_names_reverification(self) -> None:
        result = self.run_map("repair-packet", "assets/agents/leaves_capabilities/security-and-hardening/SKILL.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(packet["disposition"], "inspect-before-repair")
        self.assertIn("verifier:provenance", packet["requiredReverification"])
        self.assertNotIn("apply", packet)

    def test_installer_impact_includes_its_verifier_and_endpoint(self) -> None:
        result = self.run_map("impact", "tooling/install.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertIn("verifier:graft-compatibility_install-audit", packet["verification"])
        self.assertIn("endpoint:.agents/chohogi", packet["affected"])

    def test_check_rejects_stale_generated_views(self) -> None:
        build = self.run_map("build")
        self.assertEqual(build.returncode, 0, build.stderr)
        result = self.run_map("check")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
