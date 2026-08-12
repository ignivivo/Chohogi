<!-- chohogi:model-policy -->

# 세션 모델 정책 계약

모델 배정은 모델명 하나를 고르는 행위가 아니다. 현재 실제로 호출 가능한
`provider + model + reasoning effort + role + 비용 근거`를 사람의 세션 정책으로
확정하고, 그 정책 안에서 작업·임시 역할에 배정하는 일이다.

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

첫 substantial 작업의 실행 배정 전에 Model Session Policy card를 제시하고 사람이 한 번
확정하거나 수정한다. 카드에는 다음을 포함한다.

1. 관측된 provider/model/reasoning effort와 관측 근거·시각, 그리고 unknown 범위
2. 역할별 후보와 선택 근거(필요 capability, reasoning floor, 알려진 가격)
3. 세션 기본 profile: 역할별 provider/model/effort, 비용 상한, fallback
4. 재검토 trigger와 이 정책이 보장하지 않는 범위

사람이 확정하기 전에는 후보를 추천할 수 있지만, 새 모델·추론도 상향 또는 승인되지 않은
비용 상향을 적용하지 않는다. 확정 뒤에는 같은 세션에서 매 역할마다 다시 묻지 않고,
승인된 profile 안에서 가장 낮은 비용의 충분한 후보를 쓴다. provider가 effort 선택을
노출하지 않으면 `not-selectable`로 기록하며, 초호기가 다른 provider의 effort 명칭을
GPT의 `low`~`ultra`와 동일하다고 가정하지 않는다. evaluator input에서는 adapter가
정규화한 `low`, `medium`, `high`, `ultra` capability tier만 쓴다.

## 재검토 trigger

아래 이벤트는 Model Session Policy card를 다시 사람에게 제시한다.

- 직전 비밀 없는 catalog 관측과 비교해 모델 추가·삭제, availability, reasoning effort,
  또는 가격 근거가 바뀜
- 현재 profile로 충족할 수 없는 작업 capability 또는 reasoning floor가 생김
- learning이 확인된 root cause와 검증된 smallest prevention을 근거로 model/effort
  escalation을 요청함
- 사람이 명시적으로 정책 변경을 요청함

비동기 감시 daemon, 가격 알림, 계정 스캔은 이 계약의 기능이 아니다. 다음 세션 시작 또는
모델 의존적 배정 전에 실제 관측을 갱신하고, 전달받은 직전 관측과 비교하는 방식만
지원한다. 지속 알림을 원하면 별도의 권한 있는 scheduler·notification provider와 그
provider의 실행 증거를 프로젝트 밖에서 명시적으로 추가해야 한다.

## 실행·산출물·한계

`python3 tooling/model-policy.py recommend --catalog <observed.json> --task <task.json>`는
현재 관측 안에서 capability·최소 reasoning tier·보고된 가격만으로 후보를 순위화하며 항상
사람 확정을 요구한다. `compare`는 두 관측의 차이를, `learning-escalation`은 확인된
learning evidence가 있을 때만 재확정을 출력한다.

세션 정책 record는 비밀 없는 관측과 사람의 확정만 담는다. 원본 대화, API key, account ID,
개인 청구 정보는 넣지 않는다. record를 어디에 보존할지는 런타임/사용자의 권한 있는
adapter가 정한다. 초호기 source와 installer는 provider 설정이나 개인 세션 저장소를
관리하지 않는다.
