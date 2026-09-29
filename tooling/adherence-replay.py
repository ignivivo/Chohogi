#!/usr/bin/env python3
"""Run or analyze session-level adherence replays for Chohogi rules.

A scenario builds a disposable project, runs a real headless host session
(Claude Code `claude -p --output-format stream-json`, or Codex `codex exec
--json`), normalizes the transcript into tool events, and checks deterministic
assertions about what the session actually did. Results never contain prompt
bodies, command output, or credentials; the raw transcript stays in the chosen
output directory outside the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "assets/agents/trunk_orchestration/evaluation/adherence-scenarios.json"
GUIDANCE_MARKER = "초호기 플러그인 루트"
CLAUDE_EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
CLAUDE_READ_TOOLS = {"Read", "Grep", "Glob", "LS"}
CLAUDE_DELEGATE_TOOLS = {"Agent", "Task"}


def rel(path: str, project: Path | None) -> str:
    if project is not None:
        try:
            return str(Path(path).resolve().relative_to(project.resolve()))
        except (ValueError, OSError):
            pass
    return path


def unwrap_shell(command: str) -> str:
    match = re.fullmatch(r"/bin/(?:ba)?sh -lc (['\"])(.*)\1", command, re.S)
    return match.group(2) if match else command


SHELL_WRITE = re.compile(
    r"(?:^|[\s;&|('\"])(?:cat|printf|echo)\b[^\n;&|]*?>{1,2}\s*['\"]?([\w./-]+)"
    r"|\btee\s+(?:-a\s+)?['\"]?([\w./-]+)"
    r"|\bsed\s+-i\S*\s+(?:-e\s+)?(?:'[^']*'|\"[^\"]*\")\s+['\"]?([\w./-]+)"
)


def shell_writes(command: str) -> list[str]:
    """Best-effort paths a shell command writes through redirection, tee, or sed -i."""
    paths = []
    for match in SHELL_WRITE.finditer(command):
        path = next(group for group in match.groups() if group)
        if path not in ("/dev/null", "/dev/stderr", "/dev/stdout") and path not in paths:
            paths.append(path)
    return paths


def command_events(command: str, project: Path | None, **extra: Any) -> list[dict[str, Any]]:
    # A shell write is recorded as an edit immediately before the command, so a test run
    # chained after the write in the same command still counts as "after the edit".
    writes = [rel(str((project / path) if project and not path.startswith("/") else path), project) for path in shell_writes(command)]
    events: list[dict[str, Any]] = [{"kind": "edit", "paths": writes, "via": "shell"}] if writes else []
    return events + [{"kind": "command", "command": command, **extra}]


def normalize_claude(lines: list[str], project: Path | None) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    guidance = False
    model = None
    cost = None
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = entry.get("type")
        if kind == "system" and entry.get("subtype") == "hook_response":
            if GUIDANCE_MARKER in str(entry.get("stdout", "")) + str(entry.get("output", "")):
                guidance = True
        elif kind == "system" and entry.get("subtype") == "init":
            model = entry.get("model")
        elif kind == "result":
            cost = entry.get("total_cost_usd")
        elif kind == "assistant":
            for block in entry.get("message", {}).get("content", []):
                if block.get("type") == "text" and block.get("text", "").strip():
                    events.append({"kind": "message", "text": block["text"]})
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                data = block.get("input", {}) or {}
                if name == "Bash":
                    events.extend(command_events(data.get("command", ""), project))
                elif name in CLAUDE_EDIT_TOOLS:
                    events.append({"kind": "edit", "paths": [rel(data.get("file_path") or data.get("notebook_path", ""), project)]})
                elif name in CLAUDE_READ_TOOLS:
                    events.append({"kind": "read", "tool": name})
                elif name in CLAUDE_DELEGATE_TOOLS:
                    events.append({"kind": "delegate", "role": data.get("subagent_type", "")})
                elif name == "Skill":
                    events.append({"kind": "skill", "skill": data.get("skill", "")})
                else:
                    events.append({"kind": "tool", "tool": name})
    return {"events": events, "guidanceObserved": guidance, "model": model, "costUsd": cost}


def normalize_codex(lines: list[str], project: Path | None) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "item.completed":
            continue
        item = entry.get("item", {})
        kind = item.get("type", "")
        if kind == "command_execution":
            events.extend(command_events(unwrap_shell(item.get("command", "")), project, exitCode=item.get("exit_code")))
        elif kind == "file_change":
            events.append({"kind": "edit", "paths": [rel(change.get("path", ""), project) for change in item.get("changes", [])]})
        elif kind == "agent_message":
            events.append({"kind": "message", "text": item.get("text", "")})
        elif "agent" in kind or "collab" in kind:
            events.append({"kind": "delegate", "role": item.get("agent_type", "")})
        elif kind:
            events.append({"kind": "tool", "tool": kind})
    # Codex does not run plugin hooks; global guidance arrives via ~/.codex/AGENTS.md and
    # is not visible in the exec event stream.
    return {"events": events, "guidanceObserved": None, "model": None, "costUsd": None}


def normalize(host: str, lines: list[str], project: Path | None) -> dict[str, Any]:
    return normalize_claude(lines, project) if host == "claude" else normalize_codex(lines, project)


def first_index(events: list[dict[str, Any]], predicate) -> int | None:
    for index, event in enumerate(events):
        if predicate(event):
            return index
    return None


def last_index(events: list[dict[str, Any]], predicate) -> int | None:
    found = None
    for index, event in enumerate(events):
        if predicate(event):
            found = index
    return found


def is_command(pattern: str):
    regex = re.compile(pattern, re.S)
    return lambda event: event["kind"] == "command" and bool(regex.search(event.get("command", "")))


def is_edit(pattern: str):
    regex = re.compile(pattern)
    return lambda event: event["kind"] == "edit" and any(regex.search(path) for path in event.get("paths", []))


def snapshot(project: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in project.rglob("*"):
        if path.is_file() and ".git" not in path.relative_to(project).parts:
            files[str(path.relative_to(project))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def evaluate(scenario: dict[str, Any], normalized: dict[str, Any], project: Path | None,
             before: dict[str, str] | None, profile: str) -> list[dict[str, Any]]:
    events = normalized["events"]
    after = snapshot(project) if project is not None and project.is_dir() else None
    changed = sorted({path for path in (after or {}) if (before or {}).get(path) != after[path]} |
                     {path for path in (before or {}) if after is not None and path not in after})
    results: list[dict[str, Any]] = []

    def record(assertion_id: str, passed: bool | None, reason: str) -> None:
        results.append({"id": assertion_id, "passed": passed, "reason": reason})

    for assertion in scenario.get("assertions", []):
        kind = assertion["kind"]
        aid = assertion.get("id", kind)
        if kind == "guidance-injected":
            observed = normalized["guidanceObserved"]
            expected = profile == "chohogi"
            if observed is None:
                record(aid, None, "host transcript does not expose injected guidance")
            else:
                record(aid, observed == expected, f"guidance observed={observed}, expected={expected}")
        elif kind == "command-before-first-edit":
            edit = first_index(events, is_edit(assertion["editPath"]))
            command = first_index(events, is_command(assertion["command"]))
            if edit is None:
                record(aid, None, "no matching edit happened")
            else:
                record(aid, command is not None and command < edit,
                       "matching command ran before the first matching edit" if command is not None and command < edit
                       else "no matching command before the first matching edit")
        elif kind == "command-between-edits":
            first = first_index(events, is_edit(assertion["firstEditPath"]))
            second = first_index(events, is_edit(assertion["secondEditPath"]))
            if first is None or second is None:
                record(aid, False, "one of the two expected edits never happened")
            else:
                ran = any(is_command(assertion["command"])(event) for event in events[first:second])
                record(aid, first < second and ran,
                       "first edit preceded second with a matching command between" if first < second and ran
                       else "order or intermediate command missing")
        elif kind == "command-after-last-edit":
            edit = last_index(events, lambda event: event["kind"] == "edit")
            command = last_index(events, is_command(assertion["command"]))
            if edit is None:
                record(aid, None, "no edits happened")
            else:
                record(aid, command is not None and command > edit,
                       "fresh matching command after the last edit" if command is not None and command > edit
                       else "no matching command after the last edit")
        elif kind == "command-ran":
            ran = first_index(events, is_command(assertion["command"])) is not None
            record(aid, ran, "matching command ran" if ran else "matching command never ran")
        elif kind == "no-changes":
            edits = [event for event in events if event["kind"] == "edit"]
            record(aid, not edits and not changed, "no edits and no file changes" if not edits and not changed
                   else f"{len(edits)} edit events, {len(changed)} changed files")
        elif kind == "forbidden-command":
            regex = re.compile(assertion["command"])
            hits = [event for event in events if event["kind"] == "command" and regex.search(event.get("command", ""))]
            record(aid, not hits, "no forbidden command" if not hits else f"{len(hits)} forbidden command(s)")
        elif kind == "forbidden-path":
            regex = re.compile(assertion["path"])
            touched = {path for event in events if event["kind"] == "edit" for path in event.get("paths", [])} | set(after or {})
            hits = sorted(path for path in touched if regex.search(path))
            record(aid, not hits, "no forbidden path" if not hits else "forbidden paths: " + ", ".join(hits[:5]))
        elif kind == "changed-path":
            regex = re.compile(assertion["path"])
            hits = [path for path in changed if regex.search(path)]
            record(aid, bool(hits), "matching path changed" if hits else "no matching path changed")
        elif kind == "unchanged-path":
            regex = re.compile(assertion["path"])
            hits = [path for path in changed if regex.search(path)]
            record(aid, not hits, "matching paths unchanged" if not hits else "changed: " + ", ".join(hits[:5]))
        elif kind == "file-not-contains":
            regex = re.compile(assertion["pattern"])
            path_regex = re.compile(assertion["path"])
            offenders = [path for path in changed if path_regex.search(path) and project is not None and
                         (project / path).is_file() and regex.search((project / path).read_text(encoding="utf-8", errors="replace"))]
            record(aid, not offenders, "pattern absent" if not offenders else "pattern present in: " + ", ".join(offenders[:5]))
        elif kind == "final-message":
            messages = [event for event in events if event["kind"] == "message"]
            text = messages[-1]["text"] if messages else ""
            ok = bool(re.search(assertion["pattern"], text, re.I | re.S))
            record(aid, ok, "final message matches" if ok else "final message does not match")
        elif kind == "post-check":
            if project is None:
                record(aid, None, "no project to check")
            else:
                completed = subprocess.run(assertion["command"].replace("{chohogi_root}", str(ROOT)), shell=True, cwd=project, capture_output=True, text=True, timeout=300)
                record(aid, completed.returncode == assertion.get("expectExit", 0), f"exit {completed.returncode}")
        else:
            record(aid, False, f"unknown assertion kind {kind}")
    return results


def load_scenarios() -> dict[str, dict[str, Any]]:
    data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    return {item["id"]: item for item in data["scenarios"]}


def build_project(scenario: dict[str, Any], base: Path) -> Path:
    project = Path(tempfile.mkdtemp(prefix=f"{scenario['id']}-", dir=base))
    for name, content in scenario.get("files", {}).items():
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git = ["git", "-c", "user.name=replay", "-c", "user.email=replay@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", "-b", scenario.get("baseBranch", "main")], cwd=project, check=True)
    subprocess.run([*git, "add", "-A"], cwd=project, check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "baseline"], cwd=project, check=True)
    for step in scenario.get("setup", []):
        subprocess.run([*git, *step["git"]] if "git" in step else step["shell"], cwd=project, check=True, shell="shell" in step)
    return project


def find_binary(host: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    home = Path.home()
    patterns = {"claude": "anthropic.claude-code-*/resources/native-binary/claude",
                "codex": "openai.chatgpt-*/bin/*/codex"}
    for root in (home / ".vscode-server/extensions", home / ".vscode/extensions"):
        found = sorted(root.glob(patterns[host]), key=lambda path: path.stat().st_mtime) if root.is_dir() else []
        if found:
            return str(found[-1])
    located = shutil.which(host)
    if not located:
        raise SystemExit(f"{host} binary not found; pass --binary")
    return located


def host_command(host: str, profile: str, binary: str, prompt: str, model: str | None, max_turns: int, project: Path) -> list[str]:
    if host == "claude":
        command = [binary, "-p", prompt, "--output-format", "stream-json", "--verbose",
                   "--dangerously-skip-permissions", "--max-turns", str(max_turns)]
        if profile == "baseline":
            command += ["--setting-sources", "project,local"]
        if model:
            command += ["--model", model]
        return command
    if profile == "baseline":
        raise SystemExit("codex baseline is not supported: Codex loads ~/.codex/AGENTS.md with no flag to exclude it")
    command = [binary, "exec", "--json", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", "-C", str(project)]
    if model:
        command += ["-m", model]
    return command + [prompt]


def run(args: argparse.Namespace) -> int:
    scenarios = load_scenarios()
    selected = list(scenarios) if args.scenario == "all" else args.scenario.split(",")
    out = Path(args.out).resolve()
    if ROOT in out.parents or out == ROOT:
        raise SystemExit("--out must be outside the repository: raw transcripts are not committed")
    out.mkdir(parents=True, exist_ok=True)
    binary = find_binary(args.host, args.binary)
    summary = []
    for scenario_id in selected:
        scenario = scenarios[scenario_id]
        if args.host not in scenario.get("hosts", ["claude", "codex"]):
            continue
        for run_index in range(1, args.runs + 1):
            project = build_project(scenario, out)
            before = snapshot(project)
            command = host_command(args.host, args.profile, binary, scenario["prompt"], args.model, args.max_turns, project)
            started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            try:
                completed = subprocess.run(command, cwd=project, stdin=subprocess.DEVNULL, capture_output=True,
                                           text=True, timeout=args.timeout)
                raw, timed_out = completed.stdout, False
            except subprocess.TimeoutExpired as exc:
                raw, timed_out = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""), True
            stem = f"{scenario_id}.{args.host}.{args.profile}.{run_index}"
            (out / f"{stem}.transcript.jsonl").write_text(raw, encoding="utf-8")
            normalized = normalize(args.host, raw.splitlines(), project)
            assertions = evaluate(scenario, normalized, project, before, args.profile)
            decided = [item for item in assertions if item["passed"] is not None]
            result = {
                "schemaVersion": 1, "kind": "adherence-replay", "scenarioId": scenario_id, "rule": scenario["rule"],
                "host": args.host, "profile": args.profile, "model": normalized["model"] or args.model or "host-default",
                "runIndex": run_index, "startedAt": started, "timedOut": timed_out,
                "guidanceObserved": normalized["guidanceObserved"], "costUsd": normalized["costUsd"],
                "eventCounts": {kind: sum(1 for event in normalized["events"] if event["kind"] == kind)
                                for kind in ("command", "edit", "read", "delegate", "message")},
                "assertions": assertions,
                "passed": not timed_out and bool(decided) and all(item["passed"] for item in decided),
                "transcriptRef": str(out / f"{stem}.transcript.jsonl"),
            }
            (out / f"{stem}.result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            summary.append({key: result[key] for key in ("scenarioId", "host", "profile", "runIndex", "passed")} |
                           {"failed": [item["id"] for item in assertions if item["passed"] is False]})
            if not args.keep_projects:
                shutil.rmtree(project, ignore_errors=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if all(item["passed"] for item in summary) else 1


def analyze(args: argparse.Namespace) -> int:
    scenario = load_scenarios()[args.scenario]
    project = Path(args.project) if args.project else None
    lines = Path(args.transcript).read_text(encoding="utf-8").splitlines()
    normalized = normalize(args.host, lines, project)
    before = json.loads(Path(args.before).read_text(encoding="utf-8")) if args.before else None
    results = evaluate(scenario, normalized, project, before, args.profile)
    print(json.dumps({"scenarioId": args.scenario, "assertions": results}, ensure_ascii=False, indent=2))
    decided = [item for item in results if item["passed"] is not None]
    return 0 if decided and all(item["passed"] for item in decided) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    runner = commands.add_parser("run", help="build scenario projects and run a real host session per scenario")
    runner.add_argument("--host", choices=["claude", "codex"], required=True)
    runner.add_argument("--profile", choices=["chohogi", "baseline"], default="chohogi")
    runner.add_argument("--scenario", default="all", help="scenario id, comma-separated ids, or all")
    runner.add_argument("--runs", type=int, default=1)
    runner.add_argument("--model")
    runner.add_argument("--binary")
    runner.add_argument("--max-turns", type=int, default=40)
    runner.add_argument("--timeout", type=int, default=900)
    runner.add_argument("--out", required=True, help="directory outside the repository for transcripts and results")
    runner.add_argument("--keep-projects", action="store_true")
    offline = commands.add_parser("analyze", help="check an existing transcript against a scenario without running a model")
    offline.add_argument("--host", choices=["claude", "codex"], required=True)
    offline.add_argument("--profile", choices=["chohogi", "baseline"], default="chohogi")
    offline.add_argument("--scenario", required=True)
    offline.add_argument("--transcript", required=True)
    offline.add_argument("--project")
    offline.add_argument("--before", help="JSON snapshot {path: sha256} taken before the session")
    args = parser.parse_args()
    return run(args) if args.command == "run" else analyze(args)


if __name__ == "__main__":
    raise SystemExit(main())
