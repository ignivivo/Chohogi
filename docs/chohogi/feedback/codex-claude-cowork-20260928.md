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
- 범위: 2026-09-28 ~ 2026-09-30. 커밋 `acf4012` ~ `e95323b`(브랜치 `agent/chohogi-v2-integrity`)와
  2026-09-30 Claude Code 세션(Opus 5.5)의 커밋 `e95323b`와 2차 진단 기록(3.16).

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
    "codex": "~/.codex/config.toml의 [agents.<이름>] config_file로 정본 TOML을 가리켜야 스폰된다(README). 2026-09-30 이 호스트에 5개 등록·live spawn 확인(3.17). `python3 tooling/codex-role-setup.py`가 MISSING/WRONG_PATH/OK를 보고하고 `--apply`는 백업 후 누락분만 추가한다. 강도는 spawn_agent의 reasoning_effort로 호출마다 준다.",
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
    "rule": "활성 계획은 최대 하나. 소유 기록이 finalize되면 계획을 historical로 바꾸고 null로 둔다. verify-project-document-registry.py가 finalize된 기록을 active로 선언하면 실패시킨다. 프로젝트가 docs/work-log/records를 쓰면 활성 계획은 executionRecord를 반드시 적는다.",
    "records": "finalize 뒤에 이벤트를 추가하면 verification.json이 reopened가 되고, 다시 finalize해야 pass다(F26). pass는 마지막 이벤트까지 검사됐다는 뜻이다."
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
| 15 | 기록의 `verification.json`이 pass면 그 작업은 끝났다 | finalize 뒤에 붙은 사실이 실패를 말해도 pass가 남았다(Codex 기록, Claude 기록 2개). 이제 reopened로 바뀐다 | Claude의 Codex 작업 검토 | `HOM-20260930-review-fixes` |

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

### 3.12 정합성 전수 점검과 결함 2건 수리 (`e95323b`, Claude 세션)

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

### 3.13 Claude 역할별 모델·추론 강도 (`e95323b`)

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

### 3.14 모델 선택 방지턱 제거 — Claude 쪽 (`e95323b`)

- **기록:** `HOM-20260930-model-choice-no-speedbump`.
- **문제:** 3.11은 공통 문장만 바꿨다. Claude에서 남은 차단 경로는 턴을 멈추는 질문 도구(`AskUserQuestion`)다.
  이번 세션도 모델 배치를 그 도구로 물었다(사용자가 먼저 요청한 경우였음).
- **해결:** AGENTS.md·`model-policy.md`·`claude-tools.md`에 "card는 같은 턴 텍스트로만, 질문 도구 금지, 사용자가
  모델부터 정하겠다고 한 경우만 예외" 추가, red-flag 행 추가. `verify-model-policy.py` 필수 문구로 고정.
  replay에 `forbidden-tool` 단언 종류와 `no-blocking-model-question` 단언 추가.
- **한계:** headless replay는 대화형 대기를 재현하지 못한다. 실제 대화 관측이 남아 있다(F14).

### 3.15 부분 저장 profile (`e95323b`)

- **기록:** `HOM-20260930-profile-gaps`.
- **문제:** 15:41 Codex 세션이 사용자 요청("GPT-6가 느리니 6 luna 대신 5.6 luna")을 GPT-6 Luna가 추천된 역할에만
  적용해 final-reviewer·debugger가 profile에 없었다. 빠진 역할은 세션 모델로 조용히 돌았고 다시 추천되지도 않았다.
- **사용자 결정:** GPT-6를 쓴다. Luna만 속도 때문에 5.6. final-reviewer·debugger는 `gpt-6-sol / medium`.
- **해결:** card가 빠진 역할을 "미저장 → 추천"으로 보여 사용자가 고르게 함(비차단, 답 전 대체값 명시).
  AGENTS.md·`model-policy.md`에 "배치에 빠진 역할이 있으면 card 실행" 추가. 테스트 먼저.

