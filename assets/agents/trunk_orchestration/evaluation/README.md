# Route evaluation

이 디렉터리는 초호기의 주장과 실제 성능을 구분해 검증한다. fixture는 모델을
자동으로 채점하는 마법이 아니라, 무엇을 확인해야 하는지 고정하는 계약이다.

## 기능 보증과의 경계

기능보증은 `../functional_assurance/registry.json`과
`python3 tooling/verify-functional-assurance.py`가 소유하는 횡단 관측 기관이다.
이 디렉터리는 route·allocation·capability의 fixture와 replay 평가를 소유한다. 기능보증이
발견한 claim–evidence 결손은 delivery에서 즉시 수용 조건으로 처리하고, 반복되거나
전신 정책을 바꿀 결손만 Homeostasis가 수리 판단으로 승격한다.

## 지금 가능한 구조 검증

`route-fixtures.json`의 각 요청에 대해 conductor가 고르는 결과를 다음 기준으로
확인한다.

1. `expected.kind`가 `direct` 또는 `defer`이면 별도 flow를 만들지 않는다. `defer`는 모든 flow를 금지하고, 변경 권한이 `requested`여도 증거 공백과 재진입 조건만 남긴 채 지속 변경을 하지 않는 보류·무변경 결과다.
2. `expected.kind`가 `daily-route` 또는 `branch`이면 정확히 하나의
   `expected.flow`를 선택한다.
3. `forbiddenFlows`에 있는 daily route·branch를 선택하거나 실제로 실행하지 않는다.
4. `requiredArtifacts`에 해당하는 산출물·증거가 응답에 있다.
5. `mutationAuthority`가 `none`이면 조사·설명·계획만 수행하고 지속 변경을 하지 않는다. `requested`는 변경 권한일 뿐이며, debugging의 증거 수집·원인 확인 전 추측 수정을 허용하지 않는다.
6. debugging은 재현 또는 증거 수집 전에 추측 수정하지 않고, learning은 확인되지 않은
   원인을 승격하지 않는다.
7. `defer` fixture는 `evidence-gap`, `no-change`, `reentry-condition`을 모두 요구해
   보류 사유와 재개 조건을 빠뜨리지 않는다.

`tooling/verify-routes.py`는 fixture와 route 문서의
정적 계약을 검증한다. 실제 모델의 선택은 아래 replay로 확인한다.

`execution-fixtures.json`은 실행 배정의 별도 행동 계약이다. 모든 fixture는 외부
controller와 불필요한 실행 방식 질문을 금지한다. `tooling/verify-execution-allocation.py`는 실행 형태 전부의 coverage, 금지 결과,
실행 배정·xylem·연속성 봉투 문서의 경계를 검사한다.

`capability-fixtures.json`은 초호기 내부 방법, Codex 기본 능력, 현재 호출 가능한 외부
provider, 프로젝트 leaf, provider 불가 시 fallback을 구분하는 행동 계약이다. 모든
fixture는 외부 controller를 금지한다. `tooling/verify-capability-boundary.py`는 이 분류·금지 결과·원본 방법론 재호출 금지를
정적으로 검사한다. 이 검사는 실제 플러그인 설치·인증 상태를 검사하거나 바꾸지 않는다.

## Replay 평가

각 fixture를 새 세션에서 실행해 다음 형식으로 결과를 남긴다. 개인 정보, 비밀값,
원문 고객 데이터는 기록하지 않는다.

```text
fixture: debug-test-failure-unknown-cause
profile: baseline | chohogi
model / effort: ...
selected kind / flow: ...
forbidden flow invocation: none | ...
persistent change despite authority=none: no | yes
artifact completeness: pass | partial | fail
unnecessary model escalation: none | ...
evidence and notes: ...
```

실행 배정 replay에는 아래도 남긴다.

```text
fixture: written-plan-no-handoff-menu
selected allocation: direct | sequential | scoped-delegation
role ownership: ...
asked user to choose execution method: no | yes
external skill acted as controller: no | yes
parallel implementation on shared files: no | yes
```

능력 경계 replay에는 아래도 남긴다.

```text
fixture: authenticated-live-action
selected capability classification: ...
runtime availability evidence: ...
external provider acted as controller: no | yes
assumed cache means authorization: no | yes
fallback changed private config or authentication: no | yes
```

baseline과 Chohogi를 비교할 때는 같은 작업 설명, 모델, 추론 강도, 도구 조건,
저장소 상태를 사용한다. 한 번의 응답으로 승패를 정하지 말고, 중요한 fixture는
반복 실행하거나 독립 검토로 채점한다.

