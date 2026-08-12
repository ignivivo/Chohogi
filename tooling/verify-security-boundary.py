#!/usr/bin/env python3
"""Verify Chohogi's pre-code security boundary contract and fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURES = ROOT / "assets/agents/trunk_orchestration/evaluation/security-boundary-fixtures.json"
REQUIRED_BOUNDARY_TERMS = (
    "pre-code-security-acceptance",
    "project-execution-gate-required",
    "machine-readable observation",
    "nonzero failure exit path",
    "A checklist, installed package, or successful command that ignores its",
    "report is not a gate.",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    arguments = parser.parse_args()
    errors: list[str] = []
    boundary = ROOT / "assets/agents/trunk_orchestration/security-boundary.md"
    delivery = ROOT / "assets/agents/trunk_orchestration/branches_workflows/delivery.md"
    project_leaves = ROOT / "assets/agents/trunk_orchestration/project-leaves.md"
    for path, terms in (
        (boundary, REQUIRED_BOUNDARY_TERMS),
        (delivery, ("security-boundary.md", "pre-code-security-acceptance")),
        (project_leaves, ("scanner·gate", "실제 verifier 또는 CI/fixture")),
    ):
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for term in terms:
            if term not in text:
                errors.append(f"{path.name} is missing required term: {term}")
    try:
        document: Any = json.loads(arguments.fixtures.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid security boundary fixtures: {exc}")
        document = {}
    fixtures = document.get("fixtures") if isinstance(document, dict) else None
    if not isinstance(document, dict) or document.get("schemaVersion") != 1 or not isinstance(fixtures, list):
        errors.append("security boundary fixtures must have schemaVersion 1 and a fixtures list")
        fixtures = []
    required_ids = {"ordinary-copy-change", "authenticated-api-change", "agent-tool-change", "release-gate-claim"}
    by_id = {item.get("id"): item for item in fixtures if isinstance(item, dict)}
    if required_ids - set(by_id):
        errors.append("security boundary fixtures missing: " + ", ".join(sorted(required_ids - set(by_id))))
    for identifier in required_ids & set(by_id):
        item = by_id[identifier]
        if not isinstance(item.get("riskSignals"), list):
            errors.append(f"{identifier}: riskSignals must be a list")
        if not isinstance(item.get("expectedDisposition"), str):
            errors.append(f"{identifier}: expectedDisposition must be a string")
    if by_id.get("ordinary-copy-change", {}).get("expectedDisposition") != "no-special-security-boundary":
        errors.append("ordinary-copy-change must not require a security gate")
    for identifier in ("authenticated-api-change", "agent-tool-change"):
        if by_id.get(identifier, {}).get("expectedDisposition") != "pre-code-security-acceptance":
            errors.append(f"{identifier} must require pre-code security acceptance")
    if by_id.get("release-gate-claim", {}).get("expectedDisposition") != "project-execution-gate-required":
        errors.append("release-gate-claim must require a project execution gate")
    if errors:
        print("Security boundary verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Security boundary verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
