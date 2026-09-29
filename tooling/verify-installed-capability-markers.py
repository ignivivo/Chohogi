#!/usr/bin/env python3
"""Scan the Chohogi repository for absorbed-provider markers that must not
reappear as active/callable references (e.g. a plugin name absorbed via the
horizontal-transfer principle). Self-contained: reads its own sibling
retired-capability-markers.json and needs no manifest.json. Chohogi has no
copy-install step; both hosts (Claude Code, Codex) read this repository
directly through their own local plugin marketplace, so the repository
itself is the thing to scan, not a separately installed tree.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def marker_entries(markers_file: Path) -> list[dict[str, object]]:
    declared = load_json(markers_file)
    if not declared:
        return []
    entries = declared.get("markers")
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict) and isinstance(entry.get("marker"), str) and entry["marker"].strip()]


SCAN_EXCLUDED_TOP_LEVEL = {".git", "docs"}  # docs/ holds historical evidence/audits that legitimately name a retired provider


def find_forbidden_markers(installed_root: Path, marker_entries_list: list[dict[str, object]]) -> list[str]:
    if not marker_entries_list or not installed_root.is_dir():
        return []
    findings: list[str] = []
    for entry in marker_entries_list:
        marker = str(entry["marker"])
        folded_marker = marker.casefold()
        exempt_paths = {str(path) for path in entry.get("exemptPaths", []) if isinstance(path, str)}
        for path in installed_root.rglob("*"):
            if path.parts and path.relative_to(installed_root).parts[0] in SCAN_EXCLUDED_TOP_LEVEL:
                continue
            if not path.is_file():
                continue
            relative = str(path.relative_to(installed_root))
            if relative in exempt_paths:
                continue
            try:
                payload = path.read_bytes()
            except OSError:
                continue
            if b"\0" in payload:
                continue
            if folded_marker in payload.decode("utf-8", errors="replace").casefold():
                findings.append(f"{relative}: {marker}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parent, help="Repository root to scan (default: this checkout)")
    parser.add_argument("--markers-file", type=Path, default=HERE / "retired-capability-markers.json")
    arguments = parser.parse_args()
    scan_root = arguments.root.resolve()
    findings = find_forbidden_markers(scan_root, marker_entries(arguments.markers_file))
    if findings:
        print(json.dumps({"status": "fail", "scanRoot": str(scan_root), "findings": findings}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "pass", "scanRoot": str(scan_root), "findings": []}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
