#!/usr/bin/env python3
"""Verify Chohogi's internal-method and external-capability boundary."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


RESOLUTIONS = frozenset(("chohogi-internal", "native-system", "capability-provider", "safe-fallback", "project-leaf"))
FORBIDDEN = frozenset((
    "external-controller",
    "copy-native-system-skill",
    "invoke-absorbed-method-source",
    "assume-cache-is-authorized",
    "mutate-private-config",
    "ask-user-execution-choice",
    "promote-project-leaf-globally",
))
REQUIRED_TERMS = (
    "<!-- chohogi:capability-selection -->",
    "<!-- chohogi:provider-authority=capability-only -->",
    "`chohogi-internal`",
    "`native-system`",
    "`capability-provider`",
    "`absorbed-method-source`",
    "`project-leaf`",
    "controller가 아니며",
    "캐시",
    "Superpowers",
)


def validate_fixture_document(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["Capability fixture document must be a JSON object."]
    errors: list[str] = []
    if data.get("schemaVersion") != 1:
        errors.append("Capability fixture schemaVersion must be 1.")
    resolutions = data.get("resolutions")
    if not isinstance(resolutions, list) or set(resolutions) != RESOLUTIONS or len(resolutions) != len(RESOLUTIONS):
        errors.append("Capability fixture resolutions must exactly declare the supported resolutions.")
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 5:
        return errors + ["Capability fixtures must contain at least five cases."]
    ids: set[str] = set()
    covered: set[str] = set()
    for index, fixture in enumerate(fixtures, start=1):
        label = f"capability fixture #{index}"
        if not isinstance(fixture, dict):
            errors.append(f"{label} must be an object.")
            continue
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            errors.append(f"{label} needs a non-empty id.")
        elif fixture_id in ids:
            errors.append(f"Duplicate capability fixture id: {fixture_id}")
        else:
            ids.add(fixture_id)
        if not isinstance(fixture.get("request"), str) or not fixture["request"].strip():
            errors.append(f"{fixture_id}: request must be non-empty.")
        resolution = fixture.get("expectedResolution")
        if resolution not in RESOLUTIONS:
            errors.append(f"{fixture_id}: expectedResolution must be known.")
        else:
            covered.add(resolution)
        artifacts = fixture.get("requiredArtifacts")
        if not isinstance(artifacts, list) or not artifacts or not all(isinstance(item, str) and item.strip() for item in artifacts):
            errors.append(f"{fixture_id}: requiredArtifacts must be a non-empty string list.")
        forbidden = fixture.get("forbiddenOutcomes")
        if not isinstance(forbidden, list) or not forbidden or not all(item in FORBIDDEN for item in forbidden):
            errors.append(f"{fixture_id}: forbiddenOutcomes must be a known non-empty list.")
        elif len(set(forbidden)) != len(forbidden):
            errors.append(f"{fixture_id}: forbiddenOutcomes cannot contain duplicates.")
        elif "external-controller" not in forbidden:
            errors.append(f"{fixture_id}: must forbid an external controller.")
    if covered != RESOLUTIONS:
        errors.append("Capability fixtures must cover every supported resolution.")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    contract_path = root / "assets/agents/chohogi/trunk/capability-selection.md"
    if not contract_path.is_file():
        errors.append(f"Missing capability-selection contract: {contract_path}")
    else:
        text = contract_path.read_text(encoding="utf-8")
        for term in REQUIRED_TERMS:
            if term not in text:
                errors.append(f"capability-selection.md is missing contract term: {term}")
    fixture_path = root / "assets/agents/chohogi/trunk/evals/capability-fixtures.json"
    data: dict[str, Any] | None = None
    if not fixture_path.is_file():
        errors.append(f"Missing capability fixtures: {fixture_path}")
    else:
        try:
            raw = json.loads(fixture_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"Invalid capability fixture JSON: {error}")
        else:
            errors.extend(validate_fixture_document(raw))
            if isinstance(raw, dict):
                data = raw
    if data is not None:
        missing_resolution = copy.deepcopy(data)
        missing_resolution["resolutions"] = ["chohogi-internal", "native-system"]
        if not validate_fixture_document(missing_resolution):
            errors.append("Negative capability mutation was accepted: missing resolution")
        permitted_controller = copy.deepcopy(data)
        permitted_controller["fixtures"][0]["forbiddenOutcomes"].remove("external-controller")
        if not validate_fixture_document(permitted_controller):
            errors.append("Negative capability mutation was accepted: external controller permitted")
    if errors:
        print("Chohogi capability-boundary verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Chohogi capability-boundary verification: PASS (internal methods, live providers, and fallback boundary are valid).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
