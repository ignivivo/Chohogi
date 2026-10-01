# Genome inheritance

Genome inheritance는 여러 프로젝트에서 재사용할 가치가 검증된 **예방 자산**을 보관하는
초호기의 상속 저장소다. 실패 원문이나 단순 관찰을 저장하지 않으며, 자동으로 읽히거나
모든 작업에 주입되지 않는다.

- `records_promotions/`: 왜 승격되었는지, 증거·범위·한계를 기록한 전역 승격 기록
- `assets_inherited/`: 실제 재사용 자산(스킬, 검사 스크립트, 계약 템플릿 등)
- `candidates/`: 확인된 예방이지만 독립 적용 증거가 부족해 자동 발견·설치되지 않는 승격 후보
- `index_registry.yaml`: Learning이 다중 프로젝트 증거로 승격한 예방 자산의 상태와 명시적 호출 조건. 승격된 자산이 없으면 `assets: []`가 정상이다.
- `xylem_provenance/provenance.json`: 위 승격 경로와 별개로, `skills/`(reusable methods) 각 항목이 어디서 왔는지(`absorb-core`=초호기 자체 baseline, `mirror-baseline`=외부 소스 압축 반영 등)와 license·origin·local delta를 추적하는 공급망 원장. `tooling/verify-provenance.py`가 `skills/`의 모든 active leaf를 빠짐없이 커버하는지 검사한다. 이 파일은 Learning 승격 자산이 아니라 reusable method 카탈로그 자체의 출처를 다룬다 — `index_registry.yaml`을 대체하지 않는다.

프로젝트에서 발생한 사건의 자세한 전후 코드와 회귀 증거는 그 프로젝트의 Git과 `docs/work-log/records/`에 한 번만 남긴다. 전역 승격이 필요하면 프로젝트 기록은 genome_inheritance 자산 ID만 가리키고, 같은 역사를 중복 복사하지 않는다. 모든 자산은 trigger/non-trigger, source record ID, 검증, owner, review signal, expiry와 retirement condition을 가진다.

`candidates/`는 활성 skill이 아니며 `index_registry.yaml`의 promotion rule을 만족하기 전에는 Codex discovery 경로나 전역 방법 카탈로그에 넣지 않는다.
