#!/usr/bin/env python3
"""Verify the replay-result contract, example, and rejection behavior."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def validate(validator: Path, data: dict[object, object]) -> bool:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(data, handle)
        result_path = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(validator), str(result_path)], capture_output=True, text=True, check=False
        ).returncode == 0
    finally:
        result_path.unlink(missing_ok=True)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    evals = root / "assets/agents/chohogi/trunk/evals"
    schema_path = evals / "replay-result.schema.json"
    example_path = evals / "replay-result.example.json"
    validator = root / "tooling/validate-replay-result.py"
    errors: list[str] = []

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Cannot load replay evaluation assets: {error}")
        schema = {}
        example = {}

    if schema.get("schemaVersion") != 1:
        errors.append("Replay schema must declare schemaVersion 1.")
    if set(schema.get("required", [])) != {
        "fixtureId", "profile", "model", "effort", "toolCondition", "repoCondition", "outcomes", "evidenceRef"
    }:
        errors.append("Replay schema required fields drifted.")
    if not validate(validator, example):
        errors.append("Replay example must pass the result validator.")

    for label, mutation in (
        ("missing schema version", {key: value for key, value in example.items() if key != "schemaVersion"}),
        ("string boolean outcome", {**example, "outcomes": {**example["outcomes"], "flowCorrect": "true"}}),
        ("boolean rework count", {**example, "outcomes": {**example["outcomes"], "reworkCount": False}}),
        ("unknown result field", {**example, "prompt": "must not be recorded"}),
    ):
        if validate(validator, mutation):
            errors.append(f"Replay validator accepted negative mutation: {label}")

    if errors:
        print("Chohogi replay evaluation verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Chohogi replay evaluation verification: PASS (schema, example, and negative mutations are valid).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
