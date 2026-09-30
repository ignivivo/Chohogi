# Codex·Claude 공동작업 기록 (cowork)

## 목적

이 문서는 **Codex와 Claude Code 둘 모두**가 이 저장소(초호기)에서 이어서 일할 때 쓰는 공동작업
기록이다. 한쪽 호스트가 찾은 문제, 원인, 의도, 해결 방법, 코드 전후 차이, 검증 결과, 틀렸다가 정정한
주장, 아직 열린 항목을 한곳에 남겨 다른 쪽이 같은 조사를 반복하거나 이미 정정된 결론을 다시 믿지
않게 한다.

- 범위: 2026-09-28 ~ 2026-09-30, Claude Code 세션(Sonnet 5 → Opus 5.5)이 사용자와 함께 한 작업.
  커밋 `acf4012` ~ `cd126dc`(브랜치 `agent/chohogi-v2-integrity`, 원격에 push됨).
- 문서 역할: `feedback-source`(`.agents/chohogi-document-registry.json`에 등록). 활성 실행 계획이
  아니며 실행 지시도 아니다. 현재 동작의 정본은 각 계약 파일과 코드이고, 이 문서는 그 경위다.
- 읽는 순서: "1. 지금 믿어도 되는 사실" → 필요한 단계의 "3. 작업 경위" → "5. 열린 항목".
- 각 작업의 세부 근거는 `docs/work-log/records/<work-id>/`의 execution record에 있다.

## 1. 지금 믿어도 되는 사실 (2026-09-30 기준)

```json
{
  "schemaVersion": 2,
  "distribution": {
    "method": "각 호스트의 로컬 플러그인 마켓플레이스로 이 저장소를 등록한다. copy-install(install.sh)은 폐기됐다.",
    "claude": "플러그인의 skills/, agents/, hooks/hooks.json을 쓴다. SessionStart hook이 AGENTS.md를 플러그인 루트 경로와 함께 주입한다(matcher 없음: 시작·재개·clear·압축 전부. 재개는 관측, clear·압축은 설정상).",
    "codex": "플러그인의 skills/만 쓴다. .codex-plugin/plugin.json은 \"hooks\": {}로 hook 자동 등록을 끈다. 전역 지침은 ~/.codex/AGENTS.md → assets/runtime_entrypoint/AGENTS.md, ~/.agents/chohogi → assets/agents 심볼릭 링크로 읽는다.",
    "commitRule": "Codex는 마켓플레이스 root를 git 커밋 상태로 복사해 스킬을 읽는다. 정본을 바꾸면 커밋해야 Codex 스킬에 반영된다. 링크로 읽는 AGENTS.md는 작업 트리를 바로 본다."
  },
  "roles": {
    "claude": "agents/*.md가 chohogi:critical-reviewer / evidence-scout / implementation-worker 서브에이전트 타입으로 노출된다.",
    "codex": "~/.codex/config.toml의 [agents.<이름>] config_file로 정본 TOML을 가리켜야 스폰된다(README). ~/.codex/agents/의 심볼릭 링크는 목록에만 뜨고 스폰이 거부된다. 2026-09-30 현재 사용자 승인 대기로 등록되지 않았다."
  },
  "alwaysInjectedRules": [
    "route 선택: conductor가 direct / defer / product-decision / delivery / debugging 중 하나를 고른다",
    "테스트 우선: 제품 코드 동작을 바꾸는 모든 변경은 크기·처리 방식과 무관하게 실패 테스트부터 쓴다. 예외는 사용자가 정한다",
    "완료 주장 관문: 직접 처리를 포함해 완료·통과를 말하기 전에 증명 명령을 이번 턴에 새로 실행한다",
    "모델: 세션 모델로 출발하고, 저장된 배치가 없으면 처음 위임 직전에 model-policy.py card를 실행해 출력을 보고 끝에 붙인다",
    "route·유지과정 진입 생략 금지 표(red flags)"
  ],
  "models": {
    "start": "역할은 모델을 지정하지 않으면 세션 모델을 물려받는다(Claude: Agent 도구 스키마, Codex: 부모·자식 세션 모두 gpt-6-luna/medium 실측).",
    "savedProfile": ".agents/chohogi-model-profile.json의 hosts.claude / hosts.codex. model-policy.py profile로 검증한다. 사용자가 답하기 전에는 만들지 않는다.",
    "upgrade": "저장된 배치(없으면 세션 모델)보다 올리는 배정만 사용자 확인을 받는다."
  },
  "externalMethodology": {
    "status": "Superpowers(obra/superpowers, MIT, 8ca22dba)의 기능은 이름으로 차단하지 않고 초호기 기관 안에 초호기식으로 다시 만들었다(초호기화).",
    "attribution": "THIRD_PARTY_NOTICES.md에만 출처를 적는다. 활성 자산은 원본 이름을 부르지 않는다."
  },
  "evidenceTool": "tooling/adherence-replay.py가 실제 claude -p / codex exec 세션을 돌려 도구 호출 순서·바뀐 파일·사후 검사로 규칙 준수를 판정한다. 모델은 정확한 id로 고정한다(별칭 거부)."
}
```

