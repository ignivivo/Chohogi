from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/verify-learning-contract.py"


def verify(home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL)], text=True, capture_output=True, check=False,
                          env={**os.environ, "CHOHOGI_LEARNING_HOME": str(home)})


class LearningLedgerTests(unittest.TestCase):
    def home(self, directory: str, signatures: list[dict], ledger: list[dict]) -> Path:
        home = Path(directory)
        (home / "failure-signatures.json").write_text(json.dumps({"schemaVersion": 1, "signatures": signatures}), encoding="utf-8")
        (home / "learning-ledger.jsonl").write_text("".join(json.dumps(item) + "\n" for item in ledger), encoding="utf-8")
        return home

    def test_repository_ledger_is_consistent(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL)], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_ledger_entry_with_an_unregistered_signature_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = self.home(directory, [{"id": "sig-a", "description": "a", "guards": []}],
                             [{"kind": "occurrence", "signature": "sig-x", "workId": "W-1"}])
            result = verify(home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sig-x", result.stdout)

    def test_signature_guard_that_does_not_exist_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = self.home(directory, [{"id": "sig-a", "description": "a", "guards": ["tooling/tests/test_missing_guard.py"]}], [])
            result = verify(home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("test_missing_guard.py", result.stdout)

    def test_recurring_signature_without_any_guard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = self.home(directory, [{"id": "sig-a", "description": "a", "guards": []}],
                             [{"kind": "occurrence", "signature": "sig-a", "workId": "W-1"},
                              {"kind": "occurrence", "signature": "sig-a", "workId": "W-2"}])
            result = verify(home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("recurring", result.stdout)


if __name__ == "__main__":
    unittest.main()
