# Codex-Claude Cowork: Claude 세션 초기 진단의 오류와 정정

## 목적

이 문서는 사람이 읽는 서술형 보고서가 아니라 **Codex가 이 프로젝트에 진입할 때 참조할 기계 가독 기록**이다. Claude Code 세션에서 사용자가 "초호기가 프로젝트를 자동 파악하지 못한다"와 "superpowers 폴더가 신뢰할 수 없게 생성된다"고 제기한 문제를, 최초 분석(틀림)과 재조사 후 정정(맞음)으로 대비해 기록한다. Codex는 아래 "정정된 결론"만 신뢰하고, "최초 분석(오류)"은 반면교사로만 참조한다.

## 사건 배경

- 세션: Claude Code (Sonnet 5), 프로젝트 `/home/ignivivo/github/Chohogi`
- 트리거: 사용자가 "초호기는 설치·실행하면 자동으로 프로젝트를 파악해야 하는데 왜 안 됐냐", "리뷰·피드백 만들 때마다 superpowers 폴더가 생기는데 검사·리뷰 능력을 못 믿겠다"고 질문
- 최초 분석자(Claude)는 `docs/chohogi/`, `docs/work-log/records/` 기존 자산을 확인하지 않고 프로젝트 루트만 보고 결론을 냈다.
- 이후 기존 문서(`docs/chohogi/plans/2026-09-23-observability-closure.md`, `docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md`, `docs/work-log/README.md`)를 읽고 최초 분석이 틀렸음을 확인했다.

## 최초 분석(오류) vs 정정된 결론

```json
{
  "schemaVersion": 1,
  "purpose": "record a verified analysis error for future Codex/Claude sessions in this project",
  "corrections": [
    {
      "claim_id": "project-leaves-unimplemented",
      "initial_claim": "프로젝트 루트에 CLAUDE.md, .agents/skills/, .codex/agents/가 없으므로 project leaves 패턴이 선언만 되고 구현되지 않았다",
      "initial_claim_status": "INCORRECT",
      "why_wrong": "프로젝트 루트 구조만 확인하고 docs/chohogi/, docs/work-log/records/ 등 실제 project-leaf 자산 디렉터리를 확인하지 않았다",
      "verified_fact": "docs/chohogi/plans/, docs/chohogi/feedback/, docs/chohogi/audits/, docs/chohogi/specs/, docs/work-log/records/ 가 이미 존재하며 다수의 execution record(LRN-0001~0011, INT-0001~0002, HOM-*)가 축적되어 있다",
      "evidence": [
        "docs/chohogi/plans/2026-09-23-observability-closure.md",
        "docs/work-log/records/HOM-20260923-observability-closure/final-verification-report.md",
        ".agents/chohogi-document-registry.json"
      ],
      "residual_gap": "observability-closure 계획(2026-09-23)이 이미 '이 Chohogi checkout에 project document registry가 없었다'는 동일 계열 문제를 확인·수정·finalize했다. 즉 이 갭은 실재했으나 이미 해결된 과거 이력이지, 현재 미해결 문제가 아니다.",
      "confidence": "high"
    },
    {
      "claim_id": "superpowers-folder-chohogi-defect",
      "initial_claim": "superpowers 폴더 생성 원인이 불명확하며 초호기의 Learning/Homeostasis 프로세스 결함일 가능성이 있다",
      "initial_claim_status": "INCORRECT",
      "why_wrong": "superpowers 폴더의 실제 출처를 조사하지 않고 추측으로 초호기 결함이라 단정했다",
      "verified_fact": "superpowers는 초호기 자산이 아니라 Codex 플러그인 마켓플레이스에서 설치된 외부 플러그인이다. diagnosing-superpowers 스킬이 세션 진단 시 /home/ignivivo/.superpowers/diagnosing-superpowers/<session-id>/case.md 에 케이스 파일을 생성한다",
      "evidence": [
        "docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md:25 — Superpowers: /home/ignivivo/.codex/plugins/cache/openai-curated-remote/superpowers/6.4.2, diagnosing-superpowers SHA ded3c780dfaf5e3e19a28ee11109303d78d59a5c",
        "docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md:129 — /home/ignivivo/.superpowers/diagnosing-superpowers/01a0cd72-39e3-7af1-bd63-e3340264af79/case.md"
      ],
      "residual_gap": "동일 감사 141~145행(\"Superpowers involvement: possible\")은 Superpowers가 divergence의 '원인'이라는 증거는 없다고 결론짓는다. 즉 superpowers 폴더 생성 자체는 정상 동작이며 결함이 아니다. 다만 초호기가 외부 diagnosing 도구의 산출물을 자신의 project-leaf 체계(docs/work-log/records/)와 통합하지 않는다는 점은 별도 관찰 대상이다.",
      "confidence": "high"
    }
  ]
}
```