### 3.16 2차 진단 C1–C8 (`DBG-20260930-diagnosis-phase2`, 수정 없음)

- **방법:** C1 잔여(F2 live, F3 파일·검증기 비교, 환류 체인 사용 흔적), C2 Claude replay 7개, C3 baseline 비교 2개,
  C4 복제본 mutation 17건, C5 규칙 10개 교차 grep, C6 git 이력 수치, C7 replay transcript의 문서 읽기 계수, C8 설치 경로 확인.
- **비용:** live 세션 합계 약 1.40 USD(F2 0.12, C2 약 1.06, C3 baseline 약 0.12, 별도 탐침 제외).
- **핵심 결과:** 8.2·8.3. 가장 무거운 것은 F21(세션이 주입 지침 밖을 읽지 않음)과 F22(검증기가 핵심 규칙 파손 대부분을 못 잡음).
- **자기 회귀:** F18·F20은 3.13의 역할 분리가 만든 회귀다. 정적 테스트·검증기는 모두 통과했지만 replay가 드러냈다.

### 3.17 Codex 설치·역할 재검토 ([`HOM-20260930-codex-role-install-live`](../../work-log/records/HOM-20260930-codex-role-install-live/events.jsonl))

- **발견/재현:** `codex plugin add chohogi@chohogi-marketplace`는 성공했으나 `~/.codex/config.toml`에
  `[agents.*]`가 0개여서 역할 5종을 스폰할 수 없었다. 이전 replay의 `--codex-role-config`는 그 실행에만
  역할을 주입했으므로 영구 설치 상태를 증명하지 못했다.
- **원인:** Codex plugin manifest에는 agents 슬롯·install lifecycle이 없다. `2372be0`은 이 제약을
  README 수동 설정으로 넘기고 F4를 user-action으로 분류했다. 따라서 설치 성공이 역할 기능 성공처럼
  보이는 발견 경계의 결함이 되었다.
- **영향:** Codex에서 critical_reviewer·evidence_scout·implementation_worker·final_reviewer·debugger를
  실제 `agent_type`으로 호출할 수 없었다. 정책 replay도 역할 등록 여부를 잘못 양성으로 볼 수 있었다.
- **수정:** 사용자 승인으로 이 호스트의 config.toml에 5개 정본 TOML을 등록했다. 재발 방지로
  `tooling/codex-role-setup.py --apply`를 추가해 누락 항목만 idempotent하게 등록하고 README에 설치 단계로
  넣었다.
- **검증:** 새 유료 `gpt-5.6-luna` Codex 세션에서 5개 agent_type을 각각 spawn해 모두 `ROLE_OK`를 받았다.
  setup 도구의 신규 실패 테스트를 먼저 실행한 뒤 구현했고, setup·adherence replay 단위 테스트 16개가 통과했다.
  raw replay 결과의 SHA-256은 work log artifact에 있다.
- **별도 결함:** 7개 Codex replay 중 일반 5개는 통과했지만 review 2개는 부모가 spawn하지 않았다.
  원인은 역할 등록이 아니라 시나리오가 `scoped-delegation` 계약을 만들지 않고 “독립 검토”만 요청한 데 있다.
  이를 역할 자동 위임 성공으로 판정하던 평가는 잘못된 테스트 계약이며 F18/F19로 유지한다.

### 3.18 남은 결함 전수 대조 (3.19에서 마무리; [work log](../../work-log/records/HOM-20260930-codex-role-install-live/events.jsonl#L20))

- **재현 명령:** `verify-project-document-registry.py`, `verify-functional-assurance.py`,
  `verify-model-policy.py`, `verify-semantic-assurance.py`, `verify-homeostasis-policy.py`,
  `verify-source-layout.py`를 현 작업 트리에서 실행했다.
