# 초호기 운영 지도

## 호출 순서

`AGENTS.md` → trunk — 하나의 일상 route → execution allocation → xylem context handoff
→ 필요한 leaf 또는 provider → 검증 → phloem feedback → learning 또는 Homeostasis admission
gate.

## 자산 경계

| 식물 기관 — 개발 기능 | 예 | 실행 정본 |
| --- | --- | --- |
| roots — foundation policy | constitution | 초호기 Git |
| trunk — workflow control | router, route, allocation, capability selection | 초호기 Git |
| branches — workflow organs | product-decision, delivery, debugging | 초호기 Git |
| vascular bundle — context and feedback | xylem context, phloem feedback | 초호기 Git |
| leaves — reusable capabilities | security, accessibility, verification methods | 초호기 Git + provenance |
| meristem — capability lifecycle | candidate, trial, promote, retire | 초호기 Git |
| regulatory processes | learning, homeostasis | 초호기 Git |
| leaves — project extensions | Sazu 계약·도메인 skill | 프로젝트 Git |
| amyloplast — learned assets | 승격된 검사·계약 | 초호기 Git |
| provider — live capability | browser, MCP, scanner, connector | 현재 런타임 |

플러그인·MCP·인증은 provider의 환경 상태이며 초호기의 설치 대상이 아니다. 반대로
흡수된 방법론은 외부 원본을 실행 중 호출하지 않는다.

## 운영 검사

- 구조: route, execution allocation, capability boundary, provenance verifier
- 설치: clean target install 뒤 `verify-install` (설치 무결성 검사)
- 행동: fixture를 새 세션에서 replay하여 flow·위임·provider controller 침범을 기록
- 개선: confirmed cause만 learning으로, 명시 요청 또는 확인된 전역 경계 증거가 scope/evidence
  gate를 통과할 때만 homeostasis로 올린다. Paired Replay는 전역 정책 후보에만 제한한다.

## 환경 지원

PowerShell은 `python` 또는 `py -3`을 사용한다. POSIX 문서의 `python3`이 Windows
Git Bash에서 Microsoft Store 별칭으로 실패할 수 있으므로, 그 환경에서는 실제 Python
경로를 명시하거나 WSL/Linux Python을 사용한다. 이 호환성은 설치 성공과 별개로 검증한다.
