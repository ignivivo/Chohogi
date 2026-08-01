#!/usr/bin/env python3
"""Supplemental Chohogi packaging checks; not a replacement for skill-creator."""

from __future__ import annotations

import re
from pathlib import Path


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "assets" / "agents" / "skills"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def check_skill(directory: Path, errors: list[str]) -> None:
    skill = directory / "SKILL.md"
    if not skill.is_file():
        fail(f"Missing SKILL.md: {directory}", errors)
        return
    if (directory / "README.md").exists():
        fail(f"Unexpected auxiliary README.md: {directory}", errors)
    lines = skill.read_text(encoding="utf-8").splitlines()
    if len(lines) < 4 or lines[0] != "---":
        fail(f"Missing YAML frontmatter: {skill}", errors)
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"Unclosed YAML frontmatter: {skill}", errors)
        return
    frontmatter: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not name:
        fail(f"Missing frontmatter name: {skill}", errors)
    elif name != directory.name or not NAME.fullmatch(name):
        fail(f"Skill name must match lowercase hyphenated directory: {skill}", errors)
    if not description:
        fail(f"Missing frontmatter description: {skill}", errors)
    body = lines[end + 1 :]
    if not any(line.strip() for line in body):
        fail(f"Empty skill body: {skill}", errors)
    if len(lines) > 500:
        fail(f"Skill exceeds 500-line guidance: {skill} ({len(lines)} lines)", errors)


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir():
        print(f"Missing Chohogi skills directory: {SKILLS}")
        return 1
    for directory in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        check_skill(directory, errors)
    if errors:
        print("Chohogi supplemental skill verification: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Chohogi supplemental skill verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