- **결과:** registry/model-policy/semantic/source-layout은 PASS. functional-assurance는 새
  `tooling/codex-role-setup.py`가 registry에 없는 상태라 FAIL이고, 이를 소비하는 homeostasis-policy도 FAIL.
  이는 setup 도구 구현 자체가 아니라 활성 tooling command의 assurance 등록 누락이다.
- **수정 계획:** setup 도구의 source·trigger·execution·verifier·limit를 functional assurance registry에
  등록하고 full verifier를 재실행한다. 이 수정 전에는 setup 도구를 완결된 설치 수리라고 주장하지 않는다.
- **기존 열린 항목:** F11, F16, F17, F20, F21, F22는 현재 source와 기존 mutation/replay evidence로
  재확인됐다. F2, F3, F10, F12, F14, F23–F25는 아직 새 Codex/Claude 관측 또는 결정이 없어 open으로 유지한다.
- **증거 연결:** 실제 5개 역할 spawn, 유료 replay 결과, parser 수리, 전수 verifier 출력은 위 work log의
  `live-role-spawn`, `live-adherence-replay`, `replay-parser-repair`, `full-audit` 이벤트와 artifact에 연결한다.

### 3.19 Claude 검토와 수리 ([`HOM-20260930-review-fixes`](../../work-log/records/HOM-20260930-review-fixes/events.jsonl))

3.17·3.18의 Codex 작업을 Claude가 검토하고, 2차 진단의 확정 결함과 함께 고쳤다. 각 행의 근거는 기록의 같은
이름 `fact` 이벤트에 있다. 모든 코드 수정은 테스트를 먼저 쓰고 실패를 본 뒤 구현했다.

| 항목 | 문제 | 추정 원인(확인됨) | 수정 방법 | 결과·근거 |
|---|---|---|---|---|
| assurance-setup | 작업 트리에서 검증기 2개·테스트 1개 FAIL | Codex가 추가한 `codex-role-setup.py`가 functional-assurance에 없음 | `installation-and-diagnostics` 항목에 도구·테스트·한계 등록. 개인 설정 예외를 nonTrigger에 명시 | 두 검증기 PASS |
| parser-test | replay 파서 수정에 테스트 없음(테스트 우선 위반) | 3.17 작업 중 생략 | 빈 값·`/session` agent_type 무시 테스트 추가 | HEAD 파서에서 실패, 수정본에서 통과 |
| setup-hardening | 역할 목록 하드코딩, 섹션 존재만 확인, 백업 없음 | F8과 같은 패턴 | 정본 TOML 디렉토리에서 역할 도출, 다른 경로를 가리키면 `WRONG_PATH`(apply가 덮어쓰지 않음), 쓰기 전 백업 | 테스트 4개. 실제 설정은 강화된 검사에서도 `OK` |
| record-reopen (F26) | finalize 뒤 이벤트가 붙어도 pass 유지 | `execution-record.py`가 추가 이벤트에서 verification을 갱신하지 않음 | finalize 이후 이벤트는 상태를 `reopened`로 바꾸고 경고. 기존 기록 3개(Codex 1, Claude 2)에 소급 적용(파생 파일만) | 테스트 red→green |
| F17 | fixed | — | 기록을 쓰는 프로젝트의 활성 계획은 `executionRecord` 필수 | 같은 기록, mutation M14 | — |
| F22 | fixed | — | `verify-runtime-entrypoint.py`, mutation 17/17 | 같은 기록 | 문구 존재만 증명(준수는 C2) |
| F20 | fixed | — | 세션 모델 상속 서술 3곳을 호스트별 사실로 교체 | 같은 기록 | — |
| F11 | fixed | — | critical-reviewer에 Bash | 같은 기록 | — |
| F3 | fixed | — | skill-creator 호스트 매핑 | `HOM-20260930-review-fixes` | — |
| F23 | partial | medium | 오류에 허용값, 주입 지침에 검증 실행 한 줄 | 같은 기록 | replay 재측정 필요 |
| scenario (F18) | Codex가 두 review 시나리오 모두에 역할을 명시함 | 3.17의 가설(문구 모호) 검증용이었으나 Codex 스스로 반증 | 자율 위임 시나리오는 원래 문구로 복원, profile 시나리오는 명시 문구 유지 | 각 시나리오가 자기 주장만 시험 |

