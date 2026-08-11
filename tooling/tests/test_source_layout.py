#!/usr/bin/env python3
"""Regression checks for active Chohogi v2 source references."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SourceLayoutTests(unittest.TestCase):
    def test_active_source_has_no_v1_layout_or_retired_skill_reference(self) -> None:
        result = subprocess.run(
            [sys.executable, "tooling/verify-source-layout.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
