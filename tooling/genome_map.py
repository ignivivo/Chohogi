#!/usr/bin/env python3
"""Build, check, and query Chohogi's source-derived genome map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "docs/chohogi/genome-map.graph.json"
OUTPUT_MARKDOWN = ROOT / "docs/chohogi/genome-map.md"
SKILL_ROOT = ROOT / "assets/agents/reusable_methods"
GENERATED = {OUTPUT_JSON, OUTPUT_MARKDOWN}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_files() -> list[Path]:
    roots = (ROOT / "assets", ROOT / "tooling", ROOT / "docs/chohogi", ROOT / "README.md", ROOT / "manifest.json")
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(
                path for path in root.rglob("*")
                if path.is_file() and path not in GENERATED and "__pycache__" not in path.parts and path.suffix != ".pyc"
            )
    return sorted(paths)


def digest(paths: list[Path]) -> str:
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(relative(path).encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def add_node(nodes: dict[str, dict[str, Any]], node_id: str, kind: str, path: str, **extra: Any) -> None:
    nodes.setdefault(node_id, {"id": node_id, "kind": kind, "path": path, **extra})


def add_edge(edges: list[dict[str, Any]], source: str, target: str, relation: str, evidence: str) -> None:
    edge = {"source": source, "target": target, "relation": relation, "evidence": evidence}
    if edge not in edges:
        edges.append(edge)


def build_graph() -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    paths = source_files()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    for component in manifest["components"]:
        component_id = f"component:{component['id']}"
        add_node(nodes, component_id, "component", component["source"], state=component["state"])
        source_id = f"asset:{component['source']}"
        add_node(nodes, source_id, "asset", component["source"])
        add_edge(edges, source_id, component_id, "activates", "manifest.json")
        add_edge(edges, "asset:manifest.json", component_id, "activates", "manifest.json")
        if component["state"] == "active":
            add_edge(edges, component_id, f"endpoint:{component['destination']}", "installs", "manifest.json")
            add_node(nodes, f"endpoint:{component['destination']}", "endpoint", component["destination"])

    for skill_file in sorted(SKILL_ROOT.glob("*/SKILL.md")):
        skill = skill_file.parent.name
        skill_id = f"skill:{skill}"
        add_node(nodes, skill_id, "skill", relative(skill_file), state="active")
        add_edge(edges, skill_id, "verifier:provenance", "verifies", "tooling/verify-provenance.py")
        for resource in skill_file.parent.rglob("*"):
            if resource.is_file() and resource != skill_file:
                resource_id = f"asset:{relative(resource)}"
                add_node(nodes, resource_id, "asset", relative(resource))
                add_edge(edges, skill_id, resource_id, "requires", relative(skill_file))

    for verifier in sorted((ROOT / "tooling").glob("verify-*.py")):
        identifier = verifier.stem.removeprefix("verify-")
        add_node(nodes, f"verifier:{identifier}", "verifier", relative(verifier))
    add_node(nodes, "verifier:provenance", "verifier", "tooling/verify-provenance.py")
    add_node(nodes, "verifier:graft-compatibility_install-audit", "verifier", "tooling/graft-compatibility_install-audit.sh")

    documents = [ROOT / "README.md"] + sorted(
        path for path in (ROOT / "docs/chohogi").rglob("*.md") if path not in GENERATED
    )
    skill_names = [path.parent.name for path in SKILL_ROOT.glob("*/SKILL.md")]
    for document in documents:
        document_id = f"document:{relative(document)}"
        document_text = document.read_text(encoding="utf-8")
        add_node(nodes, document_id, "document", relative(document))
        for skill in skill_names:
            if re.search(rf"(?<![a-z0-9-]){re.escape(skill)}(?![a-z0-9-])", document_text):
                add_edge(edges, f"skill:{skill}", document_id, "documents", relative(document))
        for candidate in re.findall(r"(?:assets|tooling|docs)/[A-Za-z0-9_./-]+", document_text):
            target = ROOT / candidate.rstrip(".,;:)")
            if target.is_file():
                asset_id = f"asset:{candidate.rstrip('.,;:)')}"
                add_node(nodes, asset_id, "asset", candidate.rstrip(".,;:)"))
                add_edge(edges, asset_id, document_id, "documents", relative(document))

    # README is the public active-capability inventory, so every reusable method
    # affects it even when a concise Korean summary does not spell out its ID.
    for skill in skill_names:
        add_edge(edges, f"skill:{skill}", "document:README.md", "documents", "manifest.json: reusable-methods")

    for source in paths:
        if source.suffix not in {".md", ".py", ".sh", ".json"}:
            continue
        source_path = relative(source)
        if source.name.startswith("verify-") and source.suffix == ".py":
            source_id = f"verifier:{source.stem.removeprefix('verify-')}"
            add_node(nodes, source_id, "verifier", source_path)
        elif source.name == "graft-compatibility_install-audit.sh":
            source_id = "verifier:graft-compatibility_install-audit"
            add_node(nodes, source_id, "verifier", source_path)
        else:
            source_id = f"asset:{source_path}"
            add_node(nodes, source_id, "asset", source_path)
        text = source.read_text(encoding="utf-8", errors="ignore")
        for candidate in re.findall(r"assets/[A-Za-z0-9_./-]+", text):
            target = ROOT / candidate.rstrip("'\"),.;:")
            if target.is_file():
                target_id = f"asset:{candidate.rstrip(chr(39) + chr(34) + '),.;:')}"
                add_node(nodes, target_id, "asset", candidate.rstrip("'\"),.;:"))
                add_edge(edges, source_id, target_id, "requires", relative(source))

    installer_id = "asset:tooling/install.sh"
    manifest_id = "asset:manifest.json"
    add_edge(edges, installer_id, manifest_id, "requires", "tooling/install.sh")
    add_edge(edges, installer_id, "verifier:graft-compatibility_install-audit", "requires", "tooling/graft-compatibility_install-audit.sh")

    return {"schemaVersion": 1, "sourceDigest": digest(paths), "nodes": sorted(nodes.values(), key=lambda node: node["id"]), "edges": sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["relation"]))}


def markdown(graph: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for node in graph["nodes"]:
        counts[node["kind"]] = counts.get(node["kind"], 0) + 1
    active_skills = [node["id"].removeprefix("skill:") for node in graph["nodes"] if node["kind"] == "skill"]
    return "\n".join((
        "# Genome map — Chohogi topology and expression", "",
        "_Generated by `python3 tooling/genome_map.py build`; do not edit manually._", "",
        f"Source digest: `{graph['sourceDigest']}`", "",
        "```mermaid", "flowchart LR",
        "  E[runtime entrypoint] --> C[conductor]",
        "  C --> W[branches workflows]", "  W --> M[reusable methods]",
        "  M --> F[functional assurance]", "  F --> H[adaptive regulation / Homeostasis]",
        "```", "",
        "## Current graph", "",
        "| Node kind | Count |", "| --- | ---: |",
        *[f"| {kind} | {count} |" for kind, count in sorted(counts.items())], "",
        "## Active reusable methods", "",
        ", ".join(f"`{skill}`" for skill in active_skills), "",
        "## Machine representation", "",
        "See `genome-map.graph.json` for nodes, edges, evidence paths, and the source digest.", "",
    ))


def write_outputs(graph: dict[str, Any]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MARKDOWN.write_text(markdown(graph), encoding="utf-8")


def impact(graph: dict[str, Any], changed_path: str) -> dict[str, Any]:
    normalized = changed_path.replace("\\", "/")
    initial = {node["id"] for node in graph["nodes"] if node["path"] == normalized}
    if not initial and "/SKILL.md" in normalized:
        initial = {f"skill:{Path(normalized).parent.name}"}
    if not initial:
        raise ValueError(f"unmapped changed path: {normalized}")
    outgoing: dict[str, set[str]] = {}
    reverse_consumer: dict[str, set[str]] = {}
    for edge in graph["edges"]:
        outgoing.setdefault(edge["source"], set()).add(edge["target"])
        if edge["relation"] in {"activates", "requires"}:
            reverse_consumer.setdefault(edge["target"], set()).add(edge["source"])
    affected = set(initial)
    queue = deque(initial)
    while queue:
        node = queue.popleft()
        for neighbor in outgoing.get(node, set()) | reverse_consumer.get(node, set()):
            if neighbor not in affected:
                affected.add(neighbor)
                queue.append(neighbor)
    nodes = {node["id"]: node for node in graph["nodes"]}
    return {
        "changed": normalized,
        "affected": sorted(affected),
        "verification": sorted(node for node in affected if nodes[node]["kind"] == "verifier"),
        "documentation": sorted(node for node in affected if nodes[node]["kind"] == "document"),
        "repairDisposition": "inspect-before-repair",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--stdout", action="store_true")
    commands.add_parser("check")
    impact_parser = commands.add_parser("impact")
    impact_parser.add_argument("changed_path")
    repair_parser = commands.add_parser("repair-packet")
    repair_parser.add_argument("changed_path")
    arguments = parser.parse_args()
    graph = build_graph()
    if arguments.command == "build":
        if arguments.stdout:
            print(json.dumps(graph, indent=2, ensure_ascii=False))
        else:
            write_outputs(graph)
    elif arguments.command == "check":
        expected_json = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"
        expected_markdown = markdown(graph)
        if not OUTPUT_JSON.is_file() or not OUTPUT_MARKDOWN.is_file() or OUTPUT_JSON.read_text(encoding="utf-8") != expected_json or OUTPUT_MARKDOWN.read_text(encoding="utf-8") != expected_markdown:
            print("genome map is stale; run: python3 tooling/genome_map.py build", file=sys.stderr)
            return 1
    else:
        try:
            result = impact(graph, arguments.changed_path)
            if arguments.command == "repair-packet":
                result = {
                    "changed": result["changed"],
                    "affected": result["affected"],
                    "observedState": "conformance-not-yet-checked",
                    "disposition": "inspect-before-repair",
                    "requiredReverification": result["verification"],
                    "documentation": result["documentation"],
                    "remainingRisk": "repair requires normal ownership and authority review",
                }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except ValueError as exc:
            print(f"genome map: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