- **검증:** unittest 140개 OK, 검증기 17개 PASS(신규 1), genome map OK.
- **Codex 작업에 남긴 질문(F27):** 3.17 기록의 두 사실이 충돌한다. "명시 문구로도 spawn_agent 호출 없음"과
  "원본 기록에 spawn_agent 호출이 있었지만 필드가 비어 있음"이 같은 실행을 말하는지 Codex가 rollout 경로로 정리해야 한다.
- **AGENTS.md 크기:** 16,199 → 16,541 bytes(+342). F24와 함께 판단할 증가분이다.

### 3.20 주입 지침 축소 ([`HOM-20261001-guidance-slim`](../../work-log/records/HOM-20261001-guidance-slim/events.jsonl))

- **문제:** AGENTS.md 8,520자(16.5KB). 모델 정책(21.7%)과 기록 방법(17.2%) 두 문단이 39%였고, replay에서 효과가
  관측된 테스트 우선·완료 관문은 7%였다. 세션은 주입 지침만 읽는다(F21).
- **방법:** 행동을 바꾸는 규칙은 명령문 한 문장씩 남기고, 도구를 쓸 때만 필요한 절차는 그 도구 출력으로 옮겼다.
  기록 방법 → `execution-record.py --help` 끝부분, 저장·상향 확인·재제시·늦은 답 규칙 → 모델 card 출력.
  `verify-runtime-entrypoint.py`에 4,000자 상한을 추가했다(상한을 올리는 것은 homeostasis 결정).
- **전후 비교(Claude, `claude-sonnet-5-5`, 시나리오당 1회):**

| 시점 | 크기 | 첫 턴 컨텍스트 | 비용(7개) | 통과 |
|---|---|---|---|---|
| 이전 (`b8ea864`) | 8,520자 | 약 38.5k | 1.115 USD | 5/7 |
| 1차 축소 | 3,191자 | 약 34.0k | 0.946 USD | 4/7(회귀 2) |
| 복원 후 | 3,331자 | 약 34.1k | 영향 시나리오 3개만 재실행 | 6/7 |

- **회귀 원인(도구 호출 비교로 확인):** (1) "계획을 만들면 registry에 등록한다"는 무조건 규칙을 빼고 조건부
  규칙("registry를 고쳤으면 검증기 실행")만 남겨, 세션이 registry를 건드리지 않았다. (2) "저장된 배치를 쓴다"를
  "Claude 역할은 역할 파일 값으로 돈다"로 줄여, 세션이 profile을 읽지 않고 위임했다. 두 규칙을 한 문장씩 복원했다.
- **교훈:** 주입 지침의 문장 하나가 곧 행동 하나다. 축소는 replay 전후 비교 없이는 하지 않는다. 도구 출력으로
  옮긴 절차는 회귀를 만들지 않았다.
- **남은 실패:** `review-delegates-on-session-model`(F19)은 축소 전후 모두 실패한다. Claude 역할은 이미
  frontmatter 기본값이 있어 card 없이도 위임이 성립한다. card 규칙이 Claude에서 필요한지 자체를 D1과 함께 재검토한다.
- **Codex 영향:** Codex는 AGENTS.md를 링크로 읽으므로 축소본을 즉시 쓴다. Codex replay 전후 비교는 아직 없다.

## 4. 두 호스트 차이 (실측 기준)

