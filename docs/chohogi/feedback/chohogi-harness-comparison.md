# ARC 하네스와 초호기 비교

## 결론

초호기에 필요한 것은 스킬 수의 확대보다 **장기 작업의 요구사항 회수, 실행 상태의 연속성, 실제 결과에 대한 평가**다. 그렇다고 ARC의 Provider Adapter로 초호기를 대체해야 한다는 뜻은 아니다. ARC adapter는 모델 호출 사이의 상태를 운반하고, 초호기는 작업의 범위·권한·결정·검증을 관리한다. 서로 다른 책임이다.

핵심 판단은 다음과 같다.

- **채택할 원칙:** 모델 이름이나 단가만이 아니라 모델·추론 수준·런타임·상태 전략을 묶어서 결과와 비용을 평가한다.
- **초호기가 이미 가진 것:** 작업 흐름, 승인 경계, 문서 소유권, 실행 기록, 기준본 확인, 제한된 비교 평가 계약.
- **보완할 것:** 기록의 존재가 실제 회수·적용으로 이어지는지 검증하고, 평가에 상태 전략과 총비용을 명시한다.
- **확인 전 구현하지 않을 것:** Codex가 이미 담당할 수 있는 native 상태 보존·compaction을 초호기가 중복 구현하는 일.
- **근거 없는 결론:** ARC 점수 향상이 스킬 추가 때문이라는 주장, 초호기의 과거 누락이 compaction 때문이라는 단정, Astra/high가 모든 업무에서 low보다 경제적이라는 일반화.

이 문서는 2026-09-14 기준의 비교 연구이며 **정책 변경안의 승인이나 구현 완료 기록이 아니다**. Sazu에서 관측된 실패와 초호기 비교를 다루므로 기존 제품 UI 비교 보고서와 분리하되, 관련 근거·제안·체크리스트는 이 문서 하나에서 관리한다. 전역 정책의 소유권은 Chohogi 저장소에 남는다.

## 1. 대상 글과 증거의 구분

