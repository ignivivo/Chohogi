<!-- chohogi:project-leaves -->

# Project leaves · 프로젝트 적응 자산 계약

Project leaf는 전역 reusable method의 이름·복사본·별칭이 아니다. 특정 프로젝트에서
반복되는 적응 경계에 대해 코드, 구성, CI, fixture, 운영 제약 중 필요한 실제 산출물을
함께 소유하는 프로젝트 자산이다.

## 생성 조건

다음이 모두 있을 때만 프로젝트에 leaf를 만든다.

- 반복되는 프로젝트 특화 문제 서명과 명시된 owner가 있다.
- 전역 method만으로는 프로젝트의 실행 경로·resource·검증을 표현할 수 없다.
- trigger와 non-trigger, 입력, 산출물, 실제 verifier 또는 CI/fixture, 폐기 조건이 있다.

전역 method의 전문 지침만 필요하면 leaf를 만들지 않는다. leaf가 없다면 비어 있는 것이
정상이다.

## 경계

- 소스와 배포 위치는 해당 프로젝트가 소유한다. 초호기 설치기는 이를 자동 설치하지 않는다.
- 프로젝트 leaf가 반복 검증을 통해 일반화 후보가 되어도, Learning과 Homeostasis의 승격
  근거 없이는 전역 reusable method나 정책으로 이동하지 않는다.
- leaf가 scanner·gate를 주장하면 실제 실행 경로, 결과 산출물, positive·negative fixture,
  실패 exit path를 프로젝트 CI에 연결한다.
- 프로젝트는 scanner·gate를 실행할 때 `python3 tooling/run-security-gate.py --project <project> --plan <project-plan> --output <project-observation> --execute`처럼 명시적으로 실행하고, 생성된 observation을 release evidence로 보존한다.
