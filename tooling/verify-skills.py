#!/usr/bin/env python3
"""Supplemental Chohogi packaging checks; not a replacement for skill-creator."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path

from semantic_contracts import SemanticContractError, frontmatter


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = Path(__file__).resolve().parent.parent
# Chohogi's actual skill source lives here; assets/agents/reusable_methods/<name>
# and assets/agents/adaptive-regulation/{learning,homeostasis} are reverse
# symlinks into this directory (Codex's local-plugin install does not follow
# symlinks, so the plugin's skills/ must hold the real files).
DEFAULT_SKILL_ROOT = ROOT / "skills"
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
    try:
        document = frontmatter(skill)
    except SemanticContractError as exc:
        fail(f"Invalid semantic frontmatter: {skill}: {exc}", errors)
        return
    name = document.get("name", "")
    description = document.get("description", "")
    if not isinstance(name, str) or not name:
        fail(f"Missing frontmatter name: {skill}", errors)
    elif name != directory.name or not NAME.fullmatch(name):
        fail(f"Skill name must match lowercase hyphenated directory: {skill}", errors)
    if not isinstance(description, str) or not description:
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
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT)
    arguments = parser.parse_args()
    skill_root = arguments.skill_root.resolve()
    errors: list[str] = []
    review_signals: list[str] = []
    if not skill_root.is_dir():
        print(f"Missing Chohogi skill root: {skill_root}")
        return 1
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
