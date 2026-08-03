# 초호기 (初號機) / Chohogi

초호기는 Codex 작업 방식을 위한 단일, 이식 가능한 하네스입니다.

초호기 자체는 Git으로 옮길 수 있는 Markdown·스크립트 자산입니다. Codex Desktop 플러그인, MCP 연결, 인증 정보, 세션, 개인 `config.toml`을 포함하거나 요구하지 않습니다. 그런 기능은 설치 뒤 현재 런타임에 실제로 노출되어 있을 때만 선택적으로 사용할 수 있는 능력일 뿐, 초호기의 제어자가 아닙니다.

이 독립성은 Codex의 기본 능력을 배제한다는 뜻이 아닙니다. 실제 `SKILL.md`를 만들거나 고칠 때는 현재 호출 가능한 `$skill-creator`의 초기화·검증 절차를 우선 사용합니다. Python 같은 그 절차의 정상 의존성도 작업 단위의 격리 환경에서 준비합니다. 초호기의 자체 검사는 이 정식 검증을 대체하지 않는 보조 안전망입니다.

## 개념 구조

- `roots`: 변하지 않는 경계와 소유권
- `trunk`: 매 작업을 하나의 작업 흐름으로 분류하는 `conductor`
- `branches`: `learning`, `homeostasis` 같은 유지·개선 흐름
- `xylem`: 프로젝트를 넘어서 재사용하는 기술 스킬과 실행 방법
- `leaves`: 각 프로젝트 Git 저장소의 도메인 스킬·계약·회귀 테스트
- `amyloplast`: 검증되어 전역 자산 후보가 된 학습 결과의 저장소

이 개념 구조와 Codex의 실제 탐색 경로는 다릅니다. `manifest.yaml`과 설치 스크립트가 둘을 연결합니다.

전체 호출 경계·provider·프로젝트 leaf의 관계는 [운영 지도](docs/OPERATING-MAP.md)에
있다. 외부 skill을 초호기에 들일지, 외부 specialist로 둘지, provider로 둘지는
`trunk/skill-adoption.md`와 `xylem/provenance.json`으로 Homeostasis가 판정한다.

## 빠른 시작

Windows PowerShell:

```powershell
./tooling/install.ps1
./tooling/doctor.ps1
```

Linux/macOS:

```bash
./tooling/install.sh
./tooling/doctor.sh
```

일반 설치는 인증·플러그인·MCP·개인 설정과 기존 사용자 자산을 건드리지 않는다.

## 일상 route와 평가

`trunk/conductor.md`는 substantial 작업에서 엄격한 진입 조건을 만족하는 흐름 하나를
고른다. 전역 자산 생성처럼 고영향 지속 변경을 요청했지만 근거가 부족한 경우도 `direct`가
아닌 `defer`다. `defer`는 어떤 route·branch도 실행하거나 지속 변경을 하지 않는다. 그중
일상 작업 절차는 `trunk/routes/`에 있다.

- `product-decision`: 사용자의 선택 또는 제품 정책이 아직 열려 있을 때만 선택지를
  근거와 함께 정리한다.
- `delivery`: 요구사항과 성공 조건이 확정된 구현을 변경·검증 증거까지 완성한다.
- `debugging`: 관측 가능한 실패의 원인을 재현과 증거로 확인한 뒤 최소 수정한다.

`learning`과 `homeostasis`는 이 일상 route와 다른 branch다. 확인된 실패를 예방
자산으로 바꾸거나, 초호기 자체를 조정할 때만 선택한다.

흐름이 선택되면 `trunk/execution-allocation.md`가 실행 형태를 하나 정한다.
`direct`는 짧은 한 경계 작업, `sequential`은 공유 구현의 기본값, `scoped-delegation`은
독립적인 읽기 조사 또는 변경 뒤 검토에만 쓴다. 이 선택은 사용자 메뉴가 아니다. 역할,
파일 소유권, 모델 수준, 검증 경계는 이 계약 안에서 정하며 주 에이전트가 통합한다.

외부 하네스에서 배운 절차는 `xylem/execution-methods.md`와
`trunk/context-packet.md`로 흡수했다. 전자는 계획·TDD·디버깅·검토·검증 방법만
공급하고, 후자는 긴 작업의 최소 상태를 잇는다. 둘 다 controller·별도 팀·실행 방식
선택지를 만들지 않는다.

`trunk/capability-selection.md`는 이 내부 방법과 실제 외부 능력을 구분한다. Codex 기본
스킬은 현재 표면에 노출됐을 때 사용하고, 플러그인·MCP·커넥터는 외부 데이터·인증된
작업·브라우저 같은 실제 능력이 필요할 때만 provider로 사용한다. provider는 삭제 대상도
controller도 아니다. 반면 Superpowers·구 Meta-harness·Caveman에서 흡수한 방법은
초호기 내부 자산만 사용하며 원본을 실행 중 다시 읽거나 호출하지 않는다.

route 문서·fixture의 정합성은 다음으로 확인한다.

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tooling\verify-routes.ps1
```

Linux/macOS:

```bash
python3 ./tooling/verify-routes.py
```

`assets/agents/chohogi/trunk/evals/README.md`는 지금 할 수 있는 route 적합성 검증과,
실제 작업이 쌓인 뒤 수행할 성능 비교를 분리해 설명한다.

실행 배정 계약과 행동 fixture는 다음으로 검증한다.

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tooling\verify-execution-allocation.ps1
```

Linux/macOS:

```bash
python3 ./tooling/verify-execution-allocation.py
```

능력 선택 경계와 fixture는 다음으로 검증한다.

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tooling\verify-capability-boundary.ps1
```

Linux/macOS:

```bash
python3 ./tooling/verify-capability-boundary.py
```

## 스킬 수명주기와 검증

새 전역 스킬은 반복 가능한 경계와 검증 근거가 있을 때만 `homeostasis` 또는 `learning`의
결정으로 만든다. 실제 스킬 생성·수정은 `$skill-creator`를 우선 사용하고, 그
`quick_validate.py`를 실행한다. 이 저장소의 보조 포장 검사는 다음과 같다.

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tooling\verify-skills.ps1
```

Linux/macOS:

```bash
python3 ./tooling/verify-skills.py
```

보조 검사는 전역 플러그인이나 다른 하네스를 요구하지 않지만, 공식 YAML 검증을 대신한다고
주장하지 않는다. 상세 절차와 fallback 표기는
`assets/agents/skills/homeostasis/references/skill-lifecycle.md`에 있다.
