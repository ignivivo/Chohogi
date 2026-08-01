#!/usr/bin/env python3
"""Verify Chohogi's route contracts and deterministic fixture schema."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


DAILY_ROUTES = frozenset(("product-decision", "delivery", "debugging"))
BRANCHES = frozenset(("learning", "homeostasis"))
FLOWS = DAILY_ROUTES | BRANCHES
SELECTION_KINDS = frozenset(("direct", "defer", "daily-route", "branch"))
MUTATION_AUTHORITIES = frozenset(("none", "requested"))
DEFER_MARKER = "<!-- chohogi:defer=no-flow-no-write -->"
DEFER_REQUIRED_ARTIFACTS = frozenset(("evidence-gap", "no-change", "reentry-condition"))
REQUIRED_SECTIONS = (
    "role",
    "entry",
    "negative-scope",
    "input",
    "method",
    "optional-capabilities",
    "exit",
    "next",
)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_defer_policy_text(label: str, text: str) -> list[str]:
    if text.count(DEFER_MARKER) != 1:
        return [f"{label} must contain exactly one defer no-flow/no-write marker."]
    return []


def validate_route_text(route: str, text: str) -> list[str]:
    errors: list[str] = []
    route_marker = f"<!-- chohogi:route={route} -->"
    if text.count(route_marker) != 1:
        errors.append(f"Route {route} must contain exactly one route marker.")

    positions: list[tuple[str, int, str]] = []
    for section in REQUIRED_SECTIONS:
        marker = f"<!-- chohogi:section={section} -->"
        if text.count(marker) != 1:
            errors.append(f"Route {route} must contain exactly one section marker: {section}")
            continue
        positions.append((section, text.index(marker), marker))

    if len(positions) != len(REQUIRED_SECTIONS):
        return errors
    if [section for section, _, _ in positions] != list(REQUIRED_SECTIONS):
        errors.append(f"Route {route} section markers are not in required order.")
        return errors

    for index, (section, start, marker) in enumerate(positions):
        end = positions[index + 1][1] if index + 1 < len(positions) else len(text)
        if not text[start + len(marker) : end].strip():
            errors.append(f"Route {route} section is empty: {section}")
    return errors


def validate_fixture_document(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Route fixture document must be a JSON object."]
    if data.get("schemaVersion") != 3:
        errors.append("Route fixture schemaVersion must be 3.")
    selection_kinds = data.get("selectionKinds")
    if (
        not isinstance(selection_kinds, list)
        or len(selection_kinds) != len(SELECTION_KINDS)
        or set(selection_kinds) != SELECTION_KINDS
    ):
        errors.append("Route fixture selectionKinds must exactly declare direct, defer, daily-route, and branch.")
    mutation_authorities = data.get("mutationAuthorities")
    if (
        not isinstance(mutation_authorities, list)
        or len(mutation_authorities) != len(MUTATION_AUTHORITIES)
        or set(mutation_authorities) != MUTATION_AUTHORITIES
    ):
        errors.append("Route fixture mutationAuthorities must exactly declare none and requested.")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 14:
        return errors + ["Route fixtures must contain at least 14 cases."]

    ids: set[str] = set()
    covered_daily: set[str] = set()
    covered_branches: set[str] = set()
    direct_count = 0
    defer_count = 0

    for index, fixture in enumerate(fixtures, start=1):
        label = f"fixture #{index}"
        if not isinstance(fixture, dict):
            errors.append(f"{label} must be an object.")
            continue
        fixture_id = fixture.get("id")
        if not non_empty_string(fixture_id):
            errors.append(f"{label} has no non-empty string id.")
            fixture_id = label
        elif fixture_id in ids:
            errors.append(f"Duplicate fixture id: {fixture_id}")
        else:
            ids.add(fixture_id)

        if not non_empty_string(fixture.get("request")):
            errors.append(f"{fixture_id} has no non-empty string request.")

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{fixture_id} has no expected object.")
            continue
        kind = expected.get("kind")
        flow = expected.get("flow")
        if kind not in SELECTION_KINDS:
            errors.append(f"{fixture_id}: expected.kind must be direct, defer, daily-route, or branch.")
        elif kind in {"direct", "defer"}:
            if kind == "direct":
                direct_count += 1
            else:
                defer_count += 1
            if flow is not None:
                errors.append(f"{fixture_id}: {kind} kind must use null flow.")
        elif kind == "daily-route":
            if flow not in DAILY_ROUTES:
                errors.append(f"{fixture_id}: daily-route must select a daily route.")
            else:
                covered_daily.add(flow)
        elif kind == "branch":
            if flow not in BRANCHES:
                errors.append(f"{fixture_id}: branch must select a branch.")
            else:
                covered_branches.add(flow)

        forbidden = fixture.get("forbiddenFlows")
        if not isinstance(forbidden, list) or not forbidden or not all(isinstance(item, str) and item in FLOWS for item in forbidden):
            errors.append(f"{fixture_id}: forbiddenFlows must be a non-empty list of known flow names.")
        else:
            if len(set(forbidden)) != len(forbidden):
                errors.append(f"{fixture_id}: forbiddenFlows cannot contain duplicates.")
            if flow in forbidden:
                errors.append(f"{fixture_id}: selected flow cannot be forbidden.")
            if kind == "defer" and (len(forbidden) != len(FLOWS) or set(forbidden) != FLOWS):
                errors.append(f"{fixture_id}: defer must forbid every known flow.")

        if fixture.get("mutationAuthority") not in MUTATION_AUTHORITIES:
            errors.append(f"{fixture_id}: mutationAuthority must be none or requested.")

        artifacts = fixture.get("requiredArtifacts")
        if not isinstance(artifacts, list) or not artifacts or not all(non_empty_string(item) for item in artifacts):
            errors.append(f"{fixture_id}: requiredArtifacts must be a non-empty string list.")
        elif kind == "defer" and not DEFER_REQUIRED_ARTIFACTS.issubset(set(artifacts)):
            missing_artifacts = ", ".join(sorted(DEFER_REQUIRED_ARTIFACTS - set(artifacts)))
            errors.append(f"{fixture_id}: defer must require evidence-gap, no-change, and reentry-condition (missing: {missing_artifacts}).")

    missing_daily = DAILY_ROUTES - covered_daily
    missing_branches = BRANCHES - covered_branches
    if direct_count == 0:
        errors.append("Fixtures must cover at least one direct outcome.")
    if defer_count == 0:
        errors.append("Fixtures must cover at least one defer outcome.")
    if missing_daily:
        errors.append("Fixtures do not cover daily routes: " + ", ".join(sorted(missing_daily)))
    if missing_branches:
        errors.append("Fixtures do not cover branches: " + ", ".join(sorted(missing_branches)))
    return errors


def run_negative_mutation_checks(
    data: dict[str, Any], route_text: str, guidance_text: str, conductor_text: str
) -> list[str]:
    """Prove the structural validators reject representative malformed contracts."""

    errors: list[str] = []
    mutations: list[tuple[str, dict[str, Any]]] = []

    missing_request = copy.deepcopy(data)
    missing_request["fixtures"][0]["request"] = ""
    mutations.append(("empty request", missing_request))

    contradictory_flow = copy.deepcopy(data)
    contradictory_flow["fixtures"][2]["expected"]["flow"] = "delivery"
    mutations.append(("selected flow forbidden by its fixture", contradictory_flow))

    branch_as_daily_route = copy.deepcopy(data)
    branch_as_daily_route["fixtures"][2]["expected"] = {"kind": "daily-route", "flow": "homeostasis"}
    mutations.append(("branch encoded as a daily route", branch_as_daily_route))

    defer_with_flow = copy.deepcopy(data)
    for fixture in defer_with_flow["fixtures"]:
        if fixture["expected"]["kind"] == "defer":
            fixture["expected"]["flow"] = "learning"
            break
    mutations.append(("defer outcome selecting a flow", defer_with_flow))

    defer_with_partial_forbidden_flows = copy.deepcopy(data)
    for fixture in defer_with_partial_forbidden_flows["fixtures"]:
        if fixture["expected"]["kind"] == "defer":
            fixture["forbiddenFlows"] = ["learning"]
            break
    mutations.append(("defer outcome not forbidding every flow", defer_with_partial_forbidden_flows))

    defer_without_reentry_condition = copy.deepcopy(data)
    for fixture in defer_without_reentry_condition["fixtures"]:
        if fixture["expected"]["kind"] == "defer":
            fixture["requiredArtifacts"] = ["evidence-gap", "no-change"]
            break
    mutations.append(("defer outcome without all required artifacts", defer_without_reentry_condition))

    duplicate_mutation_authorities = copy.deepcopy(data)
    duplicate_mutation_authorities["mutationAuthorities"].append("requested")
    mutations.append(("duplicate mutation authority", duplicate_mutation_authorities))

    for label, mutated in mutations:
        if not validate_fixture_document(mutated):
            errors.append(f"Negative fixture mutation was accepted: {label}")

    marker = "<!-- chohogi:section=method -->"
    if not validate_route_text("product-decision", route_text.replace(marker, "", 1)):
        errors.append("Negative route mutation was accepted: missing method section marker")
    if not validate_defer_policy_text("Global guidance", guidance_text.replace(DEFER_MARKER, "", 1)):
        errors.append("Negative policy mutation was accepted: missing global defer marker")
    if not validate_defer_policy_text("Conductor", conductor_text.replace(DEFER_MARKER, "", 1)):
        errors.append("Negative policy mutation was accepted: missing conductor defer marker")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    guidance_text: str | None = None
    conductor_text: str | None = None

    guidance = root / "assets/codex/AGENTS.md"
    if not guidance.is_file():
        errors.append(f"Missing global guidance: {guidance}")
    else:
        guidance_text = guidance.read_text(encoding="utf-8")
        if "trunk/routes/<flow>.md" not in guidance_text:
            errors.append("Global guidance does not direct selected daily routes to trunk/routes/<flow>.md.")
        errors.extend(validate_defer_policy_text("Global guidance", guidance_text))

    conductor = root / "assets/agents/chohogi/trunk/conductor.md"
    if not conductor.is_file():
        errors.append(f"Missing conductor: {conductor}")
    else:
        conductor_text = conductor.read_text(encoding="utf-8")
        if "routes/<flow>.md" not in conductor_text:
            errors.append("Conductor does not direct selected daily routes to routes/<flow>.md.")
        errors.extend(validate_defer_policy_text("Conductor", conductor_text))
        for route in DAILY_ROUTES:
            if f"`{route}`" not in conductor_text:
                errors.append(f"Conductor does not name daily route: {route}")

    route_texts: dict[str, str] = {}
    for route in DAILY_ROUTES:
        route_path = root / f"assets/agents/chohogi/trunk/routes/{route}.md"
        if not route_path.is_file():
            errors.append(f"Missing route: {route_path}")
            continue
        route_texts[route] = route_path.read_text(encoding="utf-8")
        errors.extend(validate_route_text(route, route_texts[route]))

    fixture_path = root / "assets/agents/chohogi/trunk/evals/route-fixtures.json"
    data: dict[str, Any] | None = None
    if not fixture_path.is_file():
        errors.append(f"Missing route fixture file: {fixture_path}")
    else:
        try:
            raw_data = json.loads(fixture_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"Invalid fixture JSON: {error}")
        else:
            errors.extend(validate_fixture_document(raw_data))
            if isinstance(raw_data, dict):
                data = raw_data

    if data is not None and "product-decision" in route_texts and guidance_text is not None and conductor_text is not None:
        errors.extend(run_negative_mutation_checks(data, route_texts["product-decision"], guidance_text, conductor_text))

    if errors:
        print("Chohogi route verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Chohogi route verification: PASS (route contracts, fixtures, and negative mutations are valid).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
