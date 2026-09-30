<!-- chohogi:platform-tools=claude -->

# Claude Code 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Claude Code 표면의 실제 도구 이름으로 번역한다. 검증 방식: 이
세션이 실제로 호출 가능한 도구 스키마를 직접 확인한 것만 적는다.

## 서브에이전트 위임

| 개념 | Claude Code 도구 |
| --- | --- |
| 임시 역할 생성(scout/implementer/task-reviewer/final-reviewer/debugger) | `Agent`에 `subagent_type: "evidence-scout"` \| `"implementation-worker"` \| `"critical-reviewer"` \| `"final-reviewer"` \| `"debugger"` — chohogi 플러그인이 `agents/*.md`로 선언한 타입이며, `claude plugin details chohogi`로 노출을 직접 확인함(검증됨) |
| 병렬 디스패치 | 한 응답 안에 `Agent` 호출을 여러 번 포함 |
| 백그라운드 실행 + 완료 대기 | `Agent`에 `run_in_background: true` — 완료 시 **자동으로** task-notification이 도착한다. 폴링하지 않는다 |
| 살아있는 역할 목록 확인 | `ListAgents` |
| 이미 만든 역할에게 이어서 지시(재개) | `SendMessage`로 `to: '<agent 이름 또는 ref>'` — 해당 에이전트가 자신의 transcript에서 이어서 실행한다 |
| 유휴 상태 알림 구독(폴링 대체) | `SendMessage`의 `notify_when_idle: true` |
| 역할 즉시 회수(중단) | `TaskStop`으로 `task_id`(agent 이름/ref) 지정 |

**"harness cannot send another message to a live subagent" 조건은 Claude Code에는
해당하지 않는다.** `SendMessage`로 이름만 정확히 알면 완료된 에이전트도 다시 불러
이어서 작업시킬 수 있다(이름이 같으면 최신 에이전트가 우선). 따라서 `task-loop.md`의
"수정 1–3라운드는 같은 implementer에게 보낸다"를 `SendMessage`로 그대로 구현한다.
위임할 때는 `model`을 명시한다 — 생략하면 세션 모델을 물려받는다.

## 역할 모델 — 검증 상태: verified (도구 스키마, 2026-09-30 frontmatter 탐침)

`Agent` 도구의 `model` 인자는 `sonnet`·`opus`·`haiku`·`fable` 별칭만 받고 추론 강도 인자는 없다. 역할별
모델과 강도는 역할 정의 파일(`agents/*.md`) frontmatter의 `model`(정확한 id)과 `effort`(`low`~`max`)로
전달한다. 2026-09-30 Claude Code 2.1.284 `claude -p` 탐침에서 부모가 `high`일 때 frontmatter `low`·`max`
역할의 transcript가 각각 `low`·`max`와 지정한 정확한 모델로 기록됐다(검증됨). frontmatter는 플러그인
전역이라 모든 프로젝트에 같은 값이 적용되고, 위임할 때 `model` 인자를 주면 모델만 덮어쓴다. Haiku는
effort를 받지 않으므로 그 역할에는 `effort`를 두지 않는다.

역할 파일이 이미 모델·강도를 싣고 있으므로 Claude에서 위임은 모델 답을 기다릴 이유가 없다.
모델 card는 같은 턴의 보고 텍스트로만 붙이고 `AskUserQuestion`으로 묻지 않는다(`model-policy.md`
"출발·추천·저장"). headless replay(`claude -p`)는 대화형 질문 대기를 재현하지 못하므로, 이 규칙의
검증은 replay의 `no-blocking-model-question` 단언(질문 도구 호출 자체를 실패로 판정)과 실제 대화 관측에 둔다.

`model-policy.md`의 "출발·추천·저장"에 따라, 저장된 profile이 역할 파일 값과 같거나 없으면 `model`을 생략한다.
결정과 전달은 분리한다. 추천 card와 profile은 정확한 모델 id(`claude-sonnet-5-5` 등)로 적고, 위임할
때만 `model-recommendations.json`의 `deliveryAlias`로 그 id를 별칭으로 바꿔 `model`에 준다
(`session`이면 생략). 별칭은 그 계열의 최신 모델로 해석되므로(Claude Code `--model` 도움말), 매핑에
없는 모델(예: 이전 세대)은 역할별로 전달할 수 없고 card가 그렇게 표시한다. Claude Code에는 모델 목록
조회 명령이 없어 카탈로그는 `unknown`이며, 사용자가 모델 선택 화면에서 본 목록을 사용자 보고 교정으로
기록한다. 도구 인자의 허용값을 모델 목록으로 쓰지 않는다.

## 격리 작업공간

| 개념 | Claude Code 도구 |
| --- | --- |
| 격리된 workspace 생성/진입 | `EnterWorktree` (`name` 또는 기존 경로의 `path`) |
| 격리 종료 | `ExitWorktree` (`action: keep`|`remove`) |

만들기 전에 이미 격리되어 있는지 확인한다: `git rev-parse --git-dir`와 `--git-common-dir`가
다르면(submodule이 아니라면 — `git rev-parse --show-superproject-working-tree`가 경로를
내면 submodule) 이미 linked worktree이므로 새로 만들지 않는다. `git worktree add`로
직접 만들지 않는다 — 하네스가 보지 못하는 상태가 생긴다. 새로 만든 뒤에는 프로젝트
의존성을 준비하고 기준 테스트를 돌려 깨끗한 출발점인지 확인한다. 기준에서 이미 실패하면
그 실패를 보고하며, 이후 실패와 섞이지 않게 기록한다.

`EnterWorktree`는 git 저장소가 아니어도 VCS-agnostic hook으로 동작한다. 이미
`EnterWorktree`로 만든 workspace가 아니면 `ExitWorktree`는 no-op이다 — 수동으로
`git worktree add`한 디렉토리는 직접 `git worktree remove`로 정리해야 한다.

## 역할 회수 규칙 적용

`execution-allocation.md`의 "결과·handoff·중단 즉시 stop/interrupt 또는 동등한 회수를
실행해 유휴 역할을 남기지 않는다"는 원칙은 Claude Code에서 다음으로 구현한다.

1. 역할 결과가 도착하면(또는 더 이상 필요 없어지면) 그 즉시 `TaskStop`으로 회수한다.
2. 결과를 기다리는 중이라도, 다음 위임을 새로 만들기 전에는 `ListAgents`로 현재
   살아있는 역할과 그 소유 경계를 먼저 확인한다.
3. worktree로 격리했다면 작업 종료 시 `ExitWorktree`로 명시적으로 닫는다. 세션이
   종료될 때까지 worktree 안에 머무르면 사용자에게 keep/remove를 다시 묻게 된다.

## 한계

이 매핑은 이 세션이 직접 확인한 도구 스키마를 근거로 한다. Claude Code의 도구
구성은 사용자 설정·플러그인·팀 구성에 따라 달라질 수 있으므로, 여기 없는 이름의
worktree/subagent 도구가 노출되어 있으면 그것을 우선한다.
