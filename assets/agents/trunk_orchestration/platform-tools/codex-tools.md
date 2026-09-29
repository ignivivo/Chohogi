<!-- chohogi:platform-tools=codex -->

# Codex 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Codex 표면의 실제 도구로 번역한다. Claude Code와 달리 이 문서의
서브에이전트 관련 내용 중 상당 부분은 **초호기가 이 환경에서 직접 검증하지 못한
관찰 보고**다 — 검증 상태를 항목마다 명시한다. Codex 세션은 여기 적힌 도구 이름을
존재한다고 가정하지 않고, 먼저 현재 컨텍스트에 실제로 노출되어 있는지 확인한다.

## 서브에이전트 위임 — 검증 상태: source-reported (이 환경에서 실행 미확인)

아래는 Codex용 외부 방법론의 플랫폼 참조 문서(v6.4.2, 2026-09-29 읽음)가 보고한 내용이다.
초호기가 live Codex 세션에서 직접 실행해 확인한 것은 아니므로, 세션은 먼저 현재 도구
목록에 실제로 노출되어 있는지 확인하고 표와 다르면 실제 도구 목록을 따른다.

| 개념 | 보고된 Codex 동작 |
| --- | --- |
| 활성화 | `~/.codex/config.toml`의 `[features] multi_agent = true`. 개인 설정이므로 초호기가 대신 바꾸지 않는다 — 노출되어 있지 않으면 사용자에게 알리고 순차 처리한다 |
| 버전 | 모델 preset에 따라 multi-agent V1 또는 V2(현재 preset은 V2) |
| 역할 생성 | `spawn_agent`. `fork_turns: "none"`이면 깨끗한 문맥, 기본값 `"all"`은 부모 transcript 전체를 복사한다 — 위임 설명 원칙상 `"none"`을 쓴다 |
| 역할 파일 | Codex 0.145+에서 `~/.codex/agents/`의 역할 파일을 `agent_type`으로 격리 fork에 붙일 수 있다. 전체 이력 fork는 `agent_type`을 거부한다 |
| 모델 | spawn마다 `model`과 `reasoning_effort`를 **둘 다** 명시한다. `model`만 주면 effort가 그 모델 기본값으로 조용히 바뀐다. 모델 이름은 현재 spawn 허용 목록과 대조한다 |
| 이어서 지시(재개) | V2: `followup_task`로 같은 역할에 메시지를 보내고 한 턴을 시킨다. 축출된 역할도 투명하게 다시 로드된다. 즉 **재전송 가능** — fix 라운드 1–3은 같은 implementer에게 보낸다 |
| 완료 대기 | `wait_agent`는 폴링이 아니라 이벤트 구독이다. 할 일이 남았으면 기다리지 않는다(완료 결과는 다음 턴에 도착). 정말 할 일이 없을 때만 `timeout_ms` 300000–600000 구간으로 기다리고, 구간마다 상태 한 줄과 `list_agents`로 보고 없이 끝난 역할을 확인한다. 5분 미만 짧은 대기를 반복하지 않는다 |
| 회수 | V2에는 `close_agent`가 없고 끝난 역할은 필요할 때 자동 축출된다. V1에서만 `close_agent`로 결과가 돌아온 reviewer와 검토를 통과한 implementer를 닫는다 |

**따라서 Codex 세션은:** 도구가 노출되어 있지 않으면 위임을 시도하지 않고
`execution-allocation.md`대로 주 에이전트가 순차 처리한다(없는 도구 호출을 지어내지
않는다). 노출되어 있으면 위 표를 따르되, 상태는 언제나 `docs/work-log/records/<work-id>/`의
execution record와 작업 설명·보고 파일에 둔다 — 재개가 가능해도 기억이 아니라 파일이
정본이다.

## 역할 정의(critical-reviewer/evidence-scout/implementation-worker) — 검증 상태: verified

