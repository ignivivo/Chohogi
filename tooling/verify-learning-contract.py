#!/usr/bin/env python3
"""Verify Learning–Phloem–Amyloplast contracts and boundary fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_LEARNING_TERMS = (
    "confirmed reproducible defect",
    "closed-no-learning",
    "primary prevention scope",
    "provisional global candidate",
    "automatic global skill creation",
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


def main() -> int:
    errors: list[str] = []
    learning = ROOT / "assets/agents/skills/learning/SKILL.md"
    record = ROOT / "assets/agents/skills/learning/references/learning-record.md"
    phloem = ROOT / "assets/agents/chohogi/trunk/vascular-bundle/phloem-feedback.md"
    amyloplast = ROOT / "assets/agents/chohogi/amyloplast/index.yaml"
    require_terms(learning, REQUIRED_LEARNING_TERMS, errors)
    require_terms(record, REQUIRED_RECORD_TERMS, errors)
    require_terms(phloem, REQUIRED_PHLOEM_TERMS, errors)
    require_terms(amyloplast, ("required_asset_fields", "retirement_condition"), errors)

    fixture_path = ROOT / "assets/agents/chohogi/trunk/evals/learning-fixtures.json"
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
