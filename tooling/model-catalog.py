#!/usr/bin/env python3
"""Read a bounded, non-secret model list from an official Codex runtime."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAX_OUTPUT_BYTES = 16 * 1024 * 1024
EFFORT_ID = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")


class CatalogError(ValueError):
    pass


def resolve_codex(binary: str | None) -> tuple[Path, str]:
    selected = binary or os.environ.get("CHOHOGI_CODEX_BINARY")
    if selected:
        path = Path(selected).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return path, "codex-binary-override"
        raise CatalogError("configured Codex executable is missing or not executable")

    # Search only the two official VS Code extension roots and the Codex publisher's
    # extension name. Do not inspect VS Code settings, extension state, or credentials.
    roots = (
        Path.home() / ".vscode" / "extensions",
        Path.home() / ".vscode-server" / "extensions",
        Path.home() / ".vscode-server-insiders" / "extensions",
    )
    candidates = [
        executable
        for root in roots
        for executable in root.glob("openai.chatgpt-*/bin/*/codex")
        if executable.is_file() and os.access(executable, os.X_OK)
    ]
    if candidates:
        return max(candidates, key=lambda item: item.stat().st_mtime_ns), "codex-vscode-runtime"
    path_candidate = shutil.which("codex")
    if path_candidate:
        return Path(path_candidate), "codex-path-runtime"
    raise CatalogError("Codex runtime executable was not found; pass --binary or set CHOHOGI_CODEX_BINARY")


def project_catalog(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, dict) or not isinstance(raw.get("models"), list):
        raise CatalogError("runtime returned an invalid model catalog")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw["models"]:
        if not isinstance(item, dict) or item.get("visibility") != "list":
            continue
        model_id = item.get("slug")
        name = item.get("display_name")
        levels = item.get("supported_reasoning_levels")
        if not isinstance(model_id, str) or not model_id.strip() or not isinstance(name, str) or not name.strip() or not isinstance(levels, list):
            raise CatalogError("runtime returned an invalid selectable model entry")
        if model_id in seen:
            raise CatalogError("runtime returned duplicate selectable model IDs")
        seen.add(model_id)
        efforts: list[str] = []
        for level in levels:
            effort = level.get("effort") if isinstance(level, dict) else None
            if not isinstance(effort, str) or not EFFORT_ID.fullmatch(effort):
                raise CatalogError("runtime returned an invalid reasoning effort")
            if effort in efforts:
                raise CatalogError("runtime returned duplicate reasoning efforts")
            efforts.append(effort)
        if not efforts:
            raise CatalogError("runtime returned a selectable model without reasoning efforts")
        default = item.get("default_reasoning_level")
        if default is not None and (not isinstance(default, str) or default not in efforts):
            raise CatalogError("runtime returned a default reasoning effort not listed as supported")
        result.append({
            "id": model_id,
            "name": name,
            "reasoningEfforts": efforts,
            "defaultReasoningEffort": default,
        })
    if not result:
        raise CatalogError("runtime returned no selectable models")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="provider", required=True)
    codex = commands.add_parser("codex", help="read the official Codex runtime catalog")
    codex.add_argument("--binary", help="explicit executable override; otherwise checks narrow VS Code extension roots before PATH")
    args = parser.parse_args()
    try:
        executable, source_kind = resolve_codex(args.binary)
        with tempfile.TemporaryFile() as output:
            completed = subprocess.run(
                [str(executable), "debug", "models"],
                check=False,
                stdout=output,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            if completed.returncode != 0:
                raise CatalogError("Codex runtime could not provide its model catalog")
            size = output.tell()
            if size > MAX_OUTPUT_BYTES:
                raise CatalogError("Codex runtime catalog exceeded the safe size limit")
            output.seek(0)
            payload = output.read(MAX_OUTPUT_BYTES + 1)
        try:
            raw = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CatalogError("Codex runtime returned malformed catalog JSON") from exc
        models = project_catalog(raw)
    except (CatalogError, OSError, subprocess.TimeoutExpired) as exc:
        message = str(exc) if isinstance(exc, CatalogError) else "Codex runtime catalog query failed or timed out"
        print(f"Model catalog: unavailable\n- {message}", file=sys.stderr)
        return 1
    card = {
        "schemaVersion": 1,
        "provider": source_kind,
        "observedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "models": models,
        "requiresUserConfirmation": True,
        "limits": "This is a projected list of models marked list-visible by the selected Codex runtime. It does not establish the model currently selected in a conversation, price, benchmark quality, API entitlement, or that the VS Code picker is synchronized with this query. Confirm this list with the user; if it differs, record their correction separately as user-reported rather than rewriting the runtime observation.",
    }
    print(json.dumps(card, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
