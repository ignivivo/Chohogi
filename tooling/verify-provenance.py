#!/usr/bin/env python3
"""Check that every Chohogi xylem skill has a bounded provenance record."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ALLOWED = {'absorb-core', 'mirror-baseline', 'attach-specialist', 'provider', 'project-leaf', 'reject'}
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'assets/agents/chohogi/xylem/provenance.json').read_text(encoding='utf-8'))
errors = []
assets = data.get('assets') if isinstance(data, dict) else None
if not isinstance(assets, list): errors.append('provenance assets must be a list')
else:
    records = {item.get('id'): item for item in assets if isinstance(item, dict)}
    skills = {p.parent.name for p in (root / 'assets/agents/skills').glob('*/SKILL.md') if p.parent.name not in {'learning', 'homeostasis'}}
    if set(records) != skills: errors.append('provenance IDs must exactly cover xylem skills')
    for name, item in records.items():
        for key in ('adoption','origin','license','baseline_revision','local_delta','required_resources','review_when'):
            if key not in item: errors.append(f'{name}: missing {key}')
        if item.get('adoption') not in ALLOWED: errors.append(f'{name}: invalid adoption')
        if not isinstance(item.get('required_resources'), list): errors.append(f'{name}: required_resources must be a list')
        for resource in item.get('required_resources', []):
            if not (root / 'assets/agents/skills' / name / resource).is_file(): errors.append(f'{name}: missing required resource {resource}')
if errors:
    print('Chohogi provenance verification: FAIL', file=sys.stderr); [print('- '+e, file=sys.stderr) for e in errors]; raise SystemExit(1)
print('Chohogi provenance verification: PASS')
