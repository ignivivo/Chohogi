#!/usr/bin/env python3
"""Classify declared security signals into deterministic pre-code requirements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "assets/agents/security_immune_system/signal-policy.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path, help="JSON object with a riskSignals array")
    arguments = parser.parse_args()
    try:
        profile = json.loads(arguments.profile.read_text(encoding="utf-8"))
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Security boundary classification: FAIL\n- invalid input: {exc}", file=sys.stderr)
        return 2
    signals = profile.get("riskSignals") if isinstance(profile, dict) else None
    mappings = policy.get("signals") if isinstance(policy, dict) else None
    if not isinstance(signals, list) or not all(isinstance(item, str) for item in signals) or not isinstance(mappings, dict):
        print("Security boundary classification: FAIL\n- profile must contain a riskSignals string array", file=sys.stderr)
        return 2
    unknown = sorted(set(signals) - set(mappings))
    if unknown:
        print("Security boundary classification: FAIL\n- unknown risk signals: " + ", ".join(unknown), file=sys.stderr)
        return 2
    requirements = sorted({requirement for signal in signals for requirement in mappings[signal]})
    result = {
        "schemaVersion": 1,
        "kind": "security-boundary-observation",
        "riskSignals": sorted(set(signals)),
        "disposition": "pre-code-security-acceptance" if signals else "no-special-security-boundary",
        "requirements": requirements,
        "releaseGateRequired": any(signal == "dependency-change" for signal in signals),
        "limits": "Classification is based only on declared signals and does not prove a project scanner ran.",
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
