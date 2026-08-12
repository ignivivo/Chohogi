#!/usr/bin/env python3
"""Inventory an external skill's complete local payload before adoption."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


LINK = re.compile(r"\[[^]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
URL = re.compile(r"https?://[^\s<>)\]]+")
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_target(raw: str) -> str | None:
    candidate = raw.split("#", 1)[0]
    if not candidate or "<" in candidate or ">" in candidate or candidate.startswith(("http://", "https://", "mailto:")):
        return None
    return candidate


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="local root of the external skill payload")
    parser.add_argument("--entry", type=Path, help="entry SKILL.md relative to source when the payload contains multiple skills")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.source.resolve()
    output = arguments.output.resolve()
    if not root.is_dir():
        print(f"Skill intake source is not a directory: {root}", file=sys.stderr)
        return 2
    if output.exists() and output.is_symlink():
        print("Intake output must not be a symlink.", file=sys.stderr)
        return 2
    files: list[Path] = []
    errors: list[str] = []
    symlinks: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            relative_link = path.relative_to(root).as_posix()
            try:
                target = path.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                errors.append(f"broken or cyclic symlink: {relative_link}: {exc}")
                continue
            if not under(target, root):
                errors.append(f"symlink escapes intake root: {relative_link}")
                continue
            record = {"path": relative_link, "target": target.relative_to(root).as_posix(), "kind": "internal"}
            if target.is_file():
                record["targetSha256"] = file_hash(target)
            elif target.is_dir():
                record["kind"] = "internal-directory"
            else:
                errors.append(f"symlink target is not a regular file or directory: {relative_link}")
                continue
            symlinks.append(record)
        elif path.is_file() and path.resolve() != output:
            files.append(path)
    entry = (root / arguments.entry).resolve() if arguments.entry else root / "SKILL.md"
    if not under(entry, root) or not entry.is_file() or entry.name != "SKILL.md":
        errors.append("missing entry SKILL.md inside intake root")
    external_references: set[str] = set()
    inventory: list[dict[str, str]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        inventory.append({"path": relative, "sha256": file_hash(path)})
        if path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        external_references.update(URL.findall(text))
    reachable: set[Path] = set()
    pending = [entry] if under(entry, root) and entry.is_file() and entry.name == "SKILL.md" else []
    while pending:
        path = pending.pop()
        if path in reachable:
            continue
        reachable.add(path)
        if path.suffix.lower() != ".md":
            continue
        text = CODE_BLOCK.sub("", path.read_text(encoding="utf-8", errors="replace"))
        for raw in LINK.findall(text):
            target = local_target(raw)
            if target is None:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"reference escapes intake root: {relative} -> {raw}")
                continue
            if not candidate.is_file():
                errors.append(f"missing local reference: {path.relative_to(root).as_posix()} -> {raw}")
            else:
                pending.append(candidate)
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "kind": "skill-intake-inventory",
        "source": str(root),
        "entry": entry.relative_to(root).as_posix() if under(entry, root) else None,
        "files": inventory,
        "symlinks": symlinks,
        "externalReferences": sorted(external_references),
        "coverage": {
            "skillFilePresent": under(entry, root) and entry.is_file() and entry.name == "SKILL.md",
            "fileCount": len(inventory),
            "containsScripts": any(item["path"].startswith("scripts/") for item in inventory),
            "containsReferences": any(item["path"].startswith("references/") for item in inventory),
            "reachableResourceCount": len(reachable),
            "internalSymlinkCount": len(symlinks),
        },
        "errors": errors,
        "limits": "Inventory is not approval, provenance verification, sandboxing, or evidence that any script is safe to execute.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if errors:
        print("Skill intake: FAIL; missing local references or unsafe paths detected:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print(f"Skill intake: PASS; inventoried {len(inventory)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
