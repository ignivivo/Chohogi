<!-- chohogi:platform-tools=claude -->

# Claude Code 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Claude Code 표면의 실제 도구 이름으로 번역한다. 검증 방식: 이
세션이 실제로 호출 가능한 도구 스키마를 직접 확인한 것만 적는다.

## 서브에이전트 위임

| 개념 | Claude Code 도구 |
| --- | --- |
| 임시 역할 생성(scout/implementer/reviewer) | `Agent` (subagent_type 지정) |
| 병렬 디스패치 | 한 응답 안에 `Agent` 호출을 여러 번 포함 |
| 백그라운드 실행 + 완료 대기 | `Agent`에 `run_in_background: true` — 완료 시 **자동으로** task-notification이 도착한다. 폴링하지 않는다 |
| 살아있는 역할 목록 확인 | `ListAgents` |
| 이미 만든 역할에게 이어서 지시(재개) | `SendMessage`로 `to: '<agent 이름 또는 ref>'` — 해당 에이전트가 자신의 transcript에서 이어서 실행한다 |
| 유휴 상태 알림 구독(폴링 대체) | `SendMessage`의 `notify_when_idle: true` |
| 역할 즉시 회수(중단) | `TaskStop`으로 `task_id`(agent 이름/ref) 지정 |

**"harness cannot send another message to a live subagent" 조건은 Claude Code에는
해당하지 않는다.** `SendMessage`로 이름만 정확히 알면 완료된 에이전트도 다시 불러
이어서 작업시킬 수 있다(이름이 같으면 최신 에이전트가 우선). 즉 흡수 대상 방법론의
"fix loop 1-3라운드는 원래 구현자에게 재전송"이라는 **기본 흐름을 그대로 쓸 수 있다** —
Codex처럼 "재전송 불가 시 fresh dispatch로 폴백"하는 예외 경로를 먼저 탈 필요가 없다.

## 격리 작업공간

| 개념 | Claude Code 도구 |
| --- | --- |
| 격리된 workspace 생성/진입 | `EnterWorktree` (`name` 또는 기존 경로의 `path`) |
| 격리 종료 | `ExitWorktree` (`action: keep`|`remove`) |

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