**Codex의 `.codex-plugin/plugin.json` 스키마에는 커스텀 서브에이전트를 선언하는
필드가 없다.** 인식되는 최상위 필드는 `name`/`version`/`interface.*`/`mcpServers`/
`skills`뿐이다(Codex CLI 바이너리에 내장된 검증 에러 문자열로 직접 확인). Claude
Code처럼 `agents/*.md`를 플러그인이 선언한 서브에이전트 타입으로 자동 로드하는
기능이 Codex에는 없다 — `assets/runtime_entrypoint/agents/*.toml`이 플러그인에
포함되어 파일로는 복사되지만, Codex가 이를 역할 정의로 인식하지 않는다.

플러그인 슬롯이 없으므로 Codex 세션은 spawn 시점에 역할 지시를 직접 조립한다
(위 표의 `~/.codex/agents/` + `agent_type` 경로는 사용자 홈 설정이므로 초호기가 설치하지
않는다):

1. 서브에이전트를 spawn하기 전에, `assets/runtime_entrypoint/agents/<role>.toml`의
   `description`과 `developer_instructions`를 읽는다.
2. 그 `developer_instructions` 전문을 spawn하는 프롬프트의 시스템 지시 부분에
   그대로 포함시킨다 — TOML 파일 경로를 서브에이전트에게 "읽으라"고 넘기지 않는다
   (서브에이전트가 격리된 컨텍스트를 가정하므로, 조립된 텍스트로 직접 전달해야
   한다).
3. `sandbox_mode`(`read-only`/`workspace-write`)를 spawn 시점의 실제 권한 설정과
   맞춘다 — read-only 역할에 쓰기 권한을 주지 않는다.

## 격리 작업공간 — 검증 상태: partially verified (git 명령 자체는 표준)

네이티브 worktree 도구(이름 예: `EnterWorktree`, `WorktreeCreate`, `/worktree` 명령,
`--worktree` 플래그)가 노출되어 있으면 그것을 쓴다. 없으면 아래로 판단한다.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` (그리고 submodule이 아님) → 이미 linked worktree 안에 있다.
  새로 만들지 않는다.
- `BRANCH`가 비어 있음 → detached HEAD. sandbox가 외부에서 관리하는 workspace일 수
  있으며, 이 경우 그 자리에서 commit까지만 하고 branch/push는 사용자의 App 네이티브
  컨트롤(예: "Create branch", "Hand off to local")로 넘긴다 — Codex가 대신 push를
  시도하지 않는다.
- `GIT_DIR != GIT_COMMON`은 submodule 안에서도 참이다.
  `git rev-parse --show-superproject-working-tree`가 경로를 내면 submodule이므로 일반
  checkout으로 취급한다.
- 둘 다 정상이면 일반 checkout이다. `git worktree add`는 네이티브 도구가 없을 때만
  쓰고, 위치는 사용자 지침 → 기존 `.worktrees/`(또는 `worktrees/`) → `.worktrees/` 순이다.
  만들기 전에 `git check-ignore`로 그 디렉토리가 무시되는지 확인하고, 아니면 먼저
  `.gitignore`에 추가해 커밋한다 — 무시되지 않은 worktree는 트리 전체를 커밋하게 된다.
  sandbox가 생성을 막으면 그 사실을 알리고 현재 디렉토리에서 진행한다.
- 새로 만든 뒤 의존성을 준비하고 기준 테스트로 깨끗한 출발점을 확인한다.

## 역할 회수 규칙 적용

`execution-allocation.md`의 "결과·handoff·중단 즉시 stop/interrupt 또는 동등한 회수를
실행해 유휴 역할을 남기지 않는다"는 원칙은 V1에서는 `close_agent`로, V2에서는 끝난
역할에 새 작업을 보내지 않고 `list_agents`로 소유 경계를 확인하는 것으로 구현한다(V2는
자동 축출). 서브에이전트 도구가 열려 있지 않다면 애초에 임시 역할을 만들지 않았으므로
회수할 대상도 없다 — 이 경우 주 에이전트가 계속 직접 처리한다.

## 한계

서브에이전트 절은 외부 방법론의 Codex 참조 문서가 보고한 내용이며, 초호기가 live Codex
세션에서 `spawn_agent`/`followup_task`/`wait_agent`/`list_agents`/`close_agent`를 직접 실행해
확인하지는 않았다. 확인되기 전까지는 "노출 여부 먼저 확인, 없으면 순차 처리, 상태는 파일에"를
기본값으로 삼는다.
