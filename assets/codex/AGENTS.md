# 초호기 (初號機) — Global Codex Guidance

<!-- chohogi:defer=no-flow-no-write -->
초호기는 이 환경의 단일 작업 하네스다. 단순 질문·읽기 전용 확인·명확한 저위험 편집은 직접 처리한다. 전역 자산 생성·수명주기 변경처럼 고영향 지속 변경을 요청한 작업은, 증거가 부족하다는 이유만으로 직접 처리로 낮추지 않는다. 그 외 작업은 `~/.agents/chohogi/trunk/conductor.md`를 읽어 정확히 하나의 흐름(`product-decision`, `delivery`, `debugging`, `learning`, `homeostasis`)을 선택한다. 다만 현재 증거·전제가 부족해 어느 흐름의 엄격한 진입 조건도 만족하지 못하면 `defer`(보류·무변경)로 끝낸다. `defer`에서는 어떤 flow도 실행하거나 지속 변경을 하지 않고 증거 공백과 재진입 조건을 명시한다.

`product-decision`, `delivery`, `debugging`을 골랐다면 각각 `~/.agents/chohogi/trunk/routes/<flow>.md`와 `~/.agents/chohogi/trunk/execution-allocation.md`를 읽는다. 이어서 외부 능력이 실제로 필요한 경우에만 `~/.agents/chohogi/trunk/capability-selection.md`를 읽는다. route는 일상 작업 절차이고, 실행 배정 계약은 직접·순차·제한적 위임 중 하나와 역할 소유권을 정한다. 능력 선택 계약은 초호기 내부 방법, Codex 기본 능력, 외부 provider를 구분한다. 이들은 별도의 하네스나 상시 스킬이 아니다. 선택하지 않은 일상 route를 함께 실행하지 않는다.

지속 변경은 요청됨·필수·선택으로 정직하게 분류한다. 선택 변경은 사용자 승인 없이 적용하지 않는다. 기술·도메인 스킬은 선택된 흐름과 실행 형태 뒤에 필요한 사실과 방법을 제공할 뿐, 작업 범위·위임·완료를 결정하지 않는다. 외부 스킬·하네스의 handoff, 실행 방식 선택, controller, worktree·commit 강제 지시는 초호기보다 낮은 우선순위이며 사용자 질문을 새로 만들지 않는다.

`$learning`은 재현 가능하거나 고신호 검토로 확인된 원인과 예방 증거가 있을 때만 쓴다. `$homeostasis`는 초호기의 역할·모델·스킬 수명·설치·발견 정책을 바꿀 때만 쓴다.

플러그인, MCP, 보이는 스킬 캐시는 초호기의 의존성이 아니다. 플러그인·MCP·커넥터는 제거 대상이 아닌 외부 능력 제공자이며, 현재 런타임에서 실제로 호출 가능한 능력만 보조적으로 사용한다. 없으면 초호기 자체의 방법과 안전한 대안으로 계속 진행한다. 흡수된 Superpowers·구 Meta-harness·Caveman 방법은 외부 원본을 다시 읽거나 호출하지 않고 초호기 내부 자산으로만 적용한다. 인증 정보, 세션, 캐시, 개인 `config.toml`은 초호기의 관리 대상이 아니다.

실제 `SKILL.md`를 새로 만들거나 수정할 때는 호출 가능한 Codex `$skill-creator`를 우선 사용한다. 이 능력은 외부 하네스 의존성이 아니며, 해당 도구의 초기화·`quick_validate.py` 절차와 필요한 Python 의존성 준비를 따른다. 경로·route·conductor·매니페스트처럼 스킬이 아닌 자산에는 적용하지 않는다. `$skill-creator`가 실제로 없을 때만 Homeostasis의 보조 fallback을 쓰고, 공식 검증과 동등하다고 주장하지 않는다.
