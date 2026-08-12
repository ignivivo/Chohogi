#!/usr/bin/env python3
"""Reject active v1 layout references and retired capability activation."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ACTIVE_PATHS = (ROOT / "README.md", ROOT / "assets", ROOT / "tooling", ROOT / "manifest.json")
FORBIDDEN = {
    "manifest.yaml": "v1 manifest must not remain beside manifest.json",
    "assets/agents/chohogi": "v1 Chohogi source path remains active",
    "assets/agents/skills": "v1 reusable-skill source path remains active",
    "assets/epidermis_entrypoint": "runtime endpoint must not use the misleading epidermis name",
    "leaves_capabilities": "global reusable methods must not masquerade as project leaves",
    "reusable-leaves": "manifest component must use reusable-methods, not project leaves",
    "leaf-methods.md": "reusable method catalog must not be named as a project leaf",
    "trunk_orchestration/security-boundary.md": "security boundary must belong to security_immune_system",
    "trunk_orchestration/evaluation/security-boundary-fixtures.json": "security fixtures must belong to security_immune_system",
    "amyloplast": "v1 organ name remains active",
    "`grill-me`를 사용": "retired grill-me remains an active route capability",
}


def files() -> list[Path]:
    result: list[Path] = []
    for path in ACTIVE_PATHS:
        if path.is_file():
            result.append(path)
        elif path.is_dir():
            result.extend(item for item in path.rglob("*") if item.is_file())
    return result


def main() -> int:
    errors: list[str] = []
    for path in files():
        if path.name == "verify-source-layout.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term, reason in FORBIDDEN.items():
            if term in text:
                errors.append(f"{path.relative_to(ROOT)}: {reason}")
    if (ROOT / "manifest.yaml").exists():
        errors.append("manifest.yaml: v1 manifest must be removed")
    if errors:
        print("Chohogi source-layout verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Chohogi source-layout verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
