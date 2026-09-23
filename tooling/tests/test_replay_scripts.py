"""Regression tests for replay result validation and aggregation parity."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUMMARIZER = ROOT / "tooling" / "summarize-replays.py"
VALIDATOR = ROOT / "tooling" / "validate-replay-result.py"


class ReplayScriptTests(unittest.TestCase):
    def write_result(self, directory: Path, payload: dict) -> Path:
        path = directory / "result.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def invalid_result(self) -> dict:
        return {
            "schemaVersion": 1,
            "fixtureId": "fixture",
            "profile": "unknown-profile",
            "model": "model",
            "effort": "low",
            "toolCondition": "tools",
            "repoCondition": "clean",
            "outcomes": {
                "flowCorrect": True,
                "artifactsComplete": True,
                "externalController": False,
                "executionChoicePrompt": False,
                "unnecessaryEscalation": False,
                "persistentChangeWithoutAuthority": False,
                "reworkCount": True,
            },
            "unexpected": "must be rejected",
        }

    def test_summarizer_rejects_every_result_the_canonical_validator_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result_path = self.write_result(Path(temporary_directory), self.invalid_result())
            validator = subprocess.run([sys.executable, str(VALIDATOR), str(result_path)], text=True, capture_output=True, check=False)
            summarizer = subprocess.run([sys.executable, str(SUMMARIZER), str(result_path)], text=True, capture_output=True, check=False)
        self.assertNotEqual(validator.returncode, 0)
        self.assertNotEqual(summarizer.returncode, 0)


if __name__ == "__main__":
    unittest.main()
