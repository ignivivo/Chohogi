# Sazu 사주 프로젝트 → 초호기 운영 하네스 handoff

> 작성일: 2026-09-22
> 대상: 초호기의 계획·실행 배정·작업 기록 운영 개선
> 범위: Sazu에서 실제로 발생한 계획 드리프트·중복·검수 병목과 예방 기준

## 1. 왜 이 handoff를 남기는가

Sazu 사주 프로젝트는 계산 엔진과 해석 계약을 상당히 구현했지만, 작업 중 발견된
문헌·제품·검수 요구를 그때그때 별도 문서에 추가하면서 실행 속도가 크게 떨어졌다.
이미 구현한 것을 다시 계획하거나, 완료된 작업을 다른 전문가 검토에서 다시 시작하는
중복도 발생했다.

이 handoff는 Sazu의 명리 규칙 자체를 초호기에 이식하는 문서가 아니다. 다음과 같은
반복 방지·상태 정합성·handoff 운영 원칙을 일반화해 전달한다.

## 2. 확인된 사실과 근거

### 구현은 대부분 재사용 가능했다

- `src/lib/calendar/manseryeok-adapter.ts`: 한국 KASI 기반 만세력으로 교체
- `src/lib/saju.ts`: 원국·대운·세운 계산과 진태양시 context 연결
- `src/lib/interpretation/`: Fact → RuleEvaluation → Resolver → Claim → projection 경계
- 신살 앵커·위치·원국/대운/세운 ledger
- 무료·유료가 같은 Claim graph를 소비하는 projection 구조

근거: `docs/work-log/records/DEL-20260922-manseryeok-migration/`, 전체 테스트·lint·build
결과, `docs/work-log/records/REV-20260922-saju-process-thesis/synthesis.md`.

### 실제 병목은 코드 재작성보다 운영 상태였다

- corpus는 36 rule atoms / 47 fixtures / source ledger 27 records였지만 문서 일부는
  33/42/24를 계속 표시했다.
- registry가 legacy `status`를 별도로 보유하고 corpus의 실제 상태와 충돌했다.
- `calculationStatus`, `interpretationStatus`, `variantStatus`를 도입했지만 corpus에
  직접 이행하지 않고 registry에서 파생했다.
- PRD·remediation plan·PROJECT-STATE가 서로 다른 완료 상태를 한동안 보유했다.
- hidden-stem source audit/adjudication, strength adjudication/protocol처럼 연결된 검토가
  여러 work-log로 분리됐다.
- publication gate가 계산 Fact와 개인화 해석 Claim을 모두 같은 승인 조건으로 막아,
  고객용 Claim이 0개인 상태를 정상 테스트로 고정했다.

근거: `docs/work-log/records/REV-20260922-saju-process-antithesis/synthesis.md`,
`REV-20260922-saju-process-thesis/synthesis.md`, `PROJECT-STATE.md`,
`src/lib/interpretation/contract-validator.ts`, `publication-policy.ts`.

## 3. Sazu에서 채택한 최종 운영 기준

현재 실행 순서는 [Sazu 사주 마감 실행 큐](../../../../Sazu/docs/plans/2026-09-22-saju-finish-queue.md)에
고정했다.

1. 문서 소유권을 분리한다.
   - PRD/PD: 결정과 범위
   - active plan 하나: 실행 큐와 완료 조건
   - PROJECT-STATE: 현재 상태
   - work-log: 과거 근거·정반합·검증 결과
2. 이미 있는 코드·Claim·renderer를 먼저 재사용한다.
3. 계산 Fact 승인과 해석 Claim 승인을 분리한다.
4. 작은 원자 하나를 계산 → Resolver → 무료 요약 → 유료 상세까지 연결하는 수직 slice로
   완료한다.
5. 각 slice마다 정·반·합과 fixture·검증 명령을 하나의 work-log에 기록한다.
6. 새 계획·새 전역 점수·새 Evidence Graph는 기존 구현의 실제 누락이 확인될 때만 만든다.

## 4. 초호기 하네스에 반영할 예방 규칙

### 작업 시작 시

- 현재 active plan과 PROJECT-STATE를 먼저 읽고, 이미 완료된 producer·consumer·fixture를
  capability map으로 고정한다.
- 같은 기능을 다루는 과거 work-log를 검색해 “재사용 / 수정 / 신규”를 명시한다.
- 문서 수치와 코드·validator 수치가 다르면 구현보다 먼저 drift를 기록하고 기준본을
  하나 선택한다.

### 전문가 검토 시

- 두 전문가를 독립적으로 실행하되, 최종 산출물은 정·반·합 통합본 하나를 반드시 만든다.
- 정·반 문서는 독립 근거이고, 합 문서만 다음 구현의 결정 입력이다.
- 같은 규칙을 다시 검토할 때는 이전 synthesis와 변경 diff를 reviewer에게 전달하고, 새
  근거가 없으면 “변경 없음”으로 종료한다.

### 완료 판정 시

- “구조가 존재함”과 “고객 Claim이 공개됨”을 분리한다.
- 테스트가 빈 projection을 정상으로 기대하면, 문서에서 콘텐츠 완성이라고 쓰지 않는다.
- 전체 테스트 통과는 코드 회귀 증거일 뿐 명리 해석 승인이나 상용 콘텐츠 완성을 뜻하지 않는다.
- work-log outcome에는 실제 artifact 경로, 검증 명령, 남은 위험을 포함한다.

## 5. 초호기 적용 시 권장 변경

1. active plan을 하나만 허용하고, 이전 plan은 자동으로 archive 링크를 남긴다.
2. plan 상태에 `implemented`, `gated`, `content-review`, `blocked-by-evidence`를 구분한다.
3. 문서 수치가 corpus·validator 출력과 다르면 finalize를 거부한다.
4. 독립 reviewer 응답을 받은 뒤 integrator가 반드시 synthesis artifact를 생성해야 완료로
   인정한다.
5. 동일한 scope·근거·코드 경로를 가진 새 작업은 이전 record를 재사용하도록 경고한다.
6. “완료” 보고 전에 사용자 결과 surface에 실제 claim이 도달했는지 producer-consumer 검사를
   요구한다.

## 6. 적용하지 않는 것

- Sazu의 한국 명리 규칙·출처·고객 콘텐츠를 초호기 전역 자산으로 복사하지 않는다.
- private prompt, 내부 원문 reasoning, 비밀값, 고객 개인정보를 handoff에 넣지 않는다.
- 특정 모델·특정 명리 학파를 초호기 공통 정책으로 승격하지 않는다.

## 7. 현재 Sazu의 재개 기준

다음 Sazu 작업은 새 아키텍처가 아니라 `P0 원장·게이트 정합화 → P1 첫 승인 수직 slice →
P2 영역 확장 → P3 제품 통합` 순서로 재개한다. 각 단계가 끝나면 Sazu의 PROJECT-STATE와
해당 work-log만 갱신하며, 초호기에는 이 handoff의 일반 운영 교훈만 참조시킨다.