## 2. 틀렸다가 정정된 주장

다른 세션이 아래의 "초기 주장"을 다시 믿지 않도록 남긴다. 모두 이번 기간에 초호기 측(Claude 세션)이
한 주장이다.

| # | 초기 주장 | 사실 | 어떻게 드러났나 | 정정 커밋·기록 |
|---|---|---|---|---|
| 1 | 프로젝트 루트에 `CLAUDE.md`·`.agents/skills/`가 없으니 project leaf가 구현되지 않았다 | `docs/chohogi/`, `docs/work-log/records/`에 이미 구현·축적되어 있었다 | 기존 문서를 읽지 않고 루트만 봤다 | 이 문서 초판(2026-09-28) |
| 2 | superpowers 폴더는 초호기 결함일 수 있다 | 외부 플러그인(diagnosing-superpowers)의 산출 경로였다. 원인은 그 플러그인이 도구 이름 경로(`~/.superpowers/`, `docs/superpowers/plans/`)를 고정해 쓰는 데 있다 | `docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md`, 원본 소스 확인 | 초판, `fbbbad1` |
| 3 | diagnosing-superpowers 소스는 볼 수 없다(컴파일됨) | 로컬 플러그인 캐시에 평문 Markdown으로 있었다 | 사용자 지적 후 캐시 확인 | `642d02b` |
| 4 | SessionStart hook이 두 호스트 모두에 지침을 주입한다 | Codex는 플러그인 hook을 신뢰 승인 전에는 건너뛴다. 그동안 Codex에 들어간 지침은 옛 install.sh 사본이었다 | `codex exec` 세션 기록에 hook 출력 없음 | `af54e01` |
| 5 | Codex는 플러그인 hook을 아예 실행하지 않는다 | 매니페스트에 `hooks` 필드가 없으면 자동 등록하고, 신뢰 승인 뒤에는 실행한다(지침 이중 주입) | 원본 테스트 주석 확인 → `--dangerously-bypass-hook-trust`로 재현 | `2372be0` |
| 6 | Codex 역할은 `~/.codex/agents/` 심볼릭 링크로 연결되고 검증됐다 | 목록에만 뜨고 스폰은 "agent type is currently not available"로 거부된다 | 역할 목록만 보고 판단. 실제 스폰 시험으로 드러남 | `2372be0` |
| 7 | Codex에서 `fork_turns: all`이면 `agent_type`이 거부된다(원본 문서) | 거부 원인은 링크였다. `config_file` 역할은 `all`에서도 스폰됐다 | 역할 파일을 일반 파일·링크·`config_file`로 나눠 비교 | `2372be0` |
| 8 | Claude가 자기 세션 모델을 `claude-sonnet-5-5`로 잘못 적었다 | 실제로 `claude-sonnet-5-5`였다. `--model sonnet` 별칭이 09-29에는 `claude-sonnet-5`, 09-30에는 `claude-sonnet-5-5`로 해석됐다 | 사용자 지적 후 세션 `init` 이벤트 확인 | `2a93ae4`, `HOM-20260930-replay-model-pinning` |
| 9 | 테스트 우선 개선(Claude 0/2 → 2/2)은 규칙 효과다 | 날짜 간 모델이 바뀌어 교란됐다. `claude-sonnet-5` 고정 재실행 2/2로 규칙 효과를 다시 확인했다 | #8 조사 중 | `2a93ae4` |

교훈: 이름이 목록에 보이는 것, 설치 명령이 성공한 것, 문서에 적힌 것은 동작 증거가 아니다. 새 세션을
실제로 돌려 transcript에서 확인한 것만 "검증됨"으로 적는다.

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
- **해결(당시):** 원본 이름 제거, 명시적 금지 문단, 이름 스캐너(`retired-capability-markers.json` +
  `verify-installed-capability-markers.py`), `session-forensics` 신설, homeostasis Method에
  execution record 단계 연결, `platform-tools/{claude,codex}-tools.md` 신설.