## 재조사로 확인된 실제 미해결 사항

최초 분석은 틀렸지만, 사용자가 느낀 "검증을 믿을 수 없다"는 우려 자체는 **초호기가 공식 문서에서 스스로 인정한 한계**와 부합한다. 아래는 추측이 아니라 초호기 소스에 명문화된 내용이다.

```json
{
  "confirmed_limitations": [
    {
      "source": "functional_assurance/registry.json",
      "field": "limits",
      "statement": "declared evidence is not equivalent to semantic or fresh-session proof",
      "meaning_for_codex": "Functional Assurance 통과 = 선언된 claim과 evidence 경로의 존재 확인일 뿐, 실제 런타임 동작이나 모델의 준수를 증명하지 않는다"
    },
    {
      "source": "functional_assurance/semantic-contract-registry.json",
      "field": "limits",
      "statement": "Strict declaration parsing proves only unambiguous interpretation",
      "meaning_for_codex": "JSON/YAML 문법 검증 통과는 의미론적 정확성과 무관하다"
    },
    {
      "source": "docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md",
      "field": "section 2, second-to-last paragraph",
      "statement": "The evidence supports a project-plan failure first and a Chohogi transition/semantic-acceptance gap second; it does not prove a universal Chohogi defect from this one project. Confidence: high for the first clause, medium for the second.",
      "meaning_for_codex": "Sazu 프로젝트에서 발생한 scope divergence의 1차 원인은 프로젝트 계획(P0~P3 큐) 자체의 결함이고, 2차로 초호기의 '전환/의미론적 수용' 갭이 medium 신뢰도로 지목되었다. 이 2차 항목은 아직 Chohogi 저장소에 execution record나 plan으로 반영되지 않은 열린 항목이다."
    }
  ],
  "open_item_requiring_followup": {
    "description": "초호기의 conductor/state-transition이 '프로젝트 계획의 전제가 사용자에 의해 명시적으로 부정되었을 때' 이를 감지해 plan 재검토를 트리거하는 메커니즘이 있는지 확인 필요",
    "evidence_pointer": "docs/chohogi/audits/2026-09-28-sazu-source-first-divergence.md:121-124 (6.6 Request conflicts, 두 번째 finding)",
    "recommended_next_flow": "debugging 또는 homeostasis (반복성·system-level 여부에 따라 conductor.md 기준으로 재판정 필요)",
    "not_yet_done": "이 항목에 대한 execution record, plan, 또는 decision은 아직 생성되지 않았다"
  }
}
```

## Codex를 위한 행동 지침

1. 이 프로젝트에 진입할 때 `.agents/chohogi-document-registry.json`의 `activeExecutionPlan`을 먼저 읽어라. 프로젝트 루트에 `CLAUDE.md`가 없다고 해서 project-leaf 체계가 없다고 단정하지 마라 — `docs/chohogi/`, `docs/work-log/records/`를 먼저 확인하라.
2. superpowers 관련 산출물(`/home/ignivivo/.superpowers/`, `~/.codex/plugins/cache/*/superpowers/`)을 발견해도 초호기 결함으로 단정하지 마라. 이는 별도 provider(diagnosing-superpowers)의 정상 산출물이다.
3. Functional Assurance/Semantic Assurance 통과를 "검증 완료"로 사용자에게 보고하지 마라. 반드시 "선언-근거 일치 확인이며 런타임/의미 증명이 아님"을 명시하라.
4. "open_item_requiring_followup"은 아직 어떤 route도 선택되지 않은 상태다. 이 항목을 다룰 때는 conductor.md 기준으로 debugging/homeostasis 중 하나를 명시적으로 선택하고 evidence를 남겨라. 이 feedback 문서 자체가 plan이나 실행 지시가 아니다.

## 문서 상태

- role: feedback-source (observation)
- 이 문서는 `.agents/chohogi-document-registry.json`에 등록되어야 하며, 등록 전까지는 Conductor의 feedback-scan 대상이 아니다.
- 활성 실행 계획을 대체하지 않는다. 현재 활성 계획은 `docs/chohogi/plans/2026-09-23-observability-closure.md`이며 이미 finalize되었다(2026-09-23).
