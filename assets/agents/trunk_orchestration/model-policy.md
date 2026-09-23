<!-- chohogi:model-policy -->

# 세션 모델 정책 계약

모델 배정은 모델명 하나를 고르는 행위가 아니다. 현재 실제로 호출 가능한
`provider + model + reasoning effort + role + 비용 근거`를 사람의 세션 정책으로
확정하고, 그 정책 안에서 작업·임시 역할에 배정하는 일이다.

## 권고와 사용자 선택

전역 기본 모델 profile이나 허용 모델 목록은 두지 않는다. Codex와 Claude는 서로 다른
실행 표면이므로 각각 자기 runtime에서 관측된 모델만 별도 후보로 제시한다. 권고는 강제
설정이나 allowlist가 아니라 비용·역할별 시작점이며, 사용자는 관측된 다른 모델과 effort를
자유롭게 선택할 수 있다. 새 프로젝트마다 첫 substantial 배정 전에 해당 runtime의 목록과
역할별 후보를 보여주고 확인받는다.

- 현재 공식 런타임 카탈로그에서 provider·model·effort 조합이 실제 선택 가능한지 확인한다.
  공개 모델 문서만으로 이 환경의 가용성을 보증하지 않는다.
- 사용자가 권고와 다른 조합을 선택하면 해당 프로젝트·역할 범위의 선택으로
  기록한다. 이를 다른 역할이나 프로젝트의 기본값으로 조용히 확대하지 않는다.
- 권고·선택 검증 도구는 후보·관측·계약만 확인하며 모델 실행이나 개인 설정 변경을
  강제하지 않는다.

## 실행 가능한 선택 확인

`recommend`는 실제 runtime catalog와 task capability·최소 추론 조건이 주어졌을 때 적격
조합을 보여준다. 후보를 허용 목록으로 제한하거나 저장된 전역 profile과 일치시킬 필요는
없다. `select`는 사용자가 명시한 임의의 관측 조합을 확인한다. 이 도구는 provider 실행,
품질 순위, 설정 변경을 통제하지 않는다.

## 2026-09-23 근거 갱신

아래 수치는 모델을 보편적으로 서열화하지 않는다. 작업·effort·harness가 다른 결과를
한 점수로 합치지 않으며, 외부 지표는 프로젝트별 직접 평가의 대체물이 아니다.

| 출처·조건 | 관측 결과 | 정책에서 허용되는 해석 |
| --- | --- | --- |
| Artificial Analysis 독립 평가, Intelligence Index v4.3.2, GPT-6 Luna/high 대 GPT-5.6 Sol/high | 종합 32 대 42, GDPval-AA 1290 대 1480, Terminal-Bench 4.0 5% 대 21%, AA 지수 평가의 task당 비용 $0.03 대 $0.81 | Luna/high는 평가상 매우 저렴한 후보이나, 일반 지식 작업·코딩에서 Sol/high와 동급이라고 볼 수 없다. task 비용은 해당 평가의 토큰 사용과 가격표를 반영한 추정치이며 보편 업무의 비용을 뜻하지 않는다. |
| OpenAI 내부 factuality 평가, GPT-6 Luna의 높은 effort 대 GPT-5.6 Sol | OpenAI는 오류 신고가 붙은 대화의 자체 평가에서 Luna가 Sol 수준의 사실성을 약 1/100 비용으로 달성했다고 보고했다. 정확한 effort 조합과 작업비용 계산 세부는 해당 요약에 명시되지 않았다. | 오류가 신고된 대화로 구성되어 일반 사용을 대표하지 않고, 점수는 응답 길이로 통제하지 않았지만 OpenAI의 verbosity sweep에서는 길이 의존성이 거의 없었다고 한다. 사실성 평가의 특정 결과를 코딩·계획 완성도로 확대하지 않는다. |
| Artificial Analysis, GPT-6 Sol/max 대 GPT-5.6 Sol/max | 종합 48 대 47, AA Intelligence Index의 task당 평균비용 약 $1.06 대 $1.99. GPT-6 Luna/max coding agent 지수는 전 세대 대비 2점 하락; GDPval-AA 약 75 Elo와 AA-Briefcase 약 45 Elo 하락, 더 짧은 산출물에서 rubric 항목이 빠지는 경향을 보고했다. | GPT-6 Sol/max는 이 평가에서 비용 효율 후보로 유망하다. max 결과를 medium/high의 보장으로 확대하지 않는다. Luna는 단가 인하만으로 품질 향상을 주장하지 않는다. |
| Artificial Analysis 독립 평가, Claude Opus 5.5 (adaptive reasoning, max effort, default fallback) 대 GPT-6 Sol/max | AA Intelligence Index 58 대 48, 해당 평가의 task당 평균비용 약 $5.98 대 $1.06 | 이 실행 조건에서 Opus는 더 높은 종합점수, Sol은 더 낮은 task 비용을 보인다. fallback을 포함한 해당 평가 설정의 비용은 실제 프로젝트 업무에 일반화되지 않는다. |
| Artificial Analysis 독립 평가, GPT-6 Sol/max 및 Luna/max 대 GPT-5.6 동급 모델 | Sol Coding Agent Index 57(+2), 작업당 $2.99(약 50% 절감); Luna 지수 41(-2), SWE-Atlas-QnA 44 대 49, DeepSWE 64% 대 66%, 비용은 약 60% 절감. Intelligence Index 작업당 비용은 Luna $0.07, Sol $1.06. | **비용 우선 Codex 권고의 근거:** Luna는 매우 저렴하지만 복잡한 코딩에서 동급이 아니므로 기본 시험 후보로 두고 검증·재작업을 추적한다. Sol은 Luna가 반복 실패하거나 재작업 비용이 커질 때 올리는 단계다. Astra는 평시 기본값이 아니라 비용 상향을 감수할 사용자가 고르는 예외다. 이 비용은 API 벤치마크 비용이며 Codex 구독 quota 소모량과 같지 않다. |
| Google DeepMind Gemini 3.8 Flash model card의 DeepSWE v1.1 | Gemini 3.8 Flash 73.7%, Claude Opus 5 74.0%, GPT-5.6 Sol 72.7%; Gemini Flash 가격은 프로모션 $0.75/$3.75, 일반 $1.50/$7.50 per 1M input/output tokens | 코딩 후보로 검토할 근거다. 제공자 model-card 결과이며, GPT-6 Sol/Luna 또는 초호기의 실제 작업 결과와 직접 비교한 것은 아니다. |

