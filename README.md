# 초호기 (初號機) / Chohogi

초호기는 Codex 작업을 위한 이식 가능한 단일 하네스다. 초호기는 workflow,
authority, skill lifecycle, 설치·발견, 검증 정책을 소유한다. 플러그인·MCP·인증·개인
설정은 필요할 때 호출하는 provider이지 초호기의 controller가 아니다.

초호기는 Linux, WSL, Docker 같은 POSIX shell 환경을 지원한다. native Windows와
PowerShell adapter는 지원하지 않는다.

## 빠른 시작

```bash
bash tooling/install.sh
bash tooling/verify-install.sh
```

The installer obtains its inventory from `manifest.json`. A v1 owned install is staged,
then preserved under `~/.agents/chohogi-backups/` before v2 is promoted. List backups
with `bash tooling/prune-backups.sh`; removal requires the displayed absolute path and
`--confirm`.

## 현재 구조

현재 기관, 호출 관계, active capability, verification coverage는 사람이 직접 갱신하는
문서가 아니라 source에서 생성한 [genome map](docs/chohogi/genome-map.md)으로 본다.
AI agent는 같은 내용의 `docs/chohogi/genome-map.graph.json`을 읽어 변경 영향 범위를
계산한다.

```bash
python3 tooling/genome_map.py build
python3 tooling/genome_map.py impact assets/agents/reusable_methods/security-and-hardening/SKILL.md
python3 tooling/genome_map.py check
python3 tooling/verify-security-boundary.py
```

## 운영 원칙

- conductor는 substantial 작업에서 하나의 workflow만 선택한다.
- capability와 provider는 선택된 workflow 뒤에만 사용하며 controller가 될 수 없다.
- `learning`은 확인된 실패의 최소 예방을 다루고, `homeostasis`는 초호기 자체의
  정책·수명주기·설치·발견·정합성을 다룬다.
- `security_immune_system`은 위험 신호를 코드 전 수용 조건으로 분류하고, 전 프로젝트가
  공유하는 scanner/CI gate protocol을 소유한다. 프로젝트별 scanner 설정은 adapter이지 leaf가 아니다.
- Homeostasis repair loop는 변경점의 영향 집합을 계산하고, 선언 대비 실제 상태를
  검사한 뒤 repair packet을 낸다. 수리와 재검증은 정상 권한 절차로 수행한다.

세부 계약은 `assets/agents/`에, 설치 대상 연결은 `manifest.json`에 있다.
