<!-- chohogi:method-selection -->

# Reusable methods · 실행 방법 카탈로그

Branch는 순서·산출물·종료 조건을 정하고, reusable method는 실제 전문 방법을 제공한다. 이 문서는
controller가 아니며 TDD·조사·리뷰를 모든 작업에 강제하지 않는다.

- 순수 규칙, 상태 전이, 확인된 회귀에는 실패 조건과 회귀 검증을 먼저 설계한다.
- UI 탐색, 구성, 문서, 레거시 변경은 수용 조건과 직접 검증에 맞는 방법을 고른다. 실질적인 사용자 대면 UI 추가·재설계·시각 상호작용 변경에서는 먼저 `frontend-surface`로 과업·위계·구성·기존 시스템 적합성·후속 위험 handoff를 검토한다. 이는 UI 내부의 검토 순서일 뿐 route·권한·완료 조건을 선택하는 controller가 아니다.
- 변경된 사용자 대면 semantic·interactive surface에는 `accessibility`를 반드시 적용한다. 미디어·폰트·모션·above-the-fold·client rendering 또는 렌더링 비용 변화에는 `performance`와 필요시 `core-web-vitals`를 적용하고, 비동기 UI 상태 변화에는 `react-async-state-safety`를 적용한다.
- 원인 불명 실패는 재현·관찰·가설 판별을 우선하며, 원인 확인 전 추측 수정하지 않는다.
- 고위험 계약·보안·개인정보·결제·다중 소비자 변경은 독립 검토를 고려한다.
- 선택한 reusable method가 없거나 부적합해도 수용 조건·회귀 위험·검증 증거의 의무는 남는다. 프로젝트 leaf는 전역 method의 별칭이 아니라 프로젝트의 코드·CI·fixture를 가진 적응 자산일 때만 만든다. 이
  카탈로그는 별도 controller가 아니다.
