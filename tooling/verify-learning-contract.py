#!/usr/bin/env python3
"""Verify Learning–Phloem–Amyloplast contracts and boundary fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_LEARNING_TERMS = (
    "confirmed reproducible defect",
    "closed-no-learning",
    "primary prevention scope",
    "provisional global candidate",
    "automatic global skill creation",
    "learning-assessment",
    "learningRequired",
    "confirmedDefect",
)
REQUIRED_RECORD_TERMS = (
    "mechanismLayer",
    "primaryPreventionScope",
    "applicability",
    "contributingContexts",
    "trigger/non-trigger",
    "Never store API keys",
    "two real projects",
)
REQUIRED_PHLOEM_TERMS = (
    "controller·새 route selector",
    "closed-no-learning",
    "원문 프롬프트",
    "destination",
)


def require_terms(path: Path, terms: tuple[str, ...], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing required contract: {path}")
        return
    text = path.read_text(encoding="utf-8")
    for term in terms:
        if term not in text:
            errors.append(f"{path.name} is missing required term: {term}")


def check_ledger(errors: list[str]) -> None:
    """The failure-signature registry and ledger that drive the learning loop stay consistent."""
    override = os.environ.get("CHOHOGI_LEARNING_HOME")
    home = Path(override) if override else ROOT / "assets/agents/vascular-bundle_circulation"
    registry_path = home / "failure-signatures.json"
    if not registry_path.is_file():
        errors.append(f"failure signature registry is missing: {registry_path}")
        return
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"failure signature registry is invalid JSON: {exc}")
        return
    signatures = {}
    for item in registry.get("signatures", []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("description"):
            errors.append("each failure signature needs an id and a description")
            continue
        signatures[item["id"]] = item
        for guard in item.get("guards", []):
            if not (ROOT / guard).exists():
                errors.append(f"failure signature {item['id']} names a guard that does not exist: {guard}")
    ledger_path = home / "learning-ledger.jsonl"
    entries = []
    if ledger_path.is_file():
        for number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                errors.append(f"learning ledger line {number} is invalid JSON")
    for entry in entries:
        if entry.get("signature") not in signatures:
            errors.append(f"learning ledger names an unregistered signature: {entry.get('signature')}")
    for sig, item in signatures.items():
        works = {entry.get("workId") for entry in entries if entry.get("signature") == sig}
        guarded = item.get("guards") or any(entry.get("guard") for entry in entries if entry.get("signature") == sig)
        if len(works) > 1 and not guarded:
            errors.append(f"failure signature {sig} is recurring ({len(works)} works) but has no guard")


def main() -> int:
    errors: list[str] = []
    learning = ROOT / "assets/agents/adaptive-regulation/learning/SKILL.md"
    record = ROOT / "assets/agents/adaptive-regulation/learning/references/learning-record.md"
    phloem = ROOT / "assets/agents/vascular-bundle_circulation/phloem-feedback.md"
    execution_record = ROOT / "tooling/execution-record.py"
    genome_inheritance = ROOT / "assets/agents/genome_inheritance/index_registry.yaml"
    require_terms(learning, REQUIRED_LEARNING_TERMS, errors)
    require_terms(record, REQUIRED_RECORD_TERMS, errors)
    require_terms(phloem, REQUIRED_PHLOEM_TERMS, errors)
    require_terms(execution_record, ("learning-assessment", "learningRequired", "confirmedDefect", "missingLearningAssessment"), errors)
    require_terms(genome_inheritance, ("required_asset_fields", "retirement_condition"), errors)
    check_ledger(errors)

    fixture_path = ROOT / "assets/agents/trunk_orchestration/evaluation/learning-fixtures.json"
    try:
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid learning fixture document: {exc}")
        data = {}
    fixtures = data.get("fixtures") if isinstance(data, dict) else None
    if data.get("schemaVersion") != 1:
        errors.append("Learning fixture schemaVersion must be 1.")
    if not isinstance(fixtures, list) or len(fixtures) < 5:
        errors.append("Learning fixtures must contain at least five boundary cases.")
    else:
        ids = {fixture.get("id") for fixture in fixtures if isinstance(fixture, dict)}
        required = {
            "react-async-not-next-or-vercel",
            "domain-contract-stays-project-local",
            "readonly-diagnosis-no-durable-record",
            "sensitive-payload-redacted",
            "candidate-expiry-prunes",
        }
        missing = required - ids
        if missing:
            errors.append("Learning fixtures missing: " + ", ".join(sorted(missing)))

    if errors:
        print("Chohogi learning contract verification: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Chohogi learning contract verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
