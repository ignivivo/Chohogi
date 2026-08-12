#!/usr/bin/env python3
"""Normalize observed model catalogs and produce bounded session-policy decisions.

This tool never discovers providers, reads credentials, or changes model settings.
Provider/runtime adapters must supply an already exposed, non-secret catalog.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EFFORT = ("low", "medium", "high", "ultra")


class ContractError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON at {path}: {exc}") from exc


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be a non-empty string")
    return value


def validate_catalog(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ContractError("catalog schemaVersion must be 1")
    text(value.get("observedAt"), "catalog.observedAt")
    observations = value.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ContractError("catalog.observations must be a non-empty list")
    identities: set[tuple[str, str]] = set()
    for index, item in enumerate(observations):
        prefix = f"catalog.observations[{index}]"
        if not isinstance(item, dict):
            raise ContractError(f"{prefix} must be an object")
        identity = (text(item.get("provider"), f"{prefix}.provider"), text(item.get("model"), f"{prefix}.model"))
        if identity in identities:
            raise ContractError(f"duplicate catalog model: {identity[0]}/{identity[1]}")
        identities.add(identity)
        if not isinstance(item.get("available"), bool):
            raise ContractError(f"{prefix}.available must be boolean")
        levels = item.get("reasoningLevels")
        if not isinstance(levels, list) or not levels or any(level not in EFFORT for level in levels) or len(set(levels)) != len(levels):
            raise ContractError(f"{prefix}.reasoningLevels must be unique supported effort levels")
        capabilities = item.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or any(not isinstance(capability, str) or not capability.strip() for capability in capabilities):
            raise ContractError(f"{prefix}.capabilities must be a non-empty string list")
        text(item.get("source"), f"{prefix}.source")
        price = item.get("price")
        if price is not None:
            if not isinstance(price, dict):
                raise ContractError(f"{prefix}.price must be an object")
            for key in ("inputUsdPerMillion", "outputUsdPerMillion"):
                if not isinstance(price.get(key), (int, float)) or isinstance(price[key], bool) or price[key] < 0:
                    raise ContractError(f"{prefix}.price.{key} must be a non-negative number")
    return value


def validate_task(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ContractError("task schemaVersion must be 1")
    text(value.get("role"), "task.role")
    capabilities = value.get("requiredCapabilities")
    if not isinstance(capabilities, list) or any(not isinstance(item, str) or not item.strip() for item in capabilities):
        raise ContractError("task.requiredCapabilities must be a string list")
    effort = value.get("minimumReasoning")
    if effort not in EFFORT:
        raise ContractError("task.minimumReasoning must be low, medium, high, or ultra")
    return value


def price_total(item: dict[str, Any]) -> float:
    price = item.get("price")
    if not isinstance(price, dict):
        return float("inf")
    return float(price["inputUsdPerMillion"]) + float(price["outputUsdPerMillion"])


def candidates(catalog: dict[str, Any], task: dict[str, Any]) -> list[dict[str, Any]]:
    minimum = EFFORT.index(task["minimumReasoning"])
    required = set(task["requiredCapabilities"])
    eligible = [
        item for item in catalog["observations"]
        if item["available"]
        and required.issubset(set(item["capabilities"]))
        and max(EFFORT.index(level) for level in item["reasoningLevels"]) >= minimum
    ]
    eligible.sort(key=lambda item: (price_total(item), item["provider"], item["model"]))
    return [{"provider": item["provider"], "model": item["model"], "reasoning": min((level for level in item["reasoningLevels"] if EFFORT.index(level) >= minimum), key=EFFORT.index), "priceKnown": isinstance(item.get("price"), dict)} for item in eligible]


def compare(current: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, str]]:
    old = {(item["provider"], item["model"]): item for item in prior["observations"]}
    new = {(item["provider"], item["model"]): item for item in current["observations"]}
    changes: list[dict[str, str]] = []
    for key in sorted(new.keys() - old.keys()):
        changes.append({"kind": "model-added", "provider": key[0], "model": key[1]})
    for key in sorted(old.keys() - new.keys()):
        changes.append({"kind": "model-removed", "provider": key[0], "model": key[1]})
    for key in sorted(old.keys() & new.keys()):
        before, after = old[key], new[key]
        for field, kind in (("available", "availability-changed"), ("reasoningLevels", "reasoning-changed"), ("price", "price-changed")):
            if before.get(field) != after.get(field):
                changes.append({"kind": kind, "provider": key[0], "model": key[1]})
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    recommend = subparsers.add_parser("recommend")
    recommend.add_argument("--catalog", type=Path, required=True)
    recommend.add_argument("--task", type=Path, required=True)
    comparison = subparsers.add_parser("compare")
    comparison.add_argument("--catalog", type=Path, required=True)
    comparison.add_argument("--prior", type=Path, required=True)
    escalation = subparsers.add_parser("learning-escalation")
    escalation.add_argument("--catalog", type=Path, required=True)
    escalation.add_argument("--learning", type=Path, required=True)
    args = parser.parse_args()
    try:
        catalog = validate_catalog(read_json(args.catalog))
        if args.command == "recommend":
            task = validate_task(read_json(args.task))
            result = {"schemaVersion": 1, "role": task["role"], "candidates": candidates(catalog, task), "requiresHumanConfirmation": True, "limits": "Candidates are ranked only by declared capability, selectable effort, and reported public price; they do not prove quality, account availability, or effective billed cost."}
        elif args.command == "compare":
            changes = compare(catalog, validate_catalog(read_json(args.prior)))
            result = {"schemaVersion": 1, "changes": changes, "requiresHumanReconfirmation": bool(changes), "limits": "Only supplied catalog facts are compared; no provider was queried by this tool."}
        else:
            learning = read_json(args.learning)
            if not isinstance(learning, dict) or learning.get("confirmedRootCause") is not True or learning.get("preventionVerified") is not True:
                raise ContractError("learning escalation requires confirmedRootCause and preventionVerified")
            text(learning.get("evidenceId"), "learning.evidenceId")
            task = validate_task({"schemaVersion": 1, "role": learning.get("requestedRole"), "requiredCapabilities": [], "minimumReasoning": learning.get("requestedMinimumReasoning")})
            result = {"schemaVersion": 1, "evidenceId": learning["evidenceId"], "candidates": candidates(catalog, task), "requiresHumanReconfirmation": True, "reason": "verified-learning-escalation"}
    except ContractError as exc:
        print(f"Model policy: FAIL\n- {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