- **이후:** 금지 문단과 스캐너는 3.6에서 "차단은 잘못된 접근"이라는 사용자 판단으로 제거됐다.

### 3.2 설치 구조: install.sh → 플러그인 (`acf4012`, `4ef16dc`, `dc79e49`, `7c0f55a`)

- **문제:** install.sh가 `.claude/skills/`를 건너뛰고, 역방향 링크를 링크째 복사하고, 설치본과 정본이
  갈라졌다.
- **의도:** 원본 방법론처럼 각 호스트의 공식 로컬 플러그인 마켓플레이스를 쓴다. 단 검증 없이 폐기하지
  않고 두 CLI에서 직접 확인한다.
- **발견:** Codex는 플러그인 캐시로 복사할 때 **심볼릭 링크를 따라가지 않는다**(`4ef16dc`에서 링크 대신
  실제 복사로 시험해 확인). Claude Code는 로드 시점에 링크를 따라간다.
- **해결:** 정본 스킬 위치를 저장소 루트 `skills/`로 옮기고 옛 위치를 역방향 링크로 바꿨다(`dc79e49`).
  install.sh와 부속 도구(doctor, graft audit, prune-backups 등)를 전부 삭제하고 `manifest.json`을
  `destination/installMode`에서 `pluginSlot`으로 재설계했다(`7c0f55a`).
- **전후:**

```diff
- "destination": "~/.codex/AGENTS.md", "installMode": "copy"
+ "pluginSlot": "hooks"
```

```json
{"hooks": {"SessionStart": [{"hooks": [{"type": "command",
  "command": "root=\"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}\"; echo \"<!-- chohogi:plugin-root=$root -->\"; ... sed \"s|~/.agents/chohogi|$root/assets/agents|g\" \"$root/assets/runtime_entrypoint/AGENTS.md\""}]}]}}
```

