---
name: session-forensics
metadata:
  chohogi_assurance: advisory
description: "Diagnose why a past agent session (Codex/Claude) diverged from its intended outcome — scope drift, repeated containment work, a plan that quietly excluded the real goal, or a tool/skill failure — by reading the actual session rollout/transcript turn-by-turn with file:line evidence. Use inside the debugging route when the failure is not a code bug but the agent's own prior work/plan drifting from user intent, and a later human partner needs an evidence-backed case file rather than a guess."
---

# Session forensics

이 방법은 코드 버그가 아니라 **과거 에이전트 세션 자체**(계획 선택, 스킬 사용, 반복 작업,
요청 충돌)를 진단 대상으로 삼는다. `debugging` route 안에서만 쓰며, route·권한·완료를
스스로 정하지 않는다. 재현 가능한 코드 결함이면 `debugging.md`의 일반 절차를 그대로 쓴다.

## 언제 쓰는가

- 사용자가 "왜 이 세션이 의도한 결과 대신 다른 걸 했는가"를 물을 때
- 반복된 봉쇄·정리·재작업이 있었는데 원래 목표는 진행되지 않았을 때
- 세션이 선언된 계획(active-plan)을 따랐는지, 그 계획 자체가 목표를 배제했는지 구분해야
  할 때
- 나중에 사람이 검토할 근거 기반 case file이 필요할 때 (인상·추측 요약은 이 방법의
  대상이 아니다)

## 절차

1. **문제 정의**: 조사 대상 세션 id(들)과 사용자가 실제로 궁금해하는 질문을 한 문장으로
   고정한다. "느낌이 이상하다"가 아니라 관측된 증상(반복 작업, 목표 미달성, scope 이탈)으로
   좁힌다.
2. **Triage verdict**: 세션이 선언된 active-plan/정책을 따랐는지 먼저 확인한다. 따랐다면
   그 계획 자체가 목표를 배제했는지(`docs/**/plans/*.md`의 범위 문구)를 파일:줄로 인용해
   판정한다. 이 판정이 이후 모든 finding의 뼈대다.
3. **Environment**: OS, harness/버전, 사용된 모델(변경 시점 포함), 설치된 plugin/extension,
   적용된 지침 파일(AGENTS.md/CLAUDE.md/project leaf) 경로를 관측 가능한 것만 적는다.
   확인 못 한 항목은 추측하지 말고 `unknown`으로 남긴다.
4. **Sessions examined**: role(main/subagent), session id, 절대 경로, 측정된 줄 수/바이트
   수를 표로 남긴다. 분석에서 제외한 후보 세션과 그 이유도 `Rejected candidates`로 남긴다.
5. **Timeline**: turn 단위로 (가능하면 줄 번호·시각과 함께) 요청 한 줄 요약과 발생한 이벤트를
   나열한다. 시각을 추출하지 못했으면 "not extracted"라고 쓴다 — 빈칸으로 얼버무리지 않는다.
6. **Findings**: 최소 아래 범주로 나누고, 각 finding에 `evidence`(정확한 파일:줄과 인용문)와
   `confidence`(high/medium/low)를 반드시 단다. evidence 없는 주장은 finding이 아니라
   가설이다.
   - 스킬/도구 사용 타임라인
   - 계획 준수 여부 (선언된 범위와 실제 작업의 일치/불일치)
   - 반복 작업 (같은 파일·같은 결론을 되풀이한 지점)
   - 실패와 복구 (도구 실패, patch 재시도, 롤백)
   - 품질 증거 (검증 통과가 실제로 무엇을 증명했는지, 무엇을 증명하지 못했는지)
   - 요청 충돌 (사용자의 서로 다른 turn 지시가 모순될 때 무엇을 우선했는지)
   - 비용·시간 (하네스가 실제로 제공하는 counter만 인용; 없으면 `unavailable`이라고 쓰고
     계산하지 않는다)
   - 사용된 외부 provider/plugin/skill (이름·버전·관여 가능성. "관여했다"는 관측과 "원인이다"는
     인과 주장은 분리한다 — 대개는 `possible`까지만 정직하게 말할 수 있다)
7. **Coverage notes**: 읽지 않은 것, 하네스가 제공하지 않아 확인 불가능한 기능, 사람이
   직접 재확인해야 할 지점을 명시한다. "세션이 진행 중이었는가" 여부도 남긴다.

## 산출물

이 방법의 결과는 `debugging` route의 종료 산출물(원인 상태, 증거, 제안)을 세션 단위로
확장한 case 문서다. material 조사라면 execution-record의 `fact`/`decision`/`outcome`으로
남기거나, 프로젝트의 feedback/audit 문서 root에 파일로 남긴다. 이 문서 자체가 active-plan이
되지 않으며, 발견한 원인을 스스로 구현하지 않는다 — `debugging.md`의 "다음 분기"를 그대로
따른다.

## 한계

이 방법은 관측된 로그가 실제로 존재하고 읽을 수 있을 때만 동작한다. 토큰·비용 총계는
하네스가 노출하는 counter가 없으면 계산하지 않는다. "가능성"과 "원인"을 구분하되, 하나의
세션·하나의 프로젝트에서 나온 결론을 보편적 결함으로 일반화하지 않는다 — 같은 패턴이
독립된 두 번째 세션/프로젝트에서 재현될 때만 confidence를 올린다.

이 절차는 외부 provider(diagnosing-superpowers 계열 스킬)가 만들던 case file의 산출물
구조(문제 정의·환경·세션 목록·타임라인·범주별 finding·커버리지 노트)를 관찰해 초호기
내부 방법으로 재구성한 것이며, 그 provider의 이름·경로·원본 지침을 실행에 사용하지 않는다.
