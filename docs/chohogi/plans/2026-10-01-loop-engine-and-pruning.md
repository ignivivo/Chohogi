# 학습 루프 엔진과 문서 정리

> **상태:** 완료(historical, 2026-10-01). 실행 기록 `HOM-20261001-loop-engine-and-pruning` finalize pass.
> 현재 활성 계획은 없다. 아래 "이관된 열린 항목"은 다시 열 조건이 생기면 새 계획으로 연다. 공동작업 기록
> (`docs/chohogi/feedback/codex-claude-cowork-20260928.md`, historical)에서 이관한 항목을 포함한다.

## 목표

1. learning 루프가 사건으로 돌게 한다: 트리거, 실패 유형 원장, 반복이면 검사 필수, 종료 조건.
2. 완료·수리 주장이 증거보다 강해지지 않게 한다.
3. 세션과 도구 어느 쪽도 쓰지 않는 규칙 문서를 정리하고, 오케스트레이션 문서 총량이 늘지 않게 한다.

3단계(제품 프로젝트 검증)는 사용자가 제품 프로젝트에서 초호기를 직접 쓰며 진행한다. 이 계획 범위가 아니다.

## 근거

- learning 마지막 사용 2026-08-12. 2026-10-01 기록 15개 중 learning 관문을 켠 기록 0개(공동작업 기록 3.21).
- 하루 안에 같은 실패 유형이 2~5회 반복(공동작업 기록 3.21, 이 계획의 실행 기록).
- 세션은 문장보다 도구와 검사를 따른다: 주입 지침의 문장 하나를 빼자 회귀, 검사는 같은 누락을 즉시 잡음(3.20).
- 작은 작업 replay 26개에서 route 문서 읽기는 4회뿐이었다. 큰 대화형 작업에서는 conductor·route 문서를 읽었다.

## 작업

상태 값은 `todo`, `in-progress`, `done`, `deferred`만 쓴다. `done` 행은 통과한 실행 기록 id와 증거 종류
(`static`, `replay`, `live`)를 증거 열에 적는다.

| id | 작업 | 상태 | 증거 |
|---|---|---|---|
| P0 | 공동작업 기록 종료, D2·D3 사용자 결정 기록, 활성 계획 등록 | done | `HOM-20261001-loop-engine-and-pruning` (static) |
| P1-trigger | debugging·homeostasis 기록, 사용자 교정·검증 실패 사실이 있는 기록은 finalize 전에 learning-assessment 필요(사유 있는 opt-out만 허용) | done | `HOM-20261001-loop-engine-and-pruning` (static: red→green tests) |
| P1-ledger | 실패 유형 등록부와 원장, assessment의 signature, 반복 유형은 존재하는 검사 없이 닫을 수 없음, learning-scan | done | `HOM-20261001-loop-engine-and-pruning` (static: red→green tests, verify-learning-contract) |
| P1-seed | 2026-09-30·10-01의 반복 유형을 원장에 등록하고 각 유형의 검사를 연결 | done | `HOM-20261001-loop-engine-and-pruning` (static: learning-scan, 8 signatures) |
| P1-status | 활성 계획의 done 행이 통과한 기록과 증거 종류를 인용하는지 검사 | done | `HOM-20261001-loop-engine-and-pruning` (static: red→green tests) |
| P2-measure | 세션 읽기와 도구 의존으로 문서별 사용 여부 측정 | done | `HOM-20261001-loop-engine-and-pruning` (replay: 26 sessions read counts; static: dependency map) |
| P2-prune | 사용되지 않는 문서 보관, 오케스트레이션 문서 총량 상한 | done | `HOM-20261001-loop-engine-and-pruning` (static: 2 docs removed, 2,138-line budget) |
| P2-replay | 7개 시나리오 replay 전후 비교 | done | `HOM-20261001-loop-engine-and-pruning` (replay: before 5/7, after 6/7, no lost rule) |

## 이관된 열린 항목 (이 계획에서 다루지 않음)

| 항목 | 다시 열 조건 |
|---|---|
| F14 모델 선택 비차단의 대화형 관측 | 대화형 세션에서 첫 지시와 위임이 함께 있을 때 |
| F19 Claude card 규칙의 필요성 | 사용자가 결정할 때 |
| F23(Codex), F27 | Codex 세션에서 초호기를 쓸 때 |
| F25 Claude 플러그인 캐시 잔여 사본 | 사용자가 정리를 원할 때 |
