# 초호기 (初號機) / Chohogi

초호기는 Codex·Claude Code 작업을 위한 이식 가능한 단일 하네스다. 초호기는 workflow,
authority, skill lifecycle, 설치·발견, 검증 정책을 소유한다. 플러그인·MCP·인증·개인
설정은 필요할 때 호출하는 provider이지 초호기의 controller가 아니다.

초호기는 자기 자신을 각 실행 표면의 공식 로컬 플러그인 마켓플레이스로 배포한다.
copy-install 스크립트는 없다 — 정본 저장소가 곧 배포되는 자산이다.

## 빠른 시작

```bash
# Claude Code
claude plugin marketplace add <이 저장소 경로>
claude plugin install chohogi@chohogi-marketplace

# Codex
codex plugin marketplace add <이 저장소 경로>
codex plugin add chohogi@chohogi-marketplace
```

Claude Code는 플러그인의 `skills/`, `agents/`, `hooks/hooks.json`(전역 지침 주입)을 바로
노출한다. Codex는 플러그인의 `skills/`만 쓴다(hook은 아래처럼 끄고, 역할 슬롯은 없다). 전역
지침은 정본을 가리키는 링크로, 역할은 `config.toml`의 정본 경로 등록으로 연결한다(복사하지 않는다):

```bash
R=<이 저장소 경로>
ln -s $R/assets/runtime_entrypoint/AGENTS.md ~/.codex/AGENTS.md
ln -s $R/assets/agents ~/.agents/chohogi
```

역할은 링크가 아니라 `~/.codex/config.toml`에 정본 경로로 등록한다. `~/.codex/agents/`에 링크를
두면 역할 목록에는 보이지만 스폰이 거부된다.

```toml
[agents.critical_reviewer]
config_file = "<이 저장소 경로>/assets/runtime_entrypoint/agents/critical-reviewer.toml"

[agents.evidence_scout]
config_file = "<이 저장소 경로>/assets/runtime_entrypoint/agents/evidence-scout.toml"

[agents.implementation_worker]
config_file = "<이 저장소 경로>/assets/runtime_entrypoint/agents/implementation-worker.toml"

[agents.final_reviewer]
config_file = "<이 저장소 경로>/assets/runtime_entrypoint/agents/final-reviewer.toml"

[agents.debugger]
config_file = "<이 저장소 경로>/assets/runtime_entrypoint/agents/debugger.toml"
```

Codex 플러그인 매니페스트는 `"hooks": {}`로 `hooks/hooks.json` 자동 등록을 끈다. Codex의 전역
지침은 위 AGENTS.md 링크 하나로만 들어간다.

링크는 작업 트리를 바로 가리키지만, Codex의 플러그인 스킬은 마켓플레이스 root를 git 커밋
상태로 복사한 것이고 Claude Code는
심볼릭 링크를 세션 로드 시점에 따라간다 — **정본을 바꾼 뒤에는 반드시 커밋**해야
Codex 쪽에도 반영된다.

## 현재 구조

현재 기관, 호출 관계, active capability, verification coverage는 사람이 직접 갱신하는
문서가 아니라 source에서 생성한 [genome map](docs/chohogi/genome-map.md)으로 본다.
AI agent는 같은 내용의 `docs/chohogi/genome-map.graph.json`을 읽어 변경 영향 범위를
계산한다.

```bash
python3 tooling/genome_map.py build
python3 tooling/genome_map.py impact assets/agents/reusable_methods/security-and-hardening/SKILL.md
python3 tooling/genome_map.py check
python3 tooling/verify-security-boundary.py
```

## 운영 원칙

- conductor는 substantial 작업에서 하나의 workflow만 선택한다.
- capability와 provider는 선택된 workflow 뒤에만 사용하며 controller가 될 수 없다.
- `learning`은 확인된 실패의 최소 예방을 다루고, `homeostasis`는 초호기 자체의
  정책·수명주기·설치·발견·정합성을 다룬다.
- `security_immune_system`은 위험 신호를 코드 전 수용 조건으로 분류하고, 전 프로젝트가
  공유하는 scanner/CI gate protocol을 소유한다. 프로젝트별 scanner 설정은 adapter이지 leaf가 아니다.
- Homeostasis repair loop는 변경점의 영향 집합을 계산하고, 선언 대비 실제 상태를
  검사한 뒤 repair packet을 낸다. 수리와 재검증은 정상 권한 절차로 수행한다.

세부 계약은 `assets/agents/`에, 설치 대상 연결은 `manifest.json`에 있다.
