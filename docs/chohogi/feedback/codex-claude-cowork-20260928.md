# Codex·Claude 공동작업 기록 (cowork)

## 0. 이 문서를 읽는 AI를 위한 규약

- 1차 독자는 이 저장소에서 이어서 일할 **AI 세션(Codex·Claude Code)**이다. 사람 가독성보다 다음
  세션이 같은 조사를 반복하지 않고, 정정된 결론을 다시 믿지 않고, 열린 항목을 이어받는 것이 목적이다.
- 권위 순서: 실행 기록(`docs/work-log/records/<work-id>/events.jsonl`, `verification.json`) > 코드·계약
  파일 > 이 문서. 이 문서는 색인과 경위다. 충돌하면 기록과 코드를 믿고 이 문서를 고친다.
- 식별자는 안정적이다. 검토 결과는 `F<n>`, 기준은 `C<n>`, 정정은 `#<n>`으로 부르고 번호를 재사용하지
  않는다. 상태 값은 `fixed | open | candidate | user-action | not-started | partial | done`만 쓴다.
- "검증됨"은 이번 기간에 명령을 새로 실행하거나 새 세션 transcript로 확인한 것만 뜻한다. 날짜·호스트
  버전을 붙인다. 문서 서술·목록 노출·설치 성공은 증거가 아니다(2장 교훈).
- 갱신 방법: 1장 JSON은 현재 사실로 덮어쓴다. 2장 정정표와 3장 경위는 추가만 한다. 8장 검토안은 항목
  상태를 바꾸고 근거 기록을 붙인다.
- 문서 역할: `feedback-source`(`.agents/chohogi-document-registry.json`). 활성 실행 계획이 아니며
  실행 지시도 아니다. 8장의 "예정"은 권고 순서이고, 각 항목은 착수할 때 conductor로 route를 다시 고른다.
- 범위: 2026-09-28 ~ 2026-09-30. 커밋 `acf4012` ~ `934d20a`(브랜치 `agent/chohogi-v2-integrity`)와
  2026-09-30 Claude Code 세션(Opus 5.5)의 **미커밋** 작업 트리 변경 4건(7장).

## 1. 지금 믿어도 되는 사실 (2026-09-30 기준)

