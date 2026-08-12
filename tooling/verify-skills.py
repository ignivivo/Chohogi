#!/usr/bin/env python3
"""Supplemental Chohogi packaging checks; not a replacement for skill-creator."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL_ROOTS = (
    ROOT / "assets" / "agents" / "reusable_methods",
    ROOT / "assets" / "agents" / "adaptive-regulation",
)
INTAKE = ROOT / "tooling" / "scan-skill-intake.py"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def check_skill(directory: Path, errors: list[str], review_signals: list[str]) -> None:
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
        review_signals.append(
            f"{directory.name}: {len(lines)} lines; review whether the body should remain whole or move conditional detail to resources"
        )


def check_resource_graph(directory: Path, skill_root: Path, errors: list[str]) -> None:
    """Require every active skill's reachable local resources to resolve in its install root."""
    entry = directory.joinpath("SKILL.md").relative_to(skill_root)
    with tempfile.TemporaryDirectory(prefix="chohogi-skill-resource-") as temporary:
        report = Path(temporary) / "inventory.json"
        result = subprocess.run(
            [sys.executable, str(INTAKE), str(skill_root), "--entry", str(entry), "--output", str(report)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown intake failure"
        fail(f"Skill resource graph invalid for {directory.name}: {detail}", errors)


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--reusable-root", type=Path, default=DEFAULT_SKILL_ROOTS[0])
    parser.add_argument("--adaptive-root", type=Path, default=DEFAULT_SKILL_ROOTS[1])
    arguments = parser.parse_args()
    skill_roots = (arguments.reusable_root.resolve(), arguments.adaptive_root.resolve())
    errors: list[str] = []
    review_signals: list[str] = []
    if not all(path.is_dir() for path in skill_roots):
        print("Missing Chohogi skill roots: " + ", ".join(str(path) for path in skill_roots))
        return 1
    for skill_root in skill_roots:
        for directory in sorted(path for path in skill_root.iterdir() if path.is_dir()):
            check_skill(directory, errors, review_signals)
            check_resource_graph(directory, skill_root, errors)
    if errors:
        print("Chohogi supplemental skill verification: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    for signal in review_signals:
        print(f"Skill review signal: {signal}")
    print("Chohogi supplemental skill verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
