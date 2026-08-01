# LRN-0001 — 일상 route 계약과 보류 경계

- 상태: `confirmed`
- 기록일: 2026-08-01
- 소유 경계: 초호기 `trunk`의 conductor·daily route·route evaluation
- 분류: Markdown 작업 지침 / Codex 작업 분류 / 계약 검증 / 고신호 독립 감사
- 예방 범위: 초호기 자체. 새 프로젝트 스킬이나 역할에는 적용하지 않음.

## 관측된 문제

초호기는 `product-decision`, `delivery`, `debugging`의 이름과 선택 기준은 있었지만,
각 흐름의 입력·절차·금지 행동·종료 조건을 별도 계약으로 강제하지 않았다. 따라서 같은
요청도 세션마다 다른 작업 절차로 해석될 수 있었고, 다음 구체적 결함이 독립 감사에서
확인됐다.

- 증거가 없는 전역 스킬 생성 요구를 `direct`로 낮춰 해석할 여지
- debugging의 진단-only 종료와 상위 표의 무조건적인 `수정 검증` 요구의 충돌
- 변경 권한(`requested`)과 원인 확인 전 수정 금지의 혼동
- `defer`가 실제로 모든 flow를 금지하고 재진입 조건을 남기는지 검증하지 않음
- Python·PowerShell 검증기의 배열 중복 판정 차이

## 가설과 판정

| 가설 | 판정 | 근거 |
| --- | --- | --- |
| 모델 등급을 높이면 분류가 안정된다 | 기각 | 문제는 추론량이 아니라 문서 계약과 fixture 부재였다. |
| 새 전역 스킬·역할이 필요하다 | 기각 | 기존 conductor와 세 daily route의 경계를 보강하는 것이 최소 예방책이었다. |
| daily route 계약과 구조 검증이 필요하다 | 확인 | 독립 감사가 위 결함을 재현했고, 음성 변이를 포함한 검증기가 모두 거부했다. |

## 수정과 근거

`assets/agents/chohogi/trunk/routes/`에 세 daily route의 공통 섹션 계약을 추가하고,
`trunk/evals/route-fixtures.json` 및 `tooling/verify-routes.py/.ps1`로 문서·fixture
경계를 검사한다.

핵심 전후 차이는 다음과 같다.

```text
이전: substantial 작업 → 이름이 있는 흐름을 선택
이후: substantial 작업 → 엄격한 진입 조건이 맞는 흐름 하나
      조건이 없고 고영향 지속 변경이면 defer(no-flow, no-write)
```

`defer` fixture는 다음 산출물을 모두 요구한다.

```text
evidence-gap + no-change + reentry-condition
```

이는 변경 권한이 있더라도 원인·효과 근거가 없으면 지속 변경을 하지 않는다는 뜻이다.
debugging도 `재현·관측 근거·원인 상태·제안 또는 권한 있는 수정 검증`으로 바꿔
진단-only 종료와 일치시켰다.

## 검증과 예방 판정

실행한 검증:

- Windows Python: `tooling/verify-routes.py` 통과
- Windows PowerShell: `tooling/verify-routes.ps1` 통과
- WSL Python: `tooling/verify-routes.py` 통과
- Windows·WSL의 새 임시 홈 설치 및 `doctor` 통과
- 활성 Windows 설치본의 핵심 자산 SHA-256 일치
- 구현자와 분리된 계약 감사 및 fixture 비열람 독립 재생 통과

검증기는 빈 요청, 금지된 흐름 선택, branch를 daily route로 인코딩한 경우, flow를 가진
`defer`, 모든 flow를 금지하지 않은 `defer`, `defer` 필수 산출물 누락, 중복된
`mutationAuthorities`, 필수 section/정책 marker 누락을 각각 거부한다.

가장 작은 예방책은 새 skill이 아니라 기존 conductor의 명시와 fixture 기반 verifier다.
이 기록은 초호기 고유 변경의 상세 이력이며, 아직 다른 독립 프로젝트에서 같은 원인과
예방 효과가 확인되지 않았으므로 amyloplast로 승격하지 않는다.

## 이후 검토

- 실제 서로 다른 모델·새 세션 replay 결과가 충분히 쌓이면 분류 정확도, 불필요한 모델
  승격, 재작업 횟수를 baseline과 비교한다.
- 동일한 contract drift가 다른 프로젝트에서도 확인될 때만 amyloplast 승격을 재평가한다.
