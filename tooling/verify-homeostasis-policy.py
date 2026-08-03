#!/usr/bin/env python3
"""Verify Homeostasis admission and evaluation-budget boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require_terms(path: Path, terms: tuple[str, ...], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing required policy: {path}")
        return
    text = path.read_text(encoding="utf-8")
    for term in terms:
        if term not in text:
            errors.append(f"{path.name} is missing required term: {term}")


def main() -> int:
    errors: list[str] = []
    skill = ROOT / "assets/agents/skills/homeostasis/SKILL.md"
    admission = ROOT / "assets/agents/skills/homeostasis/references/admission-policy.md"
    conductor = ROOT / "assets/agents/chohogi/trunk/conductor.md"
    transition = ROOT / "assets/agents/chohogi/trunk/state-transition.md"
    budget = ROOT / "assets/agents/chohogi/trunk/evals/evaluation-budget-policy.md"
    manifest = ROOT / "manifest.yaml"

    require_terms(skill, ("Scope gate", "Evidence gate", "evaluation-budget-policy.md"), errors)
    require_terms(admission, ("## Enter", "## Do not enter", "approved-global-change"), errors)
    require_terms(conductor, ("`learning`과 `homeostasis`는 일상 흐름과 경쟁하는 route가 아니다",), errors)
    require_terms(transition, ("scope gate", "evidence gate", "자동 시작되지는 않는다"), errors)
    require_terms(budget, ("Never run baseline and candidate for every task", "Shared skill", "Route, role, or model policy", "25%"), errors)
    require_terms(manifest, ("id: evaluation-budget-policy", "id: homeostasis"), errors)

    fixture_path = ROOT / "assets/agents/chohogi/trunk/evals/homeostasis-admission-fixtures.json"
    try:
        fixture_doc = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid Homeostasis admission fixtures: {exc}")
        fixture_doc = {}
    fixtures = fixture_doc.get("fixtures") if isinstance(fixture_doc, dict) else None
    if fixture_doc.get("schemaVersion") != 1:
        errors.append("Homeostasis admission fixture schemaVersion must be 1.")
    if not isinstance(fixtures, list) or len(fixtures) < 6:
        errors.append("Homeostasis admission fixtures must contain at least six cases.")
    else:
        ids = {item.get("id") for item in fixtures if isinstance(item, dict)}
        expected_ids = {
            "requested-global-model-policy",
            "single-project-react-bug",
            "install-discovery-divergence",
            "interesting-external-plugin",
            "project-candidate-without-global-effect",
            "paired-replay-for-global-route-candidate",
        }
        if expected_ids - ids:
            errors.append("Homeostasis admission fixtures miss required cases: " + ", ".join(sorted(expected_ids - ids)))
        outcomes = {item.get("expected") for item in fixtures if isinstance(item, dict)}
        if outcomes != {"enter", "do-not-enter"}:
            errors.append("Homeostasis admission fixtures must cover enter and do-not-enter outcomes.")

    if errors:
        print("Chohogi Homeostasis policy verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Chohogi Homeostasis policy verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
