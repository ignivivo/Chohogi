#!/usr/bin/env python3
"""Guard the declared POSIX-only Chohogi execution boundary."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PosixOnlyTests(unittest.TestCase):
    def test_tooling_contains_no_native_powershell_adapter(self) -> None:
        self.assertEqual(list((ROOT / "tooling").glob("*.ps1")), [])

    def test_active_harness_documents_do_not_advertise_powershell_execution(self) -> None:
        active_documents = [
            ROOT / "README.md",
            ROOT / "assets/agents/adaptive-regulation/homeostasis/SKILL.md",
            ROOT / "assets/agents/adaptive-regulation/homeostasis/references/skill-lifecycle.md",
            ROOT / "assets/agents/trunk_orchestration/evaluation/README.md",
        ]
        for document in active_documents:
            self.assertNotIn(".ps1", document.read_text(encoding="utf-8"), document)


if __name__ == "__main__":
    unittest.main()