## 구조화된 replay 기록

각 실행 결과는 `replay-result.schema.json`의 필드만 가진 JSON으로 별도 평가 저장소나
비밀 없는 작업 기록에 남긴다. 원문 프롬프트·출생정보·고객정보·비밀값·도구 payload는
기록하지 않는다. `validate-replay-result.py <result.json>`은 필수 필드와 결과 축을
검사한다. baseline과 chohogi는 같은 fixture·model·effort·toolCondition·repoCondition
조합으로 최소 두 번씩 실행한 뒤에만 비용·재작업·controller 침범을 비교한다.
`replay-result.example.json`은 결과 형식 검증용일 뿐 성능 증거가 아니며,
`summarize-replays.py`는 검증된 결과 파일만 profile별 지표로 집계한다.

## 세션 준수 replay

위 replay는 사람이 새 세션을 돌리고 결과를 적는다. 세션이 규칙을 실제로 따랐는지는
`tooling/adherence-replay.py`가 기계적으로 확인한다. `adherence-scenarios.json`의 각
시나리오는 버릴 프로젝트를 만들고, 실제 호스트 세션(Claude Code `claude -p
--output-format stream-json`, Codex `codex exec --json`)을 실행한 뒤, 모델이 한 말이 아니라
**도구 이벤트 순서·바뀐 파일·사후 검사**로 단언을 판정한다(예: 수정 전에 테스트를 돌렸는가,
마지막 변경 뒤에 검증을 다시 했는가, 테스트 파일을 약하게 고치지 않았는가, 도구 이름이 붙은
경로를 만들지 않았는가, 요청하지 않은 push·merge를 하지 않았는가).

```bash
python3 tooling/adherence-replay.py run --host claude --profile chohogi --model <고정 모델> --out <저장소 밖 경로>
python3 tooling/adherence-replay.py run --host claude --profile baseline --model <같은 모델> --out <저장소 밖 경로>
python3 tooling/adherence-replay.py run --host codex --profile chohogi --out <저장소 밖 경로>
python3 tooling/adherence-replay.py analyze --host claude --scenario <id> --transcript <file> [--project <dir>]
```

- `baseline`은 Claude Code에서 사용자 설정을 빼(`--setting-sources project,local`) 초호기 플러그인
  없이 실행한다. 두 profile은 같은 모델을 고정한다.
- 모델은 별칭(`sonnet` 등)이 아니라 정확한 id(`claude-sonnet-5-5` 등)로 고정한다. 별칭은 날짜에 따라
  다른 모델을 가리킬 수 있어 전후 비교를 조용히 깨뜨린다(2026-09-29 `sonnet`→`claude-sonnet-5`,
  09-30 →`claude-sonnet-5-5` 관측). 도구는 Claude 별칭을 거부하고, 결과에 요청 모델(`requestedModel`)과
  실제로 돈 모델(`model`)을 함께 남긴다. 비교는 `model`이 같은 결과끼리만 한다. Codex는 `~/.codex/AGENTS.md`를 끄는 옵션이
  없어 baseline을 지원하지 않는다.
- 원문 transcript는 `--out`(저장소 밖)에만 남고, 결과 JSON에는 단언별 통과 여부와 짧은 사유,
  이벤트 수, 비용만 들어간다.
- 실행은 모델 비용을 쓰므로 `evaluation-budget-policy.md`의 paired replay 조건 안에서만 한다.
  한 번의 실행은 관측이지 비율이 아니다.
- 새 규칙을 넣을 때는 먼저 baseline에서 그 규칙이 깨지는 시나리오를 확인하고(빨강), 규칙을 넣은
  뒤 chohogi profile에서 통과하는지(초록) 본다. 통과가 규칙 때문인지 가리려면 둘 다 필요하다.

## 실제 작업 성능 평가

실제 작업이 충분히 쌓인 뒤에는 같은 유형의 작업군에서 다음을 비교한다.

- route 선택·산출물 계약 충족률
- 사용자 정정·재작업 횟수
- 검증 누락과 같은 실패의 재발
- 불필요한 고비용 모델·위임 호출
- 실행 방식 질문·외부 controller 재발
- 완료까지 걸린 반복 횟수와 사용 가능한 토큰·비용 정보

효과 없는 skill·규칙은 보유 수를 늘리기 위해 유지하지 않는다. 확인된 실패만
`learning`을 통해 가장 작은 예방 자산으로 바꾸며, 초호기 자체의 정책·수명 주기를
바꿀 증거가 있을 때만 `homeostasis`로 승격한다.
