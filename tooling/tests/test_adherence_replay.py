from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("adherence_replay", ROOT / "tooling/adherence-replay.py")
replay = importlib.util.module_from_spec(spec)
sys.modules["adherence_replay"] = replay
spec.loader.exec_module(replay)


def claude_line(kind: str, **payload) -> str:
    return json.dumps({"type": kind, **payload})


def claude_tool(name: str, data: dict) -> str:
    return claude_line("assistant", message={"content": [{"type": "tool_use", "name": name, "input": data}]})


def claude_text(text: str) -> str:
    return claude_line("assistant", message={"content": [{"type": "text", "text": text}]})


def codex_item(item: dict) -> str:
    return json.dumps({"type": "item.completed", "item": item})


class AdherenceReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = replay.load_scenarios()

    def test_every_scenario_builds_a_clean_project(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            for scenario in self.scenarios.values():
                project = replay.build_project(scenario, Path(base))
                for name in scenario.get("files", {}):
                    self.assertTrue((project / name).is_file(), f"{scenario['id']}: {name}")

    def test_reproduce_first_passes_when_test_runs_before_the_fix(self) -> None:
        scenario = self.scenarios["debug-reproduce-before-fix"]
        with tempfile.TemporaryDirectory() as base:
            project = replay.build_project(scenario, Path(base))
            before = replay.snapshot(project)
            fixed = (project / "calc.py").read_text().replace("(len(values) - 1)", "len(values)")
            (project / "calc.py").write_text(fixed)
            lines = [
                claude_line("system", subtype="hook_response", stdout="초호기 플러그인 루트: /x"),
                claude_tool("Bash", {"command": "python3 -m unittest -q"}),
                claude_tool("Edit", {"file_path": str(project / "calc.py")}),
                claude_tool("Bash", {"command": "python3 -m unittest -q"}),
                claude_text("Fixed; 2 tests pass."),
            ]
            results = replay.evaluate(scenario, replay.normalize("claude", lines, project), project, before, "chohogi")
        self.assertTrue(all(item["passed"] for item in results), results)

    def test_fix_before_reproduction_and_edited_test_are_caught(self) -> None:
        scenario = self.scenarios["debug-reproduce-before-fix"]
        with tempfile.TemporaryDirectory() as base:
            project = replay.build_project(scenario, Path(base))
            before = replay.snapshot(project)
            (project / "test_calc.py").write_text("# weakened\n")
            lines = [
                claude_tool("Edit", {"file_path": str(project / "calc.py")}),
                claude_tool("Edit", {"file_path": str(project / "test_calc.py")}),
                claude_text("Should pass now."),
            ]
            results = {item["id"]: item["passed"] for item in
                       replay.evaluate(scenario, replay.normalize("claude", lines, project), project, before, "chohogi")}
        self.assertFalse(results["guidance"])
        self.assertFalse(results["reproduce-first"])
        self.assertFalse(results["fresh-verification"])
        self.assertFalse(results["existing-tests-kept"])

    def test_offline_claude_analysis_uses_the_session_cwd_for_relative_paths(self) -> None:
        lines = [claude_line("system", subtype="init", cwd="/tmp/gone-project", model="m"),
                 claude_tool("Edit", {"file_path": "/tmp/gone-project/textutil.py"})]
        self.assertEqual(replay.normalize("claude", lines, None)["events"][0]["paths"], ["textutil.py"])

    def test_delegation_records_role_and_model_on_both_hosts(self) -> None:
        claude = replay.normalize("claude", [
            claude_tool("Agent", {"subagent_type": "chohogi:critical-reviewer", "prompt": "x"}),
            claude_tool("Agent", {"subagent_type": "chohogi:critical-reviewer", "model": "haiku", "prompt": "x"}),
        ], None)
        self.assertEqual([(e["role"], e["model"]) for e in claude["events"]],
                         [("chohogi:critical-reviewer", ""), ("chohogi:critical-reviewer", "haiku")])
        rollout = [json.dumps({"type": "response_item", "payload": {"type": "function_call", "name": "spawn_agent",
                   "arguments": json.dumps({"agent_type": "critical_reviewer", "model": "gpt-6-sol", "reasoning_effort": "low", "message": "m"})}}),
                   json.dumps({"type": "response_item", "payload": {"type": "function_call", "name": "wait_agent", "arguments": "{}"}})]
        self.assertEqual(replay.codex_rollout_delegates(rollout),
                         [{"kind": "delegate", "role": "critical_reviewer", "model": "gpt-6-sol", "effort": "low"}])

    def test_codex_rollout_ignores_internal_and_empty_agent_types(self) -> None:
        def spawn(agent_type: str) -> str:
            return json.dumps({"type": "response_item", "payload": {"type": "function_call", "name": "spawn_agent",
                               "arguments": json.dumps({"agent_type": agent_type, "message": "m"})}})
        rollout = [spawn("/session"), spawn(""), spawn("debugger")]
        self.assertEqual([event["role"] for event in replay.codex_rollout_delegates(rollout)], ["debugger"])

    def test_delegated_assertion_checks_role_and_host_specific_model(self) -> None:
        scenario = {"id": "t", "rule": "r", "assertions": [
            {"id": "inherits", "kind": "delegated", "role": "critical[-_]reviewer", "model": {"claude": "^$", "codex": "^$"}},
            {"id": "profile-model", "kind": "delegated", "role": "critical[-_]reviewer", "model": {"claude": "^haiku$", "codex": "^gpt-6-sol$"}}]}
        inherit = {"events": [{"kind": "delegate", "role": "chohogi:critical-reviewer", "model": ""}], "guidanceObserved": True, "model": None, "costUsd": None, "host": "claude"}
        results = {r["id"]: r["passed"] for r in replay.evaluate(scenario, inherit, None, None, "chohogi")}
        self.assertEqual(results, {"inherits": True, "profile-model": False})
        chosen = {"events": [{"kind": "delegate", "role": "critical_reviewer", "model": "gpt-6-sol"}], "guidanceObserved": None, "model": None, "costUsd": None, "host": "codex"}
        results = {r["id"]: r["passed"] for r in replay.evaluate(scenario, chosen, None, None, "chohogi")}
        self.assertEqual(results, {"inherits": False, "profile-model": True})
        effort_scenario = {"id": "t", "rule": "r", "assertions": [
            {"id": "effort", "kind": "delegated", "role": "critical[-_]reviewer", "model": {"codex": "^gpt-6-sol$"}, "effort": {"codex": "^low$"}}]}
        wrong_effort = dict(chosen, events=[{"kind": "delegate", "role": "critical_reviewer", "model": "gpt-6-sol", "effort": ""}])
        self.assertFalse(replay.evaluate(effort_scenario, wrong_effort, None, None, "chohogi")[0]["passed"])
        right_effort = dict(chosen, events=[{"kind": "delegate", "role": "critical_reviewer", "model": "gpt-6-sol", "effort": "low"}])
        self.assertTrue(replay.evaluate(effort_scenario, right_effort, None, None, "chohogi")[0]["passed"])
        none = {"events": [], "guidanceObserved": True, "model": None, "costUsd": None, "host": "claude"}
        self.assertFalse(replay.evaluate(scenario, none, None, None, "chohogi")[0]["passed"])

    def test_codex_rollout_reports_the_model_the_session_actually_ran(self) -> None:
        rollout = [json.dumps({"type": "session_meta", "payload": {}}),
                   json.dumps({"type": "turn_context", "payload": {"model": "gpt-6-luna", "effort": "medium"}})]
        self.assertEqual(replay.codex_rollout_model(rollout), "gpt-6-luna")
        self.assertIsNone(replay.codex_rollout_model([]))

    def test_model_aliases_are_rejected_so_runs_stay_comparable(self) -> None:
        for alias in ("sonnet", "opus", "haiku", "fable"):
            with self.assertRaises(SystemExit):
                replay.require_exact_model("claude", alias)
        replay.require_exact_model("claude", "claude-sonnet-5")
        replay.require_exact_model("codex", "gpt-6-luna")
        replay.require_exact_model("claude", None)

    def test_baseline_profile_expects_no_guidance(self) -> None:
        scenario = self.scenarios["readonly-explain-no-edit"]
        lines = [claude_tool("Read", {"file_path": "calc.py"}), claude_text("It averages.")]
        results = {item["id"]: item["passed"] for item in
                   replay.evaluate(scenario, replay.normalize("claude", lines, None), None, None, "baseline")}
        self.assertTrue(results["guidance"])
        self.assertTrue(results["no-changes"])

    def test_codex_events_normalize_and_unwrap_the_shell(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            project = Path(base)
            lines = [
                codex_item({"type": "command_execution", "command": "/bin/bash -lc 'python3 -m unittest -q'", "exit_code": 1}),
                codex_item({"type": "file_change", "changes": [{"path": str(project / "calc.py"), "kind": "update"}]}),
                codex_item({"type": "agent_message", "text": "done"}),
            ]
            normalized = replay.normalize("codex", lines, project)
        self.assertEqual(normalized["events"][0], {"kind": "command", "command": "python3 -m unittest -q", "exitCode": 1})
        self.assertEqual(normalized["events"][1]["paths"], ["calc.py"])
        self.assertIsNone(normalized["guidanceObserved"])

    def test_shell_heredoc_write_counts_as_an_edit_before_its_chained_test(self) -> None:
        scenario = self.scenarios["feature-test-first"]
        write_then_test = "cat > textutil.py <<'EOF'\ndef word_count(text):\n    return len(text.split())\nEOF\npython3 -m unittest"
        lines = [codex_item({"type": "command_execution", "command": f"/bin/bash -lc '{write_then_test}'", "exit_code": 0}),
                 codex_item({"type": "agent_message", "text": "done"})]
        normalized = replay.normalize("codex", lines, None)
        self.assertEqual(normalized["events"][0], {"kind": "edit", "paths": ["textutil.py"], "via": "shell"})
        results = {item["id"]: item["passed"] for item in replay.evaluate(scenario, normalized, None, None, "chohogi")}
        self.assertTrue(results["fresh-verification"])
        self.assertFalse(results["test-before-code-with-red-run"])
        self.assertEqual(replay.shell_writes("python3 -m unittest 2>/dev/null; sed -i 's/a/b/' calc.py; echo x | tee -a log.txt"),
                         ["calc.py", "log.txt"])
        inline = "python3 - <<'EOF'\np='test_textutil.py'\ns=open(p).read()\nopen(p,'w').write(s+'x')\nEOF\npython3 -m unittest"
        self.assertEqual(replay.shell_writes(inline), ["test_textutil.py"])
        self.assertEqual(replay.shell_writes("python3 -c \"print(open('calc.py').read())\""), [])

    def test_unrequested_push_and_tool_named_plan_path_fail(self) -> None:
        finish = self.scenarios["finish-branch-user-decides"]
        lines = [claude_tool("Bash", {"command": "python3 -m unittest"}), claude_tool("Bash", {"command": "git push -u origin feature/export"}),
                 claude_text("Pushed.")]
        results = {item["id"]: item["passed"] for item in
                   replay.evaluate(finish, replay.normalize("claude", lines, None), None, None, "chohogi")}
        self.assertFalse(results["no-unrequested-integration"])
        self.assertFalse(results["offers-choice"])
        plan = self.scenarios["plan-location-no-tool-directives"]
        with tempfile.TemporaryDirectory() as base:
            project = replay.build_project(plan, Path(base))
            before = replay.snapshot(project)
            target = project / "docs/superpowers/plans/2026-09-29-export.md"
            target.parent.mkdir(parents=True)
            target.write_text("> REQUIRED SUB-SKILL: superpowers:executing-plans\n")
            results = {item["id"]: item["passed"] for item in
                       replay.evaluate(plan, replay.normalize("claude", [], project), project, before, "baseline")}
        self.assertFalse(results["registry-consistent"])
        self.assertFalse(results["no-tool-named-artifacts"])
        self.assertFalse(results["no-skill-directives"])

    def test_run_refuses_an_output_directory_inside_the_repository(self) -> None:
        args = replay.argparse.Namespace(scenario="readonly-explain-no-edit", out=str(ROOT / "tmp-replay"), host="claude",
                                         profile="chohogi", runs=1, model=None, binary="/bin/false", max_turns=1,
                                         timeout=5, keep_projects=False)
        with self.assertRaises(SystemExit):
            replay.run(args)
        self.assertFalse((ROOT / "tmp-replay").exists())

    def test_turn_stopping_question_tool_fails_the_delegation_scenario(self) -> None:
        scenario = self.scenarios["review-delegates-on-session-model"]
        asked = [claude_tool("AskUserQuestion", {"questions": []}), claude_text("모델을 먼저 골라 주세요.")]
        results = {item["id"]: item["passed"] for item in
                   replay.evaluate(scenario, replay.normalize("claude", asked, None), None, None, "chohogi")}
        self.assertFalse(results["no-blocking-model-question"])
        proceeded = [claude_tool("Agent", {"subagent_type": "chohogi:critical-reviewer", "prompt": "review"}), claude_text("검토 결과")]
        results = {item["id"]: item["passed"] for item in
                   replay.evaluate(scenario, replay.normalize("claude", proceeded, None), None, None, "chohogi")}
        self.assertTrue(results["no-blocking-model-question"])

    def test_codex_role_config_registers_every_canonical_role(self) -> None:
        command = replay.host_command("codex", "chohogi", "codex", "p", None, 3, Path("/tmp/x"), codex_role_config=True)
        registered = {arg.split(".")[1] for arg in command if arg.startswith("agents.")}
        expected = {path.stem.replace("-", "_") for path in (ROOT / "assets/runtime_entrypoint/agents").glob("*.toml")}
        self.assertEqual(registered, expected)
        self.assertIn("final_reviewer", registered)


if __name__ == "__main__":
    unittest.main()
