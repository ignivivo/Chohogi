# Third-party notices

## Superpowers

- Repository: https://github.com/obra/superpowers
- Revision studied: `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (release v6.4.2, 2026-09-25); skills also read from the v6.4.2 Codex plugin package
- Copyright (c) 2025 Jesse Vincent
- License: MIT (full text below)

Chohogi did not copy Superpowers files. Each asset below was written for Chohogi, in
Chohogi's structure and vocabulary, after studying the named Superpowers source. Some
wording and structure follow the source closely, so this notice covers those
portions.

| Chohogi asset | Built from Superpowers source |
| --- | --- |
| `skills/session-forensics/SKILL.md` | `skills/diagnosing-superpowers/` |
| `assets/runtime_entrypoint/AGENTS.md` — section "route·유지과정 진입을 생략하지 않는다" (red-flag table) | `skills/using-superpowers/SKILL.md` |
| `assets/agents/trunk_orchestration/task-loop.md` | `skills/executing-plans/SKILL.md`, `skills/subagent-driven-development/SKILL.md` |
| `assets/agents/trunk_orchestration/plan-authoring.md` | `skills/writing-plans/SKILL.md` |
| `assets/agents/trunk_orchestration/execution-allocation.md` — sections "위임 설명과 회수 뒤 통합" and the model-tier paragraph | `skills/dispatching-parallel-agents/SKILL.md`, `skills/subagent-driven-development/SKILL.md` (Model Selection) |
| `assets/agents/trunk_orchestration/branches_workflows/delivery.md` — test-first rules in step 6 | `skills/test-driven-development/SKILL.md` |
| same file — section "완료 주장 관문" | `skills/verification-before-completion/SKILL.md` |
| `assets/runtime_entrypoint/AGENTS.md` — completion-claim paragraph, and `assets/agents/trunk_orchestration/conductor.md` — direct-handling sentence | `skills/verification-before-completion/SKILL.md` |
| same file — section "검토 결과 수용" | `skills/receiving-code-review/SKILL.md` |
| same file — section "통합 종료" | `skills/finishing-a-development-branch/SKILL.md` |
| `assets/agents/trunk_orchestration/branches_workflows/debugging.md` — additions to steps 3–4 (one hypothesis, boundary instrumentation, three failed fixes) | `skills/systematic-debugging/SKILL.md` |
| `assets/agents/trunk_orchestration/branches_workflows/product-decision.md` — section for design work | `skills/brainstorming/SKILL.md` |
| `agents/critical-reviewer.md`, `assets/runtime_entrypoint/agents/critical-reviewer.toml` — review rules added 2026-09-29 | `skills/requesting-code-review/code-reviewer.md` |
| `agents/implementation-worker.md`, `assets/runtime_entrypoint/agents/implementation-worker.toml` — report contract added 2026-09-29 | `skills/subagent-driven-development/SKILL.md` |
| `assets/agents/trunk_orchestration/platform-tools/claude-tools.md`, `codex-tools.md` — workspace isolation rules | `skills/using-git-worktrees/SKILL.md` |
| `skills/homeostasis/references/skill-lifecycle.md` — section "Observe the failure before writing the skill" | `skills/writing-skills/SKILL.md` |
| `tooling/adherence-replay.py`, `assets/agents/trunk_orchestration/evaluation/adherence-scenarios.json`, `tooling/tests/test_adherence_replay.py` | `tests/claude-code/test-helpers.sh`, `tests/explicit-skill-requests/run-test.sh`, `tests/claude-code/test-worktree-native-preference.sh`, `tests/claude-code/test-subagent-driven-development-integration.sh` |

`assets/agents/genome_inheritance/xylem_provenance/provenance.json` records the same
origin for the reusable method `session-forensics`.

```text
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
