from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/verify-status-provenance.py"


class StatusProvenanceTests(unittest.TestCase):
    def run_case(self, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
            root = Path(handle.name).parent
            (root / "resolution.md").write_text("resolution\n", encoding="utf-8")
            (root / "evidence.txt").write_text("evidence\n", encoding="utf-8")
            json.dump(payload, handle)
            handle.flush()
            return subprocess.run([sys.executable, str(TOOL), "--input", handle.name, "--root", str(root)], text=True, capture_output=True, check=False)

    def test_equal_or_weaker_derived_status_passes(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}], "claims": [{"id": "scope", "sourceStatus": "verified", "sourceEvidenceRefs": ["source-1"], "derivedStatus": "degraded"}]})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_status_claim_requires_traceable_source_evidence(self) -> None:
        result = self.run_case({"schemaVersion": 1, "claims": [{"id": "scope", "sourceStatus": "verified", "derivedStatus": "verified"}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sourceEvidenceRefs", result.stdout)

    def test_malformed_source_reference_fails_without_crashing(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}], "claims": [{"id": "scope", "sourceStatus": "verified", "sourceEvidenceRefs": [{}], "derivedStatus": "verified"}]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("sourceEvidenceRefs", result.stdout)

    def test_malformed_status_and_catalog_ids_fail_without_crashing(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": [], "path": "evidence.txt"}], "claims": [{"id": "scope", "sourceStatus": [], "derivedStatus": "healthy"}]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("sourceStatus and derivedStatus must be known", result.stdout)

    def test_non_boolean_conflict_flag_fails_closed(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}], "claims": [{"id": "conflict", "sourceStatus": "verified", "sourceEvidenceRefs": ["source-1"], "derivedStatus": "healthy", "sourceConflict": "true", "conflictDisposition": "deferred"}]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("sourceConflict must be a boolean", result.stdout)

    def test_stronger_status_requires_explicit_resolution_and_evidence(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}], "claims": [{"id": "scope", "sourceStatus": "provisional", "sourceEvidenceRefs": ["source-1"], "derivedStatus": "approved"}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicitPromotion", result.stdout)

    def test_explicit_promotion_can_pass(self) -> None:
        result = self.run_case({"schemaVersion": 1, "resolutionCatalog": [{"id": "RES-1", "path": "resolution.md"}], "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}, {"id": "test-1", "path": "evidence.txt"}], "claims": [{"id": "scope", "sourceStatus": "provisional", "sourceEvidenceRefs": ["source-1"], "derivedStatus": "approved", "explicitPromotion": True, "resolutionRef": "RES-1", "evidenceRefs": ["test-1"], "owner": "authorized-owner"}]})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unresolved_source_conflict_cannot_support_positive_derived_claim(self) -> None:
        result = self.run_case({"schemaVersion": 1, "evidenceCatalog": [{"id": "source-1", "path": "evidence.txt"}], "claims": [{"id": "conflict", "sourceStatus": "verified", "sourceEvidenceRefs": ["source-1"], "derivedStatus": "healthy", "sourceConflict": True, "conflictDisposition": "deferred"}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unresolved source conflict", result.stdout)


if __name__ == "__main__":
    unittest.main()
