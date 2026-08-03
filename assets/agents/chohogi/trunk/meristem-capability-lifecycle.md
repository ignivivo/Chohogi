<!-- chohogi:meristem=capability-lifecycle -->

# Meristem · capability lifecycle

Meristem은 상시 controller나 자동 agent 생성기가 아니다. Homeostasis가 반복 증거를 검토할
때만 후보 자산의 생성·시험·승격·퇴화를 판정하는 lifecycle gate다.

## 상태

`candidate → trial → resolution`만 사용한다. candidate는 자동 발견·자동 호출·영구 권한을
갖지 않는다.

## 후보 필수 정보

문제 서명, owner, trigger/non-trigger, 기존 자산 중복 검사, 비교 대상, 평가 fixture, 예상
효과·허용 비용·오탐, expiry, rollback 또는 prune 조건을 남긴다.

## 해소

1. 기존 leaf에 흡수
2. 프로젝트 leaf로 귀속
3. 전역 후보 유지
4. Homeostasis가 승인한 전역 core·역할 정책 보강
5. `superseded`, `rejected`, `retired`로 퇴화

새 조직계·영구 역할은 독립 사례, 적대적 반례, 비교 평가, owner, 폐기 계획을 요구하는
4번의 고문턱 사례다. 한 번의 인상적인 실행이나 단순 prompt 별칭으로 만들지 않는다.
