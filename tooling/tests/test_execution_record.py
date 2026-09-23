#!/usr/bin/env python3
"""Regression tests for durable project execution records."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/execution-record.py"


class ExecutionRecordTests(unittest.TestCase):
    def invoke(self, project: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(TOOL), "--project", str(project), *arguments], text=True, capture_output=True, check=False)

    def begin(self, project: Path, contract: dict[str, object]) -> None:
        path = project / "contract-input.json"
        path.write_text(json.dumps(contract), encoding="utf-8")
        result = self.invoke(project, "begin", "--work-id", "sample", "--contract", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_non_visual_contract_finalizes_without_patch_or_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "src").mkdir()
            (project / "src/app.ts").write_text("export {};\n", encoding="utf-8")
            self.begin(project, {"schemaVersion": 1, "acceptance": [{"id": "typecheck", "requiredArtifacts": [{"kind": "test-result"}]}]})
            artifact = project / "typecheck.txt"
            artifact.write_text("pass\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "typecheck", "--kind", "test-result", "--path", str(artifact)).returncode, 0)
            result = self.invoke(project, "finalize", "--work-id", "sample")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_finalize_rejects_registered_artifact_when_bytes_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": [{"id": "proof", "requiredArtifacts": [{"kind": "test-result"}]}]})
            artifact = project / "proof.txt"
            artifact.write_text("original pass\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "proof", "--kind", "test-result", "--path", str(artifact)).returncode, 0)
            artifact.write_text("changed after registration\n", encoding="utf-8")
            result = self.invoke(project, "finalize", "--work-id", "sample")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("staleArtifacts", result.stdout)

    def test_review_includes_registered_artifact_path_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            artifact = project / "proof.txt"
            artifact.write_text("pass\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "proof", "--kind", "test-result", "--path", str(artifact)).returncode, 0)
            result = self.invoke(project, "review", "--work-id", "sample")
        self.assertEqual(result.returncode, 0, result.stderr)
        registered = json.loads(result.stdout)["artifacts"][0]
        self.assertEqual(registered["path"], str(artifact))
        self.assertEqual(len(registered["sha256"]), 64)

    def test_handoff_projects_open_acceptance_and_verified_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "objective": "ship", "acceptance": [
                {"id": "checked", "requiredArtifacts": [{"kind": "test-result"}]},
                {"id": "pending", "requiredArtifacts": [{"kind": "screenshot"}]},
            ]})
            artifact = project / "test.txt"
            artifact.write_text("pass\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "checked", "--kind", "test-result", "--path", str(artifact)).returncode, 0)
            self.assertEqual(self.invoke(project, "checkpoint", "--work-id", "sample", "--id", "mapped", "--summary", "consumer mapped").returncode, 0)
            result = self.invoke(project, "handoff", "--work-id", "sample")
        self.assertEqual(result.returncode, 0, result.stderr)
        handoff = json.loads(result.stdout)
        self.assertEqual(handoff["workId"], "sample")
        self.assertEqual(handoff["openAcceptance"], [{"id": "pending", "kinds": ["screenshot"]}])
        self.assertEqual(handoff["latestCheckpoint"]["id"], "mapped")
        self.assertEqual(handoff["artifactRefs"][0]["path"], str(artifact))
        self.assertEqual(set(handoff), {"schemaVersion", "workId", "baseline", "objective", "openAcceptance", "latestCheckpoint", "recentDecisions", "artifactRefs", "nextBoundary", "limits"})

    def test_handoff_rejects_changed_registered_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            artifact = project / "test.txt"
            artifact.write_text("pass\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "proof", "--kind", "test-result", "--path", str(artifact)).returncode, 0)
            artifact.write_text("changed\n", encoding="utf-8")
            result = self.invoke(project, "handoff", "--work-id", "sample")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("registered artifact", result.stderr)

    def test_visual_contract_requires_only_declared_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": [{"id": "mobile-ui", "requiredArtifacts": [{"kind": "screenshot"}]}]})
            failed = self.invoke(project, "finalize", "--work-id", "sample")
            self.assertNotEqual(failed.returncode, 0)
            shot = project / "mobile.png"
            shot.write_bytes(b"image")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "mobile-ui", "--kind", "screenshot", "--path", str(shot)).returncode, 0)
            self.assertEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)

    def test_verified_consumer_requires_its_declared_evidence_before_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": [{
                "id": "reading-surface",
                "consumerEvidence": [{
                    "consumer": "result route",
                    "status": "verified",
                    "artifactKind": "consumer-test",
                }],
            }]})
            result = self.invoke(project, "finalize", "--work-id", "sample")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missingConsumerEvidence", result.stdout)
            evidence = project / "consumer-test.txt"
            evidence.write_text("result route consumes projection\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "artifact", "--work-id", "sample", "--acceptance-id", "reading-surface", "--kind", "consumer-test", "--path", str(evidence)).returncode, 0)
            self.assertEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)

    def test_consumer_evidence_requires_a_valid_status_and_complete_deferred_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            contract = {
                "schemaVersion": 1,
                "acceptance": [{
                    "id": "result",
                    "consumerEvidence": [{"consumer": "result route", "status": "deferred"}],
                }],
            }
            path = project / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            result = self.invoke(project, "begin", "--work-id", "sample", "--contract", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deferred consumer evidence needs a reason", result.stderr)

    def test_resume_returns_last_checkpoint_and_rejects_changed_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            source = project / "source.txt"
            source.write_text("before", encoding="utf-8")
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            self.assertEqual(self.invoke(project, "checkpoint", "--work-id", "sample", "--id", "mapped", "--summary", "mapped files").returncode, 0)
            resumed = self.invoke(project, "resume", "--work-id", "sample")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertEqual(json.loads(resumed.stdout)["checkpoint"]["id"], "mapped")
            source.write_text("after", encoding="utf-8")
            self.assertNotEqual(self.invoke(project, "resume", "--work-id", "sample").returncode, 0)

    def test_decision_and_outcome_are_append_only_review_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            decision = self.invoke(project, "decision", "--work-id", "sample", "--id", "rendering", "--topic", "responsive-ui", "--observations", '["TSX/React project", "static breakpoint layout"]', "--options", '["css-only", "react-state"]', "--selected", "css-only", "--rationale", "no client state", "--review-trigger", "interaction appears")
            self.assertEqual(decision.returncode, 0, decision.stderr)
            outcome = self.invoke(project, "outcome", "--work-id", "sample", "--summary", "implemented", "--feedback", "accepted", "--remaining-risk", "none")
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            events = [json.loads(line) for line in (project / "docs/work-log/records/sample/events.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([item["event"] for item in events[-2:]], ["decision", "outcome"])
            self.assertEqual(events[-2]["selected"], "css-only")

    def test_review_groups_facts_decisions_and_outcomes_without_raw_prompt_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            fact = self.invoke(project, "fact", "--work-id", "sample", "--kind", "project-trait", "--summary", "TSX/React project", "--details", '{"source":"package.json"}')
            self.assertEqual(fact.returncode, 0, fact.stderr)
            decision = self.invoke(project, "decision", "--work-id", "sample", "--id", "rendering", "--topic", "responsive-ui", "--observations", '["static breakpoint layout"]', "--options", '["css-only", "react-state"]', "--selected", "css-only", "--rationale", "no client state", "--review-trigger", "interaction appears")
            self.assertEqual(decision.returncode, 0, decision.stderr)
            self.assertEqual(self.invoke(project, "outcome", "--work-id", "sample", "--summary", "implemented", "--feedback", "accepted").returncode, 0)
            result = self.invoke(project, "review", "--work-id", "sample")
            self.assertEqual(result.returncode, 0, result.stderr)
            review = json.loads(result.stdout)
            self.assertEqual(review["facts"][0]["kind"], "project-trait")
            self.assertEqual(review["decisions"][0]["selected"], "css-only")
            self.assertEqual(review["outcomes"][0]["feedback"], "accepted")
            self.assertNotIn("prompt", json.dumps(review).lower())

    def test_invalid_decision_json_is_rejected_without_appending_an_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            result = self.invoke(project, "decision", "--work-id", "sample", "--id", "bad", "--topic", "topic", "--observations", "not-json", "--options", '[]', "--selected", "none", "--rationale", "none", "--review-trigger", "none")
            self.assertNotEqual(result.returncode, 0)
            events = (project / "docs/work-log/records/sample/events.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(events), 1)

    def test_required_decision_review_requires_independent_response_and_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            capability_map = self.invoke(project, "capability-map", "--work-id", "sample", "--id", "ui-surface", "--scope", "mobile banner behavior", "--findings", '[{"layer":"component","capability":"conditional rendering","evidence":"src/Banner.tsx"}]', "--prior-feedback", '["previous CSS-only change needed rework"]')
            self.assertEqual(capability_map.returncode, 0, capability_map.stderr)
            decision = self.invoke(project, "decision", "--work-id", "sample", "--id", "rendering", "--topic", "responsive-ui", "--observations", '["static breakpoint layout"]', "--options", '["css-only", "react-state"]', "--selected", "css-only", "--rationale", "no client state", "--review-trigger", "interaction appears", "--review-required", "--capability-map-id", "ui-surface", "--capabilities-considered", '["conditional rendering", "css media query"]')
            self.assertEqual(decision.returncode, 0, decision.stderr)
            packet = self.invoke(project, "review-request", "--work-id", "sample", "--decision-id", "rendering")
            self.assertEqual(packet.returncode, 0, packet.stderr)
            packet_data = json.loads(packet.stdout)
            self.assertEqual(packet_data["decision"]["selected"], "css-only")
            self.assertEqual(packet_data["capabilityMap"]["id"], "ui-surface")
            self.assertNotEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)
            response = self.invoke(project, "review-response", "--work-id", "sample", "--decision-id", "rendering", "--verdict", "no-blocking-findings", "--findings", '[]', "--rationale", "state is not needed")
            self.assertEqual(response.returncode, 0, response.stderr)
            self.assertNotEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)
            resolution = self.invoke(project, "review-resolution", "--work-id", "sample", "--decision-id", "rendering", "--disposition", "accepted", "--summary", "kept CSS-only with reviewer confirmation")
            self.assertEqual(resolution.returncode, 0, resolution.stderr)
            self.assertEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)

    def test_required_decision_is_rejected_without_a_capability_map_and_considered_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            result = self.invoke(project, "decision", "--work-id", "sample", "--id", "bad", "--topic", "implementation", "--observations", '[]', "--options", '["local edit"]', "--selected", "local edit", "--rationale", "quick", "--review-trigger", "rework", "--review-required")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("capability map", result.stderr)

    def test_prior_feedback_is_available_to_a_new_capability_map(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            contract = project / "contract.json"
            contract.write_text('{"schemaVersion": 1, "acceptance": []}', encoding="utf-8")
            self.assertEqual(self.invoke(project, "begin", "--work-id", "prior", "--contract", str(contract)).returncode, 0)
            self.assertEqual(self.invoke(project, "outcome", "--work-id", "prior", "--summary", "reworked", "--feedback", "missed an existing capability", "--remaining-risk", "check similar routes").returncode, 0)
            self.assertEqual(self.invoke(project, "begin", "--work-id", "sample", "--contract", str(contract)).returncode, 0)
            result = self.invoke(project, "prior-feedback", "--work-id", "sample")
            self.assertEqual(result.returncode, 0, result.stderr)
            feedback = json.loads(result.stdout)["priorFeedback"]
            self.assertEqual(feedback[0]["workId"], "prior")
            self.assertIn("missed", feedback[0]["feedback"])

    def test_prior_feedback_preserves_recorded_source_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            contract = project / "contract.json"
            contract.write_text('{"schemaVersion": 1, "acceptance": []}', encoding="utf-8")
            self.assertEqual(self.invoke(project, "begin", "--work-id", "prior", "--contract", str(contract)).returncode, 0)
            source = project / "feedback.md"
            source.write_text("original feedback", encoding="utf-8")
            self.assertEqual(self.invoke(project, "feedback", "--work-id", "prior", "--source", str(source), "--summary", "needs plan update", "--impact", "consumer", "--disposition", "plan-updated", "--target", "docs/active-plan.md").returncode, 0)
            self.assertEqual(self.invoke(project, "begin", "--work-id", "sample", "--contract", str(contract)).returncode, 0)
            result = self.invoke(project, "prior-feedback", "--work-id", "sample")
            feedback = json.loads(result.stdout)["priorFeedback"][-1]
            self.assertEqual(feedback["impact"], "consumer")
            self.assertEqual(feedback["target"], "docs/active-plan.md")
            self.assertEqual(len(feedback["sha256"]), 64)

    def test_feedback_event_records_source_impact_and_response(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            source = project / "docs/feedback/review.md"
            source.parent.mkdir(parents=True)
            source.write_text("# review\nconsumer is stale\n", encoding="utf-8")
            result = self.invoke(project, "feedback", "--work-id", "sample", "--source", str(source), "--summary", "consumer is stale", "--impact", "consumer", "--disposition", "plan-updated", "--target", "docs/plan.md")
            self.assertEqual(result.returncode, 0, result.stderr)
            review = json.loads(self.invoke(project, "review", "--work-id", "sample").stdout)
            self.assertEqual(review["feedback"][0]["disposition"], "plan-updated")
            self.assertEqual(len(review["feedback"][0]["sha256"]), 64)

    def test_feedback_scan_reports_unprocessed_markdown_and_excludes_recorded_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            root = project / "docs/feedback"
            root.mkdir(parents=True)
            pending = root / "pending.md"
            recorded = root / "recorded.md"
            pending.write_text("pending\n", encoding="utf-8")
            recorded.write_text("recorded\n", encoding="utf-8")
            self.assertEqual(self.invoke(project, "feedback", "--work-id", "sample", "--source", str(recorded), "--summary", "reviewed", "--impact", "none", "--disposition", "no-action", "--reason", "not actionable").returncode, 0)
            result = self.invoke(project, "feedback-scan", "--work-id", "sample", "--root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([item["path"] for item in json.loads(result.stdout)["pending"]], [str(pending.resolve())])

    def test_feedback_scan_can_use_declared_project_document_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            source = project / "review.md"
            source.write_text("review\n", encoding="utf-8")
            registry = project / "registry.json"
            registry.write_text(json.dumps({"schemaVersion": 1, "documents": [{"path": "review.md", "role": "review-synthesis", "authority": "review", "state": "active", "scan": True}]}), encoding="utf-8")
            result = self.invoke(project, "feedback-scan", "--registry", str(registry))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["pending"][0]["path"], str(source.resolve()))

    def test_finalize_blocks_when_declared_feedback_source_is_unprocessed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            source = project / "feedback.md"
            source.write_text("new feedback\n", encoding="utf-8")
            registry = project / "registry.json"
            registry.write_text(json.dumps({"schemaVersion": 1, "documents": [{"path": "feedback.md", "role": "feedback-source", "authority": "observation", "state": "active"}]}), encoding="utf-8")
            contract = project / "contract.json"
            contract.write_text(json.dumps({"schemaVersion": 1, "feedbackRegistry": "registry.json", "acceptance": []}), encoding="utf-8")
            self.assertEqual(self.invoke(project, "begin", "--work-id", "sample", "--contract", str(contract)).returncode, 0)
            result = self.invoke(project, "finalize", "--work-id", "sample")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pendingFeedback", result.stdout)

    def test_registry_projects_must_declare_feedback_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".agents").mkdir()
            (project / ".agents/chohogi-document-registry.json").write_text('{"schemaVersion":1,"documents":[]}', encoding="utf-8")
            contract = project / "contract.json"
            contract.write_text('{"schemaVersion":1,"acceptance":[]}', encoding="utf-8")
            result = self.invoke(project, "begin", "--work-id", "sample", "--contract", str(contract))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("feedbackRegistry", result.stderr)

    def test_scope_lock_blocks_finalize_until_every_requested_item_has_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            contract = project / "contract.json"
            contract.write_text(json.dumps({"schemaVersion": 1, "requestedItems": [{"id": "one", "description": "first"}, {"id": "two", "description": "second"}], "acceptance": []}), encoding="utf-8")
            self.assertEqual(self.invoke(project, "begin", "--work-id", "sample", "--contract", str(contract)).returncode, 0)
            self.assertNotEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)
            self.assertIn("unresolvedScopeItems", self.invoke(project, "finalize", "--work-id", "sample").stdout)
            self.assertEqual(self.invoke(project, "scope-item", "--work-id", "sample", "--id", "one", "--status", "implemented", "--summary", "done").returncode, 0)
            self.assertEqual(self.invoke(project, "scope-item", "--work-id", "sample", "--id", "two", "--status", "deferred", "--summary", "later", "--reason", "blocked by approval").returncode, 0)
            self.assertEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)

    def test_material_tradeoff_requires_decision_report_and_user_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.begin(project, {"schemaVersion": 1, "acceptance": []})
            self.assertEqual(self.invoke(project, "capability-map", "--work-id", "sample", "--id", "rendering", "--scope", "banner", "--findings", '[{"layer":"framework","capability":"conditional rendering","evidence":"Banner.tsx"}]').returncode, 0)
            decision = self.invoke(project, "decision", "--work-id", "sample", "--id", "implementation", "--topic", "mobile behavior", "--observations", '["mobile differs"]', "--options", '["CSS-only", "component rendering"]', "--selected", "component rendering", "--rationale", "clearer structure", "--review-trigger", "interaction appears", "--requires-user-decision", "--capability-map-id", "rendering", "--capabilities-considered", '["conditional rendering", "CSS media query"]')
            self.assertEqual(decision.returncode, 0, decision.stderr)
            self.assertNotEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)
            report = self.invoke(project, "decision-report", "--work-id", "sample", "--decision-id", "implementation", "--tradeoffs", '["CSS is faster initially", "component rendering reduces conditional markup debt"]', "--delivery-cost", '{"cssOnly":"small","componentRendering":"small-to-medium","confidence":"low"}', "--reversibility", "both reversible; component boundary affects tests", "--unknowns", '["future interaction requirement"]')
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertNotEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)
            resolution = self.invoke(project, "decision-resolution", "--work-id", "sample", "--decision-id", "implementation", "--selected", "component rendering", "--owner", "user", "--summary", "user accepted the recommended option")
            self.assertEqual(resolution.returncode, 0, resolution.stderr)
            self.assertEqual(self.invoke(project, "finalize", "--work-id", "sample").returncode, 0)


if __name__ == "__main__":
    unittest.main()
