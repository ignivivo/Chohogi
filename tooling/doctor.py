#!/usr/bin/env python3
"""Report the installed Chohogi state without changing it or running an audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKER = ".chohogi-owner.json"


def load_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    arguments = parser.parse_args()
    manifest = load_json(ROOT / "manifest.json")
    if manifest is None:
        print(json.dumps({"status": "invalid-source", "error": "manifest.json is unreadable"}))
        return 1

    from manifest_registry import install_plan

    plan = install_plan(manifest)
    home = arguments.home
    root_marker = load_json(home / ".agents" / "chohogi" / MARKER)
    expected_digest = plan["registryDigest"]
    missing_active: list[str] = []
    for action in plan["actions"]:
        destination = str(action["destination"])
        installed = home / destination
        mode = action["mode"]
        if (mode == "file" and not installed.is_file()) or (mode == "tree" and not installed.is_dir()):
            missing_active.append(destination)
    unexpected_retired = [
        destination for destination in plan["retiredDestinations"] if (home / str(destination)).exists()
    ]
    backup_root = home / ".agents" / "chohogi-backups"
    backups = sorted(str(path) for path in backup_root.iterdir()) if backup_root.is_dir() else []
    digest_matches = bool(root_marker and root_marker.get("registryDigest") == expected_digest)
    status = "healthy" if digest_matches and not missing_active and not unexpected_retired else "drift"
    report = {
        "status": status,
        "installed": {
            "layoutVersion": root_marker.get("layoutVersion") if root_marker else None,
            "ownerMarker": str(home / ".agents" / "chohogi" / MARKER) if root_marker else None,
        },
        "registry": {"layoutVersion": plan["layoutVersion"], "digestMatches": digest_matches},
        "components": {"missingActive": missing_active, "unexpectedRetired": unexpected_retired},
        "backups": backups,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
