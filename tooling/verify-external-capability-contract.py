#!/usr/bin/env python3
"""Validate project-attached external capability contracts and surface conflicts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_PATH = Path(".agents") / "chohogi-external-capabilities.json"
REQUIRED_PROHIBITIONS = {"artifact-path", "commit", "workflow", "completion"}


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(document: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    reports: list[str] = []
    if not isinstance(document, dict) or document.get("schemaVersion") != 1:
        return ["contract must be an object with schemaVersion 1"], reports
    capabilities = document.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        return ["capabilities must be a non-empty list"], reports
    ids: set[str] = set()
    for index, capability in enumerate(capabilities, start=1):
        label = f"capability #{index}"
        if not isinstance(capability, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = capability.get("id")
        if not non_empty_string(identifier):
            errors.append(f"{label} needs a non-empty id")
        elif identifier in ids:
            errors.append(f"duplicate capability id: {identifier}")
        else:
            ids.add(identifier)
        for field in ("provider", "purpose", "trigger", "nonTrigger"):
            if not non_empty_string(capability.get(field)):
                errors.append(f"{identifier}: {field} must be a non-empty string")
        if capability.get("state") != "attach-specialist":
            errors.append(f"{identifier}: state must be attach-specialist")
        actions = capability.get("allowedActions")
        if not isinstance(actions, list) or not actions or not all(non_empty_string(item) for item in actions):
            errors.append(f"{identifier}: allowedActions must be a non-empty string list")
        prohibitions = capability.get("prohibitedControllerClaims")
        if not isinstance(prohibitions, list) or not all(non_empty_string(item) for item in prohibitions):
            errors.append(f"{identifier}: prohibitedControllerClaims must be a string list")
        else:
            missing = REQUIRED_PROHIBITIONS - set(prohibitions)
            if missing:
                errors.append(f"{identifier}: missing prohibited controller claims: {', '.join(sorted(missing))}")
        conflicts = capability.get("conflicts")
        if not isinstance(conflicts, list):
            errors.append(f"{identifier}: conflicts must be a list")
            continue
        for conflict_index, conflict in enumerate(conflicts, start=1):
            if not isinstance(conflict, dict) or not all(non_empty_string(conflict.get(field)) for field in ("externalRequirement", "chohogiResolution", "userReport")):
                errors.append(f"{identifier}: conflict #{conflict_index} needs externalRequirement, chohogiResolution, and userReport")
                continue
            reports.append(f"USER-REPORT {identifier}: {conflict['userReport']} Resolution: {conflict['chohogiResolution']}")
    return errors, reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    arguments = parser.parse_args()
    path = arguments.project / CONTRACT_PATH
    if not path.exists():
        print("External capability contract: none declared")
        return 0
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"External capability contract: FAIL\n- invalid contract: {exc}", file=sys.stderr)
        return 1
    errors, reports = validate(document)
    if errors:
        print("External capability contract: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    for report in reports:
        print(report)
    print("External capability contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
