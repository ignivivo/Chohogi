<!-- chohogi:platform-tools=claude -->

# Claude Code 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Claude Code 표면의 실제 도구 이름으로 번역한다. 검증 방식: 이
세션이 실제로 호출 가능한 도구 스키마를 직접 확인한 것만 적는다.

## 서브에이전트 위임

| 개념 | Claude Code 도구 |
| --- | --- |
| 임시 역할 생성(scout/implementer/reviewer) | `Agent`에 `subagent_type: "critical-reviewer"` \| `"evidence-scout"` \| `"implementation-worker"` — chohogi 플러그인이 `agents/*.md`로 선언한 타입이며, `claude plugin details chohogi`로 노출을 직접 확인함(검증됨) |
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

## 역할 모델 — 검증 상태: verified (도구 스키마)

`Agent` 도구의 `model` 인자는 `sonnet`·`opus`·`haiku`·`fable` 별칭을 받는다. 생략하면 역할 정의의
모델, 그것도 없으면 부모 세션 모델을 물려받는다(사용자가 기본 서브에이전트 모델을 따로 설정한
경우 제외). 초호기 역할 정의(`agents/*.md`)에는 모델이 없으므로 생략하면 세션 모델이다. 역할별
추론 강도는 이 도구로 지정할 수 없어 `not-selectable`로 기록하고 세션 강도를 따른다.

`model-policy.md`의 "출발·추천·저장"에 따라, 저장된 profile이 없으면 `model`을 생략한다.
`.agents/chohogi-model-profile.json`의 `hosts.claude`에 역할 값이 있으면 그 별칭을 `model`로 준다
(`session`이면 생략). 추천 card의 선택지는 이 네 별칭 안에서만 만들고, 호출 가능한 전체 목록과
가격은 공식 조회 수단이 없으면 `unknown`으로 둔다.

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
