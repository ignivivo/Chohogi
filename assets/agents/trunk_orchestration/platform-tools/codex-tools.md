<!-- chohogi:platform-tools=codex -->

# Codex 도구 매핑

`execution-allocation.md`가 말하는 "역할", "위임", "회수"는 하네스 중립적 개념이다.
이 문서는 그 개념을 Codex 표면의 실제 도구로 번역한다. Claude Code와 달리 이 문서의
서브에이전트 관련 내용 중 상당 부분은 **초호기가 이 환경에서 직접 검증하지 못한
관찰 보고**다 — 검증 상태를 항목마다 명시한다. Codex 세션은 여기 적힌 도구 이름을
존재한다고 가정하지 않고, 먼저 현재 컨텍스트에 실제로 노출되어 있는지 확인한다.

## 서브에이전트 위임 — 검증 상태: verified in this environment (2026-09-29~30, codex-cli 0.155.0-alpha.16.3)

| 항목 | 관측 | 근거 |
| --- | --- | --- |
| 활성화 | `multi_agent` stable **true**(기본값), `multi_agent_v2` false | `codex features list` |
| 모델에게 노출된 협업 도구 | `spawn_agent`, `send_message`(턴 없이 전달), `followup_task`(기존 역할에 새 작업 + 턴), `wait_agent`, `interrupt_agent`, `list_agents` | `codex debug prompt-input`의 multi_agent_role 지시 |
| 위임 허용 조건 | Codex가 "사용자 또는 적용되는 AGENTS.md/skill 지시가 서브에이전트·위임·병렬 작업을 명시적으로 요청하지 않으면 spawn하지 말라"는 지시를 넣는다 | 같은 출력의 `multi_agent_mode` |
| 초호기 역할 | `config_file`로 등록하면 `critical_reviewer`, `evidence_scout`, `implementation_worker`, `final_reviewer`, `debugger`로 스폰된다. `~/.codex/agents/`의 **심볼릭 링크는 목록에는 뜨지만 스폰이 "agent type is currently not available"로 거부된다** | 2026-09-30 시험 역할 비교: 일반 파일 성공, 같은 내용의 링크 실패, `-c agents.<name>.config_file=<정본>` 성공 |
| 문맥 전파 | `fork_turns`로 부모 문맥을 얼마나 넘길지 정한다. 위임 설명 원칙상 최소(`"none"`)로 넘긴다. `config_file` 역할은 `fork_turns: "all"`에서도 거부되지 않았다 | 같은 날 세션 기록 |
| 모델 상속 | `model`을 생략한 스폰은 부모 세션의 모델·effort로 돈다 | 부모와 자식 세션 기록의 `turn_context`가 모두 `gpt-6-luna`/`medium` |
| 스스로 위임 | 역할이 사용 가능하고 모델 확인 대기가 없을 때, 사용자가 위임을 지시하지 않은 위험 변경 검토 요청에서 `critical_reviewer`를 스스로 스폰하고 결과를 받아 전달했다(1회) | 같은 날 세션 기록 |

**Codex 세션은:**
1. `execution-allocation.md`가 `scoped-delegation`을 고르면 그 계약이 위임을 명시적으로 요청한 것이다
   (AGENTS.md에 같은 문장이 있다). 그 외에는 위임하지 않는다.
2. 역할은 `agent_type`에 위 세 이름 중 하나를 준다. 역할 정의를 프롬프트에 복사해 넣지 않는다.
   역할이 등록되어 있지 않아 거부되면 기본 `worker`/`explorer`에 정본 TOML의
   `developer_instructions`를 위임 메시지에 넣어 띄우고, 이때 역할의 `sandbox_mode`가 강제되지
   않는다는 사실을 결과에 남긴다.