```json
{
  "schemaVersion": 3,
  "distribution": {
    "method": "각 호스트의 로컬 플러그인 마켓플레이스로 이 저장소를 등록한다. copy-install(install.sh)은 폐기됐다.",
    "claude": "플러그인의 skills/, agents/, hooks/hooks.json을 쓴다. SessionStart hook이 AGENTS.md를 플러그인 루트 경로와 함께 주입한다.",
    "codex": "플러그인의 skills/만 쓴다. .codex-plugin/plugin.json은 \"hooks\": {}로 hook 자동 등록을 끈다. 전역 지침은 ~/.codex/AGENTS.md → assets/runtime_entrypoint/AGENTS.md, ~/.agents/chohogi → assets/agents 심볼릭 링크로 읽는다.",
    "commitRule": "Codex는 마켓플레이스 root를 git 커밋 상태로 복사해 스킬을 읽는다(캐시는 심볼릭 링크를 복사하지 않음). 정본을 바꾸면 커밋해야 Codex 스킬에 반영된다. 링크로 읽는 AGENTS.md는 작업 트리를 바로 본다."
  },
  "roles": {
    "set": ["evidence-scout", "implementation-worker", "critical-reviewer", "final-reviewer", "debugger"],
    "source": "assets/runtime_entrypoint/agents/<role>.toml이 정본, agents/<role>.md는 Claude용 미러. 본문·설명 일치는 tooling/tests/test_role_definitions.py가 강제한다.",
    "profileRoleToFile": {"scout": "evidence-scout", "implementer": "implementation-worker", "task-reviewer": "critical-reviewer", "final-reviewer": "final-reviewer", "debugger": "debugger"},
    "claude": "agents/*.md frontmatter의 model(정확한 id)과 effort(low|medium|high|xhigh|max)가 역할별로 실제 적용된다. 플러그인 전역 값이다. Agent 도구의 model 인자(별칭만)는 모델만 덮어쓰고 강도는 못 바꾼다. Haiku는 effort를 받지 않는다.",
    "claudeCurrentPlacement": {"evidence-scout": "claude-haiku-4-5 / (없음)", "implementation-worker": "claude-sonnet-5-5 / medium", "critical-reviewer": "claude-sonnet-5-5 / high", "final-reviewer": "claude-opus-5-5 / high", "debugger": "claude-opus-5-5 / high"},
    "codex": "~/.codex/config.toml의 [agents.<이름>] config_file로 정본 TOML을 가리켜야 스폰된다(README). 5개 역할 모두 사용자 승인 대기로 미등록. 강도는 spawn_agent의 reasoning_effort로 호출마다 준다.",
    "codexCurrentPlacement": {"scout": "gpt-5.6-luna / low", "implementer": "gpt-5.6-luna / medium", "task-reviewer": "gpt-5.6-luna / medium", "final-reviewer": "gpt-6-sol / medium", "debugger": "gpt-6-sol / medium"},
    "codexPlacementRationale": "사용자 결정: GPT-6를 쓴다. Luna만 5.6으로 내린 이유는 Luna의 장점이 속도인데 GPT-6 Luna가 느리게 관측됐기 때문이다(2026-09-30). Sol 역할은 GPT-6 유지."
  },
  "models": {
    "start": "역할은 모델을 지정하지 않으면 Claude는 역할 파일 frontmatter 값, Codex는 세션 모델을 쓴다.",
    "savedProfile": ".agents/chohogi-model-profile.json의 hosts.claude / hosts.codex(둘 다 사용자 확정, 2026-09-30). model-policy.py profile로 검증한다. 이 파일은 아직 git 미추적이다.",
    "claudeCatalog": "unknown. Claude Code 2.1.284에는 모델 목록 조회 명령이 없다. 사용자가 모델 선택 화면에서 본 목록(Opus 5.5, Sonnet 5.5, Fable 5.1, Haiku 4.5, Sonnet 5, Opus 5)은 user-reported correction으로만 기록한다.",
    "claudeAlias": "별칭(sonnet/opus/haiku/fable)은 그 계열의 최신 모델로 해석된다(CLI --model 도움말). 이전 세대(claude-sonnet-5, claude-opus-5)는 별칭으로 고를 수 없다. 매핑은 model-recommendations.json의 deliveryAlias.",
    "card": "추천·저장은 정확한 모델 id로 한다. card는 역할 파일 값과 비교해 '역할 파일 값 그대로(model 인자 생략)' 또는 불일치 경고를 보인다. 저장된 배치에 없는 역할은 '미저장 → 추천'으로 보여 사용자가 고르게 하고, 답 전까지 Codex는 세션 모델, Claude는 역할 파일 값으로 진행한다. 배치에 빠진 역할이 있으면 저장된 배치가 있어도 card를 실행한다.",
    "nonBlocking": "모델 선택은 방지턱이 아니다. card는 같은 턴의 보고 텍스트로만 내고, 턴을 멈추는 질문 도구(AskUserQuestion, request_user_input)로 묻거나 답을 기다리며 턴을 끝내지 않는다. 사용자가 모델부터 정하겠다고 명시한 경우만 예외.",
    "upgrade": "저장된 배치(없으면 세션 모델)보다 올리는 배정만 사용자 확인을 받는다."
  },
  "documents": {
    "activeExecutionPlan": null,
    "rule": "활성 계획은 최대 하나. 소유 기록이 finalize되면 계획을 historical로 바꾸고 null로 둔다. verify-project-document-registry.py가 finalize된 기록을 active로 선언하면 실패시킨다."
  },
  "alwaysInjectedRules": [
    "route 선택: conductor가 direct / defer / product-decision / delivery / debugging 중 하나를 고른다",
    "테스트 우선: 제품 코드 동작 변경은 실패 테스트부터. 예외는 사용자가 정한다",
    "완료 주장 관문: 완료·통과를 말하기 전에 증명 명령을 이번 턴에 새로 실행한다",
    "모델: 역할 배정이 임박했거나 조언 요청 시에만 card, 비차단",
    "route·유지과정 진입 생략 금지 표(red flags)"
  ],
  "evidenceTool": "tooling/adherence-replay.py가 실제 claude -p / codex exec 세션을 돌려 도구 호출 순서·바뀐 파일·사후 검사로 규칙 준수를 판정한다. 모델은 정확한 id로 고정한다. headless 실행은 대화형 질문 대기를 재현하지 못한다."
}
```

## 2. 틀렸다가 정정된 주장

다른 세션이 아래의 "초기 주장"을 다시 믿지 않도록 남긴다.

