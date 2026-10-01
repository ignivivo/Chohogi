#!/usr/bin/env python3
"""Reject derived status claims that outrun their declared source evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


RANK = {
    "failed": 0,
    "unknown": 0,
    "deferred": 1,
    "degraded": 1,
    "provisional": 2,
    "verified": 3,
    "healthy": 3,
    "approved": 3,
}


def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        return ["status provenance schemaVersion must be 1"]
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["status provenance claims must be a non-empty list"]
    errors: list[str] = []
    resolutions = {item["id"]: item for item in data.get("resolutionCatalog", []) if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()} if isinstance(data.get("resolutionCatalog", []), list) else {}
    evidence = {item["id"]: item for item in data.get("evidenceCatalog", []) if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()} if isinstance(data.get("evidenceCatalog", []), list) else {}
    seen: set[str] = set()

    def evidence_refs_exist(refs: object) -> bool:
        return isinstance(refs, list) and bool(refs) and all(
            isinstance(ref, str)
            and ref in evidence
            and isinstance(evidence[ref].get("path"), str)
            and (root / evidence[ref]["path"]).is_file()
            for ref in refs
        )

    def resolution_exists(ref: object) -> bool:
        return isinstance(ref, str) and ref in resolutions and isinstance(resolutions[ref].get("path"), str) and (root / resolutions[ref]["path"]).is_file()

    for item in claims:
        if not isinstance(item, dict):
            errors.append("status provenance claims must be objects")
            continue
        claim_id = item.get("id")
        if not isinstance(claim_id, str) or not claim_id.strip() or claim_id in seen:
            errors.append("status provenance claim ids must be unique and non-empty")
            continue
        seen.add(claim_id)
        source = item.get("sourceStatus")
        derived = item.get("derivedStatus")
        if not isinstance(source, str) or not isinstance(derived, str) or source not in RANK or derived not in RANK:
            errors.append(f"{claim_id}: sourceStatus and derivedStatus must be known")
            continue
        source_refs = item.get("sourceEvidenceRefs")
        if not isinstance(source_refs, list) or not source_refs:
            errors.append(f"{claim_id}: sourceEvidenceRefs must identify source evidence")
        elif not evidence_refs_exist(source_refs):
            errors.append(f"{claim_id}: sourceEvidenceRefs are not in evidenceCatalog")
        if RANK[derived] > RANK[source]:
            if item.get("explicitPromotion") is not True:
                errors.append(f"{claim_id}: stronger derived status needs explicitPromotion")
            if not isinstance(item.get("resolutionRef"), str) or not item["resolutionRef"].strip():
                errors.append(f"{claim_id}: stronger derived status needs resolutionRef")
            if not isinstance(item.get("evidenceRefs"), list) or not item["evidenceRefs"]:
                errors.append(f"{claim_id}: stronger derived status needs evidenceRefs")
            if not isinstance(item.get("owner"), str) or not item["owner"].strip():
                errors.append(f"{claim_id}: stronger derived status needs owner")
            if not resolution_exists(item.get("resolutionRef")):
                errors.append(f"{claim_id}: resolutionRef is not in resolutionCatalog")
            if not evidence_refs_exist(item.get("evidenceRefs")):
                errors.append(f"{claim_id}: evidenceRefs are not in evidenceCatalog")
        source_conflict = item.get("sourceConflict", False)
        if not isinstance(source_conflict, bool):
            errors.append(f"{claim_id}: sourceConflict must be a boolean")
        elif source_conflict:
            disposition = item.get("conflictDisposition")
            if not isinstance(disposition, str) or disposition not in {"unknown", "deferred", "resolved"}:
                errors.append(f"{claim_id}: source conflict needs a disposition")
            elif disposition != "resolved" and derived not in {"unknown", "deferred"}:
                errors.append(f"{claim_id}: unresolved source conflict cannot support a positive derived claim")
            elif disposition == "resolved" and not resolution_exists(item.get("resolutionRef")):
                errors.append(f"{claim_id}: resolved source conflict needs a cataloged resolutionRef")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid status provenance input: {exc}")
        return 1
    errors = validate(data, args.root.resolve())
    if errors:
        print("Status provenance verification: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Status provenance verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
