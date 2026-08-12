#!/usr/bin/env python3
"""Verify that active Chohogi capabilities declare evidence proportional to their claim."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "assets/agents/functional_assurance/registry.json"
KINDS = {"advisory", "deterministic-check", "policy-gate", "provider-backed", "reference"}
ORGAN_ROOTS = {
    "assets/epidermis_entrypoint",
    "assets/agents/trunk_orchestration",
    "assets/agents/adaptive-regulation",
    "assets/agents/genome_inheritance",
    "assets/agents/vascular-bundle_circulation",
    "assets/agents/reusable_methods",
    "assets/agents/functional_assurance",
    "assets/agents/security_immune_system",
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_exists(value: Any) -> bool:
    return isinstance(value, str) and (ROOT / value).exists()


def assurance_marker(skill: Path) -> str | None:
    for line in skill.read_text(encoding="utf-8").splitlines()[1:20]:
        if line.strip().startswith("chohogi_assurance:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    arguments = parser.parse_args()
    errors: list[str] = []
    try:
        registry = json.loads(arguments.registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Functional assurance verification: FAIL\n- invalid registry: {exc}", file=sys.stderr)
        return 1
    assurances = registry.get("assurances") if isinstance(registry, dict) else None
    if registry.get("schemaVersion") != 1 or not isinstance(assurances, list):
        errors.append("registry must have schemaVersion 1 and an assurances list")
        assurances = []
    ids: set[str] = set()
    covered_roots: set[str] = set()
    covered_sources: set[str] = set()
    for item in assurances:
        if not isinstance(item, dict):
            errors.append("assurance entry must be an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append("assurance id must be a non-empty string")
            continue
        if identifier in ids:
            errors.append(f"duplicate assurance id: {identifier}")
        ids.add(identifier)
        kind = item.get("kind")
        if kind not in KINDS:
            errors.append(f"{identifier}: invalid kind {kind!r}")
        for key in ("trigger", "nonTrigger", "output", "limits"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{identifier}: missing {key}")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{identifier}: sources must be a non-empty list")
            sources = []
        for source in sources:
            if not source_exists(source):
                errors.append(f"{identifier}: missing source {source}")
            else:
                covered_sources.add(source)
                covered_roots.update(root for root in ORGAN_ROOTS if source == root or source.startswith(f"{root}/"))
        for key in ("verifiers", "fixtures"):
            values = item.get(key)
            if not isinstance(values, list) or not values:
                errors.append(f"{identifier}: {key} must be a non-empty list")
                continue
            for value in values:
                if not source_exists(value):
                    errors.append(f"{identifier}: missing {key[:-1]} {value}")
        if kind in {"deterministic-check", "policy-gate", "provider-backed"}:
            if not isinstance(item.get("execution"), str) or not item["execution"].strip():
                errors.append(f"{identifier}: {kind} requires an execution path")
        if kind == "advisory" and "automatic" in item.get("output", "").lower():
            errors.append(f"{identifier}: advisory output must not claim automatic enforcement")
    missing_roots = ORGAN_ROOTS - covered_roots
    if missing_roots:
        errors.append("uncovered active organ roots: " + ", ".join(sorted(missing_roots)))
    skill_roots = (ROOT / "assets/agents/reusable_methods", ROOT / "assets/agents/adaptive-regulation")
    expected_skills = {relative(path.parent) for root in skill_roots for path in root.glob("*/SKILL.md")}
    covered_skill_roots: set[str] = set()
    for skill in expected_skills:
        matches = [item for item in assurances if isinstance(item, dict) and skill in item.get("sources", [])]
        if len(matches) != 1:
            errors.append(f"{skill}: must map to exactly one assurance record")
            continue
        covered_skill_roots.add(skill)
        marker = assurance_marker(ROOT / skill / "SKILL.md")
        if marker != matches[0].get("kind"):
            errors.append(f"{skill}: chohogi-assurance marker must match registry kind {matches[0].get('kind')!r}")
    missing_skills = expected_skills - covered_skill_roots
    if missing_skills:
        errors.append("uncovered active skills: " + ", ".join(sorted(missing_skills)))
    expected_tools = {relative(path) for path in (ROOT / "tooling").iterdir() if path.is_file() and path.suffix in {".py", ".sh"}}
    missing_tools = expected_tools - covered_sources
    if missing_tools:
        errors.append("uncovered tooling commands: " + ", ".join(sorted(missing_tools)))
    if errors:
        print("Functional assurance verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Functional assurance verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