- **남은 오해:** 이 단계에서 "hook이 두 호스트 모두에 적용된다"고 적었으나 Codex에 대해서는 틀렸다
  (2장 #4, #5).

### 3.3 역할 노출 (`1b793dd`)

- **해결:** Claude Code 플러그인의 `agents/` 슬롯에 `critical-reviewer`, `evidence-scout`,
  `implementation-worker`를 추가했다(Codex TOML이 정본이고 `.md`는 형식이 달라 링크가 아닌 사본).
- **Codex:** 플러그인 매니페스트에 역할 필드가 없다. 당시에는 "스폰 시 TOML 지시문을 프롬프트에 조립"으로
  적었다. 이후 3.7에서 링크, 3.9에서 `config_file`로 바뀌었다.

### 3.4 스킬 진입 강제 규칙 (`6a79851`)

- **문제:** 이 세션이 homeostasis·learning 파일 경로를 알면서도 정식으로 Method를 따르지 않았다.
- **해결:** 원본의 "red flags" 형식을 초호기 문맥으로 다시 써서 AGENTS.md에 "route·유지과정 진입을
  생략하지 않는다" 표를 넣었다(매 세션 주입).

### 3.5 전수조사 5건 (`de26aec`, `642d02b`)

| 발견 | 조치 |
|---|---|
| `verify-provenance.py` 실패: `session-forensics`가 provenance에 미등록 | 등록 |
| 폐기된 설치 구조를 설계로 규정한 2026-08-11 설계 문서가 registry에서 `active` | `historical`로 재분류, 배너 추가 |
| 같은 날짜 계획 문서의 내부 배너가 "approved" | Historical 배너로 동기화 |
| 이름 스캐너가 `.claude/worktrees/`(다른 ref의 중첩 체크아웃)를 스캔 | 제외 목록에 `.claude` 추가(이후 스캐너 자체 삭제) |
| `xylem_provenance/provenance.json`과 `index_registry.yaml`의 관계가 문서에 없음 | README에 두 레지스트리 역할 구분 명시 |

`642d02b`: provenance의 원본 출처를 "확인 불가"에서 실제 저장소·저자·라이선스·버전으로 정정(2장 #3).

### 3.6 차단 → 초호기화 (`fbbbad1`, `e9ec1ec`, `2661eba`)

- **사용자 판단:** "남의 장기를 그대로 이식하면 면역반응이 일어난다. 차단이 아니라 초호기 조직으로 바꿔
  장착해야 한다."
- **원인 재정의:** 충돌은 원본을 그대로 들여온 데서 왔다. 원본이 도구 이름 경로를 고정해 쓰고, 생성
  문서에 자기 스킬 호출 지시를 적어 다음 세션의 conductor를 우회했다.
- **해결:** 금지 문단과 이름 스캐너를 삭제하고, 원본 15개 스킬의 기능을 소유 기관별로 다시 만들었다.
  스킬 14개를 따로 만드는 안은 conductor 옆에 두 번째 호출 층을 만들어 같은 충돌을 되풀이하므로
  기각했다(`HOM-20260929-method-naturalization` decision).

| 원본 기능 | 초호기 소유 기관 |
|---|---|
| 계획 작성 | 신규 `trunk_orchestration/plan-authoring.md` |
| 계획 실행(직접·위임) | 신규 `trunk_orchestration/task-loop.md` |
| 완료 전 검증, TDD, 검토 수용, 브랜치 마무리 | `branches_workflows/delivery.md` |
| 체계적 디버깅 | `branches_workflows/debugging.md` |
| 브레인스토밍 | `branches_workflows/product-decision.md` |
| 병렬 위임 | `execution-allocation.md` |
| 코드 리뷰 요청 | critical-reviewer / implementation-worker 역할 정의 |
| 작업공간 격리 | `platform-tools/*.md` |
| 스킬 작성 | `skills/homeostasis/references/skill-lifecycle.md` |
| 세션 진단 | `skills/session-forensics` |
| 스킬 호출 규율 | AGENTS.md red-flags 표 |

- **전후 예:** `delivery.md`에 "완료 주장 관문", "검토 결과 수용", "통합 종료" 절 추가.
  `debugging.md`에 "수정이 세 번 실패하면 네 번째를 시도하지 않고 구조 문제로 decision-report" 추가.
- **finalize 실패 1건:** 기록을 "닫았다"는 커밋(`e9ec1ec`) 시점에 feedback 문서 두 개에 응답 기록이 없어
  finalize가 실패했었다. 응답 기록 후 `2661eba`에서 실제로 닫았다.

### 3.7 옛 사본 제거, Codex 연결, 준수 검사기, 완료 관문 전역화 (`af54e01`, `eb225e7`)

- **발견:** 플러그인과 나란히 install.sh 사본이 남아 옛 버전 초호기(삭제된 금지 문단 포함)가 한 벌 더
  주입되고 있었다. 사본 위치: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.agents/chohogi/`,
  `~/.claude/skills`·`~/.agents/skills`의 초호기 스킬 14개씩, `~/.codex/agents/*.toml`.
- **조치:** 지우지 않고 `~/.chohogi-legacy-install-20260929/`로 옮겼다. Codex 지침은 정본 링크로 복구하고
  새 `codex exec` 세션에서 로드를 확인했다.
- **준수 검사기(`tooling/adherence-replay.py`):** 원본 테스트(`tests/claude-code/test-helpers.sh`,
  `tests/explicit-skill-requests/run-test.sh` 등)의 방식, 즉 headless 실행 → transcript의 도구 호출 판정 →
  결과물 검사 → 반복 실행을 초호기 형식으로 만들었다. 결과 JSON에는 단언별 통과 여부만 남고 원문
  transcript는 저장소 밖에만 둔다.
- **첫 발견:** 초호기가 있어도 두 호스트 모두 함수를 추가하고 테스트를 한 번도 돌리지 않은 채 완료를
  말했다. 원인은 완료 관문이 `delivery.md` 안에만 있어 "저위험 직접 처리"로 분류된 작업이 읽지 않은 것.
- **해결:** 완료 관문을 AGENTS.md와 conductor의 직접 처리 문장으로 올렸다.

```diff
- 짧은 질문, 읽기 전용 확인, 범위가 명확한 저위험 편집은 바로 수행한다.
+ 짧은 질문, 읽기 전용 확인, 범위가 명확한 저위험 편집은 바로 수행한다. 바로 수행한 편집에도
+ `branches_workflows/delivery.md`의 완료 주장 관문은 적용된다 — 바꾼 뒤 검증 명령을 새로 실행하고
+ 결과와 함께 보고한다.
```

- **검사기 자체 결함(실제 transcript로 발견·수정):** 계획 시나리오 단언이 초호기상 정당한 선택까지
  실패로 판정 → registry 검사기 통과로 판정 변경. 셸 heredoc·리다이렉트 쓰기를 편집으로 못 잡음 → 감지
  추가. 여러 줄 명령을 검증 패턴에 못 맞춤 → `re.S`.
- **출처 고지:** `THIRD_PARTY_NOTICES.md` 신설(MIT 전문, 초호기 파일별 출처 표).

### 3.8 테스트 우선을 항상 (`4d016ce`, `ad7b491`)

- **문제:** 규칙이 "테스트가 의미 있는 보호막이면"이라 모델이 작은 작업을 예외로 판단했다(0/4). Codex는
  `delivery.md`를 직접 읽은 세션에서도 코드를 먼저 썼다.
- **사용자 결정:** 원본처럼 항상.
- **전후:**

```diff
- 6. 기능·버그 수정에서 테스트가 의미 있는 보호막이면 실패 조건을 먼저 명확히 하고
-    구현한다. 기계적 문서 변경처럼 해당하지 않는 경우에는 억지 TDD를 적용하지 않는다.
+ 6. 제품 코드의 동작을 바꾸는 모든 변경 — 새 기능, 버그 수정, 리팩터링, 동작 변경 — 은
+    크기와 처리 방식에 관계없이 실패하는 테스트를 먼저 쓴다. ... 예외는 버리는 시험 코드,
+    생성된 코드, 설정 파일뿐이며 에이전트가 아니라 사용자가 정한다.
```

- **검증:** Claude 2/2, Codex 2/2가 테스트 먼저 → 실패 확인 → 구현 → 전체 재검증. 모델 교란은 3.10 참고.

### 3.9 모델: 확인 후 출발 → 세션 모델로 출발 (`2372be0`, `36f4b5a`)

- **문제:** Codex는 위험 변경 검토를 스스로 위임하려다 "새 프로젝트면 모델 목록을 확인받는다" 규칙에
  걸려 질문만 보내고 멈췄다. 확인 결과를 저장할 곳이 없어 새 세션마다 다시 물을 수 있었다.
- **사용자 결정:** 기본값(세션 모델)으로 시동을 건 뒤 역할별 추천을 보여주고, 사용자가 수용·변경·세분화한다.
- **해결:**
  - `model-policy.md` "출발·추천·저장": 세션 모델 출발, 비차단 카드, `.agents/chohogi-model-profile.json`에
    호스트별 저장, 올리는 배정만 확인.
  - `model-policy.py profile`(미확정·모르는 호스트·인증정보·빈 값 거부), `card`(저장 배치 또는
    `model-recommendations.json`의 날짜·근거 달린 추천).
  - 카드는 문장 규칙으로는 두 호스트 모두 건너뛰었다(Claude 0/2, Codex 0/2). 명령에 묶은 첫 문구에서
    Claude는 명령만 실행하고 출력을 보고에서 뺐다. "처음 위임 직전에 `model-policy.py card` 실행, 출력을
    보고 맨 끝에 원문 그대로, 모르는 값은 `session`, red-flag 한 줄"로 보강한 최종 규칙에서 Claude 1/1,
    Codex 1/1.
- **Codex 정정:** 매니페스트에 `"hooks": {}` 추가, 링크 역할 제거, `config_file` 등록 방법을 README에 기록.

```diff
  ".codex-plugin/plugin.json"
+ "hooks": {}
```

```toml
# README (적용은 사용자 승인 대기)
[agents.critical_reviewer]
config_file = "<저장소>/assets/runtime_entrypoint/agents/critical-reviewer.toml"
```

### 3.10 모델 별칭 교란 정정 (`2a93ae4`, `cd126dc`)

- **문제:** 사용자가 "Sonnet 5.5와 Sonnet 5는 다른 모델"이라고 지적했다. 조사해 보니 replay 도구에 넘긴
  `sonnet` 별칭이 날짜마다 다른 모델로 해석되어 날짜 간 비교가 섞였다(2장 #8, #9).
- **해결:** Claude 별칭을 거부하고, 요청 모델과 실제 모델(`init` 이벤트 / Codex rollout `turn_context`)을
  결과에 함께 남긴다. `claude-sonnet-5` 고정 재실행으로 테스트 우선 효과(2/2)를 다시 확인했다.

## 4. 두 호스트 차이 (실측 기준)

| 항목 | Claude Code | Codex (codex-cli 0.155.0-alpha.16.3) |
|---|---|---|
| 전역 지침 | 플러그인 SessionStart hook | `~/.codex/AGENTS.md` 링크. 플러그인 hook은 `"hooks": {}`로 끔 |
| 스킬 | 플러그인 `skills/`(`chohogi:*`) | 플러그인 캐시(커밋 상태 복사)의 `skills/`. 링크는 따라가지 않음 |
| 역할 | 플러그인 `agents/` → `chohogi:<role>` | `config.toml`의 `config_file`. `~/.codex/agents` 링크는 스폰 거부 |
| 위임 도구 | `Agent`(`subagent_type`, `model`), `SendMessage`, `TaskStop` | `spawn_agent`(`agent_type`, `model`, `reasoning_effort`, `fork_turns`), `followup_task`, `wait_agent`, `list_agents`, `interrupt_agent` |
| 위임 허용 | 호스트 쪽 제한은 관측되지 않음 | 사용자나 AGENTS.md가 명시할 때만 스폰. AGENTS.md에 "실행 배정이 위임을 고르면 명시적 요청" 문장 있음 |
| 모델 생략 시 | 세션 모델 상속 | 세션 모델 상속(실측) |
| 역할별 강도 | 지정 불가(`not-selectable`) | `reasoning_effort`. `model`만 주면 강도가 그 모델 기본값으로 바뀜 |
| 세션 기록 | `claude -p --output-format stream-json`에 hook·도구 호출·비용 | `codex exec --json`에는 명령·파일 변경만. 스폰은 `~/.codex/sessions/.../rollout-*.jsonl` |
| 샌드박스 | — | 이 WSL 환경에서 기본 샌드박스가 시작되지 않음. replay는 버리는 프로젝트에서만 우회 |

## 5. 열린 항목

| 항목 | 상태 | 담당·조건 |
|---|---|---|
| Codex 역할 `config.toml` 등록 | 사용자 승인 대기 | 승인되면 README의 세 항목 추가 후 새 세션에서 스폰 확인 |
| Sazu의 `.agents/chohogi-external-capabilities.json` 부재 | Sazu 저장소가 할 일 | 초호기 쪽 원인: 외부 specialist 사용을 감지해 계약 선언을 요구하는 자동 트리거가 어느 호스트에도 없음(선언 규칙은 문장뿐) |
| route 파일을 실제로 읽었는지 측정 | 보류(중요도 중하) | replay에 관측용 단언으로 추가 예정 |
| 계획 전제가 사용자에 의해 부정될 때 계획 재검토 트리거 | 열림(초판 이월) | `sazu-source-first-divergence.md:121-124`. 아직 route 미선택 |
| 작업 중 자동 로깅(PostToolUse) | 논의만 함 | 미착수 |
| replay 관측 수 | 칸마다 1~2회 | 비율 주장 금지. 필요 시 `evaluation-budget-policy.md` 안에서 추가 |
| Codex 기준선(초호기 없음) replay | 미지원 | Codex가 `~/.codex/AGENTS.md`를 끄는 옵션이 없음 |
| 이전 Codex replay의 실제 모델 | 미기록 | `2a93ae4` 이후부터 기록됨 |

## 6. 두 호스트 공통 행동 지침

1. 진입 시 `.agents/chohogi-document-registry.json`의 활성 계획과 이 문서의 1·2장을 먼저 본다.
2. 목록에 보이는 것, 설치 성공, 문서 서술을 동작 증거로 쓰지 않는다. 새 세션 실행과 transcript로
   확인한 것만 "검증됨"으로 적고, 날짜와 호스트 버전을 붙인다.
3. 정본을 바꾸면 커밋한다. 커밋하지 않으면 Codex의 플러그인 스킬은 옛 내용을 본다.
4. 외부 방법을 들일 때는 이름으로 막지 말고, 기능을 소유 기관에 초호기 어휘로 다시 만든다. 출처는
   `THIRD_PARTY_NOTICES.md`에만 쓴다. 도구 이름이 붙은 경로나 다른 하네스의 스킬 호출 지시를 산출물에
   남기지 않는다.
5. 규칙이 지켜지는지 의심되면 `tooling/adherence-replay.py`로 시나리오를 돌린다. 모델은 정확한 id로
   고정하고, 결과의 `model`이 같은 것끼리만 비교한다.
6. 판정이 이상하면 결론을 내기 전에 transcript를 직접 읽는다. 이번 기간에 검사기 결함 다섯 건이 그렇게
   드러났다.
7. 개인 설정(`config.toml`, `settings.json`)과 홈 디렉토리 파일은 사용자 승인 없이 바꾸지 않는다. 옮길
   때는 지우지 말고 백업 폴더로 옮긴다.

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
