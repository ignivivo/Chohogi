#!/usr/bin/env python3
"""Verify that the runtime entrypoint can load and still states Chohogi's core rules.

Sessions act on the injected guidance and rarely open route documents
(DBG-20260930-diagnosis-phase2, F21), so a silently deleted rule sentence or a
broken hook path removes a rule without any other check failing (F22). This
checks the SessionStart hook's referenced paths and one anchor phrase per core
rule. An anchor proves the sentence is present, not that a session follows it.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

T = "assets/agents/trunk_orchestration/"
ANCHORS = {
    "assets/runtime_entrypoint/AGENTS.md": (
        "~/.agents/chohogi/trunk_orchestration/conductor.md",  # route selection entry (the red-flag text names it again)
        "실패하는 테스트를 먼저",               # test-first
        "완료 주장은 처리 방식과 무관하다",       # completion gate
        "| 생각 | 실제 |",                     # skip red-flag table
        "execution-record.py",                # material work record
    ),
    T + "conductor.md": ('"진입한다"는 해당 skill',),
    T + "branches_workflows/delivery.md": ("실패하는 테스트를 먼저",),
    T + "branches_workflows/debugging.md": ("네 번째 수정을 시도하지 않는다",),
    T + "task-loop.md": ("## 최종 검토",),
    "skills/homeostasis/SKILL.md": ("execution-record.py --project", "decide the smallest prevention first"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()
    errors: list[str] = []
    hook = root / "hooks/hooks.json"
    if not hook.is_file():
        errors.append("hooks/hooks.json is missing")
    else:
        paths = re.findall(r"\$root/([A-Za-z0-9_./-]+)", hook.read_text(encoding="utf-8"))
        if not paths:
            errors.append("hooks/hooks.json references no $root/ path")
        for rel in paths:
            if not (root / rel).exists():
                errors.append(f"hooks/hooks.json references a missing path: {rel}")
    for rel, anchors in ANCHORS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel} is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"{rel} lost its core-rule anchor: {anchor}")
    if errors:
        print("Runtime entrypoint verification: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Runtime entrypoint verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