3. 같은 역할에 이어서 지시할 때(`task-loop.md` 수정 1–3라운드)는 `followup_task`를 쓴다.
4. 기다릴 때는 `wait_agent`로 5–10분 구간씩 기다리고, 구간마다 `list_agents`로 보고 없이 끝난
   역할을 확인한다. 짧은 대기를 반복하지 않는다. 할 일이 남아 있으면 기다리지 않는다.
5. 모델은 `model-policy.md`의 "출발·추천·저장"을 따른다. 저장된 profile이 없으면 `model`과
   `reasoning_effort`를 생략해 세션 모델을 물려준다. `.agents/chohogi-model-profile.json`의
   `hosts.codex`에 값이 있으면 그 역할의 `model`과 `reasoning_effort`를 둘 다 준다 — `model`만 주면
   effort가 그 모델 기본값으로 바뀐다. 값이 `session`이면 생략한다.
6. 상태는 execution record와 작업 설명·보고 파일에 둔다.

`close_agent`는 이 버전의 모델 노출 목록에 없다. 회수는 끝난 역할에 새 작업을 보내지 않고
`list_agents`로 소유 경계를 확인하는 것으로 한다. 도구 목록이 위와 다르면 실제 목록을 따른다.

## 역할 정의(critical-reviewer/evidence-scout/implementation-worker/final-reviewer/debugger) — 검증 상태: verified

Codex 플러그인 매니페스트에는 역할 슬롯이 없다(인식 필드: `name`/`version`/`interface.*`/`mcpServers`/
`skills`). Codex 0.155의 역할 로더는 `~/.codex/agents/`의 일반 파일, 또는 `config.toml`의
`[agents.<이름>] config_file = "<경로>"`가 가리키는 TOML(`name`, `description`, `sandbox_mode`,
`developer_instructions`, 선택 `nickname_candidates`)을 읽는다. 초호기는 복사본을 두지 않고
`config_file`로 정본(`assets/runtime_entrypoint/agents/<role>.toml`)을 가리킨다. 설정은 README에
있다. `~/.codex/agents/`에 심볼릭 링크를 두면 목록에는 보이지만 스폰이 거부되므로 쓰지 않는다.

## 전역 지침 — 검증 상태: verified

Codex는 플러그인 매니페스트에 `hooks` 필드가 없으면 `hooks/hooks.json`을 자동으로 찾아
등록하지만, 사용자가 신뢰를 승인하기 전에는 조용히 건너뛴다(`codex exec`에서 출력 없음,
`--dangerously-bypass-hook-trust`를 주면 초호기 hook이 실행되어 지침이 한 번 더 들어감). 초호기는
`.codex-plugin/plugin.json`에 `"hooks": {}`를 두어 이 자동 등록을 끈다 — 빈 객체여야 하며 필드
생략·빈 배열은 자동 등록으로 돌아간다. 전역 지침은 `~/.codex/AGENTS.md` →
`assets/runtime_entrypoint/AGENTS.md` 링크로 읽고, 지침 안의 `~/.agents/chohogi/...` 경로는
`~/.agents/chohogi` → `assets/agents` 링크로 정본을 가리킨다. AGENTS.md는 파일 읽기라 링크가
동작한다(새 세션에서 지침 로드 확인). 역할 파일과는 다르다.

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

`execution-allocation.md`의 "결과·handoff·중단 즉시 회수해 유휴 역할을 남기지 않는다"는 원칙은
이 버전에서 진행 중인 역할은 `interrupt_agent`로 멈추고, 끝난 역할에는 새 작업을 보내지 않으며,
새 위임 전에 `list_agents`로 살아 있는 역할과 소유 경계를 확인하는 것으로 구현한다. 서브에이전트
도구가 노출되어 있지 않으면 역할을 만들지 않고 주 에이전트가 순차 처리한다.

## 한계

위 관측은 2026-09-29~30 이 환경의 codex-cli 0.155.0-alpha.16.3 기준이다. Codex 버전이 바뀌면
`codex features list`, `codex debug prompt-input "x"`, 새 `codex exec` 세션으로 다시 확인한다.
