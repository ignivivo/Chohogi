#!/usr/bin/env python3
"""Verify the internal document lifecycle and reference contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "assets/agents/trunk_orchestration/document-lifecycle.md"
FIXTURES = ROOT / "assets/agents/trunk_orchestration/evaluation/document-lifecycle-fixtures.json"
ROLES = {"decision", "active-plan", "state-projection", "execution-record", "feedback-source", "review-synthesis", "history"}
REQUIRED = ("active-plan", "state-projection", "execution-record", "review-synthesis", "history", "파생 상태·완료·건강·승인")


def main() -> int:
    errors: list[str] = []
    if not DOC.is_file():
        errors.append(f"missing document lifecycle contract: {DOC}")
    else:
        text = DOC.read_text(encoding="utf-8")
        errors.extend(f"document lifecycle contract missing: {term}" for term in REQUIRED if term not in text)
    if not FIXTURES.is_file():
        errors.append(f"missing document lifecycle fixtures: {FIXTURES}")
    else:
        try:
            data = json.loads(FIXTURES.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid document lifecycle fixtures: {exc}")
        else:
            if data.get("schemaVersion") != 1 or set(data.get("roles", [])) != ROLES:
                errors.append("document lifecycle fixtures must declare exactly the seven roles")
            fixtures = data.get("fixtures", [])
            if not isinstance(fixtures, list) or len(fixtures) < 4:
                errors.append("document lifecycle fixtures need at least four cases")
            seen: set[str] = set()
            for item in fixtures if isinstance(fixtures, list) else []:
                if not isinstance(item, dict) or not item.get("id") or item.get("id") in seen:
                    errors.append("document lifecycle fixture ids must be unique and non-empty")
                    continue
                seen.add(item["id"])
                if item.get("role") not in ROLES or not isinstance(item.get("executable"), bool) or not item.get("expectedAuthority"):
                    errors.append(f"invalid document lifecycle fixture: {item.get('id')}")
    if errors:
        print("\n".join(errors))
        return 1
    print("Chohogi document lifecycle verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
