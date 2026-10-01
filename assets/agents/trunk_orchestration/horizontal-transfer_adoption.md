<!-- chohogi:skill-adoption -->
<!-- chohogi:adoption-authority=homeostasis -->

# 외부 자산 채택 계약

외부 skill·방법 묶음·provider를 발견했을 때 Homeostasis가 적용한다. 이는 매 작업의
controller가 아니며, 현재 작업에서 이미 호출 가능한 능력을 막지 않는다.

## 판정 상태

| 상태 | 의미 | 정본 |
| --- | --- | --- |
| `absorb-core` | 초호기의 흐름·배정·검증을 구성 | 초호기 내부 자산만 실행 |
| `mirror-baseline` | 오프라인에서도 필요한 범용 지침 | 초호기 이식본 + provenance |
| `attach-specialist` | 가끔 필요한 전문 지침 | 외부 원본, 현재 호출 가능할 때만 사용 |
| `provider` | 인증·MCP·도구·원격 데이터가 필요한 실제 능력 | 외부 provider, 초호기는 호출만 결정 |
| `project-leaf` | 한 프로젝트에만 유효한 규칙 | 프로젝트 Git |
| `reject` | 중복·불명확·위험·검증 불가 | 채택하지 않음 |

## 최소 증거

채택 전 원본 주소, 라이선스, 기준 revision 또는 `unverified`, trigger와 non-trigger,
필요 리소스, 충돌 가능성, 검증 방법을 기록한다. `security_immune_system/project-adapter-contract.md`와
`tooling/scan-skill-intake.py`의 intake protocol에 따라 원본 root 전체에
`python3 tooling/scan-skill-intake.py <source-root> --output <redacted-inventory.json>`를 실행해
SKILL.md, script, reference, URL, 누락 resource, symlink를 함께 inventory한다. root 내부의
regular file·directory symlink는 target 경로와 file hash를 기록한 뒤에만 허용하고, root 밖·깨진·순환
symlink는 fail-closed한다. inventory는
승인·안전성 증명이 아니며, 실행 전 review·provenance·sandbox 경계를 대체하지 않는다. 한 번의
인상적인 응답이나 SKILL.md 한 파일만으로 전역 자산으로 승격하지 않는다. 외부 원본의
controller·사용자 질문·역할 배정은 흡수하지 않는다.

## 재평가와 폐기

원본 변경, 반복 실패, 참조 누락, 다른 자산과의 중복, 또는 두 번의 무효 사용은
재평가 신호다. `mirror-baseline`은 원본과의 차이·필요 리소스가 검증되지 않으면
`attach-specialist`, `project-leaf`, 또는 `reject`로 낮춘다. provider의 설치·인증·삭제는
초호기의 책임이 아니다.