| 항목 | Claude Code (2.1.284) | Codex (codex-cli 0.155.0-alpha.16.3) |
|---|---|---|
| 전역 지침 | 플러그인 SessionStart hook | `~/.codex/AGENTS.md` 링크. 플러그인 hook은 `"hooks": {}`로 끔 |
| 스킬 | 플러그인 `skills/`(`chohogi:*`) | 플러그인 캐시(커밋 상태 복사)의 `skills/`. 링크는 따라가지 않음 |
| 역할 | 플러그인 `agents/` → `chohogi:<role>` 5종 | `config.toml`의 `config_file`(2026-09-30 live 등록·5종 spawn 확인). `~/.codex/agents` 링크는 스폰 거부 |
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
11. **주입 지침을 고칠 때는 replay 전후 비교를 한다.** 문장 하나가 행동 하나다(3.20). 4,000자 상한을 넘기려면
    homeostasis로 결정한다.

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
| `e95323b` | 09-30 | 3.12–3.15: `DBG-20260930-integrity-audit`, `HOM-20260930-integrity-repair`, `HOM-20260930-claude-role-effort`, `HOM-20260930-model-choice-no-speedbump`, `HOM-20260930-profile-gaps` |
| `ecc1e78` | 09-30 | 3.16: 2차 진단 `DBG-20260930-diagnosis-phase2` |
| (이 행 다음 커밋, `git log --grep HOM-20260930-review-fixes`) | 09-30 | 3.17(Codex 작업, 함께 커밋)·3.19: `HOM-20260930-codex-role-install-live`, `HOM-20260930-review-fixes` |
| (`git log --grep HOM-20261001-guidance-slim`) | 10-01 | 3.20: 주입 지침 축소 |

## 8. 초호기 검토안 (2026-09-30 시작, 2차 진단 완료)

### 8.1 목적과 전제

초호기의 문제를 기준별로 증거와 함께 찾고, 확정된 것만 고친다. 사용자 합의 사항:
- 문서에 정의된 것, 실제로 존재하는 것, 올바르게 호출되어 기능하는 것은 다른 문제다. 스킬·역할·도구가
  연쇄적으로 작동할 때의 정합성까지 본다(C1).
- 정합성을 먼저 본다. 체인이 끊겨 있으면 "규칙을 안 따른다"(C2)가 실제로는 "따를 수 없는 구조"일 수 있다.
- 진단은 읽기 전용 debugging route. 수정은 항목별로 homeostasis 진입 조건을 확인한 뒤 따로 한다.
- 2차 진단(`DBG-20260930-diagnosis-phase2`)은 **수정 없이** 발견만 남겼다. Codex 검토(8.5)를 거친 뒤 수정한다.

### 8.2 기준과 결과

