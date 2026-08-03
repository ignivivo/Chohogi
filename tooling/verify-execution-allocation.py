#!/usr/bin/env python3
"""Verify Chohogi's self-contained execution-allocation contract."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


MODES = frozenset(("direct", "sequential", "scoped-delegation"))
FORBIDDEN = frozenset(
    (
        "ask-user-execution-choice",
        "external-controller",
        "parallel-implementation",
        "persistent-change",
        "mandatory-worktree",
    )
)
REQUIRED_ALLOCATION_TERMS = (
    "<!-- chohogi:execution-allocation -->",
    "`direct`",
    "`sequential`",
    "`scoped-delegation`",
    "<!-- chohogi:execution-choice=internal -->",
    "외부 스킬의 handoff",
)
REQUIRED_METHOD_TERMS = (
    "<!-- chohogi:xylem=execution-methods -->",
    "<!-- chohogi:xylem-authority=methods-only -->",
    "원인 확인 전",
    "별도 controller",
)
REQUIRED_PACKET_TERMS = (
    "<!-- chohogi:context-packet -->",
    "긴 작업",
    "별도 하네스가 아니라 trunk",
    "비밀값",
)


def validate_fixture_document(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["Execution fixture document must be a JSON object."]
    errors: list[str] = []
    if data.get("schemaVersion") != 1:
        errors.append("Execution fixture schemaVersion must be 1.")
    if not isinstance(data.get("modes"), list) or set(data["modes"]) != MODES or len(data["modes"]) != len(MODES):
        errors.append("Execution fixture modes must exactly declare direct, sequential, scoped-delegation.")
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 5:
        return errors + ["Execution fixtures must contain at least five cases."]
    ids: set[str] = set()
    covered: set[str] = set()
    for index, fixture in enumerate(fixtures, start=1):
        label = f"execution fixture #{index}"
        if not isinstance(fixture, dict):
            errors.append(f"{label} must be an object.")
            continue
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            errors.append(f"{label} needs a non-empty id.")
        elif fixture_id in ids:
            errors.append(f"Duplicate execution fixture id: {fixture_id}")
        else:
            ids.add(fixture_id)
        if not isinstance(fixture.get("request"), str) or not fixture["request"].strip():
            errors.append(f"{fixture_id}: request must be non-empty.")
        mode = fixture.get("expectedMode")
        if mode not in MODES:
            errors.append(f"{fixture_id}: expectedMode must be a known mode.")
        else:
            covered.add(mode)
        artifacts = fixture.get("requiredArtifacts")
        if not isinstance(artifacts, list) or not artifacts or not all(isinstance(item, str) and item.strip() for item in artifacts):
            errors.append(f"{fixture_id}: requiredArtifacts must be a non-empty string list.")
        forbidden = fixture.get("forbiddenOutcomes")
        if not isinstance(forbidden, list) or not forbidden or not all(item in FORBIDDEN for item in forbidden):
            errors.append(f"{fixture_id}: forbiddenOutcomes must be known non-empty outcomes.")
        elif len(set(forbidden)) != len(forbidden):
            errors.append(f"{fixture_id}: forbiddenOutcomes cannot contain duplicates.")
        elif "ask-user-execution-choice" not in forbidden or "external-controller" not in forbidden:
            errors.append(f"{fixture_id}: must forbid execution-choice prompts and external controllers.")
    if covered != MODES:
        errors.append("Execution fixtures must cover every allocation mode.")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    files = {
        root / "assets/agents/chohogi/trunk/execution-allocation.md": REQUIRED_ALLOCATION_TERMS,
        root / "assets/agents/chohogi/xylem/execution-methods.md": REQUIRED_METHOD_TERMS,
        root / "assets/agents/chohogi/trunk/context-packet.md": REQUIRED_PACKET_TERMS,
    }
    for path, required_terms in files.items():
        if not path.is_file():
            errors.append(f"Missing execution asset: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                errors.append(f"{path.name} is missing contract term: {term}")
    fixture_path = root / "assets/agents/chohogi/trunk/evals/execution-fixtures.json"
    data: dict[str, Any] | None = None
    if not fixture_path.is_file():
        errors.append(f"Missing execution fixtures: {fixture_path}")
    else:
        try:
            raw = json.loads(fixture_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"Invalid execution fixture JSON: {error}")
        else:
            errors.extend(validate_fixture_document(raw))
            if isinstance(raw, dict):
                data = raw
    if data is not None:
        missing_mode = copy.deepcopy(data)
        missing_mode["modes"] = ["direct", "sequential"]
        if not validate_fixture_document(missing_mode):
            errors.append("Negative execution mutation was accepted: missing allocation mode")
        permitted_prompt = copy.deepcopy(data)
        permitted_prompt["fixtures"][0]["forbiddenOutcomes"].remove("ask-user-execution-choice")
        if not validate_fixture_document(permitted_prompt):
            errors.append("Negative execution mutation was accepted: execution-choice prompt permitted")
    if errors:
        print("Chohogi execution allocation verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Chohogi execution allocation verification: PASS (allocation contract, xylem methods, packet, and fixtures are valid).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
