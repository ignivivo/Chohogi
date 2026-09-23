#!/usr/bin/env python3
"""Maintain project-owned, reviewable execution records.

Records preserve observed facts, material decisions, outcomes, and only the
artifacts a work contract explicitly asks to verify. They never store raw
prompts, private reasoning, credentials, or complete tool payloads.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

def digest(path: Path) -> str:
    h = hashlib.sha256()
    for file in sorted(p for p in path.rglob('*') if p.is_file()):
        relative = file.relative_to(path)
        if '.git' in relative.parts or relative.parts[:2] == ('docs', 'work-log'):
            continue
        h.update(str(relative).encode()); h.update(file.read_bytes())
    return h.hexdigest()
def root(project: Path, work_id: str) -> Path: return project / 'docs/work-log/records' / work_id
def load(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def event(folder: Path, data: dict):
    data['at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with (folder/'events.jsonl').open('a', encoding='utf-8') as f: f.write(json.dumps(data, ensure_ascii=False)+'\n')

def parse_json(value: str, label: str):
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{label} must be valid JSON: {exc.msg}') from exc

def dump(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def registry_sources(project: Path, registry_path: Path) -> list[Path]:
    data=load(registry_path); sources=[]
    for item in data.get('documents', []) if isinstance(data, dict) else []:
        if not isinstance(item, dict) or item.get('role') not in {'feedback-source','review-synthesis'} or item.get('state') != 'active' or item.get('scan') is False: continue
        target=(project / str(item.get('path'))).resolve()
        if target.is_file(): sources.append(target)
        elif target.is_dir(): sources.extend(path for path in target.rglob('*.md') if path.is_file() and 'archive' not in path.relative_to(target).parts)
    return sorted(set(sources))

def recorded_feedback_sources(project: Path) -> set[tuple[str, str]]:
    records=project/'docs/work-log/records'; found=set()
    for candidate in records.iterdir() if records.is_dir() else []:
        trail=candidate/'events.jsonl'
        if not trail.is_file(): continue
        for item in events(candidate):
            if item.get('event') == 'feedback': found.add((item.get('source'), item.get('sha256')))
    return found


def contract_errors(contract: dict) -> list[str]:
    errors: list[str] = []
    requested = contract.get('requestedItems', [])
    if requested:
        if not isinstance(requested, list): errors.append('requestedItems must be a list')
        else:
            seen=set()
            for item in requested:
                if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'].strip() or not isinstance(item.get('description'), str) or not item['description'].strip():
                    errors.append('requestedItems need unique id and description'); continue
                if item['id'] in seen: errors.append(f'duplicate requested item: {item["id"]}')
                seen.add(item['id'])
    for acceptance in contract.get('acceptance', []):
        if not isinstance(acceptance, dict):
            errors.append('acceptance items must be objects')
            continue
        evidence = acceptance.get('consumerEvidence')
        if evidence is None:
            continue
        if not isinstance(evidence, list):
            errors.append('consumerEvidence must be a list')
            continue
        for item in evidence:
            if not isinstance(item, dict) or not isinstance(item.get('consumer'), str) or not item['consumer'].strip():
                errors.append('consumer evidence needs a non-empty consumer')
                continue
            status = item.get('status')
            if status not in {'verified', 'deferred'}:
                errors.append('consumer evidence status must be verified or deferred')
            elif status == 'verified' and (not isinstance(item.get('artifactKind'), str) or not item['artifactKind'].strip()):
                errors.append('verified consumer evidence needs an artifactKind')
            elif status == 'deferred' and (not isinstance(item.get('reason'), str) or not item['reason'].strip()):
                errors.append('deferred consumer evidence needs a reason')
    return errors


def missing_consumer_evidence(state: dict) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for acceptance in state['contract'].get('acceptance', []):
        for item in acceptance.get('consumerEvidence', []):
            if item['status'] != 'verified':
                continue
            artifact_kind = item['artifactKind']
            found = any(
                artifact['acceptanceId'] == acceptance.get('id')
                and artifact['kind'] == artifact_kind
                and artifact['status'] == 'pass'
                for artifact in state['artifacts']
            )
            if not found:
                missing.append({'acceptanceId': acceptance.get('id', ''), 'consumer': item['consumer'], 'artifactKind': artifact_kind})
    return missing


def artifact_status(artifact: dict) -> dict[str, str] | None:
    """Return a current integrity failure for one registered artifact, if any."""
    path = Path(artifact["path"])
    if not path.is_file():
        return {"path": str(path), "reason": "missing"}
    current = hashlib.sha256(path.read_bytes()).hexdigest()
    if current != artifact["sha256"]:
        return {"path": str(path), "reason": "changed"}
    return None


def open_acceptance(state: dict) -> list[dict[str, object]]:
    """Project contract obligations without copying unbounded record contents."""
    open_items: list[dict[str, object]] = []
    for item in state["contract"].get("acceptance", []):
        kinds = {value["kind"] for value in item.get("requiredArtifacts", []) if value.get("kind")}
        seen = {value["kind"] for value in state["artifacts"] if value["acceptanceId"] == item.get("id") and value["status"] == "pass"}
        remaining = sorted(kinds - seen)
        if remaining:
            open_items.append({"id": item.get("id"), "kinds": remaining})
    return open_items

def review(folder: Path):
    groups = {'baseline': [], 'facts': [], 'capabilityMaps': [], 'decisions': [], 'decisionReviews': [], 'decisionReports': [], 'decisionResolutions': [], 'outcomes': [], 'feedback': [], 'scopeItems': [], 'artifacts': [], 'checkpoints': []}
    categories = {'begin': 'baseline', 'fact': 'facts', 'capability-map': 'capabilityMaps', 'decision': 'decisions', 'review-request': 'decisionReviews', 'review-response': 'decisionReviews', 'review-resolution': 'decisionReviews', 'decision-report': 'decisionReports', 'decision-resolution': 'decisionResolutions', 'outcome': 'outcomes', 'feedback': 'feedback', 'scope-item': 'scopeItems', 'artifact': 'artifacts', 'checkpoint': 'checkpoints'}
    for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        category = categories.get(item.get('event'))
        if category: groups[category].append(item)
    return groups

def events(folder: Path):
    return [json.loads(line) for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]

def decision_event(folder: Path, decision_id: str):
    for item in reversed(events(folder)):
        if item.get('event') == 'decision' and item.get('id') == decision_id:
            return item
    return None

def capability_map_event(folder: Path, map_id: str):
    for item in reversed(events(folder)):
        if item.get('event') == 'capability-map' and item.get('id') == map_id:
            return item
    return None
def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--project',type=Path,required=True); sub=p.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('begin'); b.add_argument('--work-id',required=True); b.add_argument('--contract',type=Path,required=True)
    for name in ('artifact','checkpoint','resume','fact','prior-feedback','feedback','feedback-scan','scope-item','capability-map','decision','review-request','review-response','review-resolution','decision-report','decision-resolution','outcome','review','handoff','finalize'):
        q=sub.add_parser(name); q.add_argument('--work-id',required=name != 'feedback-scan')
        if name=='artifact': q.add_argument('--acceptance-id',required=True); q.add_argument('--kind',required=True); q.add_argument('--path',type=Path,required=True)
        if name=='checkpoint': q.add_argument('--id',required=True); q.add_argument('--summary',required=True)
        if name=='fact': q.add_argument('--kind',required=True); q.add_argument('--summary',required=True); q.add_argument('--details',default='{}')
        if name=='feedback':
            q.add_argument('--source', type=Path, required=True); q.add_argument('--summary', required=True)
            q.add_argument('--impact', choices=('none', 'plan', 'consumer', 'policy', 'execution'), required=True)
            q.add_argument('--disposition', choices=('plan-updated', 'deferred', 'rejected', 'no-action'), required=True)
            q.add_argument('--target', default=''); q.add_argument('--reason', default='')
        if name=='feedback-scan': q.add_argument('--root', type=Path); q.add_argument('--registry', type=Path)
        if name=='scope-item': q.add_argument('--id', required=True); q.add_argument('--status', choices=('implemented','deferred','excluded'), required=True); q.add_argument('--summary', required=True); q.add_argument('--reason', default='')
        if name=='capability-map': q.add_argument('--id',required=True); q.add_argument('--scope',required=True); q.add_argument('--findings',required=True); q.add_argument('--prior-feedback',default='[]')
        if name=='decision':
            q.add_argument('--id', required=True); q.add_argument('--topic', required=True); q.add_argument('--observations', required=True); q.add_argument('--options', required=True); q.add_argument('--selected', required=True); q.add_argument('--rationale', required=True); q.add_argument('--review-trigger', required=True); q.add_argument('--review-required', action='store_true'); q.add_argument('--requires-user-decision', action='store_true'); q.add_argument('--capability-map-id'); q.add_argument('--capabilities-considered',default='[]')
        if name=='review-request': q.add_argument('--decision-id', required=True)
        if name=='review-response': q.add_argument('--decision-id', required=True); q.add_argument('--verdict', choices=('no-blocking-findings','findings','block'), required=True); q.add_argument('--findings', required=True); q.add_argument('--rationale', required=True)
        if name=='review-resolution': q.add_argument('--decision-id', required=True); q.add_argument('--disposition', choices=('accepted','revised'), required=True); q.add_argument('--summary', required=True)
        if name=='decision-report': q.add_argument('--decision-id', required=True); q.add_argument('--tradeoffs', required=True); q.add_argument('--delivery-cost', required=True); q.add_argument('--reversibility', required=True); q.add_argument('--unknowns', required=True)
        if name=='decision-resolution': q.add_argument('--decision-id', required=True); q.add_argument('--selected', required=True); q.add_argument('--owner', choices=('user','authorized-owner'), required=True); q.add_argument('--summary', required=True)
        if name=='outcome': q.add_argument('--summary', required=True); q.add_argument('--feedback', default=''); q.add_argument('--remaining-risk', default='')
    a=p.parse_args(); project=a.project.resolve()
    if not project.is_dir(): print('project path is missing',file=sys.stderr); return 2
    if a.cmd=='feedback-scan':
        source_paths=[]
        if a.root:
            feedback_root=a.root.resolve()
            if not feedback_root.is_dir(): print('feedback root is missing', file=sys.stderr); return 2
            source_paths.extend(path for path in feedback_root.rglob('*.md') if path.is_file() and 'archive' not in path.relative_to(feedback_root).parts)
            scan_root=str(feedback_root)
        elif a.registry:
            registry_path=a.registry.resolve()
            if not registry_path.is_file(): print('document registry is missing', file=sys.stderr); return 2
            try: registry_data=load(registry_path)
            except (OSError, json.JSONDecodeError) as exc: print(f'invalid document registry: {exc}', file=sys.stderr); return 2
            source_paths.extend(registry_sources(project, registry_path))
            scan_root=str(registry_path)
        else:
            print('feedback-scan needs --root or --registry', file=sys.stderr); return 2
        recorded=recorded_feedback_sources(project)
        pending=[]
        for source in sorted(set(source_paths)):
            key=(str(source), file_sha256(source))
            if key not in recorded: pending.append({'path':str(source),'sha256':key[1]})
        print(json.dumps({'root':scan_root,'pending':pending}, ensure_ascii=False, indent=2)); return 0
    if a.cmd=='begin':
        try: contract=load(a.contract)
        except (OSError, json.JSONDecodeError) as exc: print(f'invalid contract: {exc}',file=sys.stderr); return 2
        if not isinstance(contract, dict) or contract.get('schemaVersion') != 1 or not isinstance(contract.get('acceptance', []), list):
            print('invalid contract: expected schemaVersion 1 and acceptance list',file=sys.stderr); return 2
        errors = contract_errors(contract)
        if (project/'.agents/chohogi-document-registry.json').is_file() and not isinstance(contract.get('feedbackRegistry'), str):
            errors.append('projects with a document registry must declare feedbackRegistry in material contracts')
        if errors:
            print('invalid contract: ' + '; '.join(errors), file=sys.stderr); return 2
        folder=root(project,a.work_id)
        try: folder.mkdir(parents=True,exist_ok=False)
        except FileExistsError: print('work record already exists',file=sys.stderr); return 2
        state={'workId':a.work_id,'baseline':digest(project),'contract':contract,'artifacts':[],'checkpoints':[]}
        (folder/'contract.json').write_text(json.dumps(contract,indent=2,ensure_ascii=False),encoding='utf-8'); (folder/'state.json').write_text(json.dumps(state,indent=2),encoding='utf-8'); event(folder,{'event':'begin','baseline':state['baseline']}); return 0
    folder=root(project,a.work_id)
    if not (folder/'state.json').is_file(): print('work record is missing',file=sys.stderr); return 2
    state=load(folder/'state.json')
    if a.cmd=='handoff':
        stale=[issue for artifact in state['artifacts'] if (issue:=artifact_status(artifact))]
        if stale:
            print("registered artifact is missing or changed; handoff requires fresh evidence", file=sys.stderr)
            return 1
        history=events(folder)
        requested_ids={item.get('id') for item in state['contract'].get('requestedItems', []) if isinstance(item, dict)}
        resolved_scope={item.get('id') for item in history if item.get('event') == 'scope-item' and item.get('status') in {'implemented','deferred','excluded'}}
        open_scope=sorted(requested_ids-resolved_scope)
        decisions=[{"id": item["id"], "selected": item["selected"], "topic": item["topic"]} for item in history if item.get("event") == "decision"][-3:]
        checkpoint=state["checkpoints"][-1] if state["checkpoints"] else None
        handoff={
            "schemaVersion": 1,
            "workId": state["workId"],
            "baseline": state["baseline"],
            "objective": state["contract"].get("objective", ""),
            "openAcceptance": open_acceptance(state),
            "latestCheckpoint": checkpoint,
            "recentDecisions": decisions,
            "artifactRefs": [{key: artifact[key] for key in ("acceptanceId", "kind", "path", "sha256")} for artifact in state["artifacts"]],
            "nextBoundary": (f"resolve scope items: {', '.join(open_scope)}" if open_scope else "complete the first open acceptance item, or finalize when none remain"),
            "limits": "This projection excludes raw prompts, private reasoning, credentials, complete tool payloads, and provider-native state.",
        }
        event(folder, {"event":"handoff","workId":state["workId"],"openAcceptance":handoff["openAcceptance"]})
        print(json.dumps(handoff, ensure_ascii=False, indent=2))
        return 0
    if a.cmd=='checkpoint':
        item={'id':a.id,'summary':a.summary,'baseline':digest(project),'status':'pass'}; state['checkpoints'].append(item); (folder/'state.json').write_text(json.dumps(state,indent=2),encoding='utf-8'); event(folder,{'event':'checkpoint','id':a.id,'status':'pass'}); return 0
    if a.cmd=='resume':
        passed=[item for item in state['checkpoints'] if item.get('status')=='pass']
        if not passed: print('no passing checkpoint',file=sys.stderr); return 1
        if digest(project) != passed[-1]['baseline']:
            print('baseline changed since checkpoint; reconciliation required',file=sys.stderr); return 1
        print(json.dumps({'checkpoint':passed[-1]})); event(folder,{'event':'resume','checkpoint':passed[-1]['id']}); return 0
    if a.cmd=='fact':
        try: details=parse_json(a.details, 'details')
        except ValueError as exc: print(exc,file=sys.stderr); return 2
        event(folder, {'event':'fact','kind':a.kind,'summary':a.summary,'details':details}); return 0
    if a.cmd=='scope-item':
        requested={item.get('id') for item in state['contract'].get('requestedItems', []) if isinstance(item, dict)}
        if a.id not in requested: print('scope item is not declared in requestedItems', file=sys.stderr); return 2
        if any(item.get('event') == 'scope-item' and item.get('id') == a.id for item in events(folder)): print('scope item already resolved', file=sys.stderr); return 2
        if a.status in {'deferred','excluded'} and not a.reason.strip(): print(f'{a.status} scope item needs a reason', file=sys.stderr); return 2
        event(folder, {'event':'scope-item','id':a.id,'status':a.status,'summary':a.summary,'reason':a.reason.strip()}); return 0
    if a.cmd=='feedback':
        source=a.source.resolve()
        if not source.is_file(): print('feedback source is missing', file=sys.stderr); return 2
        if a.disposition == 'plan-updated' and not a.target.strip(): print('plan-updated feedback needs a target', file=sys.stderr); return 2
        if a.disposition in {'deferred', 'rejected', 'no-action'} and not a.reason.strip(): print(f'{a.disposition} feedback needs a reason', file=sys.stderr); return 2
        registry_path=project/'.agents/chohogi-document-registry.json'
        if registry_path.is_file():
            try: registry_data=load(registry_path)
            except (OSError, json.JSONDecodeError) as exc: print(f'invalid document registry: {exc}', file=sys.stderr); return 2
            declared_sources={str(path) for path in registry_sources(project, registry_path)}
            if str(source) not in declared_sources: print('feedback source is not an active declared registry source', file=sys.stderr); return 2
            if a.disposition == 'plan-updated' and a.target.strip() != str(registry_data.get('activeExecutionPlan', '')).strip():
                print('feedback target must be the declared active execution plan', file=sys.stderr); return 2
        event(folder, {'event':'feedback','source':str(source),'sha256':file_sha256(source),'summary':a.summary,'impact':a.impact,'disposition':a.disposition,'target':a.target.strip(),'reason':a.reason.strip()}); return 0
    if a.cmd=='prior-feedback':
        items=[]
        records=project/'docs/work-log/records'
        for candidate in sorted(records.iterdir() if records.is_dir() else []):
            if candidate == folder or not (candidate/'events.jsonl').is_file(): continue
            for item in events(candidate):
                if item.get('event') == 'outcome' and (item.get('feedback') or item.get('remainingRisk')):
                    items.append({'workId':candidate.name,'summary':item.get('summary',''),'feedback':item.get('feedback',''),'remainingRisk':item.get('remainingRisk',''),'at':item.get('at','')})
                if item.get('event') == 'feedback':
                    items.append({'workId':candidate.name,'summary':item.get('summary',''),'feedback':item.get('reason',''),'source':item.get('source',''),'sha256':item.get('sha256',''),'impact':item.get('impact',''),'disposition':item.get('disposition',''),'target':item.get('target',''),'at':item.get('at','')})
        print(json.dumps({'priorFeedback':items}, ensure_ascii=False)); return 0
    if a.cmd=='capability-map':
        try:
            findings=parse_json(a.findings, 'findings'); prior_feedback=parse_json(a.prior_feedback, 'prior feedback')
            if not isinstance(findings, list) or not isinstance(prior_feedback, list): raise ValueError('findings and prior feedback must be JSON lists')
        except ValueError as exc: print(exc,file=sys.stderr); return 2
        if capability_map_event(folder, a.id): print('capability map already exists',file=sys.stderr); return 2
        event(folder, {'event':'capability-map','id':a.id,'scope':a.scope,'findings':findings,'priorFeedback':prior_feedback}); return 0
    if a.cmd=='decision':
        try:
            observations=parse_json(a.observations, 'observations'); options=parse_json(a.options, 'options'); considered=parse_json(a.capabilities_considered, 'capabilities considered')
            if not isinstance(observations, list) or not isinstance(options, list) or not isinstance(considered, list): raise ValueError('observations, options, and capabilities considered must be JSON lists')
            if (a.review_required or a.requires_user_decision) and (not a.capability_map_id or not considered): raise ValueError('review-required or user-decision request needs a capability map and non-empty capabilities considered')
            if a.capability_map_id and not capability_map_event(folder, a.capability_map_id): raise ValueError('capability map is missing')
        except ValueError as exc: print(exc,file=sys.stderr); return 2
        item={'id':a.id,'topic':a.topic,'observations':observations,'options':options,'selected':a.selected,'rationale':a.rationale,'reviewTrigger':a.review_trigger,'reviewRequired':a.review_required,'requiresUserDecision':a.requires_user_decision,'capabilityMapId':a.capability_map_id,'capabilitiesConsidered':considered}
        event(folder, {'event':'decision', **item}); return 0
    if a.cmd=='review-request':
        decision=decision_event(folder, a.decision_id)
        if not decision: print('decision is missing',file=sys.stderr); return 2
        capability_map=capability_map_event(folder, decision.get('capabilityMapId')) if decision.get('capabilityMapId') else None
        packet={'decision': {key: decision[key] for key in ('id','topic','observations','options','selected','rationale','reviewTrigger','reviewRequired','requiresUserDecision','capabilityMapId','capabilitiesConsidered')}, 'capabilityMap': capability_map}
        event(folder, {'event':'review-request','decisionId':a.decision_id}); print(json.dumps(packet, ensure_ascii=False)); return 0
    if a.cmd=='review-response':
        if not decision_event(folder, a.decision_id): print('decision is missing',file=sys.stderr); return 2
        try:
            findings=parse_json(a.findings, 'findings')
            if not isinstance(findings, list): raise ValueError('findings must be a JSON list')
        except ValueError as exc: print(exc,file=sys.stderr); return 2
        event(folder, {'event':'review-response','decisionId':a.decision_id,'verdict':a.verdict,'findings':findings,'rationale':a.rationale}); return 0
    if a.cmd=='review-resolution':
        history=events(folder)
        if not any(item.get('event') == 'review-response' and item.get('decisionId') == a.decision_id for item in history):
            print('review response is missing',file=sys.stderr); return 2
        event(folder, {'event':'review-resolution','decisionId':a.decision_id,'disposition':a.disposition,'summary':a.summary}); return 0
    if a.cmd=='decision-report':
        if not decision_event(folder, a.decision_id): print('decision is missing',file=sys.stderr); return 2
        try:
            tradeoffs=parse_json(a.tradeoffs, 'tradeoffs'); delivery_cost=parse_json(a.delivery_cost, 'delivery cost'); unknowns=parse_json(a.unknowns, 'unknowns')
            if not isinstance(tradeoffs, list) or not isinstance(delivery_cost, dict) or not isinstance(unknowns, list): raise ValueError('tradeoffs and unknowns must be JSON lists; delivery cost must be a JSON object')
        except ValueError as exc: print(exc,file=sys.stderr); return 2
        item={'event':'decision-report','decisionId':a.decision_id,'tradeoffs':tradeoffs,'deliveryCost':delivery_cost,'reversibility':a.reversibility,'unknowns':unknowns}
        event(folder, item); print(json.dumps(item, ensure_ascii=False)); return 0
    if a.cmd=='decision-resolution':
        history=events(folder)
        if not any(item.get('event') == 'decision-report' and item.get('decisionId') == a.decision_id for item in history):
            print('decision report is missing',file=sys.stderr); return 2
        event(folder, {'event':'decision-resolution','decisionId':a.decision_id,'selected':a.selected,'owner':a.owner,'summary':a.summary}); return 0
    if a.cmd=='outcome':
        event(folder, {'event':'outcome','summary':a.summary,'feedback':a.feedback,'remainingRisk':a.remaining_risk}); return 0
    if a.cmd=='review':
        print(json.dumps(review(folder), ensure_ascii=False, indent=2)); return 0
    if a.cmd=='artifact':
        if not a.path.is_file(): print('artifact path is missing',file=sys.stderr); return 2
        registered={'acceptanceId':a.acceptance_id,'kind':a.kind,'path':str(a.path.resolve()),'sha256':hashlib.sha256(a.path.read_bytes()).hexdigest(),'status':'pass'}
        state['artifacts'].append(registered); (folder/'state.json').write_text(json.dumps(state,indent=2),encoding='utf-8'); event(folder,{'event':'artifact',**registered}); return 0
    missing=[{"acceptanceId": item["id"], "kinds": item["kinds"]} for item in open_acceptance(state)]
    missing_consumers=missing_consumer_evidence(state)
    stale=[issue for artifact in state['artifacts'] if (issue:=artifact_status(artifact))]
    history=events(folder)
    required_reviews=[item['id'] for item in history if item.get('event') == 'decision' and item.get('reviewRequired')]
    resolved={item.get('decisionId') for item in history if item.get('event') == 'review-resolution' and item.get('disposition') in {'accepted','revised'}}
    unresolved_reviews=sorted(set(required_reviews)-resolved)
    user_decisions=[item['id'] for item in history if item.get('event') == 'decision' and item.get('requiresUserDecision')]
    user_resolved={item.get('decisionId') for item in history if item.get('event') == 'decision-resolution' and item.get('owner') in {'user','authorized-owner'}}
    unresolved_user_decisions=sorted(set(user_decisions)-user_resolved)
    requested_ids={item.get('id') for item in state['contract'].get('requestedItems', []) if isinstance(item, dict)}
    resolved_scope={item.get('id') for item in history if item.get('event') == 'scope-item' and item.get('status') in {'implemented','deferred','excluded'}}
    unresolved_scope=sorted(requested_ids-resolved_scope)
    pending_feedback=[]
    feedback_registry=state['contract'].get('feedbackRegistry')
    if isinstance(feedback_registry, str):
        registry_path=(project / feedback_registry).resolve()
        if registry_path.is_file():
            recorded=recorded_feedback_sources(project)
            pending_feedback=[str(source) for source in registry_sources(project, registry_path) if (str(source), file_sha256(source)) not in recorded]
        else:
            pending_feedback=[feedback_registry]
    report={'status':'pass' if not missing and not missing_consumers and not stale and not unresolved_reviews and not unresolved_user_decisions and not pending_feedback and not unresolved_scope else 'fail','missingArtifacts':missing,'missingConsumerEvidence':missing_consumers,'staleArtifacts':stale,'unresolvedDecisionReviews':unresolved_reviews,'unresolvedUserDecisions':unresolved_user_decisions,'pendingFeedback':pending_feedback,'unresolvedScopeItems':unresolved_scope}; (folder/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); event(folder,{'event':'finalize','status':report['status'],'staleArtifacts':stale,'missingConsumerEvidence':missing_consumers,'pendingFeedback':pending_feedback,'unresolvedScopeItems':unresolved_scope}); print(json.dumps(report)); return 0 if report['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
