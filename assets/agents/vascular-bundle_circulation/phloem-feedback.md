<!-- chohogi:phloem=feedback-contract -->

# Phloem · 역방향 환류 계약

Phloem은 종료된 Delivery 또는 Debugging의 정제된 결과를 Learning 또는 Homeostasis로
되돌린다. controller·새 route selector·자동 전역 지식 주입기가 아니다.

## 진입 조건

- 원인이 `confirmed`이고, 재현 또는 고신호 검토 근거가 있다.
- 가장 작은 예방책이 해당 failure signature를 잡는 검증을 통과했다.
- 귀속지와 민감도·보존 범위를 판정할 수 있다.

## 최소 봉투

`failureSignature`, 영향, `causeStatus`, 기각한 가설, mechanism layer, primary prevention
scope, applicability, 기여 조건, evidence reference, 예방책, trigger/non-trigger, 검증 결과,
owner, expiry, destination만 보낸다.

원문 프롬프트, 고객·출생 정보, API 키·세션, 전체 도구 payload·로그는 넣지 않는다. 증거가
부족하면 `closed-no-learning`으로 종료하고 영속 자산을 만들지 않는다.
