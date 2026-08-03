# Route evaluation

이 디렉터리는 초호기의 주장과 실제 성능을 구분해 검증한다. fixture는 모델을
자동으로 채점하는 마법이 아니라, 무엇을 확인해야 하는지 고정하는 계약이다.

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

`tooling/verify-routes.ps1` 또는 `tooling/verify-routes.py`는 fixture와 route 문서의
정적 계약을 검증한다. 실제 모델의 선택은 아래 replay로 확인한다.

`execution-fixtures.json`은 실행 배정의 별도 행동 계약이다. 모든 fixture는 외부
controller와 불필요한 실행 방식 질문을 금지한다. `tooling/verify-execution-allocation.ps1`
또는 `tooling/verify-execution-allocation.py`는 실행 형태 전부의 coverage, 금지 결과,
실행 배정·xylem·연속성 봉투 문서의 경계를 검사한다.

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

baseline과 Chohogi를 비교할 때는 같은 작업 설명, 모델, 추론 강도, 도구 조건,
저장소 상태를 사용한다. 한 번의 응답으로 승패를 정하지 말고, 중요한 fixture는
반복 실행하거나 독립 검토로 채점한다.

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