```json
[
  {"id": "C1", "name": "정합성", "status": "done",
   "result": "A층 깨끗. B: Claude는 저장소를 live 로드(확인), Codex 역할 미등록(F4). C: F3 확정, F2는 Claude에서 비결함. D: F1 수리했으나 부분적(F17). E: 위임 체인 Claude live 확인, 환류 체인은 learning이 6주간 미사용(F16)."},
  {"id": "C2", "name": "실제 준수", "status": "done",
   "result": "Claude replay 7개 1회씩(claude-sonnet-5-5, 합계 약 1.06 USD): 4 통과, 3 실패(F18 시나리오 모호, F19 카드 생략+틀린 보고, F23 registry 상태값 오류+프로젝트 밖 쓰기). 7개 세션 모두 초호기 route 문서를 읽지 않음(F21)."},
  {"id": "C3", "name": "비용", "status": "done",
   "result": "첫 턴 컨텍스트 +11.2k 토큰(38.4k 대 27.2k), 작은 작업 비용 약 2배. 대신 테스트 우선은 초호기에서만 지켜짐(baseline 위반). F24."},
  {"id": "C4", "name": "검증의 실효성", "status": "done",
   "result": "핵심 규칙 17곳 단일 파손 중 5곳만 검출(F22). 테스트 우선·완료 관문·red-flag·conductor 경로·hook 경로 파손을 아무 검증기도 못 잡음. F1 상태 재현도 통과(F17)."},
  {"id": "C5", "name": "일관성", "status": "done",
   "result": "10개 규칙 표본 중 '역할은 세션 모델을 물려받는다'가 3곳에서 새 사실과 모순(F20). learning-우선·세 번 실패 중단 규칙은 각 1곳에만 있고 주입 지침에 없음."},
  {"id": "C6", "name": "자기증식", "status": "done",
   "result": "주입 지침 AGENTS.md 4.6KB(08-12) → 16.2KB(09-30), 최근 1주에 +6.2KB. 규칙 문서 추가:삭제 약 19:1. 09-22 이후 기록 전부 자기 유지(HOM/DBG). F24."},
  {"id": "C7", "name": "이해 가능성", "status": "done",
   "result": "실측: 세션은 주입 지침 밖의 문서를 따라가지 않는다(F21). 따라서 규칙의 실효 위치는 AGENTS.md 한 파일이고, 나머지 약 15k줄은 이번 표본에서 행동에 기여하지 않았다."},
  {"id": "C8", "name": "호스트 이식성", "status": "partial",
   "result": "Claude 쪽은 측정 완료. Codex 쪽 replay·F2·F4 검증은 Codex 검토자에게 넘김(8.5)."}
]
```

### 8.3 발견 항목

심각도: `high`(규칙이 실제로 작동하지 않거나 거짓 PASS), `medium`(특정 경로에서 틀린 행동), `low`(정리).

