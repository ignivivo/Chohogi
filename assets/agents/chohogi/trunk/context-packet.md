<!-- chohogi:context-packet -->

# 연속성 작업 봉투

긴 작업에서 결론·근거·다음 경계를 압축해 컨텍스트 단절과 중복 실행을 막는다. 이는
별도 하네스가 아니라 trunk가 관리하는 최소 기록이다.

## 만들 때

- 두 개 이상의 실행 세포·검토 경계가 있는 substantial 작업
- 여러 차례에 걸친 구현, 또는 컨텍스트 단절 위험

짧은 직접 처리에는 만들지 않는다. 비밀값, 원문 개인 정보, 긴 대화 전문은 넣지 않는다.

## 최소 형식

```text
task: <식별자와 목표>
flow / allocation: <flow> / <direct|sequential|scoped-delegation>
accepted constraints: <수용 조건·제외 범위>
ownership: <역할: 파일 또는 읽기 전용 경계>
decisions: <결정과 근거>
evidence: <명령·결과·관측>
next: <완료 항목 또는 다음 하나의 경계>
```

주 에이전트만 봉투를 갱신하고, 각 역할은 자신의 근거만 보고한다. Git과 프로젝트
work log가 장기 역사이며 이 봉투는 현재 작업을 잇는 압축본일 뿐이다.
