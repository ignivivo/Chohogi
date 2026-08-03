#!/usr/bin/env python3
"""Validate privacy-safe Chohogi replay result JSON files."""
from __future__ import annotations
import json, sys
from pathlib import Path
REQUIRED={'schemaVersion','fixtureId','profile','model','effort','toolCondition','repoCondition','outcomes','evidenceRef'}
OUTCOMES={'flowCorrect','artifactsComplete','externalController','executionChoicePrompt','unnecessaryEscalation','persistentChangeWithoutAuthority','reworkCount'}
BOOLEAN_OUTCOMES=OUTCOMES-{'reworkCount'}
def main() -> int:
 p=Path(sys.argv[1]) if len(sys.argv)==2 else None
 if not p or not p.is_file(): print('Usage: validate-replay-result.py <result.json>',file=sys.stderr); return 2
 d=json.loads(p.read_text(encoding='utf-8')); e=[]
 if set(d) - (REQUIRED|{'cost','tokens','notes'}) : e.append('unknown top-level field')
 if not REQUIRED <= set(d): e.append('missing required field')
 if d.get('schemaVersion') != 1: e.append('schemaVersion must be 1')
 if d.get('profile') not in {'baseline','chohogi'}: e.append('invalid profile')
 if not isinstance(d.get('outcomes'),dict) or set(d.get('outcomes',{})) != OUTCOMES: e.append('outcomes must exactly match schema')
 if isinstance(d.get('outcomes'),dict) and type(d['outcomes'].get('reworkCount')) is not int: e.append('reworkCount must be integer')
 if isinstance(d.get('outcomes'),dict):
  for name in BOOLEAN_OUTCOMES:
   if not isinstance(d['outcomes'].get(name),bool): e.append(f'{name} must be boolean')
 for field in REQUIRED-{'schemaVersion','outcomes'}:
  if not isinstance(d.get(field),str) or not d[field].strip(): e.append(f'{field} must be a non-empty string')
 if not isinstance(d.get('evidenceRef'),str) or not d['evidenceRef'].strip(): e.append('evidenceRef required')
 if e: print('Replay result: FAIL\n- '+'\n- '.join(e),file=sys.stderr); return 1
 print('Replay result: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
