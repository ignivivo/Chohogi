#!/usr/bin/env python3
"""Exhaustively scan a repository for user-supplied retired capability markers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def text_files(root: Path):
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        if b"\0" not in payload:
            yield path, payload.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--forbid", action="append", required=True, help="Case-insensitive marker that must not occur anywhere under --root.")
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    if not root.is_dir():
        print(f"Retired capability scan: FAIL\n- root is not a directory: {root}", file=sys.stderr)
        return 1
    markers = [marker.casefold() for marker in arguments.forbid if marker.strip()]
    if not markers:
        print("Retired capability scan: FAIL\n- at least one non-empty --forbid marker is required", file=sys.stderr)
        return 1
    findings: list[str] = []
    for path, text in text_files(root):
        folded = text.casefold()
        for marker in markers:
            if marker in folded:
                findings.append(f"{path.relative_to(root)}: retired capability marker found: {marker}")
    if findings:
        print("Retired capability scan: FAIL", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Retired capability scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