| # | 초기 주장 | 사실 | 어떻게 드러났나 | 정정 커밋·기록 |
|---|---|---|---|---|
| 1 | 프로젝트 루트에 `CLAUDE.md`·`.agents/skills/`가 없으니 project leaf가 구현되지 않았다 | `docs/chohogi/`, `docs/work-log/records/`에 이미 구현·축적되어 있었다 | 기존 문서를 읽지 않고 루트만 봤다 | 이 문서 초판(2026-09-28) |
| 2 | superpowers 폴더는 초호기 결함일 수 있다 | 외부 플러그인(diagnosing-superpowers)의 산출 경로였다 | `docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md`, 원본 소스 확인 | 초판, `fbbbad1` |
| 3 | diagnosing-superpowers 소스는 볼 수 없다(컴파일됨) | 로컬 플러그인 캐시에 평문 Markdown으로 있었다 | 사용자 지적 후 캐시 확인 | `642d02b` |
| 4 | SessionStart hook이 두 호스트 모두에 지침을 주입한다 | Codex는 플러그인 hook을 신뢰 승인 전에는 건너뛴다 | `codex exec` 세션 기록에 hook 출력 없음 | `af54e01` |
| 5 | Codex는 플러그인 hook을 아예 실행하지 않는다 | 매니페스트에 `hooks` 필드가 없으면 자동 등록하고, 신뢰 승인 뒤에는 실행한다 | `--dangerously-bypass-hook-trust`로 재현 | `2372be0` |
| 6 | Codex 역할은 `~/.codex/agents/` 심볼릭 링크로 연결되고 검증됐다 | 목록에만 뜨고 스폰은 거부된다 | 실제 스폰 시험 | `2372be0` |
| 7 | Codex에서 `fork_turns: all`이면 `agent_type`이 거부된다 | 거부 원인은 링크였다 | 역할 파일을 일반 파일·링크·`config_file`로 나눠 비교 | `2372be0` |
| 8 | Claude가 자기 세션 모델을 잘못 적었다 | `--model sonnet` 별칭이 날짜마다 다른 모델로 해석됐다 | 세션 `init` 이벤트 확인 | `2a93ae4`, `HOM-20260930-replay-model-pinning` |
| 9 | 테스트 우선 개선(Claude 0/2 → 2/2)은 규칙 효과다 | 날짜 간 모델이 바뀌어 교란됐다. 고정 재실행으로 다시 확인했다 | #8 조사 중 | `2a93ae4` |
| 10 | layout-v2 계획이 없는 스크립트(`verify-manifest-registry.py` 등)를 가리키니 결함이다 | 그 계획은 registry에 `historical`로 등록된 역사 문서다. 결함 아님 | registry 대조 | `DBG-20260930-integrity-audit` |
| 11 | Claude 모델 선택지는 `sonnet`·`opus`·`haiku`·`fable` 네 개다 | 그것은 `Agent` 도구 **인자의 허용값**이지 모델 목록이 아니다. 선택 화면에는 6개 모델이 따로 있다 | 사용자 스크린샷, 코드 추적 | `HOM-20260930-integrity-repair` |
| 12 | `sonnet` 별칭은 Sonnet 5와 5.5 사이에서 모호하다 | 별칭은 항상 그 계열의 **최신**이다. 이전 세대는 별칭으로 고를 수 없다 | CLI `--model` 도움말 | 같은 기록 |
| 13 | Claude는 역할별 추론 강도를 지정할 수 없다(`not-selectable`) | 역할 파일 frontmatter `effort`가 역할별로 적용된다. 인자에 없다는 것만 보고 능력이 없다고 판단한 오류 | 바이너리 검증 코드 → `claude -p` 탐침 transcript | `HOM-20260930-claude-role-effort` |
| 14 | 역할 본문의 `${CLAUDE_EFFORT}`로 강도를 관측할 수 있다 | 역할 본문에서는 치환되지 않는다. 첫 탐침의 `EFFORT=60`은 무의미한 값이었다 | 두 번째 탐침에서 문자 그대로 반환 | 같은 기록 |

