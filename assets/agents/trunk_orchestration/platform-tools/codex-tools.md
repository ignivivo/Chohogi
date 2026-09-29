<!-- chohogi:platform-tools=codex -->

# Codex 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Codex 표면의 실제 도구로 번역한다. Claude Code와 달리 이 문서의
서브에이전트 관련 내용 중 상당 부분은 **초호기가 이 환경에서 직접 검증하지 못한
관찰 보고**다 — 검증 상태를 항목마다 명시한다. Codex 세션은 여기 적힌 도구 이름을
존재한다고 가정하지 않고, 먼저 현재 컨텍스트에 실제로 노출되어 있는지 확인한다.

## 서브에이전트 위임 — 검증 상태: unverified

관찰된 도구 이름: `spawn_agent`, `wait_agent`, `close_agent`.

**활성화 조건이 불명확하다.** 흡수 대상이었던 외부 방법론은 `~/.codex/config.toml`에
`[features] multi_agent = true`를 추가하면 이 도구들이 열린다고 설명했다. 그런데
Codex 자체 공식 참조(`codex-self-knowledge.md` 경로의 upgrade 문서)는 "multi_agent"를
**OpenAI Responses API의 베타 기능**으로 설명한다 — `OpenAI-Beta: responses_multi_agent=v1`
HTTP 헤더와 API 요청 바디의 `multi_agent: {enabled, max_concurrent_subagents}` 파라미터,
그리고 `multi_agent_call`/`multi_agent_call_output`/`agent_message` 아이템 처리가
필요한, **API를 직접 호출하는 통합 레벨의 기능**이다.

이 둘이 같은 스위치를 가리키는지, Codex CLI가 내부적으로 이 API 기능을 이 config
키로 노출하는지는 초호기가 확인하지 못했다. `config.toml`에 그 키를 써넣으라고
지시하는 것과, 실제로 그 키가 이 Codex 버전에서 읽히는 것은 다른 주장이다. 이
불일치가 과거 세션에서 서브에이전트 위임이 조용히 실패한 원인일 가능성이 있다.

**따라서 Codex 세션은:**
1. `spawn_agent`/`wait_agent`/`close_agent`가 현재 컨텍스트에 실제로 노출되어
   있는지부터 확인한다. 노출되어 있지 않다고 `config.toml`을 추측으로 고치지 않는다
   — 설정 파일 변경은 초호기의 관리 대상이 아니다(개인 설정).
2. 노출되어 있지 않으면 병렬/서브에이전트 위임을 시도하지 않고, `execution-allocation.md`
   의 "역할을 만들 수 없거나 현재 표면이 지원하지 않으면 주 에이전트가 같은 경계를
   순차 처리한다"를 따른다. 없는 도구 호출을 지어내지 않는다.
3. 노출되어 있으면, 완료 확인은 **명시적으로 `wait_agent`를 호출해야만** 이루어진다
   고 가정한다 — Claude Code처럼 백그라운드 완료가 자동으로 알려오지 않는다. 작업이
   끝난 역할은 `close_agent`로 즉시 닫아 유휴 상태로 남기지 않는다.
4. "이미 완료된 서브에이전트에게 다시 메시지를 보낼 수 있는지"도 unverified다.
   가능하다는 근거가 없으므로, fix 라운드마다 매번 brief 파일·report 파일 경로를
   새 위임에 실어 보내는 방식(상태를 파일로 영속화)을 기본으로 삼는다. 이는 이미
   초호기의 `execution-record.py`가 `docs/work-log/records/<work-id>/`에 append-only로
   기록하는 것과 같은 방향이며, 별도 워크스페이스 폴더를 새로 만들지 않는다.

## 역할 정의(critical-reviewer/evidence-scout/implementation-worker) — 검증 상태: verified

**Codex의 `.codex-plugin/plugin.json` 스키마에는 커스텀 서브에이전트를 선언하는
필드가 없다.** 인식되는 최상위 필드는 `name`/`version`/`interface.*`/`mcpServers`/
`skills`뿐이다(Codex CLI 바이너리에 내장된 검증 에러 문자열로 직접 확인). Claude
Code처럼 `agents/*.md`를 플러그인이 선언한 서브에이전트 타입으로 자동 로드하는
기능이 Codex에는 없다 — `assets/runtime_entrypoint/agents/*.toml`이 플러그인에
포함되어 파일로는 복사되지만, Codex가 이를 역할 정의로 인식하지 않는다.

**이건 흡수 대상 외부 방법론도 겪은 동일한 제약이다.** 그 방법론은 Codex에서
"agents/" 슬롯을 아예 쓰지 않고, 서브에이전트를 spawn하는 시점에 프롬프트
템플릿(brief 파일)을 직접 채워 넣는 방식으로 우회했다. Codex 세션은 같은 방식을
쓴다:

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
- 둘 다 정상이면 일반 checkout이다. `git worktree add`는 네이티브 도구가 없을 때만
  쓰고, `.worktrees/`가 `.gitignore`에 없으면 먼저 추가한다.

## 역할 회수 규칙 적용

`execution-allocation.md`의 "결과·handoff·중단 즉시 stop/interrupt 또는 동등한 회수를
실행해 유휴 역할을 남기지 않는다"는 원칙은, 서브에이전트 도구가 실제로 열려 있을
때만 `close_agent`로 구현한다. 열려 있지 않다면 애초에 임시 역할을 만들지 않았으므로
회수할 대상도 없다 — 이 경우 주 에이전트가 계속 직접 처리한다.

## 한계

이 문서의 서브에이전트 절 대부분은 초호기가 이 환경에서 직접 실행해 확인한 것이
아니라, 흡수 대상 외부 방법론의 관찰 보고와 Codex 자체 문서를 대조한 결과다.
`spawn_agent`/`wait_agent`/`close_agent`의 실제 존재·활성화 조건·재전송 가능 여부는
`unverified`로 남기며, 확인되기 전까지 이 문서의 예방적 지침(존재 여부 먼저 확인,
없으면 순차 처리, 파일로 상태 영속화)을 기본값으로 삼는다.
