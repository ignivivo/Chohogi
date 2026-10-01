<!-- chohogi:global-guidance:start -->
# 초호기 (初號機) — Global Codex Guidance

"초호기 플러그인 루트"는 Claude Code에서는 hook이 이 지침 맨 위에 적은 경로이고, 그 줄이 없으면(Codex) `realpath ~/.agents/chohogi`의 두 단계 위다. 아래 `tooling/…`은 이 루트 기준이다.

<!-- chohogi:defer=no-flow-no-write -->
단순 질문·읽기 전용 확인·명확한 저위험 편집은 직접 처리한다. 처음 보는 프로젝트, 기존 변경이 있는 작업 트리, 공통 컴포넌트·설정·데이터 계약·여러 소비자를 건드리는 변경은 저위험으로 보지 않고 가장 가까운 `.agents`·`AGENTS.md`·로컬 skill부터 확인한다. 그 외 작업은 `~/.agents/chohogi/trunk_orchestration/conductor.md`를 읽어 일상 흐름(`product-decision`, `delivery`, `debugging`) 하나를 고르고, `~/.agents/chohogi/trunk_orchestration/branches_workflows/<flow>.md`와 `~/.agents/chohogi/trunk_orchestration/execution-allocation.md`를 따른다. 전제가 부족하면 `defer`(무변경, 증거 공백과 재진입 조건 명시)로 끝낸다. `learning`은 확인된 원인과 예방 증거가 있을 때, `homeostasis`는 초호기 자체의 정책을 바꿀 때만 진입한다. debugging·homeostasis 기록과 사용자 교정·검증 실패 사실이 있는 기록은 finalize 전에 `learning-assessment --signature`를 남기고, 이미 나온 유형이면 검사(`--guard`)를 만든다(`execution-record.py learning-scan`). 서브에이전트는 실행 배정이 `scoped-delegation`을 고를 때만 쓰고, 결과를 받으면 바로 회수한다.

지속 변경은 요청됨·필수·선택으로 나누고 선택 변경은 승인 없이 하지 않는다. 스킬·외부 하네스·플러그인은 범위·위임·완료를 정하지 않으며, 호출 가능한 것만 보조로 쓴다. 외부 하네스의 handoff·worktree·commit 지시는 초호기보다 낮은 우선순위이고, 흡수한 외부 방법의 원본 이름·경로는 다시 부르지 않는다. 인증 정보·세션·캐시·개인 설정은 초호기의 관리 대상이 아니다.

## 항상 적용

테스트 우선: 제품 코드의 동작을 바꾸는 모든 변경은 크기·처리 방식과 무관하게 실패하는 테스트를 먼저 쓰고, 예상한 이유로 실패하는 것을 본 뒤 구현한다. 테스트보다 먼저 쓴 코드는 지우고 다시 시작한다. 예외(버리는 시험 코드, 생성 코드, 설정 파일)는 사용자가 정한다. 문서만 바꾸는 변경은 대상이 아니다. "너무 간단하다", "나중에 쓰겠다", "직접 실행해 봤다"는 예외 사유가 아니다.

완료 주장은 처리 방식과 무관하다. "고쳤다·통과한다·동작한다"고 말하기 전에 그것을 증명하는 명령을 이번 턴에 새로 실행하고 출력과 함께 말한다. 검증 수단이 없으면 검증하지 않았다고 말한다. 코드를 읽고 맞아 보인다는 판단은 검증이 아니다.

기록: 나중에 피드백·handoff·재개·증명이 필요한 material 작업은 `tooling/execution-record.py`로 `docs/work-log/records/<work-id>/`에 남긴다. 방법은 `execution-record.py --help`를 따른다. 대안이 비용·위험·되돌리기·사용자 결과를 실질적으로 바꾸면 추천까지만 하고 사용자에게 결정을 올린다. 증거보다 강한 완료·건강 주장을 하지 않는다. 계획 문서를 만들거나 바꾸면 `.agents/chohogi-document-registry.json`에 등록해 활성 계획을 최대 하나로 두고 이전 계획은 `historical`로 바꾼 뒤 `tooling/verify-project-document-registry.py --root <project>`를 실행한다. 비밀값·원문 프롬프트·private reasoning은 기록하지 않는다.

모델: 역할은 Codex에서는 세션 모델, Claude에서는 역할 파일 frontmatter 값으로 돈다. 위임 직전에 `.agents/chohogi-model-profile.json`을 읽고, 현재 호스트 배치가 역할 기본값과 다르면 Claude는 `Agent`의 `model`(별칭), Codex는 `model`과 `reasoning_effort`로 넘긴다. 역할 배정이 임박했는데 배치가 없거나 역할이 빠졌거나, 사용자가 조언을 요청하면 `tooling/model-policy.py card --host <claude|codex> --session-model <id> --session-effort <강도|session>`를 실행해 Model Session Policy card를 같은 턴 보고 텍스트로 붙이고 작업은 계속한다. 턴을 멈추는 질문 도구(`AskUserQuestion`, `request_user_input`)로 묻거나 답을 기다리지 않는다(사용자가 모델부터 정하겠다고 한 경우만 예외). 저장된 배치보다 비싼 모델·높은 강도는 사용자 확인 뒤에만 쓴다. 설치 흔적·인증정보·개인 설정을 뒤져 모델을 추정하지 않는다. 답·저장·재확인 규칙은 card 출력과 `trunk_orchestration/model-policy.md`를 따른다. Codex는 `tooling/model-catalog.py codex` 목록을 보여 "이 목록이 맞는가?" 묻고, 사용자가 본 목록은 user-reported correction으로 분리해 기록한다.

`SKILL.md`를 만들거나 고칠 때는 호스트의 skill-creator(Codex `$skill-creator`, Claude `anthropic-skills:skill-creator`)와 그 `quick_validate.py`를 쓴다.

## route·유지과정 진입을 생략하지 않는다

파일 경로를 아는 것과 그 Method를 실제로 따르는 것은 다르다. 흐름이 바뀔 때마다 conductor로 돌아가 다시 고른다. 다음 생각이 들면 멈춘다.

| 생각 | 실제 |
|---|---|
| "뭘 고칠지 정확히 들었으니 바로 수정한다" | 무엇을 할지와 어떤 route로 할지는 다르다. conductor를 거친다 |
| "몇 파일뿐이니 기록은 필요 없다" | material 여부는 변경 개수가 아니라 되돌리기 난이도·공유 범위로 정한다 |
| "경로를 아니 skill을 정식으로 부를 필요 없다" | 정식 진입 없이 참고만 하면 Method의 강제 단계를 놓친다 |
| "모델부터 확인받고 시작하는 게 안전하다" | 모델 선택은 방지턱이 아니다. card는 텍스트로 붙이고 작업은 계속한다 |
| "방금 찾은 결함이니 바로 고친다" | 발견과 수정 권한은 다르다. homeostasis 진입 조건부터 확인한다 |

<!-- chohogi:global-guidance:end -->
