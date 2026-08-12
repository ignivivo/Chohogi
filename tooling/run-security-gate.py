#!/usr/bin/env python3
"""Execute a project-owned security plan and emit a fail-closed observation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


KINDS = {"secret-scan", "dependency-scan", "sast", "dast", "prompt-injection"}


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def relative_artifact(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return value


def validate_check(item: Any) -> list[str]:
    if not isinstance(item, dict):
        return ["check must be an object"]
    errors: list[str] = []
    if not isinstance(item.get("id"), str) or not item["id"].strip():
        errors.append("check id must be a non-empty string")
    if item.get("kind") not in KINDS:
        errors.append(f"check kind must be one of {', '.join(sorted(KINDS))}")
    command = item.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(arg, str) and arg for arg in command):
        errors.append("check command must be a non-empty argument array; shell strings are forbidden")
    artifacts = item.get("requiredArtifacts")
    if not isinstance(artifacts, list) or any(relative_artifact(value) is None for value in artifacts):
        errors.append("requiredArtifacts must contain only project-relative paths")
    timeout = item.get("timeoutSeconds", 300)
    if not isinstance(timeout, int) or not 1 <= timeout <= 900:
        errors.append("timeoutSeconds must be an integer between 1 and 900")
    return errors


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="explicitly allow configured project commands to run")
    arguments = parser.parse_args()
    project = arguments.project.resolve()
    plan = arguments.plan.resolve()
    output = arguments.output.resolve()
    if not arguments.execute:
        print("Refusing to execute a project security plan without --execute.", file=sys.stderr)
        return 2
    if not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 2
    if not under(plan, project) or not plan.is_file():
        print("Security plan must be an existing file inside --project.", file=sys.stderr)
        return 2
    if not under(output, project):
        print("Security observation output must be inside --project.", file=sys.stderr)
        return 2
    try:
        document = json.loads(plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid security plan: {exc}", file=sys.stderr)
        return 2
    checks = document.get("checks") if isinstance(document, dict) else None
    errors: list[str] = []
    if not isinstance(document, dict) or document.get("schemaVersion") != 1:
        errors.append("security plan must have schemaVersion 1")
    if not isinstance(checks, list) or not checks:
        errors.append("security plan must contain a non-empty checks list")
        checks = []
    identifiers: set[str] = set()
    for item in checks:
        errors.extend(validate_check(item))
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            if item["id"] in identifiers:
                errors.append(f"duplicate check id: {item['id']}")
            identifiers.add(item["id"])
    if errors:
        print("Invalid security plan:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 2
    observations: list[dict[str, Any]] = []
    for item in checks:
        started = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(item["command"], cwd=project, text=True, capture_output=True, timeout=item.get("timeoutSeconds", 300), check=False)
            exit_code: int | None = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = None
        artifacts = item.get("requiredArtifacts", [])
        missing = [value for value in artifacts if not (project / value).is_file()]
        passed = not timed_out and exit_code == 0 and not missing
        observations.append({
            "id": item["id"],
            "kind": item["kind"],
            "status": "pass" if passed else "fail",
            "exitCode": exit_code,
            "timedOut": timed_out,
            "missingArtifacts": missing,
            "durationMs": round((time.monotonic() - started) * 1000),
        })
    report = {
        "schemaVersion": 1,
        "kind": "project-security-observation",
        "plan": plan.relative_to(project).as_posix(),
        "status": "pass" if all(item["status"] == "pass" for item in observations) else "fail",
        "checks": observations,
        "limits": "A passing command proves only that the configured check executed and supplied its required artifacts.",
    }
    write(output, report)
    if report["status"] == "fail":
        print(f"Security gate: FAIL; see {output}", file=sys.stderr)
        return 1
    print(f"Security gate: PASS; wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
