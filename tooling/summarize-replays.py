#!/usr/bin/env python3
"""Summarize already validated, privacy-safe Chohogi replay result JSON files."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

BOOLEAN_OUTCOMES = (
    "flowCorrect", "artifactsComplete", "externalController", "executionChoicePrompt",
    "unnecessaryEscalation", "persistentChangeWithoutAuthority",
)

def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        raise ValueError(f"{path}: not a schemaVersion 1 replay result")
    outcomes = data.get("outcomes")
    if not isinstance(outcomes, dict) or not all(isinstance(outcomes.get(key), bool) for key in BOOLEAN_OUTCOMES):
        raise ValueError(f"{path}: invalid boolean outcomes")
    if not isinstance(outcomes.get("reworkCount"), int):
        raise ValueError(f"{path}: invalid reworkCount")
    return data

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: summarize-replays.py <result.json> [result.json ...]", file=sys.stderr)
        return 2
    records = [load(Path(arg)) for arg in sys.argv[1:]]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["profile"]].append(record)
    summary: dict[str, Any] = {"recordCount": len(records), "profiles": {}}
    for profile, items in sorted(groups.items()):
        outcomes = [item["outcomes"] for item in items]
        summary["profiles"][profile] = {
            "runs": len(items),
            "flowCorrectRate": sum(item["flowCorrect"] for item in outcomes) / len(items),
            "artifactCompleteRate": sum(item["artifactsComplete"] for item in outcomes) / len(items),
            "externalControllerRate": sum(item["externalController"] for item in outcomes) / len(items),
            "executionChoicePromptRate": sum(item["executionChoicePrompt"] for item in outcomes) / len(items),
            "unnecessaryEscalationRate": sum(item["unnecessaryEscalation"] for item in outcomes) / len(items),
            "unauthorizedPersistentChangeRate": sum(item["persistentChangeWithoutAuthority"] for item in outcomes) / len(items),
            "meanReworkCount": sum(item["reworkCount"] for item in outcomes) / len(items),
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
