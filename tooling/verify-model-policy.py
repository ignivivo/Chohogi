#!/usr/bin/env python3
"""Verify the bounded session model-policy contract and its executable fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []
    policy = ROOT / "assets/agents/trunk_orchestration/model-policy.md"
    runtime = ROOT / "assets/runtime_entrypoint/AGENTS.md"
    evaluator = ROOT / "tooling/model-policy.py"
    tests = ROOT / "tooling/tests/test_model_policy.py"
    for path, terms in {
        policy: ("<!-- chohogi:model-policy -->", "Model Session Policy card", "reasoning effort", "unknown", "추정하지 않는다", "learning"),
        runtime: ("model-policy.md", "Model Session Policy"),
        evaluator: ("never discovers providers", "requiresHumanConfirmation", "requiresHumanReconfirmation"),
    }.items():
        if not path.is_file():
            errors.append(f"Missing model-policy asset: {path}")
            continue
        content = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in content:
                errors.append(f"{path.name} is missing required term: {term}")
    if not tests.is_file():
        errors.append(f"Missing model-policy behavioral tests: {tests}")
    else:
        result = subprocess.run([sys.executable, "-m", "unittest", "tooling/tests/test_model_policy.py"], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append("Model-policy behavioral fixtures failed: " + result.stderr.strip())
    if errors:
        print("Model policy verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Model policy verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