찾은 글은 [GeekNews의 「GPT-6 Astra: 하네스가 곧 제품이다」](https://news.hada.io/topic?id=33301)다. 연결 원문은 Mangat Rai의 2026-09-04 Few-Shot Academy 글이다. 논지는 단일 모델의 응답보다 기억·도구·문맥 관리·실행 제어를 포함한 시스템을 평가하자는 것이다. 원문의 업무 20~50개 평가 제안은 실무적 권고이지 통계적으로 증명된 필수 표본 수가 아니다. [원문](https://fewshotacademy.com/blog/gpt-6-astra-the-harness-is-the-product).[^1]

| 증거 | 답할 수 있는 질문 | 답하지 못하는 질문 |
| --- | --- | --- |
| GeekNews·Few-Shot 해설 | 결과의 제품적 의미와 평가 제안 | 구성요소별 인과 효과, 초호기의 실제 성능 |
| ARC 결과·평가 정책 | 해당 게임·설정에서의 점수와 비용, 비교 조건 | 일반 코딩·제품 개발의 성공률 |
| ARC 공개 코드 | 현재 참조 구현의 상태 전달·게임 실행 방식 | 과거 Astra 평가에 쓰인 모든 설정의 동일성 |
| PRO-LONG 논문 | 다른 기억·도구 조건을 비교한 실험 | ARC Provider Adapter의 필수 스킬 목록 |
| OpenAI 공식 문서 | API 기능과 책임 경계 | 현재 이 Codex 세션의 숨겨진 내부 구현 |
| 초호기 현재 소스·감사 기록 | 정책과 도구가 실제 보장하는 범위 | 새 세션의 준수율·경제성에 대한 실측 결론 |

## 2. ARC 결과의 올바른 해석

ARC-AGI-3의 제한된 게임 환경에서는 같은 Astra/high도 하네스에 따라 다음 결과를 보였다. 비용은 해당 평가 실행의 비용이지 일반 업무 1건의 가격이 아니다. 표는 ARC 블로그의 반올림 값을 따른다. [ARC 발표](https://arcprize.org/blog/astra).[^2]

| 추론 수준 | Standard 점수 / 비용 | Provider Adapter 점수 / 비용 |
| --- | --- | --- |
| low | 17.5% / $38,166 | 98.0% / $21,298 |
| high | 54.8% / $40,705 | 99.9% / $18,817 |
| max | 62.7% / $26,098 | 98.6% / $17,332 |

동일 high 비교는 +45.1%p, 약 53.8% 비용 감소다. 반면 대표 수치 62.7→99.9는 max와 high의 비교이므로 동일 추론 조건이라고 쓰면 안 된다. 3.66배 속도·49% 토큰 감소는 두 하네스 모두 해결한 167개 게임-추론 수준 쌍에 대한 집계다. 실패한 실행까지 포함하는 보편적 개선율이 아니다. [ARC 발표](https://arcprize.org/blog/astra).[^2]

**분석:** 이는 하네스 조건이 성능을 크게 바꿀 수 있다는 강한 증거다. 그러나 상태 보존·압축·프롬프트 차이 등이 묶여 있으므로 각 요소의 단독 효과까지 분리한 실험은 아니다. 실제 서비스에는 비결정적 도구, 사용자 변경 요청, 비가역적 행동과 권한 문제가 더해진다. 게임 점수를 곧바로 제품 성공률이나 AGI 판정으로 옮길 수 없다.

### 모델 비용 판단에 주는 수정점

이 결과에서는 추론을 많이 하더라도 불필요한 게임 행동과 후속 호출을 줄여 총비용이 낮아질 수 있었다. 따라서 ‘낮은 effort = 저렴한 작업’이라는 등식은 성립하지 않는다. 다만 Terra/high와 Sol/low의 우열을 이 Astra 실험으로 판정할 수는 없다.

권장 비교 지표는 다음과 같다.

`수용 결과당 비용 = (성공·실패·재시도 전체의 모델 비용 + 도구 비용) / 수용된 결과 수`

여기에 사람의 검토·재작업 시간, 지연시간, 실패율, 안전 위반을 별도로 보고한다. 수용 결과가 0이면 비율을 유리하게 계산하지 않고 실패로 표시한다. 캐시 입력과 추론 토큰의 과금 범주를 확인하여 중복 계산을 피한다. **현재 승인된 Astra/low 정책은 이 연구로 변경하지 않는다.**

## 3. 공급자 중립 Standard harness

여기서 Standard는 국제 표준 인증이나 모든 에이전트의 표준 설계가 아니라 **ARC가 정의한 공통 최소 평가 조건**이다. 서로 다른 공급자의 모델을 유사한 인터페이스에서 비교하기 위해, 모델이 보이는 메모에 필요한 내용을 남기도록 한다. Provider Adapter 결과는 별도 조건으로 보고한다. [ARC 평가 정책](https://arcprize.org/policy).[^3]

공개 구현의 공통 실행 루프는 다음과 같다.

`게임 관측 → 모델 입력 → 행동 파싱·검증 → 게임 실행 → 새 관측 → 반복·종료·기록`

관측에는 격자와 게임 상태·사용 가능한 행동 등이 들어간다. 게임 행동 한도, 재시도, 종료 판정, 사용량 기록은 루프가 관리한다. `manual_rolling`은 가시적인 메시지 이력을 사용하며 한도가 넘으면 오래된 내용을 제거한다. 매 호출마다 반드시 완전히 초기화되는 구조라고 설명하면 부정확하다. 모델이 지속적으로 재기록한 메모는 이후에도 남을 수 있다. [agent.py](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/agent.py).[^4]

중립성의 장점은 공급자별 특수 기능의 영향을 줄이는 것이다. 한계는 특정 공급자의 실제 배포 기능까지 충분히 사용한 최고 성능을 측정하지 않는다는 것이다. **공통 조건의 비교와 배포 시스템의 비교는 경쟁하는 정답이 아니라 서로 다른 질문**이다.

## 4. OpenAI Provider Adapter의 실제 구성

검토한 공개 저장소는 `arcprize/arc-agi-3-benchmarking`, 기준 commit은 `eb6b8cd5ca8ad001339bb0184fdb979e93031679`이다. 동일한 게임 실행 루프에서 공급자 고유의 상태 전달 방식을 사용하는 구조다. [저장소](https://github.com/arcprize/arc-agi-3-benchmarking).[^4]

| 부분 | 실제 책임 |
| --- | --- |
| `agent.py`, `base.py` | 관측, 모델 차례, 행동 검증·실행, 종료·예산 |
| `runtime_registry.py` | adapter 식별자와 가능한 상태 전략 연결 |
| `runtime_state.py` | 상태 형식·adapter/strategy 호환성 검증, 안전한 메타데이터 |
| `openai_runtime.py` | native 응답 항목 보존·재전달, compaction 이후 이력 정리 |
| `runtime_adapters.py`, `runtime_clients.py` | Responses API 요청 변환과 SDK 호출 |
| `model_configs.yaml` | 모델·추론·상태 전략·문맥 한도 등 실행 설정 |
| recording 관련 모듈 | 행동·사용량·실행 증거 기록 |

특히 `openai.responses.v1`의 `continuous_conversation` 경로는 다음과 같이 동작한다.

1. 이전 `input_items`와 새 관측을 결합한다.
2. Responses API에서 재사용 가능한 native output 항목을 받는다.
3. 메시지뿐 아니라 암호화된 reasoning·compaction 항목도 다음 상태에 남긴다.
4. 자동 compaction 항목이 생기면 가장 최근 압축 항목부터 이후 이력을 유지한다.
5. 감사용 메타데이터에는 항목 종류·수량 등을 남기고 암호화된 내용 자체를 제거한다.

**중요한 구현 세부사항:** 이 경로는 `store: false`, `include: [reasoning.encrypted_content]`, `reasoning.context: auto`, `reasoning.summary: auto`를 요구한다. `previous_response_id`·`conversation` 및 background 모드와의 혼용은 거부한다. 즉, 이 참조 구현은 서버 저장 conversation ID를 잇는 대신 호출자가 opaque 항목을 다시 전달한다. [openai_runtime.py](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/openai_runtime.py).[^5]

저장소에는 `previous_response_id`를 이용하는 별도 adapter 경로도 있다. 이것을 위 `continuous_conversation` 구현과 혼동하면 안 된다. [runtime_adapters.py](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/runtime_adapters.py).[^6]

공개 YAML의 Provider Adapter 예시는 **Sol/max**이며 압축 임계값은 175,000이다. 이것을 Astra 발표 실행의 정확한 설정이라고 단정할 수 없다. [model_configs.yaml](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/model_configs.yaml).[^7]

OpenAI 공식 문서도 자동 compaction과 opaque 항목의 재사용을 설명한다. 다만 명시적 `/responses/compact`의 반환값은 그대로 전달하라는 별도 규칙이 있다. 위 참조 코드의 자동 압축 후 이력 정리를 모든 압축 방식에 일반화해서는 안 된다. 암호화된 항목은 사람이 읽는 요약이나 공개된 내부 추론 전문과 동일하지 않다. [Compaction](https://developers.openai.com/api/docs/guides/compaction).[^8]

### 어떤 스킬을 쓰는가?

**공개 ARC 참조 하네스에서는 `SKILL.md` 기반 스킬 로더나 스킬 묶음을 확인하지 못했다.** 행동 파싱·게임 제어·상태 전달을 수행하는 코드가 있으며, 이를 Codex의 스킬과 동일시하면 안 된다. 이 결론의 범위는 검토한 공개 저장소이며 공급자의 비공개 내부 전체가 아니다. [공개 구현](https://github.com/arcprize/arc-agi-3-benchmarking/tree/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking).[^4]

OpenAI에서 말하는 Agent Skills는 `SKILL.md`와 참고자료·스크립트 등을 묶은 재사용 지침이다. Responses의 shell 도구나 Agents API sandbox에 별도로 제공할 수 있지만, 이것이 ARC adapter에 자동으로 설치되었다는 뜻은 아니다. [Skills 공식 문서](https://developers.openai.com/api/docs/guides/tools-skills).[^9]

또한 **OpenAI Provider Adapter ≠ OpenAI의 완성된 Codex/Agents API 하네스**다. 전자는 이 벤치마크의 Responses 연결 구현이고, 후자는 세션·도구 실행 등을 관리하는 더 넓은 런타임이다. [Agents 비교](https://developers.openai.com/api/docs/guides/agents).[^10]

## 5. 이론적·실험적 근거

### 5.1 긴 컨텍스트와 필요한 정보의 활용은 다르다

`Lost in the Middle`은 관련 정보의 위치에 따라 장문 활용 성능이 달라지는 현상을 보였다. 이는 ‘문맥에 들어 있다’와 ‘필요할 때 정확히 활용한다’가 다름을 뒷받침한다. 다만 과거 모델·과제의 연구이므로 Astra에서 동일한 감소 폭이 발생한다고 단정할 수는 없다. [Liu 외, TACL 2024](https://aclanthology.org/2024.tacl-1.9/).[^11]

**초호기 적용 판단:** AGENTS에 요구를 적거나 PD 파일을 만들어 두는 것으로는 충분하지 않다. 작업 시작·관련 소비자 수정·검증 시점에 해당 조항을 회수하고 실제 결과와 대조해야 한다. 더 큰 프롬프트로 모든 문서를 상시 주입하는 방식만이 해답은 아니다.

### 5.2 요약 시점의 선택과 필요 시점의 검색

PRO-LONG은 기록 시 모든 중요도를 미리 예측하는 요약 대신, 외부 기록을 두고 필요한 시점에 프로그램으로 접근하는 방식을 연구한다. GPT-5.5 실험의 도구 조건에서는 read-only 23.1%, grep 추가 27.2%, Python 추가 38.3%, write/edit 추가 41.2%가 보고된다. 이는 Astra의 99.9% 실험과 다른 모델·조건이다. [PRO-LONG 논문](https://arxiv.org/pdf/2607.20064).[^12]

**초호기 적용 판단:** 짧은 작업 봉투와 정확한 원본의 재접근을 병행해야 한다. 다만 ‘모든 대화·개인정보·도구 출력을 영구 기록’하는 설계는 초호기의 프라이버시 계약과 충돌한다. 승인된 문서·검증 증거의 식별자와 위치를 남기고 필요한 범위만 회수하는 것이 적합하다. 원문이 필요한 실행 로그는 접근권한·보존기간이 있는 런타임 계층에 분리해야 한다.

### 5.3 재사용 가능한 도구와 내장 스킬은 다르다

ARC는 별도의 **PRO-LONG 실험**에서 Astra가 sandbox 안에 탐색·전투·상태 동기화 코드를 만드는 모습을 소개한다. 이는 Provider Adapter 점수의 필수 구성 설명이 아니다. [ARC의 별도 도구 실험](https://arcprize.org/blog/astra).[^2]

**초호기 적용 판단:** 반복 계산·검증은 작은 실행 도구로 외부화할 수 있다. 그러나 일회성으로 만든 코드를 즉시 전역 스킬로 승격하면 안 된다. 프로젝트 도구로 검증한 뒤 재사용성이 입증된 경우에만 기존 learning·homeostasis 경계를 따른다.

### 5.4 비동기 실행과 변경 지시에는 별도의 안전 제어가 필요하다

OpenAI의 비동기 도구 호출에서도 실행·작업 식별·결과 연결은 애플리케이션 책임이다. Mid-turn steering은 새 요구를 전달하지만 이미 시작한 도구를 취소하거나 완료된 쓰기를 되돌리지 않는다. 따라서 올바른 호출 ID, 오래된 결과의 처리, 중복 실행 방지, 승인 경계가 필요하다. [Async tool calling](https://developers.openai.com/api/docs/guides/async-tool-calling), [Steering](https://developers.openai.com/api/docs/guides/steering).[^13][^14]

**초호기 적용 판단:** 새 사용자 메시지는 정책적으로 범위를 바꿀 수 있지만 실행 중인 외부 쓰기의 취소를 자동 보장하지 않는다. 외부 효과 직전에 최신 승인 상태를 확인하고, 취소·재시도·보상 행동은 실제 도구 계층에서 관리해야 한다. 이는 위 API의 책임 경계에서 도출한 설계 제안이지, 현재 초호기에 결함이 재현되었다는 보고는 아니다.

## 6. 현재 초호기와의 비교

초호기 기준은 Chohogi 저장소의 현재 작업 트리다. HEAD는 `72cbf00a96a5c87c15362e956d1221be867c3c06`이지만 미커밋 수정이 있어 HEAD만으로 현재 정책을 재현할 수 없다. 아래는 실제 현재 파일을 근거로 하며, 설치·인증 캐시로 런타임을 추정하지 않는다.

| 축 | ARC Standard | ARC OpenAI Adapter | 현재 초호기 |
| --- | --- | --- | --- |
| 목적 | 공통 최소 조건 모델 비교 | 공급자 특수 상태 기능을 사용한 비교 | 실제 작업의 범위·권한·역할·검증 관리 |
| 기억 | 가시적 메시지·모델 메모 | native opaque 상태·compaction | 작업 봉투·문서·실행 기록; 내부 모델 상태는 Codex 소관 |
| 지식 회수 | 게임 이력 | 보존된 상태 재사용 | 경로 안내·prior-feedback; 실제 회수 여부는 에이전트 실행에 의존 |
| 도구 | 제한된 게임 행동 | 같은 게임 행동과 상태 adapter | shell·파일·브라우저 등 현재 런타임이 노출한 능력 |
| 스킬 | 공개 참조 구현에서 로더 없음 | 공개 참조 구현에서 로더 없음 | 관련 방법 지침과 프로젝트 도메인 leaf |
| 완료 증거 | 게임 상태·점수·행동 수 | 동일 평가 + 상태 전이 메타데이터 | 선언된 artifact·검토·승인 기록; 의미적 완전성까지 자동 보증하지 않음 |
| 재개 | 보존된 게임·메시지 조건에 의존 | 호환되는 native 상태 전달 | checkpoint 기준본 검사; 모델 실행 상태 복원과는 다름 |
| 비용 판단 | 평가 실행 비용 | 상태 전략별 평가 실행 비용 | 현재 후보 정렬은 단가 합 중심; 작업 총비용은 별도 실측 필요 |

### 확인된 강점

초호기는 controller 중복 방지, 외부 능력과 권한의 분리, 문서 책임, 실행 기록의 개인정보 제한을 명시한다. 또한 평가 계약은 동일 fixture·모델·추론·도구 조건에서 baseline과 후보를 비교하고, 무권한 쓰기·프라이버시 침해를 하드 실패로 본다. 이는 최신 런타임 기능이 생겼다고 버릴 규칙이 아니다. [평가 계약](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/evaluation/README.md), [평가 예산](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/evaluation/evaluation-budget-policy.md).

### 확인된 한계와 미확인 영역

1. **작업 봉투는 요약이지 native state가 아니다.** 관련 문서를 다시 찾을 수 있게 하지만 요약 과정의 누락을 자동 복원하지 않는다. [context-packet](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/context-packet.md).
2. **checkpoint는 실행 상태 복원이 아니다.** 기록 도구는 기준본 일치를 확인하지만 provider reasoning 상태나 미완료 도구를 복구하는 런타임은 아니다. [execution-record.py](/home/ignivivo/github/Chohogi/tooling/execution-record.py), [기록 계약](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/execution-record-contract.md).
3. **현재 비용 후보 정렬은 단순하다.** `price_total()`은 입력·출력 100만 토큰 단가를 더한다. 후보는 이를 기준으로 정렬하고 허용된 최소 effort를 고른다. 입출력 비중·캐시·재시도·성공률·상태 전략을 반영하는 작업 비용 최적화가 아니다. [model-policy.py:82](/home/ignivivo/github/Chohogi/tooling/model-policy.py:82).
4. **평가 계약은 있지만 runtime 조건이 충분히 구조화되어 있지는 않다.** 현재 replay schema에는 모델·effort·toolCondition 등이 있으나 상태 전략·압축 이벤트·캐시·실행 비용을 각각 필수 필드로 정의하지 않는다. 자유 텍스트로 보완할 수는 있지만 비교 누락을 막기 어렵다. [replay schema](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/evaluation/replay-result.schema.json).
5. **파일·검증 통과는 실제 준수율이 아니다.** 초호기 자체 감사도 기계적 검증과 fresh-agent 실행 증거를 구분한다. Sazu 공유파트 누락 기록 역시 ‘결정이 존재한다’와 ‘화면에 반영됐다’가 다름을 보여준다. 이를 compaction의 직접 결과로 단정할 증거는 없다. [기능 현실 감사](/home/ignivivo/github/Chohogi/docs/chohogi/audits/2026-09-03-functional-reality-gap.md), [Sazu 누락 감사](../work-log/records/DBG-20260909-sharing-decision-drift/audit.md).
6. **Codex 내부 상태 전략은 미확인이다.** 초호기 자체에 Responses adapter가 없다는 사실은 현재 Codex에 native 상태 보존이 없다는 증거가 아니다. 먼저 공개된 런타임 능력과 관측 가능한 메타데이터를 확인해야 한다.

## 7. 도입 방향과 우선순위 — 미승인 제안

추천 구조는 초호기의 권한을 유지하면서 실행 계층의 능력을 활용하는 것이다.

```text
초호기: 목표·범위·승인·소유권·수용 기준
  └─ Codex 또는 선택한 런타임: 세션·문맥·상태·도구 실행
       ├─ 필요한 스킬/프로젝트 문서: 방법·승인 요구사항
       └─ 모델/provider: native 추론·응답·지원되는 압축

프로젝트 기록: 결정·근거·결과의 감사 경로 — opaque 상태 저장소와 분리
```

| 우선순위 | 제안 | 비용·위험 | 채택 전 확인 |
| --- | --- | --- | --- |
| P0 | 평가 조건에 runtime/API surface/state strategy/version을 명시 | 문서·schema 검토 중심, 상대적으로 낮음 | 기존 평가 도구와 consumer 호환 |
| P0 | 요구 조항 → 관련 consumer → 검증 → 미구현의 대조 | 기존 계약 활용, 작업별 읽기 비용 증가 가능 | 실제 누락 감소와 불필요한 문서 읽기 측정 |
| P1 | 승인 문서·증거의 ID/위치로 필요한 과거 정보 회수 | 낮음~중간, 검색 품질·권한 관리 필요 | 원문 접근권한·만료·기준본 확인 |
| P1 | 성공·실패·재시도를 포함한 비용과 재작업 관측 | 계측 범위에 따라 중간, 가시성 제한 가능 | 숨겨진 수치를 추정값으로 채우지 않기 |
| P1 | 장기 작업·중단·지시 변경의 제한된 replay | 유료 실행 시 사전 예산 필요 | sealed fixture와 중단 기준 |
| 조건부 | 자체 Responses adapter 구축 | 중간~높음, SDK 변경·상태·보안 유지 비용 | 현재 Codex 기능으로 해결 불가한 구체적 사례 |
| 보류 | 스킬 대량 추가·모든 로그 영구 저장·기본 high 승격 | 프롬프트 비용·개인정보·정책 복잡도 증가 | 현재 증거만으로 정당화되지 않음 |

비용 범위는 구조적 상대평가다. 실제 개발 일수나 API 예산은 런타임 접근 범위와 평가 과제가 정해지지 않아 산정하지 않는다.

### 권장 검증 체크리스트

아래 항목은 아직 실행되지 않았다. 가능하지 않은 주입·관측 조건은 N/A로 기록하며, 테스트하지 못한 것을 통과로 처리하지 않는다.

- [ ] 초기의 승인 요구사항을 긴 작업 말미에 다시 필요하게 만들고 정확한 원본·상태를 회수하는지 확인한다.
- [ ] 압축 전후의 결정 ID·제외 범위·실패한 접근·다음 행동이 유지되는지 확인한다.
- [ ] 문서가 존재하지만 실제 consumer가 누락된 fixture에서 에이전트가 불일치를 발견하는지 본다.
- [ ] 작업 중 새 제약을 보내고 이후 실행 범위가 바뀌는지, 이미 실행된 행동과 구분하는지 확인한다.
- [ ] 도구 결과를 지연·역순으로 제공하고 올바른 호출·기준본에 연결하는지 확인한다.
- [ ] 재시도·재개가 같은 외부 효과를 중복 실행하지 않는지 확인한다.
- [ ] 외부 쓰기·공개·결제 등 비가역적 경계 전에 최신 승인을 확인하는지 본다.
- [ ] 모델/provider 변경 시 opaque 상태의 호환성을 가정하지 않고, 이식 가능한 승인 사실·근거만 별도로 전달한다.
- [ ] 성공률과 함께 전체 호출·비용·지연·재작업·하드 가드 위반을 집계한다.
- [ ] 기준본·모델·effort·도구·스킬·runtime·adapter commit·상태 전략을 고정 또는 명시한다.

비교 축은 두 개로 나눌 수 있다. 첫째 동일 runtime에서 초호기 정책 적용의 이익을 본다. 둘째 동일 초호기 정책에서 runtime 상태 전략의 차이를 본다. 가능하면 2×2 실험으로 상호작용도 확인하되, Codex 내부 기능을 통제할 수 없으면 인과 비교라고 부르지 않고 관측 비교로 남긴다.

초호기의 현재 모델/route 정책 평가는 기본 최대 6쌍의 제한이 있다. 원문의 20~50개 과제를 그대로 유료 replay로 실행하지 않는다. 우선 소수의 대표 fixture와 수동·기계적 검증으로 시작하고, 확대는 별도 승인한다. 소수 회차 통과는 정책 활성화 근거일 수 있어도 일반 성능 우월성의 통계적 증명은 아니다. [현재 평가 예산](/home/ignivivo/github/Chohogi/assets/agents/trunk_orchestration/evaluation/evaluation-budget-policy.md).

## 8. 최종 판단과 재검토 조건

**초호기의 강점은 통제·권한·작업 구조이며, 이번 자료가 강조하는 보완점은 상태 연속성·필요 정보 회수·실측 평가다.** 작업 봉투를 native 상태와 혼동하거나, native 상태가 승인 문서와 검증을 대체한다고 생각하면 양쪽의 장점을 모두 잃는다.

먼저 기존 수단이 실제로 작동하는지 평가하고 누락을 관측해야 한다. 그다음 현재 Codex surface가 필요한 연속성을 제공하는지 확인한다. 자체 adapter는 부족한 기능이 확인되고 운영 책임과 예산이 승인된 경우의 선택지다.

재검토 조건은 공개 adapter 변경, Codex 기능의 관측 가능한 변화, 실제 장기 작업의 반복 실패, 비용·재작업 계측 결과, 혹은 모델 정책의 새 승인이다. 이 보고서는 API 호출 실험·paid replay·ARC 테스트 실행 결과를 포함하지 않는다.

## 9. 후속 검토: 실행 가능한 계약과 사관 기록

2026-09-14 후속 요구를 반영한 설계 검토다. 승인된 방향은 **작업 인계 방식 개선, 역사 기록 유지, 필수 동작의 프로그램화, 모델 설정의 YAML화, 명시적 최상위 모델 제한**이다. 구체적인 실행기·저장 형식·세부 라우팅 표는 아래 추천안이며 아직 구현하지 않았다. `astra-light`라는 표현은 별도 공식 모델 ID인지 Astra/low의 별칭인지 확인이 필요하다. 확인 전 기존 Astra/low 조합을 상한 해석의 기준으로 삼되 새 ID를 만들거나 모델 설정을 변경하지 않는다.

### 9.1 기록을 없애는 것이 아니라 책임을 나눈다

| 데이터 | 목적 | 생성·갱신 방식 | 다음 모델에 전달할 범위 |
| --- | --- | --- | --- |
| 사관 기록 | 무엇을 했고 왜 바뀌었는지 사후 점검 | 이벤트 추가, 정정은 새 이벤트, 증거 버전 참조 | 전체 주입하지 않고 필요한 사건 회수 |
| 실행 상태 | 무엇이 끝났고 다음에 무엇을 할 수 있는지 판정 | 검증된 이벤트로부터 코드가 계산 | 현재 제약·미완료 작업·증거 ID·권한·예산 |
| provider native 상태 | 동일 런타임 내 추론 연속성 | 호환되는 provider adapter가 관리 | 지원되는 동일 provider/model 경로에만 전달 |

사관 기록은 유지한다. 시각·도구 ID·실행 결과·증거 해시·설정 버전은 코드가 기록하고, 모델은 중요한 선택 이유·기각한 대안·남은 위험만 간결하게 보충하는 것이 좋다. 기록을 없애 절약하는 대신 **반복 서술과 전체 이력 재주입을 줄인다**. 사람이 작성한 `성공`이라는 설명과 도구가 관측한 `성공`을 구별한다.

실행 상태는 기록의 조회용 파생본이 될 수 있다. 승인 사실·관측 결과·미완료 검증에서 다음 행동을 계산하면, ‘역사 파일’과 ‘작업 봉투’를 서로 다른 내용으로 수동 관리할 이유가 줄어든다. 다만 파일이 같거나 해시 체인이 있다는 것만으로 기록의 진실성·작성자 권한이 보증되지는 않는다. 같은 주체가 로그와 승인값을 모두 고칠 수 있으면 신뢰 경계는 여전히 약하다.

LangGraph 문서도 thread 상태의 checkpoint와 thread 밖의 장기 store를 구분한다. 이 개념은 참고할 수 있지만 라이브러리 도입이 필수는 아니다. [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence).[^20]

### 9.2 문서, 예시, 스크립트, 실행 강제는 서로 다르다

| 수준 | 효과 | 보장하지 않는 것 |
| --- | --- | --- |
| SKILL의 자연어 규칙 | 목적·판단 기준 전달 | 실제로 읽거나 수행함 |
| 입력·출력·실패 예시 | 호출 방법과 경계 오해 감소 | 해당 호출을 생략하지 않음 |
| Python 함수·CLI | 호출했을 때 계산·검사 재현 | 에이전트가 반드시 호출함 |
| 실행기 내부 필수 gate | 통과하지 않은 해당 행동 차단 | gate 밖의 우회 경로까지 차단됨 |
| 모든 관련 호출 경로를 통제하는 gate | 명시된 기계적 정책을 실행 전에 강제 | 검사하지 않은 의미적 품질·사실성 |

핵심은 YAML이라는 확장자가 아니라 **어떤 소비자가 읽고, 실패했을 때 어디서 실행을 차단하는가**다. 테스트 실행 여부·모델 조합·승인 범위·증거 해시·예산은 코드로 검사할 수 있다. 좋은 설계인가, 해석이 충분한가 같은 판단은 여전히 모델·사람·도메인 테스트가 필요하다. 모든 작업을 하나의 고정 순서로 묶기보다 필수 선행조건과 비가역적 경계만 강제하는 편이 적합하다.

AgentSpec은 LLM 바깥에서 사건·조건·동작으로 runtime 제약을 집행하는 접근이다. 다만 의미적 판정에 모델을 쓰는 부분까지 결정론적으로 정확해지는 것은 아니다. [AgentSpec, ICSE 연구](https://arxiv.org/html/2503.18666v3).[^15]

Anthropic의 장기 에이전트 사례는 진행 기록과 구조화된 기능 목록의 효용을 보여준다. 그러나 JSON으로 쓰면 모델이 덜 잘못 수정했다는 관찰은 parser나 gate가 수정을 금지한다는 뜻이 아니다. 형식 개선과 실행 강제를 구별해야 한다. [장기 에이전트 하네스](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).[^18]

### 9.3 현재 소스에서 추가로 확인한 수정 대상

| 항목 | 관측과 근거 | 권장 수정 | 확신·범위 |
| --- | --- | --- | --- |
| 증거 등록 후 변경 | `artifact`가 해시를 저장하지만 `finalize`가 다시 비교하지 않음. 격리된 임시 fixture에서 등록 후 내용을 변경해도 `pass` 재현 | 완료 시 증거 해시·경로·기준본 검사, 과거 증거는 버전 참조, 새 상태는 재검증 | 높음, 실제 재현 |
| 사관 조회의 증거 누락 | artifact 이벤트에 경로·해시가 없고 checkpoint 이벤트에 요약·기준본이 없음. 상세는 mutable `state.json`에 있음 | 사건을 재구성하는 데 필요한 최소 상세를 append-only 이벤트에 포함 | 높음, 소스·조회 출력 확인 |
| 모델 상한의 강제 부재 | 모델 추천기는 승인 profile 입력·실제 호출을 소유하지 않음 | YAML profile의 정확한 model+effort 허용 조합을 호출 경계에서 검증 | 높음, 현재 소스·registry의 명시적 한계 |
| 모델과 effort 혼합 | 후보 선정이 공통 effort 순위·최솟값에 의존 | provider별 실제 enum과 작업 적합성을 분리; capability를 effort명으로 대체하지 않음 | 높음, 소스 확인 |
| 영향 지도 누락 | `genome_map.py impact tooling/model-policy.py`가 자기 자신만 반환하고 verifier·documentation 집합은 비었음. registry에는 관련 테스트가 존재 | 실제 consumer·테스트·설치 연결을 지도에 반영; 빈 영향 집합을 안전 증거로 쓰지 않음 | 높음, 명령 출력 관측; 근본 원인은 추가 조사 |
| 설치 경계 | 현재 manifest에 execution-record는 있으나 model-policy 실행 도구의 명시적 설치 항목은 없음 | 모델 실행 경로로 승격할 때 parser·설정·도구·runtime adapter의 배포 경로를 함께 검증 | 중간, source inventory 관측; 현재 기기 전부의 가용성을 단정하지 않음 |
| 스키마 해석 | 공통 strict YAML/JSON parser는 이미 있으나 모델 추천기는 일반 JSON loader 사용 | 기존 strict parser 재사용 + 별도의 profile schema 검증 | 높음, 소스 확인; 새 parser 중복 구현 불필요 |
| 전체 디렉터리 digest | 기록의 digest가 `.git`·work-log 외 파일을 넓게 순회 | 기준본 대상 명시, 비밀·캐시·빌드 산출물 제외, 관련 변경 감지 유지 | 높음, 소스 확인; 실제 민감값 유출은 관측하지 않음 |

근거: [execution-record.py](/home/ignivivo/github/Chohogi/tooling/execution-record.py), [model-policy.py](/home/ignivivo/github/Chohogi/tooling/model-policy.py), [strict parser](/home/ignivivo/github/Chohogi/tooling/semantic_contracts.py), [manifest](/home/ignivivo/github/Chohogi/manifest.json), [assurance registry](/home/ignivivo/github/Chohogi/assets/agents/functional_assurance/registry.json).

재현 기준 execution-record 소스 SHA-256은 `1fa8a0a17ef94471d379d5a4b22a2a7259f625f691c01e152251261a524fb6a1`이다. 순서는 임시 프로젝트에 증거를 생성하고 `begin → artifact → 증거 내용 변경 → finalize → review` 실행이다. finalize는 `status: pass`, review의 artifact에는 종류·acceptance ID·시각만 출력됐다. 이는 현재 gate를 강한 증거 무결성 검사로 해석하면 안 된다는 재현이며, 임의의 실제 프로젝트 파일을 변조한 실험은 아니다.

### 9.4 YAML 모델 정책과 사전 배정 방법

ARC에서 직접 받아들일 것은 **모델·effort·상태 전략·실행 한도를 설정으로 고정하고 그 설정으로 평가하는 방식**이다. ARC 저장소 자체가 초호기의 모든 작업에 적합한 동적 최적 라우터를 제공하는 것은 아니다. 사전 배정의 비용–품질 방법론은 RouteLLM 같은 별도 연구에서 참고해야 한다.

RouteLLM은 응답을 모두 생성한 뒤 고르는 방식이 아니라, 질문과 선호 데이터에 기반해 강한 모델과 약한 모델 중 하나를 먼저 선택한다. 품질 목표 아래 비용을 줄인다는 원칙은 적합하지만, 당시의 단일 응답 평가를 현재 장기 코딩 작업의 비용으로 그대로 대입할 수 없다. 초호기는 자체 작업 유형별 성공·재작업·시간 데이터를 수집해야 한다. [RouteLLM](https://arxiv.org/html/2406.18665v4).[^16]

권장 사전 배정 순서는 다음과 같다.

1. 현재 surface에서 호출 가능한 model/effort 조합과 승인 목록의 교집합만 만든다.
2. 작업별 필수 능력·위험·문맥 길이·시간 한도를 적용한다. 고난도 작업은 처음부터 적합한 상위 profile로 배정할 수 있어야 한다.
3. 유사 과제의 품질 하한을 충족하는 후보 중 예상 전체 비용·지연·재작업을 비교한다. 단가 합은 tie-breaker 수준의 보조 정보로 낮춘다.
4. 데이터가 부족하면 기존 승인 역할 profile을 보수적 기본값으로 사용한다. 근거 없는 성공확률을 계산하지 않는다.
5. 같은 접근의 반복·검증 실패·예산 소진을 감지하면 승인된 상한 안에서 전략 변경·재배정을 결정한다. 상한을 넘는 자동 승격은 금지한다.
6. 상한에서 실패하면 범위 축소·근거 수집·사람에게 보고 중 하나로 끝낸다. ‘끈질김’을 무한 재시도로 구현하지 않는다.

아래는 **필드 설계 예시**이며 현재 loader가 지원하는 설정이 아니다. `astra-light`가 Astra/low를 뜻한다는 확인을 전제로 내부 profile에 의미 있는 이름을 붙인 예다. 별도 provider 모델 ID라고 가정하지 않는다.

```yaml
schema_version: 1
profiles:
  astra_low_ceiling:
    provider: openai
    model: gpt-6-astra
    reasoning_effort: low
    availability: require_runtime_observation

policy:
  allowed_profiles_ref: approved_session_profiles
  ceiling_profile: astra_low_ceiling
  auto_raise_ceiling: false
  unknown_profile: deny
  missing_policy: deny

routing:
  evidence_ref: task_class_measurements
  require_quality_floor: true
  objective: total_cost_subject_to_quality_and_latency
  no_evidence: approved_role_default

execution:
  budget_ref: approved_task_budget
  validate_profile_before_each_call: true
  record_requested_and_observed_profile: true
  detect_no_progress: true
```

모델명 알파벳 순서나 단일 가격으로 ‘상한 이하’를 추정하지 않는다. 승인된 정확한 조합 목록을 사용한다. 예시의 `true`들도 실행 코드가 소비하고 거부 테스트가 있어야 의미가 있다. YAML에는 API 키나 자유로운 shell 명령 문자열을 넣지 않는다.

‘Astra/low가 high보다 저렴했다’는 경험담은 현재의 사용자 상한을 정하는 근거가 될 수 있다. 그러나 동일 과제·runtime·실패 비용이 통제되지 않았다면 보편적인 성능 법칙으로 등록하지 않는다. 반대 방향의 ARC 결과도 같은 한계로 다룬다.

### 9.5 추가로 받아들일 것과 가져오지 않을 것

- **승인·증거의 출처 분리:** 사용자 승인, 도구 관측, 모델 추정을 구별한다. 검색 문서나 tool output에 들어 있는 ‘승인됨’ 문자열로 권한이 생기면 안 된다.
- **요청과 관측 분리:** 요청한 모델·effort와 runtime이 확인해 준 값을 따로 남긴다. 확인 기능이 없으면 강제 완료가 아니라 미확인으로 표시한다.
- **재개 안전성:** 상태·정책·증거 버전을 묶고, 기준본이 바뀌면 재조정한다. 부작용 행동에는 멱등성 키·중복 억제·최신 승인 확인이 필요하다.
- **우회 검사:** YAML 오류, 없는 profile, Astra/high 지정, 누락된 증거, 등록 후 바뀐 증거, 승인 전 실행, 정책 파일의 자의적 수정, raw tool 우회를 거부하는 테스트를 둔다.
- **오류 설명:** 단순 거부뿐 아니라 누락된 선행조건·허용된 복구 행동을 기계적으로 반환한다. 안전 실패와 일시적 네트워크 실패의 재시도 정책은 분리한다.
- **수용 기준 보호:** 에이전트가 자신의 실패를 없애기 위해 필수 검사·품질 기준·예산을 낮출 수 없게 한다. 정책 변경도 별도 승인 경계를 통과한다.
- **검증기 비용 제한:** 모든 차례에 LLM 검토자를 부르는 방식을 기본으로 삼지 않는다. 결정론적 검사로 가능한 것을 먼저 처리하고 의미 판단만 제한적으로 요청한다.

PolicyGuide는 frozen workflow와 외부 추적의 효용을 보여주는 최근 연구다. 그러나 실험 구현은 LLM verifier의 판단에 의존하고 예외 시 fail-open이며, 실제 구성의 보장을 논문의 이상적 verifier 정리와 동일시할 수 없다. 부록의 시뮬레이션 전체 지연은 baseline의 약 5.45~5.78배였다. **절차 표현·외부 상태 추적·복구 안내는 참고하되, 매 차례 LLM 검토와 fail-open은 초호기의 필수 gate로 그대로 가져오지 않는다.** [PolicyGuide 본문·부록](https://arxiv.org/html/2608.19861v1).[^17]

이 보안 검토의 범위는 로컬 정책·모델 배정·파일 증거·도구 실행 경계다. 공개 문서와 repo 내용은 연구 자료이지 권한 소스가 아니다. 인증정보·계정 설정은 읽지 않았고, 외부 부작용·API 유료 실행·광범위한 공격 시험은 하지 않았다. 새로운 gate를 설치하기 전에는 실제 노출 도구와 우회 경로를 별도로 점검해야 한다.

### 9.6 구현 범위 선택과 추천 순서

| 선택지 | 얻는 것 | 한계·운영 부담 | 판단 |
| --- | --- | --- | --- |
| 설정·기록 도구만 보강 | YAML 해석, 인계 상태 생성, 증거 재검증 | 직접 도구 호출을 막지는 못함 | 필요한 기초지만 최종 목표는 아님 |
| 지원되는 실행 경계에 gate 연결 | 그 경계를 지나는 실제 호출을 강제 | 현재 Codex의 연결 가능 지점·우회 차단 능력 확인 필요 | 우선 추천, 가용성 확인 후 범위 확정 |
| 자체 모델·도구 runner 운영 | 소유한 모든 호출 경로·기록을 통합 제어 | API 비용, 상태·sandbox·인증·복구·업데이트 운영 책임 확대 | 기존 runtime이 요구를 충족하지 못할 때 별도 결정 |

추천 구현 순서는 **사관 기록의 무결성 → 인계 상태 계약 → YAML profile·거부 검사 → 실제 실행 경계 연결 → 과제별 비용 라우팅 보정**이다. 앞 단계에서도 ‘강제’를 과장하지 않는다. 예를 들어 wrapper를 우회해 raw shell을 호출할 수 있으면 wrapper 내부 검사만 보장한다고 표시해야 한다.

초호기의 ‘단일 하네스’ 원칙은 정책 소유권으로 유지할 수 있다. 다만 현재의 ‘Markdown·검증 스크립트·manifest만으로 동작’이라는 표현은 필수 런타임 gate가 추가되면 실제 구조에 맞춰 수정해야 한다. 모든 외부 framework를 새로운 controller로 도입할 필요는 없다. [현재 헌장](/home/ignivivo/github/Chohogi/assets/agents/roots_constitution/constitution.md).

이 단계의 산출물은 승인된 방향과 근거 있는 추천안이다. runtime adapter 선택·실제 우회 차단 범위·예산·`astra-light` 식별이 확정되기 전에는 전체 시스템이 프로그램적으로 강제된다고 선언하지 않는다. 관련 전역 코드·스킬·설정은 아직 변경하지 않았다.

## 출처

[^1]: Mangat Rai, [GPT-6 Astra: the harness is the product](https://fewshotacademy.com/blog/gpt-6-astra-the-harness-is-the-product), Few-Shot Academy, 2026-09-04. 발견 경로: [GeekNews](https://news.hada.io/topic?id=33301).
[^2]: Greg Kamradt, [OpenAI’s GPT-6 Astra on ARC-AGI-3](https://arcprize.org/blog/astra), ARC Prize, 2026-09-03. 수치 표·matched subset·별도 PRO-LONG 실험.
[^3]: ARC Prize, [Verified Testing Policy](https://arcprize.org/policy), ARC-AGI-3 Harnesses 절, 2026-09-14 확인.
[^4]: ARC Prize, [arc-agi-3-benchmarking](https://github.com/arcprize/arc-agi-3-benchmarking/tree/eb6b8cd5ca8ad001339bb0184fdb979e93031679), 고정 commit의 README·benchmarking 코드, 2026-09-14 확인.
[^5]: ARC Prize, [openai_runtime.py](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/openai_runtime.py), native 상태 보존·검증·압축 처리.
[^6]: ARC Prize, [runtime_adapters.py](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/runtime_adapters.py), API 변환·별도 server-state 경로.
[^7]: ARC Prize, [model_configs.yaml](https://github.com/arcprize/arc-agi-3-benchmarking/blob/eb6b8cd5ca8ad001339bb0184fdb979e93031679/benchmarking/model_configs.yaml), Sol/max Provider Adapter 예시.
[^8]: OpenAI, [Compaction](https://developers.openai.com/api/docs/guides/compaction), 2026-09-14 확인.
[^9]: OpenAI, [Skills](https://developers.openai.com/api/docs/guides/tools-skills), 2026-09-14 확인.
[^10]: OpenAI, [Agents](https://developers.openai.com/api/docs/guides/agents), 2026-09-14 확인.
[^11]: Nelson F. Liu 외, [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/), TACL 12, 2024, pp.157–173.
[^12]: [PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning](https://arxiv.org/abs/2607.20064), arXiv:2607.20064, 2026. [본문 PDF](https://arxiv.org/pdf/2607.20064), GPT-5.5 도구 조건 실험과 기억 구조.
[^13]: OpenAI, [Async tool calling](https://developers.openai.com/api/docs/guides/async-tool-calling), 2026-09-14 확인.
[^14]: OpenAI, [Mid-turn steering](https://developers.openai.com/api/docs/guides/steering), 2026-09-14 확인.
[^15]: [AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents](https://arxiv.org/html/2503.18666v3), arXiv:2503.18666v3. Runtime 제약의 사건·조건·집행과 한계.
[^16]: Isaac Ong 외, [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/html/2406.18665v4), 2025-02-23 개정본. 사전 배정·선호 기반 비용/품질 최적화.
[^17]: [PolicyGuide: From Guarding One Action to Guiding the Whole Workflow for Policy-Compliant LLM Agents](https://arxiv.org/html/2608.19861v1), 2026. §3.4, §5, Appendix D의 advisory 실행·fail-open·비용 한계.
[^18]: Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26. 진행 이력·구조화된 기능 목록·E2E 확인의 사례.
[^19]: Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), 2024-12-19. 정해진 workflow와 model-directed agent의 구분·programmatic gate.
[^20]: LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), 2026-09-14 확인. Thread checkpoint와 장기 store의 구분.

초호기·Sazu의 근거 파일은 본문에서 현재 로컬 경로로 연결했다. 파일명이 가리키는 코드·계약과 실제 실행 성능의 증명을 구분한다.
