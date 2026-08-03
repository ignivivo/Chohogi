<!-- chohogi:capability-selection -->
<!-- chohogi:provider-authority=capability-only -->

# 능력 선택 경계

Conductor가 flow를, `execution-allocation.md`가 실행 형태를 정한 뒤에만 이 계약을
적용한다. 이 문서는 무엇이 초호기의 내부 방법이고 무엇이 현재 런타임의 외부 능력인지
구분한다. 능력 제공자는 controller가 아니며, 작업의 범위·흐름·역할·완료를 정하지 않는다.

## 분류

| 분류 | 소유자 | 사용할 때 | 금지 |
| --- | --- | --- | --- |
| `chohogi-internal` | 초호기 Git 자산 | route, 실행 배정, xylem 방법, 작업 봉투가 필요할 때 | 외부 하네스 문서를 다시 읽어 절차를 결정하기 |
| `native-system` | Codex | 현재 표면에 직접 노출된 기본 스킬·도구가 작업에 맞을 때 | 초호기의 controller로 취급하거나 복제본을 만드는 일 |
| `capability-provider` | 플러그인·MCP·커넥터 | 현재 호출 가능하고, 외부 데이터·인증된 작업·브라우저·전용 도구가 실제로 필요할 때 | provider에게 흐름·위임·완료 권한을 주기 |
| `absorbed-method-source` | 비교·역사 참고본 | 실행에는 사용하지 않음 | 활성 controller·방법 의존성으로 호출하기 |
| `project-leaf` | 프로젝트 Git | 선택된 흐름 뒤 도메인 사실·계약·검증이 필요할 때 | 전역 정책이나 controller로 승격하기 |

## 선택 절차

1. 먼저 초호기 내부 route·실행 배정·xylem만으로 해결 가능한지 판단한다.
2. 외부 데이터나 실제 UI·원격 서비스 동작이 필요할 때만 `capability-provider`를 고른다.
3. provider는 현재 세션에서 실제 호출 가능한 능력이라는 증거가 있을 때만 쓴다. 캐시
   경로나 설치 흔적만으로 활성화·권한·인증을 가정하지 않는다.
4. provider가 없거나 인증·권한이 부족하면 개인 설정·비밀값·플러그인 등록을 바꾸지
   않는다. 가능한 내부 방법 또는 안전한 대안을 사용하고, 대안도 없으면 필요한 외부
   권한을 명시한다.
5. 사용자가 특정 provider를 명시적으로 요청했고 현재 호출 가능하면 그 요청을 우선한다.
   그래도 provider는 능력만 수행하며 controller가 되지 않는다.
6. 순수 Markdown 전문 skill은 `skill-adoption.md`의 상태가 `attach-specialist`일 때만
   외부 원본으로 사용한다. `absorb-core`와 `mirror-baseline`은 초호기 정본만 사용한다.

## 흡수 원칙

Superpowers·구 Meta-harness·Caveman에서 채택한 절차는 초호기 내부 자산에 이미
소화된 내용만 사용한다. 비활성화된 원본은 비교와 역사 확인을 위해 남아 있을 수 있지만,
초호기는 그것을 읽거나 호출해 계획·디버깅·테스트·검토·역할 배정을 결정하지 않는다.

## 산출물

substantial 작업 봉투에는 외부 능력을 실제로 사용한 경우에만 다음을 남긴다.

- 선택한 분류와 필요한 이유
- 호출 가능성 또는 권한 실패에 대한 비밀 없는 증거
- provider가 수행한 좁은 동작과 내부 흐름이 유지됐다는 확인
- fallback 또는 남은 외부 권한

외부 능력의 사용 여부는 사용자에게 고르게 하는 메뉴가 아니다. 제품 정책, 새 권한,
비가역 영향, 승인되지 않은 비용처럼 결과를 바꾸는 결정만 질문한다.
