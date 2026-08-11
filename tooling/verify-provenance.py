#!/usr/bin/env python3
"""Check that every active Chohogi leaf has a complete immutable provenance record."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ALLOWED = {'absorb-core', 'mirror-baseline', 'attach-specialist', 'provider', 'project-leaf', 'reject'}
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'assets/agents/genome_inheritance/xylem_provenance/provenance.json').read_text(encoding='utf-8'))
errors = []
assets = data.get('assets') if isinstance(data, dict) else None
if not isinstance(assets, list): errors.append('provenance assets must be a list')
else:
    records = {item.get('id'): item for item in assets if isinstance(item, dict)}
    skills = {p.parent.name for p in (root / 'assets/agents/leaves_capabilities').glob('*/SKILL.md')}
    if set(records) != skills: errors.append('provenance IDs must exactly cover xylem skills')
    for name, item in records.items():
        for key in ('adoption','origin','license','baseline_revision','local_delta','required_resources','trigger','non_trigger','owner','review_signal','retirement_condition'):
            if key not in item: errors.append(f'{name}: missing {key}')
        if item.get('adoption') not in ALLOWED: errors.append(f'{name}: invalid adoption')
        if not isinstance(item.get('origin'), str) or not item['origin'].startswith('https://'):
            errors.append(f'{name}: origin must be a concrete HTTPS URL')
        if not isinstance(item.get('baseline_revision'), str) or not re.fullmatch(r'[0-9a-f]{40}', item['baseline_revision']):
            errors.append(f'{name}: baseline_revision must be an immutable 40-character revision')
        if item.get('baseline_revision') in {'unpinned', 'unknown', 'unverified'}:
            errors.append(f'{name}: active provenance cannot be unpinned')
        if not isinstance(item.get('required_resources'), list): errors.append(f'{name}: required_resources must be a list')
        if not isinstance(item.get('review_signal'), list): errors.append(f'{name}: review_signal must be a list')
        for resource in item.get('required_resources', []):
            if not (root / 'assets/agents/leaves_capabilities' / name / resource).is_file(): errors.append(f'{name}: missing required resource {resource}')
if errors:
    print('Chohogi provenance verification: FAIL', file=sys.stderr); [print('- '+e, file=sys.stderr) for e in errors]; raise SystemExit(1)
print('Chohogi provenance verification: PASS')
