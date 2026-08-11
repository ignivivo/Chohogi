<!-- chohogi:state-transition -->

# 상태 전이 · State transition

초호기는 한 작업에 둘 이상의 일상 route를 활성화하지 않는다. 상태 전이는 관찰 가능한
근거와 함께만 일어나며, `learning`과 `homeostasis`는 일상 route가 아니라 종료 뒤의 유지
과정이다.

| 상태 | 허용 전이 | 전이 근거 |
| --- | --- | --- |
| `direct` | `terminal` | 짧고 명확한 저위험 작업의 직접 검증 |
| `defer` | `terminal` | 증거·결정·권한 공백과 재진입 조건 |
| `active(product-decision)` | `active(delivery)` 또는 `terminal` | 사용자 또는 승인된 결정으로 수용 조건 확정 |
| `active(debugging)` | `active(delivery)` 또는 `terminal` | 원인 확인 뒤 수정 권한·범위 확정, 또는 진단 종료 |
| `active(delivery)` | `terminal` | 수용 조건별 검증 또는 명시된 차단 조건 |
| `terminal` | `learning` | 확인된 원인, 최소 예방, 해당 서명을 잡는 검증 증거 |
| `terminal` | `homeostasis` | 초호기 자체의 정책·수명주기·설치·발견·평가 경계에 대한 요청 또는 확인된 결함 증거 |
| `learning` / `homeostasis` | `terminal` | 귀속·승격·보류·퇴화 결정과 검증 근거 |

현재 수용 조건은 handoff에도 유지한다. 새 일상 route는 이전 route의 종료 근거와 새 route의
진입 근거가 작업 봉투에 함께 있을 때만 시작한다.

Homeostasis는 Homeostasis skill의 `references/admission-policy.md`에 있는 scope gate와
evidence gate를 모두 통과한 경우에만 시작한다. 단일 프로젝트의 failure가 Learning을 통해
candidate가 되었다는 사실만으로 Homeostasis가 자동 시작되지는 않는다.
