<!-- chohogi:document-lifecycle -->

# 문서 lifecycle 및 참조 계약

이 계약은 Superpowers에서 흡수한 계획→실행→검증→피드백의 유효한 패턴을 초호기
문서 topology에 적용한다. 외부 하네스나 별도 controller를 만들지 않으며, 기존
`conductor → branch → allocation → execution record → verification → feedback`
흐름을 보강할 뿐이다.

## 역할과 권위

| 역할 | 소유하는 것 | 실행 지시인가 |
| --- | --- | --- |
| `decision` | 제품·정책 선택과 결정 이유 | 아니오 |
| `active-plan` | 현재 실행 큐·순서·완료 조건 | 예, 프로젝트당 하나 |
| `state-projection` | 현재 상태의 요약 | 아니오 |
| `execution-record` | 사실·결정·artifact·handoff·feedback 이력 | 아니오 |
| `feedback-source` | 관찰·문제 제기·외부 의견 | 아니오 |
| `review-synthesis` | 독립 검토를 통합한 판정과 반박 | 아니오 |
| `history` | 과거 맥락·감사 증거 | 아니오 |

문서에는 가능한 경우 `role`, `authority`, `state`, `consumers`, `allowedReferences`,
`forbiddenUse`를 선언한다. 선언하지 못한 문서는 실행 지시로 승격하지 않는다.

## 허용 참조 방향

```text
decision → active-plan → execution-record / code / fixtures
execution-record / verification / feedback / review-synthesis → active-plan 갱신
active-plan / execution-record / verification → state-projection
history → evidence only
```

`feedback-source`나 `review-synthesis`는 계획을 직접 대체하지 않는다. 응답은
`feedback` 이벤트로 `plan-updated`, `deferred`, `rejected`, `no-action` 중 하나를
명시하고, `plan-updated`일 때 활성 계획 target을 남긴다.

## lifecycle

```text
draft → active → executing → review → accepted | revised | deferred → historical
```

`historical` 문서는 실행 경로·현재 상태·완료 근거로 참조하지 않는다. 한 질문·독자·
소유권·변경 주기를 공유하는 문서는 통합하며, thesis/antithesis/synthesis처럼 근거와
통합 판정이 필요한 경우 대표 synthesis 하나를 현재 feedback source로 삼고 나머지는
그 근거로 연결한다.

## 금지되는 승격

- `state-projection`의 오래된 문구를 현재 active-plan보다 우선하지 않는다.
- `execution-record`의 pass나 문서 존재를 현재 계획 완료로 해석하지 않는다.
- `review-synthesis`를 새 active-plan으로 복제하지 않는다.
- `history`·archive를 현재 실행 지시로 읽지 않는다.
- 파생 상태·완료·건강·승인 값이 원본 evidence보다 강해지면 안 된다. 명시적
  resolution과 근거가 없는 상태 승격은 거부한다. `tooling/verify-status-provenance.py`
  는 각 상태 주장에 `sourceEvidenceRefs`가 선언되어 catalog된 파일로 추적 가능한지,
  승격 근거가 있는지, 미해결 원본 충돌이 긍정적 파생 상태로 바뀌지 않는지 검사한다.
  파일 존재와 참조 연결은 evidence가 그 상태 의미를 실제로 증명하는지까지 판정하지 않는다.

## 종료 검사

material 작업은 활성 실행 소유자, 소비자, 현재 수용 조건, feedback source와 남은
위험을 확인한다. 파일 존재·해시·`finalize` 통과만으로 문서 의미의 정합성이나 실제
향후 모델 준수를 주장하지 않는다.

프로젝트가 material 문서·계획을 유지하면 `.agents/chohogi-document-registry.json`을
두고 `tooling/verify-project-document-registry.py --root <project>`로 먼저 검사한다.
registry가 없는 새 material 프로젝트는 문서 권위와 활성 계획을 선언할 수 있을 때까지
`defer`하거나 registry를 만드는 범위만 수행한다. registry 검사는 선언된 경계를
검증하며, 선언되지 않은 문서의 의미 준수까지 보증하지 않는다.