출처: [OpenAI GPT-6 Sol and Luna 발표](https://openai.com/index/introducing-gpt-6-sol-and-luna/),
[OpenAI API 가격](https://developers.openai.com/api/docs/pricing),
[Artificial Analysis GPT-6 Sol/Luna 평가](https://artificialanalysis.ai/articles/gpt-6-sol-and-luna-push-the-cost-efficiency-frontier),
[Artificial Analysis Luna/high 대 GPT-5.6 Sol/high 비교](https://artificialanalysis.ai/es/models/comparisons/gpt-6-luna-high-vs-gpt-5-6-sol-high),
[Artificial Analysis Opus 5.5 대 GPT-6 Sol 비교](https://artificialanalysis.ai/models/comparisons/claude-opus-5-5-vs-gpt-6-sol),
[Anthropic Opus 5.5 발표](https://www.anthropic.com/claude-opus-5-5),
[Google DeepMind Gemini 3.8 Flash model card](https://deepmind.google/models/model-cards/gemini-3-8-flash/).

Codex의 전역 출발 권고는 **GPT-6 Luna / medium**이다. 범위가 명확한 저위험 작업은
Luna/low, 보통 구현은 Luna/medium부터 시작한다. 복잡한 작업이나 Luna의 누락으로 재작업이
반복될 때 Luna/high·xhigh 또는 GPT-6 Sol/medium을 해당 작업에서 시험한다. Sol도 비용
상향이므로 자동 승격하지 않는다. Astra는 기본 profile에서 제외하고, 사용자가 비용 대비
추가 능력이 필요한 난제라고 판단할 때만 선택 후보로 제시한다. 이는 벤치마크와 초기 실사용
평가에 근거한 가역적 권고이지 강제 배치가 아니다.

Claude는 별도의 runtime/model card에서 Anthropic 모델끼리만 후보를 제시한다. Codex와
Claude 모델을 한 실행 배치의 대체 역할로 섞지 않는다. 실제 선택 가능성은 각 runtime의
관측 결과 또는 사용자 확인으로 확정한다. 제공자 benchmark는 출처와 한계를 표시하고, 가용성은
현재 런타임 catalog에서 관측하지 못하면 `unknown`으로 둔다.

`recommend`는 적격 후보와 관측된 입력/출력 가격을 보여줄 뿐, 입력·출력 단가를 더한
인위적 비용 순위나 품질 순위를 만들지 않는다. 작업당 비용은 모델의 실제 토큰 사용,
cache, 재시도, 도구 호출, harness에 따라 달라지므로 비교 가능한 평가 근거가 있을 때만
별도로 보고한다.

소유자는 trunk의 모델 배정 정책이다. 새 프로젝트마다 첫 substantial 모델 배정 전에
역할별 권고 배치를 제시하고 확인을 받는다. 같은 프로젝트의 새 대화/session만으로는
재확인하지 않는다. 다만 새 모델·모델 버전, 가격, 가용성, effort/capability 또는 관련
benchmark 업데이트가 감지되면 프로젝트가 이미 존재하고 profile이 확정되어 있어도
Model Session Policy card를 다시 제시하고, 기존 배치를 유지할지 특정 역할을 바꾸거나
시험할지 묻는다. 이는 자동 감시·알림을 뜻하지 않는다. 공개 발표나 benchmark만 감지된
경우 런타임 선택 가능성은 별도로 확인하고, 관측되지 않으면 `unknown`으로 둔다. 사용자
확인 전에는 새 정보로 기존 프로젝트의 기본 배치를 조용히 바꾸지 않는다. 정책은 근거의
날짜를 밝히고 다음 검토 때 갱신한다.

## 관측 경계

세션 시작 시, 현재 런타임 또는 호출 가능한 capability provider가 **공식적으로 노출한**
모델 카탈로그를 관측한다. 관측에는 provider, model, 사용 가능 여부, 선택 가능한
reasoning effort, 선언된 capability, 관측 시각, 가격 근거를 포함할 수 있다.

- 인증정보, 세션 토큰, 개인 `config.toml`, 캐시, 설치 흔적을 읽어 provider나 모델을
  추정하지 않는다.
- provider별 adapter가 실제로 없거나 호출 불가하면 그 provider는 `unknown`이다.
  `unknown`을 “사용 불가”나 “사용 가능”으로 바꾸어 추측하지 않는다.
- 가격은 공식 공개 가격 또는 사람이 제공한 계정별 근거가 있을 때만 기록한다. 공개 가격은
  실제 청구액을 증명하지 않으며, 가격 근거가 없으면 비용 비교도 `unknown`이다.
- `tooling/model-policy.py`는 catalog를 **발견하지 않는다**. 외부에서 관측되어 전달된
  비밀 없는 catalog를 검증·비교·추천할 뿐이다.

## 세션 시작과 사람 확정

새 프로젝트에 처음 들어가거나, 기존 프로젝트에서 역할·비용·추론 요구가 달라지는 첫
작업의 실행 배정 전에 역할별 권고 모델과 관측 가능한 대안을 Model Session Policy card로
제시하고, 사용자가 그대로 둘지 수정할지 묻는다. 권고 profile은 편의를 위한 출발점이지
사용자의 취향이나 비용 판단을 대신하지 않는다. 사용자는 각 작업·역할별로 관측된 조합을
선택하거나 이후에도 변경할 수 있다.
프로젝트마다 기본 배치를 다시 보여주되, 같은 프로젝트의 동일한 profile 안에서 반복되는
하위 작업마다 되묻지는 않는다. 카드에는 다음을 포함한다.

1. 관측된 provider/model/reasoning effort와 관측 근거·시각, 그리고 unknown 범위
2. 역할별 후보와 선택 근거(필요 capability, reasoning floor, 역할 관련 benchmark의 조건·결과·한계, 관측된 입력/출력 가격, unknown)
3. 세션 기본 profile: 역할별 provider/model/effort, 비용 상한, fallback
4. 재검토 trigger와 이 정책이 보장하지 않는 범위

사람이 확정하기 전에는 후보를 추천할 수 있지만, 새 모델·추론도 상향 또는 승인되지 않은
비용 상향을 적용하지 않는다. 확정 뒤에는 같은 세션에서 매 역할마다 다시 묻지 않고,
사용자가 확정한 role별 profile을 쓴다. 후보가 과업 관련 결과에서 대체로 비슷하고 가격
근거도 같은 조건이면 더 낮은 비용을 우선할 수 있다. 다만 사용자가 명시적으로
다른 관측 모델이나 reasoning effort를 요청하면 그것을 사용자 선택으로 받아들인다.
저장된 전역 모델 allowlist는 없다. 이때 정확한 provider/model/effort가 현재 catalog에 있고 task capability·최소 reasoning을
충족하는지 확인한 뒤, override 범위·이유·비용 근거·남은 위험을 기록한다. override는
해당 작업 또는 사용자가 지정한 범위에만 적용하며 기본 profile을 조용히 바꾸지 않는다.
`tooling/model-policy.py select`는 관측된 원래 provider/model/effort 값을 보존해 검증한다.
공통 비교는 `low`, `medium`, `high`, `ultra`로 선언된 tier끼리만 하며, 다른 native effort는
별도 순위를 추론하지 않는다. native effort가 작업 floor와 같은 값이면 exact match로 확인할
수 있고, 서로 다른 native/common 값을 비교해야 하면 해당 선택은 `unknown` 상태로 내고
사용자에게 작업 최소 조건도 충족하는지 함께 확인한다. 선택 가능한 effort가 runtime에
노출되지 않으면 `not-selectable`로 기록한다.

## 재검토 trigger

아래 이벤트는 해당 프로젝트의 Model Session Policy card를 다시 제시하고, 기존 배치를
유지할지 변경할지 사용자에게 묻는다.

- 직전 비밀 없는 catalog 관측과 비교해 모델 추가·삭제, availability, reasoning effort,
  또는 가격 근거가 바뀜
- 새 모델/모델 버전, 가격, capability 또는 역할 관련 benchmark 업데이트가 신뢰 가능한
  출처에서 감지됨. 공개 발표만으로 현재 런타임의 가용성을 추정하지 않는다.
- 현재 profile로 충족할 수 없는 작업 capability 또는 reasoning floor가 생김
- learning이 확인된 root cause와 검증된 smallest prevention을 근거로 model/effort
  escalation을 요청함
- 사람이 명시적으로 정책 변경을 요청함

비동기 감시 daemon, 가격 알림, 계정 스캔은 이 계약의 기능이 아니다. 다음 세션 시작 또는
모델 의존적 배정 전에 실제 관측을 갱신하고, 전달받은 직전 관측과 비교하는 방식만
지원한다. 지속 알림을 원하면 별도의 권한 있는 scheduler·notification provider와 그
provider의 실행 증거를 프로젝트 밖에서 명시적으로 추가해야 한다.

## 런타임 목록 확인과 사용자 보정

Codex VS Code 확장 환경에서는 `tooling/model-catalog.py codex`로 공식 확장과 함께
배포된 Codex 런타임의 list-visible 목록을 조회할 수 있다. 이 도구는 우선 공식
`openai.chatgpt-*` 확장 폴더의 실행 파일만 제한적으로 찾고, 없으면 PATH의 Codex를
generic Codex runtime으로 명시해 사용하며, 명시 override 역시 별도 source로 표시한다.
설정·인증정보·
세션 파일은 읽지 않는다. provider 출력에서 model ID, 표시명, 선택 가능 reasoning effort와
기본 effort만 투영한다. 자유 형식 설명과 instruction 필드는 사용하거나 사용자에게
전달하지 않는다.

목록을 받은 뒤에는 새 프로젝트와 재확인 시점마다 읽힌 모델/effort 목록을 사용자에게
보여주고 “현재 선택 가능 목록이 맞는가?”를 확인한다. 사용자가 아니라고 하면 VS Code
화면에서 확인한 목록을 직접 알려줄 수 있다. 그 교정은 `user-reported-from-runtime-ui`처럼
별도 provenance로 남기며 자동 관측을 덮어쓰지 않는다. 교정된 목록 또한 프로젝트 역할별
배치를 사용자가 확정하기 전에는 profile로 취급하지 않는다. 설치된 공식 런타임 목록이
없거나 조회 실패 시에는 `unknown`으로 두고 사용자가 직접 알려주는 경로를 제공한다.

`visibility=list`는 picker에서 보일 수 있다는 사실만 뜻하며, API entitlement나 현재
picker 동기화를 보증하지 않는다. 이 조회는 Codex 확장 내부의 현재 대화 모델을 읽거나
변경하지 않는다. runtime 목록은 선택 후보 관측이지 현재 선택 모델 증거가 아니다.
Claude Code VS Code 확장의
선택 목록을 공식적으로 조회할 수 있는 인터페이스가 없거나 해당 확장이 없는 환경에서는
같은 원칙으로 `unknown`을 유지하고 화면에서 받은 사용자 교정만 별도 출처로 기록한다.

## 실행·산출물·한계

`tooling/model-policy.py` evaluator는 Chohogi source checkout에서만 실행할 수 있으며,
runtime installer는 이 evaluator와 YAML parsing dependency를 설치하지 않는다. 따라서
일반 설치본에서는 role별 후보를 policy 기준으로 대화 안에서 비교하고 사용자에게 확인한다.
evaluator를 실제 실행할 수 없는 상황에서 실행했다거나 기계적으로 검증했다고 주장하지 않는다.
Source checkout에서 `python3 tooling/model-policy.py recommend --catalog <observed.json> --task <task.json>`는
현재 관측 안에서 capability·최소 reasoning tier로 적격 후보를 추리고 관측된 입력/출력
가격을 별도 표시하며 항상 사람 확정을 요구한다. 품질이나 종합 비용 순위는 만들지 않는다.
`compare`는 두 관측의 차이를, `learning-escalation`은 확인된
learning evidence가 있을 때만 재확정을 출력한다. `select --catalog <observed.json>
--task <task.json> --provider <provider> --model <model> --reasoning <effort> --reason <text>`는
사용자가 명시한 override를 현재 관측과 task 계약에 대조한다.

세션 정책 record는 비밀 없는 관측과 사람의 확정만 담는다. 원본 대화, API key, account ID,
개인 청구 정보는 넣지 않는다. record를 어디에 보존할지는 런타임/사용자의 권한 있는
adapter가 정한다. 초호기 source와 installer는 provider 설정이나 개인 세션 저장소를
관리하지 않는다.
