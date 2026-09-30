"""Mutation test: break one core rule at a time in a clone and see whether any verifier or test fails."""
import json, re, subprocess, sys
from pathlib import Path

CLONE = Path(sys.argv[1])
T = "assets/agents/trunk_orchestration/"
VERIFIERS = [p for p in sorted((CLONE / "tooling").glob("verify-*.py"))]
ARGS = {"verify-external-capability-contract.py": ["--project", "."], "verify-project-document-registry.py": ["--root", "."]}
SKIP = {"verify-retired-capability.py", "verify-status-provenance.py"}


def para_drop(text, start):
    i = text.index(start)
    j = text.find("\n\n", i)
    return text[:i] + text[j + 2:]


def between_drop(text, start, end):
    i = text.index(start)
    j = text.index(end, i)
    return text[:i] + text[j:]


def line_drop(text, needle):
    return "\n".join(l for l in text.splitlines() if needle not in l) + "\n"


MUTATIONS = [
    ("M1 test-first paragraph removed from AGENTS.md", "assets/runtime_entrypoint/AGENTS.md", lambda t: para_drop(t, "테스트 우선도 처리 방식과 크기와 무관하다")),
    ("M2 completion gate removed from AGENTS.md", "assets/runtime_entrypoint/AGENTS.md", lambda t: para_drop(t, "완료 주장은 처리 방식과 무관하다")),
    ("M3 red-flag table removed from AGENTS.md", "assets/runtime_entrypoint/AGENTS.md", lambda t: between_drop(t, "| 생각 | 실제 |", "<!-- chohogi:global-guidance:end -->") if "<!-- chohogi:global-guidance:end -->" in t else t[: t.index("| 생각 | 실제 |")]),
    ("M4 conductor path removed from AGENTS.md", "assets/runtime_entrypoint/AGENTS.md", lambda t: t.replace("~/.agents/chohogi/trunk_orchestration/conductor.md", "the conductor")),
    ("M5 debugging row removed from conductor", T + "conductor.md", lambda t: line_drop(t, "| `debugging` |")),
    ("M6 maintenance entry paragraph removed from conductor", T + "conductor.md", lambda t: para_drop(t, '"진입한다"는 해당 skill')),
    ("M7 delivery test-first step weakened", T + "branches_workflows/delivery.md", lambda t: re.sub(r"실패하는 테스트를 먼저[^\n]*", "적절히 검증한다.", t)),
    ("M8 three-failed-fixes stop removed from debugging", T + "branches_workflows/debugging.md", lambda t: t.replace("**세 번 실패했으면 네 번째 수정을 시도하지 않는다.**", "")),
    ("M9 scoped-delegation row removed from execution allocation", T + "execution-allocation.md", lambda t: line_drop(t, "| `scoped-delegation` |")),
    ("M10 homeostasis Method step 1 (execution record) removed", "skills/homeostasis/SKILL.md", lambda t: between_drop(t, "1. State the admission evidence", "2. Run `python3 tooling/genome_map.py")),
    ("M11 Claude role mirror body diverges", "agents/critical-reviewer.md", lambda t: t.replace("Review independently", "Review quickly")),
    ("M12 Claude recommendation reverts to bare alias", T + "model-recommendations.json", lambda t: t.replace('"scout": {"model": "claude-haiku-4-5"', '"scout": {"model": "haiku"', 1)),
    ("M13 non-blocking model rule removed", "assets/runtime_entrypoint/AGENTS.md", lambda t: t.replace("턴을 멈추는 질문 도구", "질문")),
    ("M14 finalized plan marked active again", ".agents/chohogi-document-registry.json", lambda t: t.replace('"activeExecutionPlan": null', '"activeExecutionPlan": "docs/chohogi/plans/2026-09-23-observability-closure.md"').replace('"role": "history",\n      "authority": "evidence",\n      "state": "historical",', '"role": "active-plan",\n      "authority": "execution-queue",\n      "state": "active",', 1)),
    ("M15 SessionStart hook points at a wrong guidance path", "hooks/hooks.json", lambda t: t.replace("runtime_entrypoint/AGENTS.md", "runtime_entrypoint/AGENT.md")),
    ("M16 final review section removed from task loop", T + "task-loop.md", lambda t: between_drop(t, "## 최종 검토", "## 계속 진행과 멈춤")),
    ("M17 learning-first rule removed from homeostasis result", "skills/homeostasis/SKILL.md", lambda t: t.replace("let `$learning` decide the smallest prevention first; use Homeostasis only if", "use Homeostasis if")),
]


def run_checks():
    failed = []
    for v in VERIFIERS:
        if v.name in SKIP:
            continue
        r = subprocess.run([sys.executable, str(v), *ARGS.get(v.name, [])], cwd=CLONE, capture_output=True, text=True)
        if r.returncode != 0:
            failed.append(v.name)
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tooling/tests"], cwd=CLONE, capture_output=True, text=True)
    if r.returncode != 0:
        failed.append("unittest")
    return failed


base = run_checks()
print(json.dumps({"baseline_failures": base}, ensure_ascii=False))
for name, rel, fn in MUTATIONS:
    path = CLONE / rel
    original = path.read_text(encoding="utf-8")
    try:
        mutated = fn(original)
    except ValueError as exc:
        print(json.dumps({"mutation": name, "error": f"anchor not found: {exc}"}, ensure_ascii=False))
        continue
    if mutated == original:
        print(json.dumps({"mutation": name, "error": "no change applied"}, ensure_ascii=False))
        continue
    path.write_text(mutated, encoding="utf-8")
    failed = [f for f in run_checks() if f not in base]
    path.write_text(original, encoding="utf-8")
    print(json.dumps({"mutation": name, "caught": bool(failed), "by": failed}, ensure_ascii=False))