| id | 상태 | 심각도 | 요약 | 근거 | 제안 |
|---|---|---|---|---|---|
| F1 | fixed | — | 검증기가 "활성 계획 정확히 1개"를 강제해 finalize된 계획이 active로 남음 | `HOM-20260930-integrity-repair` | F17로 보완 필요 |
| F2 | candidate(Codex) | low | homeostasis skill의 루트 없는 상대 경로. Claude는 hook 루트로 해결됨(live, $0.12) | phase2 fact | Codex에서 1회 확인 |
| F3 | open | medium | skill-creator를 Codex에만 허용. Claude `anthropic-skills:skill-creator`의 `quick_validate.py`가 14개 skill 모두 Codex판과 같은 판정 | `skill-lifecycle.md:10,59`, phase2 fact | 호스트별 매핑 추가(`init_skill.py`는 Claude에 없음) |
| F4 | fixed (this host) | high | Codex 역할 5종이 설치 뒤 미등록이었던 설치·발견 결함. `codex-role-setup.py --apply`로 정본 TOML을 등록하고, 새 `gpt-5.6-luna` 세션에서 5종 모두 실제 spawn | `HOM-20260930-codex-role-install-live`, `/tmp/chohogi-live-codex-pe6ZIa` | native plugin add에는 역할 lifecycle이 없으므로 setup/doctor adapter를 설치 절차에 포함 |
| F5–F9 | fixed | — | 3.12–3.14 참조 | 각 기록 | — |
| F10 | open | low | manifest 폐기 항목 보존 규칙 비일관, 검증기도 확인 안 함 | `manifest.json` | 규칙 하나로 정리 |
| F11 | open | medium | critical-reviewer가 `git show/diff` 사용을 지시받지만 도구에 Bash 없음 | `agents/critical-reviewer.md:4` | Bash 추가 또는 diff를 packet으로 전달하도록 본문 변경 |
| F12 | open | low | genome impact가 114개를 반환해 선별력 없음 | 명령 출력 | 소비 관계 기준으로 축소 |
| F13 | fixed | — | profile 파일 커밋 | `e95323b` | — |
| F14 | open | medium | 모델 선택 비차단을 실제 대화에서 미관측 | 3.14 | 대화형 세션 관측 |
| F15 | fixed | — | 부분 저장 profile | `HOM-20260930-profile-gaps` | — |
| F16 | open | high | learning이 2026-08-12 이후 미사용. 확정 실패 수리 11건이 모두 homeostasis로 직행. learning-우선 규칙은 `skills/homeostasis/SKILL.md:111`에만 있음 | phase2 fact | 규칙을 conductor·주입 지침으로 올리거나, 실효가 없으면 규칙을 줄임(사용자 판단) |
| F17 | open | high | F1 수리가 부분적: `executionRecord`가 선택 필드라 finalize된 계획을 다시 active로 선언해도 PASS | mutation M14 | 활성 계획에 `executionRecord` 필수화 또는 records 디렉토리 역참조 |
| F18 | fixed | — | 시나리오 분리(자율 위임은 원래 문구, profile은 명시 문구) | 같은 기록 | replay 재측정 필요 |
| F19 | open | medium | profile 없는 위임에서 카드 미실행, "세션 모델을 물려받았다"고 틀리게 보고 | C2 transcript | F20 수정됨. 같은 시나리오 재측정으로 남은 원인 확인 |
| F20 | open | high | "역할은 세션 모델을 물려받는다"가 `AGENTS.md:11`, `model-policy.md:13`, `claude-tools.md:25`에 남아 역할 파일 frontmatter 사실과 모순. `claude-tools.md:25`는 같은 문서의 '역할 파일과 같으면 model 생략'과도 모순 | grep, C2 transcript | 세 문장을 호스트별 사실로 교체. **3.13에서 놓친 갱신** |
| F21 | open | high | replay 7/7 세션이 초호기 route 문서를 한 번도 읽지 않음. skill 호출 0. 행동은 주입 지침만으로 결정 | C2 transcript 분석 | 규칙 배치 재설계: 행동을 바꿔야 하는 규칙은 주입 지침에, 나머지는 필요 시 명령(검증기·card)으로 묶기. C3과 함께 판단 |
| F22 | open | high | 핵심 규칙 17곳 파손 중 12곳 미검출. hook의 지침 경로가 깨져도 PASS | mutation 결과 | 주입 지침 핵심 문장·hook 경로의 존재 검사 추가. 검증기의 한계를 functional-assurance에 명시 |
| F23 | open | medium | 계획 작성 세션이 registry에 허용되지 않는 상태 `completed`를 쓰고 검증기를 돌리지 않음. 프로젝트 밖 `/tmp/placeholder`에 잘못 쓰고 삭제 | C2 transcript, 재현 | 상태 어휘를 주입 지침 또는 검증 명령 안내로. F21과 같은 뿌리 |
| F24 | partial | medium | 주입 지침 8,520 → 3,331자, 첫 턴 컨텍스트 약 -4.5k 토큰, 4,000자 상한 | `HOM-20261001-guidance-slim` | skill·역할 설명 목록(약 4.9k자)은 미조정 |
| F26 | fixed | — | finalize 뒤 이벤트가 상태를 reopened로 바꿈. 기존 기록 3개 소급 | 같은 기록 | — |
| F27 | open(Codex) | medium | 3.17 기록의 spawn_agent 관측 두 사실이 서로 충돌 | `HOM-20260930-codex-role-install-live` events | Codex가 rollout 경로로 정리 |
| F28 | decision | medium | `codex-role-setup.py --apply`가 "개인 config.toml은 관리 대상이 아니다" 원칙의 예외가 됨 | AGENTS.md, assurance nonTrigger | 사용자가 예외를 상시로 둘지 결정(8.6) |
| F25 | open | low | `~/.claude/plugins/cache/chohogi-marketplace/chohogi/1.0.0`에 09-29 사본(agents/ 없음)이 남아 있으나 로드되지 않음 | C8 fact | 혼동 방지를 위해 기록만. 삭제는 사용자 판단 |

### 8.4 권고 순서와 이유 (2026-09-30 23시 이후 갱신)

