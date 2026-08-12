#!/usr/bin/env python3
"""Verify that active Chohogi declarations have one strict semantic interpretation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from semantic_contracts import SemanticContractError, frontmatter, strict_json, strict_yaml


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "assets/agents/functional_assurance/semantic-contract-registry.json"
DEFAULT_REUSABLE = ROOT / "assets/agents/reusable_methods"
DEFAULT_ADAPTIVE = ROOT / "assets/agents/adaptive-regulation"
EXPECTED_CONTRACTS = {
    "active-skill-frontmatter": {
        "format": "yaml-frontmatter",
        "roots": ["assets/agents/reusable_methods", "assets/agents/adaptive-regulation"],
    },
    "active-json-declarations": {
        "format": "json",
        "roots": ["manifest.json", "assets"],
        "extensions": [".json"],
    },
    "active-yaml-declarations": {
        "format": "yaml",
        "roots": ["assets"],
        "extensions": [".yaml", ".yml"],
    },
}


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def validate_skill(path: Path, errors: list[str]) -> None:
    try:
        document = frontmatter(path)
    except (OSError, SemanticContractError) as exc:
        error(errors, path, str(exc))
        return
    if not isinstance(document.get("name"), str) or not document["name"].strip():
        error(errors, path, "frontmatter name must be a non-empty string")
    if not isinstance(document.get("description"), str) or not document["description"].strip():
        error(errors, path, "frontmatter description must be a non-empty string")
    metadata = document.get("metadata")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("chohogi_assurance"), str):
        error(errors, path, "frontmatter metadata.chohogi_assurance must be a string")


def validate_skills(roots: tuple[Path, Path], errors: list[str]) -> None:
    for root in roots:
        if not root.is_dir():
            error(errors, root, "active skill root is missing")
            continue
        for skill in sorted(root.glob("*/SKILL.md")):
            validate_skill(skill, errors)


def load_registry(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        registry = strict_json(path.read_text(encoding="utf-8"))
    except (OSError, SemanticContractError) as exc:
        error(errors, path, str(exc))
        return []
    contracts = registry.get("contracts") if isinstance(registry, dict) else None
    if registry.get("schemaVersion") != 1 or not isinstance(contracts, list):
        error(errors, path, "registry must have schemaVersion 1 and a contracts list")
        return []
    if not all(isinstance(item, dict) for item in contracts):
        error(errors, path, "every semantic contract must be an object")
        return []
    return contracts


def files_for(root: Path, extensions: set[str]) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix in extensions else []
    return [path for path in sorted(root.rglob("*")) if path.is_file() and path.suffix in extensions]


def validate_structured(registry_path: Path, errors: list[str]) -> None:
    contracts = load_registry(registry_path, errors)
    by_id = {item.get("id"): item for item in contracts}
    if set(by_id) != set(EXPECTED_CONTRACTS) or len(by_id) != len(contracts):
        error(errors, registry_path, "contracts must exactly cover active skill frontmatter, JSON, and YAML declarations")
        return
    for identifier, expected in EXPECTED_CONTRACTS.items():
        actual = by_id[identifier]
        for field, value in expected.items():
            if actual.get(field) != value:
                error(errors, registry_path, f"{identifier}: {field} must be {value!r}")
    if errors:
        return
    seen: set[Path] = set()
    for contract in by_id.values():
        format_name = contract["format"]
        if format_name == "yaml-frontmatter":
            continue
        extensions = set(contract.get("extensions", []))
        parser = strict_json if format_name == "json" else strict_yaml
        for raw_root in contract.get("roots", []):
            root = ROOT / raw_root
            if not root.exists():
                error(errors, root, "declared semantic-contract root is missing")
                continue
            for path in files_for(root, extensions):
                if path in seen:
                    error(errors, path, "matches more than one semantic contract")
                    continue
                seen.add(path)
                try:
                    parser(path.read_text(encoding="utf-8"))
                except (OSError, SemanticContractError) as exc:
                    error(errors, path, str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--reusable-root", type=Path, default=DEFAULT_REUSABLE)
    parser.add_argument("--adaptive-root", type=Path, default=DEFAULT_ADAPTIVE)
    parser.add_argument("--skills-only", action="store_true")
    arguments = parser.parse_args()
    errors: list[str] = []
    validate_skills((arguments.reusable_root.resolve(), arguments.adaptive_root.resolve()), errors)
    if not arguments.skills_only:
        validate_structured(arguments.registry.resolve(), errors)
    if errors:
        print("Semantic assurance verification: FAIL", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Semantic assurance verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
