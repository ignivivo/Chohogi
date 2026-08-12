#!/usr/bin/env python3
"""Canonical strict parsers for Chohogi's declarative asset contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class SemanticContractError(ValueError):
    """A declaration cannot be interpreted unambiguously by its contract parser."""


class StrictYamlLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: StrictYamlLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise SemanticContractError("YAML mapping keys must be scalar values") from exc
        if duplicate:
            raise SemanticContractError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictYamlLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def strict_yaml(text: str) -> Any:
    try:
        return yaml.load(text, Loader=StrictYamlLoader)
    except (yaml.YAMLError, SemanticContractError) as exc:
        raise SemanticContractError(str(exc)) from exc


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SemanticContractError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def strict_json(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_json_object)
    except (json.JSONDecodeError, SemanticContractError) as exc:
        raise SemanticContractError(str(exc)) from exc


def frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SemanticContractError("missing YAML frontmatter")
    try:
        raw, _body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise SemanticContractError("unclosed YAML frontmatter") from exc
    document = strict_yaml(raw)
    if not isinstance(document, dict):
        raise SemanticContractError("frontmatter root must be a mapping")
    return document


def skill_assurance(path: Path) -> str:
    document = frontmatter(path)
    metadata = document.get("metadata")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("chohogi_assurance"), str):
        raise SemanticContractError("frontmatter metadata.chohogi_assurance must be a string")
    return metadata["chohogi_assurance"]