교훈: 이름이 목록에 보이는 것, 설치 명령이 성공한 것, 문서에 적힌 것은 동작 증거가 아니다. 또한
**전달 수단(도구 인자)의 제약을 능력 자체의 제약으로 읽지 않는다**(#11, #13). 새 세션을 실제로 돌려
transcript에서 확인한 것만 "검증됨"으로 적는다.

## 3. 작업 경위

각 단계는 문제 → 원인 → 의도 → 해결 → 전후 → 검증 → 커밋 순서다.

### 3.1 Superpowers 흔적과 흡수 원칙 위반 (`acf4012`)

- **문제:** 리뷰·피드백 작업 때마다 superpowers 폴더가 생겼다. 사용자는 초호기의 검사 능력을 믿을 수
  없다고 했다.
- **원인:** (1) 초호기 활성 자산이 흡수 원본의 이름을 부르고 있었다. (2) 외부 플러그인이 설치되어 있었고,
  그 플러그인이 만든 계획 문서의 `REQUIRED SUB-SKILL: superpowers:...` 지시를 다음 세션이 따랐다.
  (3) homeostasis 스킬 Method에 execution record 연결이 없어 이 세션 작업 자체가 기록되지 않았다.
  (4) install.sh가 learning/homeostasis를 `~/.agents/skills/`에만 설치해 Claude Code가 이 스킬들을
  발견하지 못했다.
- **해결(당시):** 원본 이름 제거, 명시적 금지 문단, 이름 스캐너, `session-forensics` 신설, homeostasis
  Method에 execution record 단계 연결, `platform-tools/{claude,codex}-tools.md` 신설.
- **이후:** 금지 문단과 스캐너는 3.6에서 "차단은 잘못된 접근"이라는 사용자 판단으로 제거됐다.

### 3.2 설치 구조: install.sh → 플러그인 (`acf4012`, `4ef16dc`, `dc79e49`, `7c0f55a`)

- **문제:** install.sh가 `.claude/skills/`를 건너뛰고, 역방향 링크를 링크째 복사하고, 설치본과 정본이
  갈라졌다.
- **발견:** Codex는 플러그인 캐시로 복사할 때 심볼릭 링크를 따라가지 않는다. Claude Code는 로드 시점에
  링크를 따라간다.
- **해결:** 정본 스킬 위치를 저장소 루트 `skills/`로 옮기고 옛 위치를 역방향 링크로 바꿨다(`dc79e49`).
  install.sh와 부속 도구를 전부 삭제하고 `manifest.json`을 `pluginSlot` 기준으로 재설계했다(`7c0f55a`).
- **남은 오해:** "hook이 두 호스트 모두에 적용된다"고 적었으나 Codex에 대해서는 틀렸다(2장 #4, #5).

### 3.3 역할 노출 (`1b793dd`)

- Claude Code 플러그인의 `agents/` 슬롯에 `critical-reviewer`, `evidence-scout`, `implementation-worker`를
  추가했다(Codex TOML이 정본이고 `.md`는 형식이 달라 링크가 아닌 사본). 3.13에서 5개로 늘었다.

### 3.4 스킬 진입 강제 규칙 (`6a79851`)

- 세션이 homeostasis·learning 파일 경로를 알면서도 정식으로 Method를 따르지 않아, AGENTS.md에 "route·유지과정
  진입을 생략하지 않는다" 표를 넣었다(매 세션 주입).

### 3.5 전수조사 5건 (`de26aec`, `642d02b`)

| 발견 | 조치 |
|---|---|
| `verify-provenance.py` 실패: `session-forensics`가 provenance에 미등록 | 등록 |
| 폐기된 설치 구조를 설계로 규정한 2026-08-11 설계 문서가 registry에서 `active` | `historical`로 재분류, 배너 추가 |
| 같은 날짜 계획 문서의 내부 배너가 "approved" | Historical 배너로 동기화 |
| 이름 스캐너가 `.claude/worktrees/`를 스캔 | 제외 목록 추가(이후 스캐너 자체 삭제) |
| `provenance.json`과 `index_registry.yaml`의 관계가 문서에 없음 | README에 역할 구분 명시 |

### 3.6 차단 → 초호기화 (`fbbbad1`, `e9ec1ec`, `2661eba`)

- **사용자 판단:** "남의 장기를 그대로 이식하면 면역반응이 일어난다. 차단이 아니라 초호기 조직으로 바꿔
  장착해야 한다."
- **해결:** 금지 문단과 이름 스캐너를 삭제하고, 원본 15개 스킬의 기능을 소유 기관별로 다시 만들었다
  (`HOM-20260929-method-naturalization`). 대응표는 `THIRD_PARTY_NOTICES.md`에 있다.

### 3.7 옛 사본 제거, Codex 연결, 준수 검사기, 완료 관문 전역화 (`af54e01`, `eb225e7`)

- 옛 install.sh 사본을 `~/.chohogi-legacy-install-20260929/`로 옮겼다. `tooling/adherence-replay.py`를
  만들었다. 두 호스트 모두 테스트를 돌리지 않고 완료를 말한 것을 발견해 완료 관문을 AGENTS.md와
  conductor 직접 처리 문장으로 올렸다.

### 3.8 테스트 우선을 항상 (`4d016ce`, `ad7b491`)

- 규칙이 조건부라 모델이 작은 작업을 예외로 판단했다(0/4). 사용자 결정으로 "항상"으로 바꿨다.
  검증: Claude 2/2, Codex 2/2.

### 3.9 모델: 확인 후 출발 → 세션 모델로 출발 (`2372be0`, `36f4b5a`)

- Codex가 모델 확인 규칙에 걸려 질문만 보내고 멈췄다. 세션 모델로 출발하고 비차단 카드로 추천,
  `.agents/chohogi-model-profile.json`에 저장하도록 바꿨다.

### 3.10 모델 별칭 교란 정정 (`2a93ae4`, `cd126dc`)

- replay 도구에 넘긴 `sonnet` 별칭이 날짜마다 다른 모델로 해석되어 비교가 섞였다. Claude 별칭을
  거부하고 요청 모델과 실제 모델을 결과에 함께 남긴다.

### 3.11 카드 비차단 범위 축소 (`934d20a`, Codex 세션)

- **문제:** 모델 선택이 원래 지시의 방지턱이 된다(사용자 보고).
- **해결:** 카드는 실제 역할 배정 직전이나 모델 조언 요청 때만. 위임 없는 작업에는 카드 없음. 답은 저장 후
  원래 작업 재개, 완료된 작업은 다시 열지 않음.
- **검증:** 정적 검증기만(`HOM-20260930-model-card-nonblocking`). live replay 없음.

### 3.12 정합성 전수 점검과 결함 2건 수리 (미커밋, Claude 세션)

- **기록:** `DBG-20260930-integrity-audit`(조사), `HOM-20260930-integrity-repair`(수리).
- **방법:** 8장 C1의 A층(정의↔존재) 전수 교차참조를 스크립트로 돌리고 문서 권위(active/historical)로
  분류했다. 이후 진입·위임·기록·환류·모델 체인을 추적했다.
- **F1(수리):** registry가 이미 finalize된 계획(`2026-09-23-observability-closure.md`)을 활성으로 선언한
  채 PASS였다. 원인은 검증기가 "활성 계획 정확히 1개"를 강제해 "없음"을 표현할 수 없던 것.
  `activeExecutionPlan: null` 허용, 활성 계획의 `executionRecord`와 active 기록의 finalize 교차검사를 추가했다.
  고친 검증기가 실제 registry의 불일치를 즉시 잡았고, registry를 historical로 고친 뒤 PASS.
- **F5(수리):** Claude 카드가 `Agent` 도구 별칭 4개를 모델 목록으로 썼다(2장 #11, #12). 추천·profile을 정확한
  id로, 카탈로그 `unknown`, 전달용 `deliveryAlias` 매핑, override 표시를 추가했다.
- **사용자 결정:** Claude 역할 배치 "비용 절감안"(scout Haiku 4.5, 나머지 Sonnet 5.5/Opus 5.5).

### 3.13 Claude 역할별 모델·추론 강도 (미커밋)

- **기록:** `HOM-20260930-claude-role-effort`.
- **문제:** 카드가 Claude 역할 강도를 `not-selectable`로 표시했다(2장 #13). 사용자가 "다른 하네스는 된다"고 지적.
- **근거:** Claude Code 2.1.284 바이너리가 플러그인 역할 파일의 `effort`를 검증한다. `claude -p` 탐침(약 $0.13):
  부모 `high`, frontmatter `low`/`max` 역할의 transcript가 각각 `low`/`max`로 기록. 실제 초호기 플러그인
  소비자 확인(약 $0.12): 부모 `low`에서 `chohogi:debugger` = `claude-opus-5-5`/`high`,
  `chohogi:implementation-worker` = `claude-sonnet-5-5`/`medium`.
  관측 위치: `~/.claude/projects/<cwd-slug>/<session>/subagents/agent-*.jsonl`의 `"effort"`, `*.meta.json`의 `agentType`.
- **해결(사용자 결정: 5개 분리, 표준 강도):** `final-reviewer`, `debugger` 역할 신설(TOML 정본 + md 미러),
  frontmatter에 model/effort. 역할 본문의 "모델·강도를 정하지 않는다" 문장을 호스트별 설명으로 교체.
  미러 일치 테스트 신설, replay의 Codex 역할 등록을 하드코딩에서 디렉토리 기반으로 변경.

### 3.14 모델 선택 방지턱 제거 — Claude 쪽 (미커밋)

- **기록:** `HOM-20260930-model-choice-no-speedbump`.
- **문제:** 3.11은 공통 문장만 바꿨다. Claude에서 남은 차단 경로는 턴을 멈추는 질문 도구(`AskUserQuestion`)다.
  이번 세션도 모델 배치를 그 도구로 물었다(사용자가 먼저 요청한 경우였음).
- **해결:** AGENTS.md·`model-policy.md`·`claude-tools.md`에 "card는 같은 턴 텍스트로만, 질문 도구 금지, 사용자가
  모델부터 정하겠다고 한 경우만 예외" 추가, red-flag 행 추가. `verify-model-policy.py` 필수 문구로 고정.
  replay에 `forbidden-tool` 단언 종류와 `no-blocking-model-question` 단언 추가.
- **한계:** headless replay는 대화형 대기를 재현하지 못한다. 실제 대화 관측이 남아 있다(F14).

### 3.15 부분 저장 profile (미커밋)

- **기록:** `HOM-20260930-profile-gaps`.
- **문제:** 15:41 Codex 세션이 사용자 요청("GPT-6가 느리니 6 luna 대신 5.6 luna")을 GPT-6 Luna가 추천된 역할에만
  적용해 final-reviewer·debugger가 profile에 없었다. 빠진 역할은 세션 모델로 조용히 돌았고 다시 추천되지도 않았다.
- **사용자 결정:** GPT-6를 쓴다. Luna만 속도 때문에 5.6. final-reviewer·debugger는 `gpt-6-sol / medium`.
- **해결:** card가 빠진 역할을 "미저장 → 추천"으로 보여 사용자가 고르게 함(비차단, 답 전 대체값 명시).
  AGENTS.md·`model-policy.md`에 "배치에 빠진 역할이 있으면 card 실행" 추가. 테스트 먼저.

## 4. 두 호스트 차이 (실측 기준)

| 항목 | Claude Code (2.1.284) | Codex (codex-cli 0.155.0-alpha.16.3) |
|---|---|---|
| 전역 지침 | 플러그인 SessionStart hook | `~/.codex/AGENTS.md` 링크. 플러그인 hook은 `"hooks": {}`로 끔 |
| 스킬 | 플러그인 `skills/`(`chohogi:*`) | 플러그인 캐시(커밋 상태 복사)의 `skills/`. 링크는 따라가지 않음 |
| 역할 | 플러그인 `agents/` → `chohogi:<role>` 5종 | `config.toml`의 `config_file`(미등록). `~/.codex/agents` 링크는 스폰 거부 |
| 위임 도구 | `Agent`(`subagent_type`, `model` 별칭만), `SendMessage`, `TaskStop` | `spawn_agent`(`agent_type`, `model`, `reasoning_effort`, `fork_turns`) 등 |
| 역할별 모델 | 역할 파일 frontmatter `model`(정확한 id, 검증됨). 인자는 별칭=계열 최신 | `model` 인자 |
| 역할별 강도 | 역할 파일 frontmatter `effort`(검증됨). 플러그인 전역, 호출마다 변경 불가 | `reasoning_effort`. `model`만 주면 강도가 그 모델 기본값으로 바뀜 |
| 모델 목록 조회 | 없음(`unknown`, 사용자 보고로만) | `codex debug models`(`tooling/model-catalog.py codex`) |
| 차단형 질문 도구 | `AskUserQuestion` — 모델 선택에 쓰지 않음 | `request_user_input` — 모델 선택에 쓰지 않음 |
| 세션 기록 | `claude -p --output-format stream-json` + `~/.claude/projects/.../subagents/` | `codex exec --json` + `~/.codex/sessions/.../rollout-*.jsonl` |

## 5. 열린 항목

8장 검토안의 `open`·`user-action`·`candidate` 항목이 열린 항목의 정본이다. 8장에 없는 이전 항목:

| 항목 | 상태 | 담당·조건 |
|---|---|---|
| Sazu의 `.agents/chohogi-external-capabilities.json` 부재 | open | Sazu 저장소가 할 일. 초호기 쪽에는 외부 specialist 사용을 감지하는 자동 트리거가 없음 |
| 계획 전제가 사용자에 의해 부정될 때 계획 재검토 트리거 | open | `sazu-source-first-divergence.md:121-124`. route 미선택 |
| 작업 중 자동 로깅(PostToolUse) | not-started | 논의만 함 |
| Codex 기준선(초호기 없음) replay | open | Codex가 `~/.codex/AGENTS.md`를 끄는 옵션이 없음 |

## 6. 두 호스트 공통 행동 지침

1. 진입 시 `.agents/chohogi-document-registry.json`(현재 활성 계획 없음)과 이 문서의 0·1·2·8장을 먼저 본다.
2. 목록에 보이는 것, 설치 성공, 문서 서술을 동작 증거로 쓰지 않는다. 새 세션 실행과 transcript로
   확인한 것만 "검증됨"으로 적고, 날짜와 호스트 버전을 붙인다.
3. 정본을 바꾸면 커밋한다. 커밋하지 않으면 Codex의 플러그인 스킬은 옛 내용을 본다.
4. 외부 방법을 들일 때는 이름으로 막지 말고, 기능을 소유 기관에 초호기 어휘로 다시 만든다.
5. 규칙이 지켜지는지 의심되면 `tooling/adherence-replay.py`로 시나리오를 돌린다. 모델은 정확한 id로 고정한다.
6. 판정이 이상하면 결론을 내기 전에 transcript를 직접 읽는다.
7. 개인 설정(`config.toml`, `settings.json`)과 홈 디렉토리 파일은 사용자 승인 없이 바꾸지 않는다.
8. **도구 인자의 허용값을 능력·모델 목록으로 읽지 않는다.** 능력이 없다고 적기 전에 설정 파일·런타임
   바이너리·실제 세션으로 다른 전달 경로를 확인한다(2장 #11, #13).
9. **모델 선택은 방지턱이 아니다.** 추천은 적절한 출발점이면 되고 선택은 사용자 몫이다. 지시받은 작업은
   같은 턴에 진행하고 card는 텍스트로 붙인다. 질문 도구로 턴을 멈추지 않는다.
10. 다른 세션이 동시에 커밋할 수 있다(3.11은 3.12 작업 도중 올라왔다). 편집 전후로 `git log`와 대상
    파일 diff를 확인하고 남의 변경을 덮어쓰지 않는다.

## 7. 커밋 목록

| 커밋 | 날짜 | 내용 |
|---|---|---|
| `acf4012` | 09-29 | 원본 방법론 흡수 1차, 플러그인 배포 전환 |
| `4ef16dc` | 09-29 | Codex가 링크를 따라가지 않는지 실제 복사로 진단 |
| `dc79e49` | 09-29 | `skills/`를 정본으로, 옛 위치는 역방향 링크 |
| `7c0f55a` | 09-29 | install.sh 생태계 삭제, manifest를 pluginSlot으로 |
| `1b793dd` | 09-29 | Claude 플러그인 agents 슬롯에 역할 3종 |
| `6a79851` | 09-29 | route·유지과정 진입 생략 금지 표 |
| `de26aec`, `642d02b` | 09-29 | 전수조사 5건, provenance 출처 정정 |
| `fbbbad1`, `e9ec1ec`, `2661eba` | 09-29 | 차단 제거, 초호기화, 기록 finalize |
| `af54e01`, `eb225e7` | 09-29 | 옛 사본 제거, Codex 링크, replay 도구, 완료 관문 전역화, 출처 고지 |
| `4d016ce`, `ad7b491` | 09-30 | 테스트 우선 항상 |
| `2372be0`, `36f4b5a` | 09-30 | 세션 모델 출발, 추천 카드, profile 저장, Codex hook·역할 정정 |
| `2a93ae4`, `cd126dc` | 09-30 | 모델 별칭 거부, 모델 id 오판 정정 |
| `934d20a` | 09-30 | 위임 없는 작업에서 모델 카드 제외(Codex 세션) |
| (미커밋) | 09-30 | 3.12–3.15: `DBG-20260930-integrity-audit`, `HOM-20260930-integrity-repair`, `HOM-20260930-claude-role-effort`, `HOM-20260930-model-choice-no-speedbump`, `HOM-20260930-profile-gaps` |

## 8. 초호기 검토안 (2026-09-30 시작)

### 8.1 목적과 전제

초호기의 문제를 기준별로 증거와 함께 찾고, 확정된 것만 고친다. 사용자 합의 사항:
- 문서에 정의된 것, 실제로 존재하는 것, 올바르게 호출되어 기능하는 것은 다른 문제다. 스킬·역할·도구가
  연쇄적으로 작동할 때의 정합성까지 본다(C1).
- 정합성을 먼저 본다. 체인이 끊겨 있으면 "규칙을 안 따른다"(C2)가 실제로는 "따를 수 없는 구조"일 수 있어
  원인을 잘못 짚기 때문이다.
- 점검은 읽기 전용 debugging route로 하고, 수정은 항목별로 homeostasis 진입 조건(scope·evidence gate)을
  확인한 뒤 따로 한다.

### 8.2 기준과 진행 상태

```json
[
  {"id": "C1", "name": "정합성", "status": "partial",
   "layers": {
     "A 정의↔존재": "done — 활성 자산에 끊긴 참조 없음(권위 분류 후). 근거: DBG-20260930-integrity-audit",
     "B 존재↔발견": "partial — Claude 관측됨(hook, chohogi:* skill, 역할). Codex는 skills 캐시=HEAD 확인, 역할 미등록(F4)",
     "C 발견↔호출": "partial — F2, F3 후보",
     "D 호출↔기능": "partial — F1 수리. 도구 테스트·검증기 통과",
     "E 연쇄": "partial — Claude 위임 체인 live 확인(3.13). 진입·기록 체인은 이 세션에서 실행됨. 환류(learning→homeostasis)와 다른 프로젝트에서의 호출은 미실행"},
   "why": "정의가 있어도 발견·호출·연쇄가 끊기면 규칙 준수를 측정할 수 없다"},
  {"id": "C2", "name": "실제 준수", "status": "not-started",
   "method": "규칙별 replay(정확한 모델 id 고정) + 실제 세션 transcript. 칸마다 관측 수를 적고 비율 주장은 evaluation-budget-policy.md 안에서만",
   "why": "매 세션 주입되는 red-flag 표 자체가 생략이 반복됐다는 신호다"},
  {"id": "C3", "name": "비용", "status": "not-started",
   "method": "전역 지침 주입량(AGENTS.md 16,064 bytes) 측정, 단순 작업에 붙는 절차(route·기록·카드) 수, 규칙별 '없으면 어떤 사고가 났나' 근거 대조",
   "why": "근거 없이 비용만 드는 규칙은 정리 후보다. 모델 선택 방지턱(F9)이 이 기준의 첫 사례였다"},
  {"id": "C4", "name": "검증의 실효성", "status": "partial",
   "found": ["F1: 검증기가 멈춘 활성 계획을 PASS", "F7: TOML↔md 미러를 아무 검사도 강제하지 않음", "F12: genome impact가 너무 넓어 선별력 없음"],
   "method": "규칙 문서를 일부러 망가뜨려 검증기가 잡는지 역시험(mutation)",
   "why": "검사 통과가 목표가 되면(Goodhart) 결함이 PASS 뒤에 숨는다. F1이 실제 사례"},
  {"id": "C5", "name": "일관성", "status": "not-started",
   "method": "핵심 규칙 10개를 골라 규칙별로 적힌 문서 위치를 표로 대조(정본 하나인가)",
   "why": "같은 규칙이 여러 문서에 다르게 있으면 세션마다 다른 쪽을 따른다(예: '활성 계획 정확히 하나'가 3곳에 있었다)"},
  {"id": "C6", "name": "자기증식", "status": "not-started",
   "method": "HOM·LRN 기록 대 프로젝트 작업 비율, 규칙 추가 대 삭제 수",
   "why": "하네스가 자기 관리에만 커지면 제품 작업 비용이 오른다"},
  {"id": "C7", "name": "이해 가능성", "status": "not-started",
   "method": "처음 온 세션이 '지금 무엇을 해야 하나'에 답을 얻기까지의 읽기 단계 수, 은유 이름(xylem·phloem 등)의 탐색 비용",
   "why": "AI 독자도 경로 추측 비용을 치른다"},
  {"id": "C8", "name": "호스트 이식성", "status": "partial",
   "found": ["F3", "F4", "F14"],
   "why": "같은 규칙이 한 호스트에서만 깨지는 경우가 반복됐다(2장 #4–#7, #13)"}
]
```

### 8.3 발견 항목

| id | 상태 | 요약 | 근거 | 다음 조치와 이유 |
|---|---|---|---|---|
| F1 | fixed | 검증기가 "활성 계획 정확히 1개"를 강제해, finalize된 계획이 active로 남은 채 PASS | `tooling/verify-project-document-registry.py`, `HOM-20260930-integrity-repair` | — |
| F2 | candidate | `skills/homeostasis/SKILL.md:31,49`가 `tooling/…`, `trunk_orchestration/…`을 기준 루트 없이 부름. 초호기 저장소 밖에서 호출되면 경로가 skill 본문만으로 안 풀림 | 파일 확인, 미실행 | 다른 프로젝트에서 homeostasis를 부르는 replay 1회로 확정. 확정되면 경로를 플러그인 루트 기준으로 고정 |
| F3 | candidate | `skills/homeostasis/references/skill-lifecycle.md:10,59`가 skill-creator를 "Codex 표면"에만 허용. Claude에는 `anthropic-skills:skill-creator`가 있는데 fallback으로 빠짐 | 파일 확인. Claude skill-creator의 `quick_validate.py` 제공 여부 미확인 | Claude skill-creator 능력 확인 후 호스트별 매핑 추가 |
| F4 | user-action | Codex 역할 5종이 `config.toml`에 미등록. Codex에서 `scoped-delegation`이 역할을 띄우지 못함 | README 등록 예시, 3.9 | 사용자 승인 후 등록 → 새 세션에서 스폰 확인 |
| F5 | fixed | Claude 카드가 도구 인자 별칭을 모델 목록으로 사용 | `HOM-20260930-integrity-repair` | — |
| F6 | fixed | Claude 역할별 강도를 불가능으로 판단 | `HOM-20260930-claude-role-effort` | — |
| F7 | fixed | TOML↔md 미러 일치를 강제하는 검사 없음 | `tooling/tests/test_role_definitions.py` | — |
| F8 | fixed | replay의 Codex 역할 등록 목록 하드코딩 | `tooling/adherence-replay.py` | — |
| F9 | fixed | Claude에서 모델 선택이 질문 도구로 작업을 멈출 수 있음 | `HOM-20260930-model-choice-no-speedbump` | 실제 대화 관측은 F14 |
| F10 | open | manifest 폐기 항목이 비일관: `grill-me`는 원본 보존, `frontend-surface`는 원본 삭제 | `manifest.json` | 폐기 자산 보존 규칙을 하나로 정함(낮은 우선순위) |
| F11 | open | `critical-reviewer` 본문은 `git show/diff/log` 사용을 지시하지만 Claude 도구 목록에 Bash가 없음(`Read, Grep, Glob, WebFetch`) | `agents/critical-reviewer.md:4` | Bash 추가 또는 본문을 도구 목록에 맞춤. 읽기 전용 경계와 함께 판단 |
| F12 | open | `genome_map.py impact tooling/model-policy.py`가 영향 114개를 반환해 선별력이 없음 | 명령 출력 | impact 계산을 실제 소비 관계로 좁힘. C4에서 다룸 |
| F13 | user-action | `.agents/chohogi-model-profile.json`이 git 미추적 | `git status` | 커밋 여부를 사용자가 정함 |
| F15 | fixed | 부분 저장 profile: Codex profile에 final-reviewer·debugger가 없어 조용히 세션 모델로 돌았고, card는 저장된 역할만 보였으며, 규칙상 저장된 배치가 있으면 card를 실행하지도 않았다 | `HOM-20260930-profile-gaps` | — |
| F14 | open | 모델 선택 비차단을 실제 대화에서 관측하지 않음. headless는 대기를 재현 못함 | 3.14 | 다음 대화형 세션에서 첫 지시 + 위임 상황을 관측해 기록 |

### 8.4 권고 순서와 이유

1. **미커밋 변경 커밋(F13 포함 결정)** — Codex는 커밋된 내용만 읽는다. 커밋 전에는 두 호스트가 다른 초호기를 본다.
2. **F4 Codex 역할 등록** — 5개 역할 체계가 Codex에서 끊겨 있다. 사용자 승인 필요.
3. **F11** — 작은 수정으로 reviewer 역할의 지시와 능력을 맞춘다.
4. **F2·F3 replay 확정** — C1 C층을 닫는다. 비용은 replay 각 1회.
5. **C2 실제 준수** — C1이 닫힌 뒤에 해야 원인을 구조와 준수로 분리할 수 있다.
6. **C4 mutation 역시험 → C3 비용 → C5 일관성** — 검증기를 믿을 수 있어야 비용·일관성 측정도 믿을 수 있다.
7. **C6·C7·C8** — 앞 단계의 수치를 입력으로 쓴다.
