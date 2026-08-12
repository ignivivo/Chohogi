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
- scanner·gate는 leaf의 책임이 아니다. 보안 면역기관의 project adapter contract에 따라
  프로젝트 구성·CI로 연결한다. leaf가 보안 관련 코드를 적응하더라도 gate의 소유권을 가져가지 않는다.
