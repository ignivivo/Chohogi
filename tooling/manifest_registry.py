#!/usr/bin/env python3
"""Resolve and validate the Chohogi-owned installation registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifest.json"
OWNERSHIP = {"managed", "runtime-endpoint", "project-local", "retired"}
INSTALL_MODES = {"file", "tree", "children", "none"}
REQUIRED_COMPONENT_FIELDS = {
    "id", "organ", "function", "source", "destination", "ownership", "activation", "state", "installMode"
}


def diagnostic(message: str) -> None:
    print(f"manifest registry: {message}", file=sys.stderr)


def relative_path(value: Any, field: str, component_id: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{component_id}: {field} must be a non-empty string")
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{component_id}: {field} escapes repository root")
        return None
    return path.as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read manifest: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("manifest root must be an object")
    return document


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    package = document.get("package")
    if document.get("schemaVersion") != 2:
        errors.append("schemaVersion must be 2")
    if not isinstance(package, dict) or package.get("id") != "chohogi":
        errors.append("package.id must be chohogi")
    if not isinstance(package, dict) or not isinstance(package.get("layoutVersion"), int):
        errors.append("package.layoutVersion must be an integer")
    components = document.get("components")
    if not isinstance(components, list) or not components:
        return errors + ["components must be a non-empty list"]

    ids: set[str] = set()
    destinations: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            errors.append("component must be an object")
            continue
        component_id = component.get("id")
        if not isinstance(component_id, str) or not component_id:
            errors.append("component id must be a non-empty string")
            continue
        if component_id in ids:
            errors.append(f"duplicate component id: {component_id}")
        ids.add(component_id)
        missing = REQUIRED_COMPONENT_FIELDS - set(component)
        if missing:
            errors.append(f"{component_id}: missing fields: {', '.join(sorted(missing))}")
            continue
        source = relative_path(component["source"], "source", component_id, errors)
        destination = relative_path(component["destination"], "destination", component_id, errors)
        ownership = component.get("ownership")
        state = component.get("state")
        install_mode = component.get("installMode")
        if ownership not in OWNERSHIP:
            errors.append(f"{component_id}: invalid ownership: {ownership!r}")
        if ownership == "retired" and state != "retired":
            errors.append(f"{component_id}: retired ownership must have retired state")
        if ownership != "retired" and state != "active":
            errors.append(f"{component_id}: active ownership must have active state")
        if ownership == "retired" and component.get("activation") != "none":
            errors.append(f"{component_id}: retired component cannot be active")
        if install_mode not in INSTALL_MODES:
            errors.append(f"{component_id}: invalid installMode: {install_mode!r}")
        elif ownership == "retired" and install_mode != "none":
            errors.append(f"{component_id}: retired component must use installMode none")
        elif ownership == "runtime-endpoint" and install_mode != "file":
            errors.append(f"{component_id}: runtime endpoint must use installMode file")
        elif ownership == "managed" and install_mode not in {"file", "tree", "children"}:
            errors.append(f"{component_id}: managed component must have an install action")
        if state == "active" and destination is not None:
            if destination in destinations:
                errors.append(f"duplicate active destination: {destination}")
            destinations.add(destination)
        if source is not None and ownership != "retired" and not (ROOT / source).exists():
            errors.append(f"{component_id}: source does not exist: {source}")
    return errors


def active_components(document: dict[str, Any], ownership: str | None) -> list[dict[str, Any]]:
    components = document["components"]
    return [
        component for component in components
        if component["state"] == "active" and (ownership is None or component["ownership"] == ownership)
    ]


def manifest_digest() -> str:
    return hashlib.sha256(DEFAULT_MANIFEST.read_bytes()).hexdigest()


def install_plan(document: dict[str, Any]) -> dict[str, Any]:
    actions: list[dict[str, str]] = []
    component_ids: list[str] = []
    for component in active_components(document, None):
        if component["ownership"] not in {"managed", "runtime-endpoint"}:
            continue
        component_ids.append(component["id"])
        source = ROOT / component["source"]
        mode = component["installMode"]
        if mode == "children":
            for child in sorted(source.iterdir()):
                if child.is_dir():
                    actions.append({
                        "component": component["id"],
                        "source": relative_to_root(child),
                        "destination": f"{component['destination'].rstrip('/')}/{child.name}",
                        "mode": "tree",
                    })
        else:
            actions.append({
                "component": component["id"],
                "source": component["source"],
                "destination": component["destination"],
                "mode": mode,
            })
    retired_destinations = [
        component["destination"] for component in document["components"]
        if component["state"] == "retired"
    ]
    return {
        "layoutVersion": document["package"]["layoutVersion"],
        "registryDigest": manifest_digest(),
        "managedComponentIds": component_ids,
        "actions": actions,
        "retiredDestinations": retired_destinations,
    }


def relative_to_root(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    components_parser = subparsers.add_parser("components")
    components_parser.add_argument("--ownership", choices=sorted(OWNERSHIP - {"retired"}))
    subparsers.add_parser("install-plan")
    arguments = parser.parse_args()
    try:
        document = load_manifest(arguments.manifest)
    except ValueError as exc:
        diagnostic(str(exc))
        return 1
    errors = validate(document)
    if errors:
        for error in errors:
            diagnostic(error)
        return 1
    if arguments.command == "validate":
        print(json.dumps({"status": "valid", "layoutVersion": document["package"]["layoutVersion"]}))
    elif arguments.command == "components":
        print(json.dumps({"components": active_components(document, arguments.ownership)}, indent=2))
    else:
        print(json.dumps(install_plan(document), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