1. **재측정(Claude·Codex 각 1회):** `review-delegates-on-session-model`, `review-uses-saved-profile`,
   `plan-location-no-tool-directives`. F19·F23·F18 수정의 효과를 확인한다. 정적 검사만으로는 준수를 증명하지 못한다(F21).
2. **F27(Codex)** — Codex 위임 실패 결론을 확정해야 Codex 쪽 F19를 다룰 수 있다.
3. **8.6 사용자 결정** — F21·F24·F16은 규칙 배치 설계이고, F28은 원칙 예외다.
4. **F2(Codex 1회), F14(대화형 관측)** — 관측만 남았다.
5. **F10·F12·F25** — 낮은 우선순위 정리. 근거: 행동에 영향이 관측되지 않았다.

### 8.5 Codex 검토 체크리스트

Codex 검토자는 아래를 독립적으로 확인하고, 결과를 이 문서 8.3의 상태 열과 새 행(반박·재현)으로 남긴다.
각 항목은 "재현됨 / 반박됨 / 확인 불가(이유)"로 판정한다. 판정 근거는 명령 출력이나 rollout 경로로 남긴다.

1. 커밋 `e95323b`의 diff를 읽고, 3.12–3.15의 설명과 실제 변경이 일치하는지 확인한다.
2. F17·F22: `git clone --local . <저장소 밖 경로>` 후 `python3 docs/work-log/records/DBG-20260930-diagnosis-phase2/mutate.py <복제본>`을
   실행해 `mutate-result.jsonl`(같은 디렉토리)과 비교한다. 스크립트는 규칙 17곳을 하나씩 깨고 검증기 16개와 unittest를 돌린다.
3. F21: `python3 tooling/adherence-replay.py run --host codex --profile chohogi --scenario all --runs 1 --model <정확한 id> --out <저장소 밖>`
   후 rollout에서 초호기 route 문서 읽기 여부를 센다. Codex는 AGENTS.md가 링크라 경로 문서를 읽을 수 있는지가 쟁점이다.
4. F2: 초호기 저장소 밖 프로젝트에서 homeostasis skill의 execution-record 명령이 경로를 찾는지 Codex에서 1회 확인한다.
5. F19·F20: Codex에서 profile 없는 위임 시나리오(`review-delegates-on-session-model`)를 1회 돌려 카드 실행 여부를 본다.
6. F16: Codex 쪽 판단 — learning-우선 규칙이 실효가 있어야 하는지, 줄여야 하는지 의견을 남긴다(수정은 하지 않는다).
7. 비용은 `evaluation-budget-policy.md` 안에서 쓰고, 실행 횟수와 비용을 이 문서에 적는다.

### 8.6 사용자 결정 항목

| id | 질문 | 선택지와 trade-off | 추천 |
|---|---|---|---|
| D1 (F21·F24) | 규칙을 어디에 둘 것인가 | (a) 행동 규칙은 주입 지침에 한 문장씩, 절차는 도구 출력으로: 3.20에서 적용·검증됨. 남은 질문은 Claude에서 card 규칙이 필요한가(F19) | (a) 유지. card 규칙의 Claude 적용 여부만 결정 필요 |
| D2 (F16) | learning을 살릴 것인가 | (a) learning-우선을 conductor·주입 지침에 올린다. (b) 실효가 없으니 homeostasis가 예방 범위를 직접 판정하도록 규칙을 줄인다 | 판단 보류. 6주간 미사용이 "불필요"인지 "진입 경로 부재"인지 증거가 없다 |
| D3 (F28) | `codex-role-setup.py --apply`를 원칙 예외로 둘 것인가 | (a) 상시 예외(명시 실행·백업·추가만). (b) 점검만 허용하고 등록은 README 수동 절차 | (a). Codex는 플러그인에 역할 슬롯이 없어 설치만으로 역할이 동작하지 않는다(3.17) |
