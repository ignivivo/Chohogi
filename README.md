# 초호기 (初號機) / Chohogi

초호기는 Codex 작업 방식을 위한 단일, 이식 가능한 하네스입니다.

초호기 자체는 Git으로 옮길 수 있는 Markdown·스크립트 자산입니다. Codex Desktop 플러그인, MCP 연결, 인증 정보, 세션, 개인 `config.toml`을 포함하거나 요구하지 않습니다. 그런 기능은 설치 뒤 현재 런타임에 실제로 노출되어 있을 때만 선택적으로 사용할 수 있는 능력일 뿐, 초호기의 제어자가 아닙니다.

## 개념 구조

- `roots`: 변하지 않는 경계와 소유권
- `trunk`: 매 작업을 하나의 작업 흐름으로 분류하는 `conductor`
- `branches`: `learning`, `homeostasis` 같은 유지·개선 흐름
- `xylem`: 프로젝트를 넘어서 재사용하는 기술 스킬
- `leaves`: 각 프로젝트 Git 저장소의 도메인 스킬·계약·회귀 테스트
- `amyloplast`: 검증되어 전역 자산 후보가 된 학습 결과의 저장소

이 개념 구조와 Codex의 실제 탐색 경로는 다릅니다. `manifest.yaml`과 설치 스크립트가 둘을 연결합니다.

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
