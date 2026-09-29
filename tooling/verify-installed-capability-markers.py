#!/usr/bin/env python3
"""Scan the installed Chohogi tree for absorbed-provider markers that must not
reappear as active/callable references (e.g. a plugin name absorbed via the
horizontal-transfer principle). Self-contained: reads its own sibling
retired-capability-markers.json and needs no manifest.json, so it works from
an installed runtime tree, not only a Chohogi source checkout.
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


def find_forbidden_markers(installed_root: Path, marker_entries_list: list[dict[str, object]]) -> list[str]:
    if not marker_entries_list or not installed_root.is_dir():
        return []
    findings: list[str] = []
    for entry in marker_entries_list:
        marker = str(entry["marker"])
        folded_marker = marker.casefold()
        exempt_paths = {str(path) for path in entry.get("exemptPaths", []) if isinstance(path, str)}
        for path in installed_root.rglob("*"):
            if ".git" in path.parts or not path.is_file():
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
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--markers-file", type=Path, default=HERE / "retired-capability-markers.json")
    arguments = parser.parse_args()
    installed_root = arguments.home / ".agents" / "chohogi"
    findings = find_forbidden_markers(installed_root, marker_entries(arguments.markers_file))
    if findings:
        print(json.dumps({"status": "fail", "installedRoot": str(installed_root), "findings": findings}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "pass", "installedRoot": str(installed_root), "findings": []}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
