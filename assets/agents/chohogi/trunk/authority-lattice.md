<!-- chohogi:authority-lattice -->

# 권한 격자 · Authority lattice

작업 권한은 자동 승계되지 않는다. 아래 권한은 낮은 단계에서 높은 단계로 암묵적으로
올라가지 않으며, 작업 봉투에 필요한 최고 권한과 근거를 남긴다.

| 권한 | 허용 범위 | 별도 근거가 필요한 경우 |
| --- | --- | --- |
| `read` | 조사·진단·검토·phloem 초안 | 모든 지속 변경 |
| `specified-write` | 사용자가 지정하거나 구현 범위로 승인한 파일 변경 | 공유 계약·외부 효과 |
| `shared-contract-write` | 생산자·소비자 계약과 관련 테스트의 동시 변경 | 영향받는 소비자와 검증 경계 |
| `external-side-effect` | 배포, 결제, 메시지, 외부 데이터 변경 | 명시적 사용자 승인 또는 기존 권한 |
| `global-asset-change` | 초호기 core, 전역 skill, amyloplast 변경 | homeostasis 또는 learning의 승격 증거 |
| `irreversible-or-costly-action` | 되돌리기 어려운 삭제, 승인되지 않은 비용 | 사용자 결정 |

Debugging의 수정 권한은 `specified-write`까지이며, 전역 정책·skill·설치 변경 권한을
부여하지 않는다. read-only 작업은 phloem 관찰 봉투를 만들 수 있지만 영속 기록은 만들지
않는다.
