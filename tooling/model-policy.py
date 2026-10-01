#!/usr/bin/env python3
"""Normalize observed model catalogs and produce bounded session-policy decisions.

This tool never discovers providers, reads credentials, or changes model settings.
Provider/runtime adapters must supply an already exposed, non-secret catalog.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EFFORT = ("low", "medium", "high", "ultra")
NATIVE_EFFORT = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")


class ContractError(ValueError):
    pass


def valid_effort(value: Any) -> bool:
    return isinstance(value, str) and bool(NATIVE_EFFORT.fullmatch(value))


def meets_minimum(actual: str, minimum: str) -> bool | None:
    """Return unknown rather than inventing an ordering for provider-native efforts."""
    if actual in EFFORT and minimum in EFFORT:
        return EFFORT.index(actual) >= EFFORT.index(minimum)
    return True if actual == minimum else None


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON at {path}: {exc}") from exc


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be a non-empty string")
    return value


def validate_catalog(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ContractError("catalog schemaVersion must be 1")
    text(value.get("observedAt"), "catalog.observedAt")
    observations = value.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ContractError("catalog.observations must be a non-empty list")
    identities: set[tuple[str, str]] = set()
    for index, item in enumerate(observations):
        prefix = f"catalog.observations[{index}]"
        if not isinstance(item, dict):
            raise ContractError(f"{prefix} must be an object")
        identity = (text(item.get("provider"), f"{prefix}.provider"), text(item.get("model"), f"{prefix}.model"))
        if identity in identities:
            raise ContractError(f"duplicate catalog model: {identity[0]}/{identity[1]}")
        identities.add(identity)
        if not isinstance(item.get("available"), bool):
            raise ContractError(f"{prefix}.available must be boolean")
        levels = item.get("reasoningLevels")
        if not isinstance(levels, list) or not levels or any(not valid_effort(level) for level in levels) or len(set(levels)) != len(levels):
            raise ContractError(f"{prefix}.reasoningLevels must be unique runtime effort identifiers")
        capabilities = item.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or any(not isinstance(capability, str) or not capability.strip() for capability in capabilities):
            raise ContractError(f"{prefix}.capabilities must be a non-empty string list")
        text(item.get("source"), f"{prefix}.source")
        price = item.get("price")
        if price is not None:
            if not isinstance(price, dict):
                raise ContractError(f"{prefix}.price must be an object")
            for key in ("inputUsdPerMillion", "outputUsdPerMillion"):
                if not isinstance(price.get(key), (int, float)) or isinstance(price[key], bool) or price[key] < 0:
                    raise ContractError(f"{prefix}.price.{key} must be a non-negative number")
    return value


def validate_task(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ContractError("task schemaVersion must be 1")
    text(value.get("role"), "task.role")
    capabilities = value.get("requiredCapabilities")
    if not isinstance(capabilities, list) or any(not isinstance(item, str) or not item.strip() for item in capabilities):
        raise ContractError("task.requiredCapabilities must be a string list")
    effort = value.get("minimumReasoning")
    if not valid_effort(effort):
        raise ContractError("task.minimumReasoning must be a valid normalized tier or exact provider-native effort")
    return value


def candidates(catalog: dict[str, Any], task: dict[str, Any]) -> list[dict[str, Any]]:
    minimum = task["minimumReasoning"]
    required = set(task["requiredCapabilities"])
    eligible = [
        item for item in catalog["observations"]
        if item["available"]
        and required.issubset(set(item["capabilities"]))
        and any(meets_minimum(level, minimum) is True for level in item["reasoningLevels"])
    ]
    result = [
        {"provider": item["provider"], "model": item["model"], "reasoning": level, "priceKnown": isinstance(item.get("price"), dict), "price": item.get("price")}
        for item in eligible
        for level in item["reasoningLevels"]
        if meets_minimum(level, minimum) is True
    ]
    result.sort(key=lambda item: (item["provider"], item["model"], EFFORT.index(item["reasoning"]) if item["reasoning"] in EFFORT else len(EFFORT), item["reasoning"]))
    return result


def explicit_selection(catalog: dict[str, Any], task: dict[str, Any], provider: str, model: str, reasoning: str) -> dict[str, Any]:
    if not valid_effort(reasoning):
        raise ContractError("requested reasoning must be a valid exact effort identifier")
    floor_check = meets_minimum(reasoning, task["minimumReasoning"])
    if floor_check is False:
        raise ContractError("requested reasoning cannot satisfy task minimum reasoning")
    item = next((candidate for candidate in catalog["observations"] if candidate["provider"] == provider and candidate["model"] == model), None)
    if item is None or not item["available"] or reasoning not in item["reasoningLevels"]:
        raise ContractError(f"requested model is not available with reasoning {provider}/{model}/{reasoning}")
    if not set(task["requiredCapabilities"]).issubset(set(item["capabilities"])):
        raise ContractError(f"requested model lacks required capabilities: {provider}/{model}")
    return {
        "provider": provider,
        "model": model,
        "reasoning": reasoning,
        "priceKnown": isinstance(item.get("price"), dict),
        "reasoningFloorCheck": "satisfied" if floor_check is True else "unknown-native-order",
    }


def compare(current: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, str]]:
    old = {(item["provider"], item["model"]): item for item in prior["observations"]}
    new = {(item["provider"], item["model"]): item for item in current["observations"]}
    changes: list[dict[str, str]] = []
    for key in sorted(new.keys() - old.keys()):
        changes.append({"kind": "model-added", "provider": key[0], "model": key[1]})
    for key in sorted(old.keys() - new.keys()):
        changes.append({"kind": "model-removed", "provider": key[0], "model": key[1]})
    for key in sorted(old.keys() & new.keys()):
        before, after = old[key], new[key]
        for field, kind in (("available", "availability-changed"), ("reasoningLevels", "reasoning-changed"), ("price", "price-changed")):
            if before.get(field) != after.get(field):
                changes.append({"kind": kind, "provider": key[0], "model": key[1]})
    return changes


PROFILE_HOSTS = {"claude", "codex"}
SECRET_KEY = re.compile(r"(api[_-]?key|token|secret|password|account|credential|billing)", re.I)


def validate_profile(value: Any) -> dict[str, Any]:
    """A saved project profile holds only user-confirmed role placements per host."""
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ContractError("profile must be an object with schemaVersion 1")
    hosts = value.get("hosts")
    if not isinstance(hosts, dict) or not hosts:
        raise ContractError("profile.hosts must be a non-empty object")
    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if SECRET_KEY.search(str(key)):
                    raise ContractError(f"{where}.{key}: profile must not hold credentials or account data")
                walk(child, f"{where}.{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{where}[{index}]")
    walk(value, "profile")
    def placement(item: Any, where: str) -> dict[str, str]:
        if not isinstance(item, dict):
            raise ContractError(f"{where} must be an object")
        return {"model": text(item.get("model"), f"{where}.model"), "effort": text(item.get("effort"), f"{where}.effort")}
    summary: dict[str, Any] = {}
    for host, entry in hosts.items():
        if host not in PROFILE_HOSTS:
            raise ContractError(f"profile.hosts.{host}: host must be one of {sorted(PROFILE_HOSTS)}")
        if not isinstance(entry, dict) or entry.get("confirmedBy") != "user":
            raise ContractError(f"profile.hosts.{host}.confirmedBy must be 'user'; unconfirmed recommendations are not saved")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(entry.get("confirmedAt", ""))):
            raise ContractError(f"profile.hosts.{host}.confirmedAt must be YYYY-MM-DD")
        roles = entry.get("roles")
        if not isinstance(roles, dict) or not roles:
            raise ContractError(f"profile.hosts.{host}.roles must be a non-empty object")
        summary[host] = {text(role, "role name"): placement(item, f"profile.hosts.{host}.roles.{role}") for role, item in roles.items()}
        overrides = entry.get("overrides", [])
        if not isinstance(overrides, list):
            raise ContractError(f"profile.hosts.{host}.overrides must be a list")
        for index, item in enumerate(overrides):
            where = f"profile.hosts.{host}.overrides[{index}]"
            if not isinstance(item, dict):
                raise ContractError(f"{where} must be an object")
            text(item.get("scope"), f"{where}.scope")
            text(item.get("role"), f"{where}.role")
            placement(item, where)
    return summary


RECOMMENDATIONS = Path(__file__).resolve().parents[1] / "assets/agents/trunk_orchestration/model-recommendations.json"
CARD_ROLES = ("scout", "implementer", "task-reviewer", "final-reviewer", "debugger")


def observed_models(path: Path | None) -> dict[str, list[str]] | None:
    if path is None:
        return None
    data = read_json(path)
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list):
        raise ContractError("observed catalog must contain a models list (tooling/model-catalog.py output)")
    return {str(item.get("id") or item.get("model")): [str(effort) for effort in (item.get("supportedReasoningEfforts") or [])]
            for item in models if isinstance(item, dict)}


def delivery_note(model: str, aliases: dict[str, str] | None) -> str:
    """How a saved or recommended model reaches a role on a host whose role argument takes only aliases."""
    if aliases is None or model == "session":
        return ""
    if model in aliases:
        return f" (Agent 인자: {aliases[model]})"
    if model in set(aliases.values()):
        return " — 별칭이라 계열의 최신 모델로 해석됨; 정확한 모델 id로 다시 저장 권장"
    return " — 역할별 전달 불가: Agent 인자가 이 모델을 고를 수 없어 세션 모델로 실행됨"


ROLE_FILES = Path(__file__).resolve().parents[1] / "agents"


def role_file_placements(role_agent: dict[str, str] | None) -> dict[str, dict[str, str]]:
    """Model and effort each role actually runs with on Claude: its plugin role file frontmatter."""
    placements: dict[str, dict[str, str]] = {}
    for role, agent in (role_agent or {}).items():
        path = ROLE_FILES / f"{agent}.md"
        if not path.is_file():
            continue
        front = path.read_text(encoding="utf-8").split("---", 2)[1]
        fields = dict(line.split(": ", 1) for line in front.strip().splitlines() if ": " in line)
        placements[role] = {"model": fields.get("model", "session"), "effort": fields.get("effort", "not-supported")}
    return placements


def placement_note(role: str, item: dict[str, str], placements: dict[str, dict[str, str]], aliases: dict[str, str] | None) -> str:
    actual = placements.get(role)
    if actual is None:
        return delivery_note(item["model"], aliases)
    if item["model"] == actual["model"] and item["effort"] == actual["effort"]:
        return " (역할 파일 값 그대로; Agent model 인자 생략)"
    note = "" if item["model"] == actual["model"] else delivery_note(item["model"], aliases)
    if item["effort"] != actual["effort"]:
        note += (f" — 역할 파일(frontmatter)은 {actual['model']} / {actual['effort']}: 강도는 역할 파일 값으로 실행되고"
                 " 모델만 Agent 인자로 덮어쓸 수 있음")
    return note


# Moved here from the injected guidance (HOM-20261001-guidance-slim): shown whenever the card asks.
ASK_RULES = ("저장한 뒤 `python3 tooling/model-policy.py profile --file .agents/chohogi-model-profile.json`로 검증합니다. "
             "저장된 배치(없으면 세션 모델)보다 비싼 모델·높은 강도는 사용자 확인 뒤에만 적용합니다. "
             "새 모델·가격·가용성·관련 평가 변화가 감지되면 저장된 배치가 있어도 이 card를 다시 제시합니다. "
             "답이 작업이 끝난 뒤에 오면 profile만 갱신하고 끝난 작업은 다시 열지 않습니다.")


def render_card(host: str, session_model: str, session_effort: str, profile_path: Path, catalog: dict[str, list[str]] | None) -> str:
    data = read_json(RECOMMENDATIONS)
    host_data = data["hosts"][host]
    aliases = host_data.get("deliveryAlias")
    placements = role_file_placements(host_data.get("roleAgent"))
    if profile_path.is_file():
        profile = read_json(profile_path)
        saved = validate_profile(profile).get(host)
        if saved:
            lines = [f"초호기 모델 배치: {profile_path}의 저장된 배치를 사용합니다 ({host}).",
                     *(f"- {role}: {item['model']} / {item['effort']}{placement_note(role, item, placements, aliases)}"
                       for role, item in saved.items())]
            for override in profile["hosts"][host].get("overrides", []):
                lines.append(f"- {override['role']} ({override['scope']}): {override['model']} / {override['effort']}"
                             f"{placement_note(override['role'], override, placements, aliases)}")
            missing = [role for role in CARD_ROLES if role not in saved]
            if missing:
                fallback = "역할 파일 값" if placements else f"세션 모델 {session_model} / {session_effort}"
                lines.append(f"profile에 없는 역할 — 선택해 주세요. 답을 받기 전까지 이 역할은 {fallback}로 진행합니다:")
                for role in missing:
                    item = host_data["roles"][role]
                    lines.append(f"- {role}: 미저장 → 추천 {item['model']} / {item['effort']} — {item['why']}")
                lines.append(ASK_RULES)
            return "\n".join(lines)
    roles = host_data["roles"]
    lines = [f"초호기 모델 배치 제안 ({host}) — 지금은 모든 역할이 세션 모델 {session_model} / {session_effort}로 돌고 있습니다."]
    host_catalog = host_data.get("catalog")
    if isinstance(host_catalog, dict) and host_catalog.get("status") == "unknown":
        lines.append(f"모델 목록: unknown — {host_catalog['reason']}")
    lines.append(f"추천 (근거: {data['basis'].split(' (')[0]}; 검토일 {data['reviewedAt']}):")
    for role in CARD_ROLES:
        item = roles[role]
        note = delivery_note(item["model"], aliases)
        if catalog is not None:
            if item["model"] not in catalog:
                note += " — 관측된 런타임 목록에 없음"
            elif item["effort"] not in ("not-selectable", "session") and item["effort"] not in catalog[item["model"]]:
                note += " — 이 강도는 관측된 목록에 없음"
        lines.append(f"- {role}: {item['model']} / {item['effort']}{note} — {item['why']}")
    lines.append("그대로 둘지, 바꿀지, 더 세세하게 정할지(예: 결제·보안 검토는 최상위) 알려주면 "
                 ".agents/chohogi-model-profile.json에 저장하고 이후 세션은 다시 묻지 않습니다. 답을 주기 전까지는 세션 모델로 계속합니다.")
    lines.append(ASK_RULES)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    recommend = subparsers.add_parser("recommend")
    recommend.add_argument("--catalog", type=Path, required=True)
    recommend.add_argument("--task", type=Path, required=True)
    selection = subparsers.add_parser("select")
    selection.add_argument("--catalog", type=Path, required=True)
    selection.add_argument("--task", type=Path, required=True)
    selection.add_argument("--provider", required=True)
    selection.add_argument("--model", required=True)
    selection.add_argument("--reasoning", required=True)
    selection.add_argument("--reason", required=True)
    comparison = subparsers.add_parser("compare")
    comparison.add_argument("--catalog", type=Path, required=True)
    comparison.add_argument("--prior", type=Path, required=True)
    escalation = subparsers.add_parser("learning-escalation")
    escalation.add_argument("--catalog", type=Path, required=True)
    escalation.add_argument("--learning", type=Path, required=True)
    saved = subparsers.add_parser("profile", help="validate a saved project profile (.agents/chohogi-model-profile.json)")
    saved.add_argument("--file", type=Path, required=True)
    card = subparsers.add_parser("card", help="render the Model Session Policy card for this host")
    card.add_argument("--host", choices=sorted(PROFILE_HOSTS), required=True)
    card.add_argument("--session-model", required=True)
    card.add_argument("--session-effort", required=True)
    card.add_argument("--profile", type=Path, default=Path(".agents/chohogi-model-profile.json"))
    card.add_argument("--observed-catalog", type=Path)
    args = parser.parse_args()
    if args.command == "card":
        try:
            print(render_card(args.host, args.session_model, args.session_effort, args.profile, observed_models(args.observed_catalog)))
        except ContractError as exc:
            print(f"Model policy: FAIL\n- {exc}", file=sys.stderr)
            return 1
        return 0
    if args.command == "profile":
        try:
            summary = validate_profile(read_json(args.file))
        except ContractError as exc:
            print(f"Model policy: FAIL\n- {exc}", file=sys.stderr)
            return 1
        print(json.dumps({"schemaVersion": 1, "hosts": summary, "requiresHumanConfirmation": False,
                          "limits": "Validates shape and user confirmation only; whether each model/effort is still selectable is checked against a fresh runtime catalog, not by this command."},
                         ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        catalog = validate_catalog(read_json(args.catalog))
        if args.command == "select":
            task = validate_task(read_json(args.task))
            reason = text(args.reason, "selection reason")
            chosen = explicit_selection(catalog, task, args.provider, args.model, args.reasoning)
            result = {"schemaVersion": 1, "role": task["role"], "selectionMode": "user-override", "selectionReason": reason, **chosen, "requiresHumanConfirmation": chosen["reasoningFloorCheck"] == "unknown-native-order", "limits": "The exact native provider/model/reasoning tuple is checked against the observed selectable list. For native effort names with no declared cross-tier mapping, the task floor remains unknown and must be confirmed by the user; no quality or billed-cost claim is made."}
        elif args.command == "recommend":
            task = validate_task(read_json(args.task))
            result = {"schemaVersion": 1, "role": task["role"], "candidates": candidates(catalog, task), "requiresHumanConfirmation": True, "limits": "Candidates are filtered by observed availability, declared capability, and selectable effort, then listed alphabetically; separate input/output prices are reported when known, without inferring quality, quality-per-dollar, or actual task cost."}
        elif args.command == "compare":
            changes = compare(catalog, validate_catalog(read_json(args.prior)))
            result = {"schemaVersion": 1, "changes": changes, "requiresHumanReconfirmation": bool(changes), "limits": "Only supplied catalog facts are compared; no provider was queried by this tool."}
        else:
            learning = read_json(args.learning)
            if not isinstance(learning, dict) or learning.get("confirmedRootCause") is not True or learning.get("preventionVerified") is not True:
                raise ContractError("learning escalation requires confirmedRootCause and preventionVerified")
            text(learning.get("evidenceId"), "learning.evidenceId")
            task = validate_task({"schemaVersion": 1, "role": learning.get("requestedRole"), "requiredCapabilities": [], "minimumReasoning": learning.get("requestedMinimumReasoning")})
            result = {"schemaVersion": 1, "evidenceId": learning["evidenceId"], "candidates": candidates(catalog, task), "requiresHumanReconfirmation": True, "reason": "verified-learning-escalation"}
    except ContractError as exc:
        print(f"Model policy: FAIL\n- {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
