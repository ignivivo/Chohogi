#!/usr/bin/env python3
"""Verify a project's declared document roles and execution owner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROLES = {"decision", "active-plan", "state-projection", "execution-record", "feedback-source", "review-synthesis", "history"}
AUTHORITIES = {"product-scope", "information-architecture", "product-decision", "execution-queue", "none", "evidence", "observation", "review"}
STATES = {"active", "historical", "draft", "retired"}


def record_finalized(record_dir: Path) -> bool:
    verification = record_dir / "verification.json"
    if not verification.is_file():
        return False
    try:
        return json.loads(verification.read_text(encoding="utf-8")).get("status") == "pass"
    except (json.JSONDecodeError, AttributeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    registry = (args.registry or root / ".agents/chohogi-document-registry.json").resolve()
    errors: list[str] = []
    if not root.is_dir():
        errors.append(f"project root is missing: {root}")
    if not registry.is_file():
        errors.append(f"document registry is missing: {registry}")
    if errors:
        print("\n".join(errors))
        return 1
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"invalid document registry: {exc}")
        return 1
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        errors.append("document registry schemaVersion must be 1")
        data = {}
    documents = data.get("documents", [])
    if not isinstance(documents, list) or not documents:
        errors.append("document registry documents must be a non-empty list")
        documents = []
    seen: set[str] = set()
    active_plans: list[str] = []
    entries_by_path: dict[str, dict[str, object]] = {}
    for item in documents:
        if not isinstance(item, dict):
            errors.append("document registry entries must be objects")
            continue
        path = item.get("path")
        role = item.get("role")
        authority = item.get("authority")
        state = item.get("state")
        if not isinstance(path, str) or not path.strip():
            errors.append("document registry entry needs a path")
            continue
        if path in seen:
            errors.append(f"duplicate document registry path: {path}")
        seen.add(path)
        entries_by_path[path] = item
        if role not in ROLES:
            errors.append(f"{path}: unknown role {role}")
        if authority not in AUTHORITIES:
            errors.append(f"{path}: unknown authority {authority}")
        if state not in STATES:
            errors.append(f"{path}: unknown state {state}")
        target = root / path
        try:
            target.resolve().relative_to(root)
        except ValueError:
            errors.append(f"{path}: declared path escapes project root")
        if not target.exists():
            errors.append(f"{path}: declared document or directory is missing")
        if role == "active-plan" and state == "active":
            active_plans.append(path)
        if role in {"state-projection", "execution-record", "feedback-source", "review-synthesis", "history"} and authority == "execution-queue":
            errors.append(f"{path}: non-plan document cannot own execution queue")
        if role == "history" and state == "active":
            errors.append(f"{path}: history cannot be active")
        for field in ("consumers", "allowedReferences", "forbiddenUse"):
            if field in item and (not isinstance(item[field], list) or not all(isinstance(value, str) and value.strip() for value in item[field])):
                errors.append(f"{path}: {field} must be a string list")
    # null declares that no plan currently owns the queue; the key itself stays required.
    if "activeExecutionPlan" not in data:
        errors.append("activeExecutionPlan must be declared (a plan path, or null when no plan is active)")
    else:
        declared = data["activeExecutionPlan"]
        if declared is None:
            if active_plans:
                errors.append(f"activeExecutionPlan is null but active plans are declared: {active_plans}")
        elif not isinstance(declared, str) or not declared.strip():
            errors.append("activeExecutionPlan must be a plan path or null")
        elif active_plans != [declared]:
            errors.append(f"activeExecutionPlan must be the only active plan; found {active_plans}")
    for path, item in entries_by_path.items():
        if item.get("role") == "active-plan" and item.get("state") == "active" and "executionRecord" in item:
            record = item["executionRecord"]
            record_entry = entries_by_path.get(record) if isinstance(record, str) else None
            if record_entry is None or record_entry.get("role") != "execution-record":
                errors.append(f"{path}: executionRecord must name a declared execution-record entry")
            elif record_finalized(root / record):
                errors.append(f"{path}: its execution record {record} is finalized; mark the plan historical or declare a new record")
        if item.get("role") == "execution-record" and item.get("state") == "active" and record_finalized(root / path):
            errors.append(f"{path}: execution record is finalized but declared active")
    for item in documents:
        if not isinstance(item, dict) or not item.get("supersededBy"):
            continue
        superseded = item["supersededBy"]
        if not isinstance(superseded, str):
            errors.append(f"{item.get('path')}: supersededBy must name another declared document")
            continue
        target = entries_by_path.get(superseded)
        # A supersession chain may end at the active plan or at a closed (historical) plan.
        if target is None or not (
            (target.get("role") == "active-plan" and target.get("state") == "active")
            or target.get("state") == "historical"
        ):
            errors.append(f"{item.get('path')}: supersededBy must point to the active plan or a historical document")
    for item in documents:
        if not isinstance(item, dict):
            continue
        allowed = item.get("allowedReferences", [])
        if isinstance(allowed, list):
            for reference in allowed:
                if reference not in entries_by_path:
                    errors.append(f"{item.get('path')}: allowedReferences must name declared documents: {reference}")
    declared_plan_paths = set(entries_by_path)
    docs_root = root / "docs"
    plan_roots = (path for path in docs_root.rglob("plans") if path.is_dir()) if docs_root.is_dir() else ()
    for plan_root in plan_roots:
        for candidate in plan_root.rglob("*.md"):
            relative = candidate.relative_to(root).as_posix()
            if not any(relative == declared or relative.startswith(declared.rstrip("/") + "/") for declared in declared_plan_paths):
                errors.append(f"{relative}: plan document is not declared in the project registry")
    if errors:
        print("Project document registry verification: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Project document registry verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
