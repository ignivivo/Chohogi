#!/usr/bin/env python3
"""Behavioral tests for the session model-policy evaluator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/model-policy.py"


class ModelPolicyTests(unittest.TestCase):
    def write_json(self, directory: Path, name: str, value: object) -> Path:
        path = directory / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def run_tool(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(TOOL), *arguments], cwd=ROOT, text=True, capture_output=True, check=False)

    def catalog(self, output_price: float = 8.0) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "observedAt": "2026-08-12T00:00:00Z",
            "observations": [
                {"provider": "codex", "model": "gpt-fast", "available": True, "reasoningLevels": ["low", "medium"], "capabilities": ["coding", "review"], "price": {"inputUsdPerMillion": 1, "outputUsdPerMillion": 2}, "source": "runtime-exposed"},
                {"provider": "codex", "model": "gpt-deep", "available": True, "reasoningLevels": ["low", "medium", "high", "ultra"], "capabilities": ["coding", "review"], "price": {"inputUsdPerMillion": 3, "outputUsdPerMillion": output_price}, "source": "runtime-exposed"},
                {"provider": "claude", "model": "unavailable", "available": False, "reasoningLevels": ["high"], "capabilities": ["coding"], "source": "runtime-exposed"},
            ],
        }

    def test_recommends_only_currently_available_model_with_required_effort(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog = self.write_json(directory, "catalog.json", self.catalog())
            task = self.write_json(directory, "task.json", {"schemaVersion": 1, "role": "reviewer", "requiredCapabilities": ["coding", "review"], "minimumReasoning": "high"})
            result = self.run_tool("recommend", "--catalog", str(catalog), "--task", str(task))
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)
        self.assertEqual(decision["candidates"][0]["model"], "gpt-deep")
        self.assertTrue(decision["requiresHumanConfirmation"])
        self.assertNotIn("unavailable", [item["model"] for item in decision["candidates"]])

    def test_catalog_change_requires_reconfirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            prior = self.write_json(directory, "prior.json", self.catalog(output_price=8.0))
            current = self.write_json(directory, "current.json", self.catalog(output_price=9.0))
            result = self.run_tool("compare", "--catalog", str(current), "--prior", str(prior))
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)
        self.assertTrue(decision["requiresHumanReconfirmation"])
        self.assertEqual(decision["changes"][0]["kind"], "price-changed")

    def test_learning_escalation_requires_confirmed_prevention_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog = self.write_json(directory, "catalog.json", self.catalog())
            learning = self.write_json(directory, "learning.json", {"confirmedRootCause": True, "preventionVerified": True, "requestedRole": "reviewer", "requestedMinimumReasoning": "ultra", "evidenceId": "learning-42"})
            result = self.run_tool("learning-escalation", "--catalog", str(catalog), "--learning", str(learning))
            invalid = self.write_json(directory, "invalid-learning.json", {"confirmedRootCause": True, "preventionVerified": False, "requestedRole": "reviewer", "requestedMinimumReasoning": "ultra", "evidenceId": "learning-42"})
            failed = self.run_tool("learning-escalation", "--catalog", str(catalog), "--learning", str(invalid))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["requiresHumanReconfirmation"])
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("preventionVerified", failed.stderr)

    def test_explicit_user_selection_can_override_automatic_candidate_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog_value = self.catalog()
            catalog_value["observations"].append({"provider": "openai", "model": "gpt-6-astra", "available": True, "reasoningLevels": ["low", "high"], "capabilities": ["coding", "review"], "source": "runtime-exposed"})
            catalog = self.write_json(directory, "catalog.json", catalog_value)
            task = self.write_json(directory, "task.json", {"schemaVersion": 1, "role": "implementation", "requiredCapabilities": ["coding"], "minimumReasoning": "low"})
            result = self.run_tool("select", "--catalog", str(catalog), "--task", str(task), "--provider", "openai", "--model", "gpt-6-astra", "--reasoning", "high", "--reason", "user requested a comparative pass")
        self.assertEqual(result.returncode, 0, result.stderr)
        selected = json.loads(result.stdout)
        self.assertEqual(selected["selectionMode"], "user-override")
        self.assertEqual(selected["model"], "gpt-6-astra")
        self.assertEqual(selected["reasoning"], "high")
        self.assertFalse(selected["requiresHumanConfirmation"])

    def test_explicit_user_selection_rejects_unobserved_or_inadequate_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog = self.write_json(directory, "catalog.json", self.catalog())
            task = self.write_json(directory, "task.json", {"schemaVersion": 1, "role": "implementation", "requiredCapabilities": ["coding"], "minimumReasoning": "low"})
            result = self.run_tool("select", "--catalog", str(catalog), "--task", str(task), "--provider", "openai", "--model", "gpt-6-astra", "--reasoning", "low", "--reason", "user requested a comparative pass")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not available", result.stderr)

    def test_native_effort_round_trips_exactly_without_cross_tier_inference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog_value = self.catalog()
            catalog_value["observations"].append({"provider": "codex-vscode-runtime", "model": "gpt-6-luna", "available": True, "reasoningLevels": ["low", "high", "xhigh", "max"], "capabilities": ["coding"], "source": "runtime-exposed"})
            catalog = self.write_json(directory, "catalog.json", catalog_value)
            task = self.write_json(directory, "task.json", {"schemaVersion": 1, "role": "reviewer", "requiredCapabilities": ["coding"], "minimumReasoning": "xhigh"})
            accepted = self.run_tool("select", "--catalog", str(catalog), "--task", str(task), "--provider", "codex-vscode-runtime", "--model", "gpt-6-luna", "--reasoning", "xhigh", "--reason", "user selected exact runtime option")
            incomparable_task = self.write_json(directory, "incomparable-task.json", {"schemaVersion": 1, "role": "reviewer", "requiredCapabilities": ["coding"], "minimumReasoning": "high"})
            incomparable = self.run_tool("select", "--catalog", str(catalog), "--task", str(incomparable_task), "--provider", "codex-vscode-runtime", "--model", "gpt-6-luna", "--reasoning", "xhigh", "--reason", "native order requires human confirmation")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(json.loads(accepted.stdout)["reasoning"], "xhigh")
        self.assertEqual(incomparable.returncode, 0, incomparable.stderr)
        self.assertTrue(json.loads(incomparable.stdout)["requiresHumanConfirmation"])
        self.assertEqual(json.loads(incomparable.stdout)["reasoningFloorCheck"], "unknown-native-order")

    def test_unscoped_recommendation_includes_observed_astra_options(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog_value = self.catalog()
            catalog_value["observations"].append({"provider": "openai", "model": "gpt-6-astra", "available": True, "reasoningLevels": ["low"], "capabilities": ["coding", "review"], "source": "runtime-exposed"})
            catalog = self.write_json(directory, "catalog.json", catalog_value)
            task = self.write_json(directory, "task.json", {"schemaVersion": 1, "role": "implementation", "requiredCapabilities": ["coding"], "minimumReasoning": "low"})
            result = self.run_tool("recommend", "--catalog", str(catalog), "--task", str(task))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gpt-6-astra", [item["model"] for item in json.loads(result.stdout)["candidates"]])


if __name__ == "__main__":
    unittest.main()
