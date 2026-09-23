# Sazu 프로젝트 감사에서 초호기로 넘기는 피드백

상태: `feedback-only`
범위: Sazu 저장소의 PRD·PD·계획·코드·테스트·명리 규칙 DB·작업 기록을 대조한 감사
원본 기록: `Sazu / REV-20260922-project-plan-audit`
목적: 초호기 정책을 즉시 바꾸는 것이 아니라, 다른 프로젝트에도 적용할 수 있는 작업 운영상의 관찰과 검토 질문을 전달한다.

## 관찰된 문제

Sazu는 다음을 비교적 잘 갖추고 있었다.

- 제품 결정, 화면 정보구조, 계산 Fact, Claim, Projection, Renderer를 분리했다.
- 단일 표준 관법과 질문별 체크리스트를 채택했다.
- Resolver와 source/rule corpus, fixture, 실행 기록을 도입했다.
- 테스트·lint·build는 통과했다.

그러나 작업 결과는 다음과 같은 운영 병목을 보였다.

1. **결정·계획·상태 문서의 수치와 상태가 뒤처졌다.** 실제 rule/fixture/source 수와 `PROJECT-STATE`, remediation plan의 기록이 달랐다.
2. **활성 계획이 둘 이상이었다.** 콘텐츠 계획과 엔진 remediation 계획이 겹치면서 현재 실행 큐가 불분명해졌다.
3. **기록은 많이 남았지만 회수·적용 여부는 별개였다.** 결정과 감사 기록이 존재해도 코드·UI 소비자가 반드시 그 내용을 반영하는 것은 아니었다.
4. **검수 게이트가 제품 결과를 과도하게 차단했다.** 모든 고객 의미 Claim에 `approved + expert-reviewed + corpus mapping`을 요구했으나, corpus의 승인 원자가 0개여서 의미 있는 개인화 결과가 거의 차단됐다.
5. **설계 성공과 제품 완성을 혼동할 위험이 있었다.** Resolver, ledger, projection 구조의 존재는 판매 가능한 콘텐츠·entitlement·공유·브라우저 검증의 완료를 뜻하지 않았다.
6. **서로 다른 상태 축이 하나로 섞였다.** 계산 정확성, 전통 규칙 근거, 제품 정책, 고객 공개 허가, 예측 타당성이 하나의 승인 상태로 압축될 위험이 있었다.

## 일반화 가능한 원칙

### 1. 결정 문서·실행 계획·운영 상태를 분리하고 단일 활성 큐를 둔다

- PRD/PD는 제품 약속과 결정만 소유한다.
- 계획 문서는 하나만 활성 실행 큐로 둔다.
- 이전 계획은 `historical`로 명시하고 현재 완료 조건을 소유하지 않는다.
- PROJECT-STATE는 수동으로 숫자를 복사하지 말고 검증 명령의 결과 또는 생성 시각을 함께 기록한다.
- 작업 기록은 감사 이력이지 백로그나 실행 지침이 아니다.

### 2. “기록됨”과 “소비됨”을 별도 수용 조건으로 둔다

각 결정에는 다음을 구분한다.

```text
결정 존재
→ 관련 소비자 식별
→ 소비자 구현 또는 명시적 보류
→ 소비자 테스트
→ 실제 화면/출력 확인
```

문서에 결정이 있다는 사실만으로 구현 완료를 표시하지 않는다.

### 3. 검수 상태를 단일 승인 플래그로 만들지 않는다

서로 다른 축을 별도로 유지한다.

```text
calculationStatus       계산 재현성·fixture 상태
protocolStatus          채택한 관법에서의 사용 가능성
sourceStatus            출처·원문 검토 상태
productPolicyStatus     임계값·가중치 등 제품 선택
publicationStatus       고객 출력 허용 여부
predictionValidity      현실 예측 타당성(별도 미검증/unknown 가능)
```

내부 검수 상태를 분리하면, 모든 세부 문헌 검토가 끝나기 전에도 명확히 채택한 기본 규칙으로 제품을 개발할 수 있다. 반대로 불확실한 변형 규칙은 `variant/provisional`로 남겨 기본 결과에서 제외할 수 있다.

### 4. 구조 구현과 제품 완성을 별도로 평가한다

다음은 독립된 acceptance gate다.

- 계산·규칙 엔진
- Claim/Resolver/Projection 계약
- 고객 콘텐츠 완성도
- 결제·entitlement·공유
- 브라우저·접근성·실제 provider 검증

앞 단계 테스트가 통과해도 뒤 단계 완료를 암시하지 않는다.

### 5. 반복 작업에서는 “문서 추가”보다 “상태 회수”를 평가한다

평가할 때 문서 수·로그 수·토큰 수를 품질 지표로 쓰지 않는다. 대신 다음을 관측한다.

- 결정 누락으로 인한 재작업 횟수
- 계획과 구현 상태의 불일치 건수
- 관련 결정이 실제 소비자에 반영된 비율
- 승인 게이트로 인해 정상 기능이 차단된 비율
- 성공 결과당 총 비용과 검토 시간

## 초호기에서 확인할 질문

이 자료만으로 전역 정책을 즉시 변경하지 않는다. 다음 반복 사례가 다른 프로젝트에서도 확인될 때에만 candidate 또는 reusable method로 승격 검토한다.

1. 초호기의 문서 회수 지침이 실제 소비자 검증까지 연결되지 않는 사례가 반복되는가?
2. execution record가 존재하지만 active plan과 상태 drift를 잡지 못하는가?
3. 하나의 승인 플래그가 계산·근거·제품 공개를 잘못 묶는가?
4. 프로젝트마다 계획 문서가 여러 개 생겨 단일 실행 큐가 사라지는가?
5. 지나치게 보수적인 gate가 제품의 정당한 기본 기능을 차단하는가?

## 현재 범위와 한계

- 이것은 Sazu 한 프로젝트의 감사에서 나온 고신호 관찰이다. 전역 정책의 인과 효과나 모든 프로젝트의 일반 법칙으로 승격하지 않는다.
- Sazu의 명리 규칙·출처·점수식은 이 문서에 복사하지 않는다. 도메인 원본과 내부 방법론은 Sazu 저장소가 소유한다.
- 이 문서는 활성 스킬·route·모델 정책이 아니며, 새 세션에 자동 주입하지 않는다.
- 전역 candidate가 필요하면 별도 `genome_inheritance/candidates` 계약과 두 프로젝트 이상의 독립 적용 증거를 따른다.

## 검증 참고

- Sazu 감사 실행 기록: `REV-20260922-project-plan-audit`
- Sazu 원본 상태 문서: `PROJECT-STATE.md`
- Sazu 활성 remediation 계획: `docs/plans/2026-09-17-saju-engine-review-remediation.md`
- 초호기 관련 기준: `assets/agents/trunk_orchestration/context-packet.md`, `execution-record-contract.md`, `genome_inheritance/README.md`
