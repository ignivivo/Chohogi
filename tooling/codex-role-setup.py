#!/usr/bin/env python3
"""Check or idempotently register Chohogi's canonical Codex roles.

Roles come from the canonical TOML directory, so a new role file is picked up
without editing this tool. Without --apply it only reports. --apply appends
missing registrations after backing up the config, and never rewrites an
existing entry: a registration that points away from the canonical file is
reported as WRONG_PATH for the user to fix.
"""
from __future__ import annotations
import argparse
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLE_DIR = ROOT / "assets/runtime_entrypoint/agents"


def canonical_roles() -> dict[str, Path]:
    return {path.stem.replace("-", "_"): path for path in sorted(ROLE_DIR.glob("*.toml"))}


def registered_path(text: str, role: str) -> str | None:
    """The config_file of [agents.<role>], '' when the table has none, None when the table is absent."""
    match = re.search(rf"^\[agents\.{re.escape(role)}\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if match is None:
        return None
    value = re.search(r'^\s*config_file\s*=\s*"([^"]*)"', match.group(1), re.M)
    return value.group(1) if value else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=Path.home() / ".codex/config.toml")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    text = args.config.read_text(encoding="utf-8") if args.config.exists() else ""
    roles = canonical_roles()
    absent = [role for role in roles if registered_path(text, role) is None]
    wrong = [role for role in roles if registered_path(text, role) not in (None, str(roles[role]))]
    if args.apply and absent:
        if args.config.exists():
            backup = args.config.with_name(f"{args.config.name}.chohogi-backup-{time.strftime('%Y%m%d-%H%M%S')}")
            backup.write_text(text, encoding="utf-8")
        blocks = [f'[agents.{role}]\nconfig_file = "{roles[role]}"\n' for role in absent]
        args.config.parent.mkdir(parents=True, exist_ok=True)
        args.config.write_text((text.rstrip() + "\n\n" if text.strip() else "") + "\n".join(blocks), encoding="utf-8")
        absent = []
    report = [f"MISSING {role}" for role in absent] + [f"WRONG_PATH {role}" for role in wrong]
    print("\n".join(report) if report else "OK")
    return 1 if report else 0


if __name__ == "__main__":
    raise SystemExit(main())
