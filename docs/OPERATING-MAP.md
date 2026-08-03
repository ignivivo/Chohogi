# 초호기 운영 지도

## 호출 순서

`AGENTS.md` → conductor(정확히 하나의 flow) → execution allocation → capability selection
→ 필요한 xylem 또는 project leaf → 검증 → confirmed failure면 learning → 초호기 정책
문제면 homeostasis.

## 자산 경계

| 경계 | 예 | 실행 정본 |
| --- | --- | --- |
| 초호기 핵심 | route, allocation, learning | 초호기 Git |
| 이식 baseline | security, accessibility | 초호기 Git + provenance |
| 외부 specialist | 가끔 쓰는 Markdown 전문 skill | 원본, attach 상태일 때만 |
| provider | browser, MCP, scanner, connector | 현재 런타임 |
| leaf | Sazu 계약·도메인 skill | 프로젝트 Git |

플러그인·MCP·인증은 provider의 환경 상태이며 초호기의 설치 대상이 아니다. 반대로
흡수된 방법론은 외부 원본을 실행 중 호출하지 않는다.

## 운영 검사

- 구조: route, execution allocation, capability boundary, provenance verifier
- 설치: clean target install 뒤 doctor
- 행동: fixture를 새 세션에서 replay하여 flow·위임·provider controller 침범을 기록
- 개선: confirmed cause만 learning으로, 전역 수명주기 변경은 homeostasis로 올린다.

## 환경 지원

PowerShell은 `python` 또는 `py -3`을 사용한다. POSIX 문서의 `python3`이 Windows
Git Bash에서 Microsoft Store 별칭으로 실패할 수 있으므로, 그 환경에서는 실제 Python
경로를 명시하거나 WSL/Linux Python을 사용한다. 이 호환성은 설치 성공과 별개로 검증한다.
