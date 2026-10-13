# 기능 설명서

## 1. 개요

이 문서는 `IT Industry Data Assistant` 프로젝트의 주요 기능을 설명한다. 프로젝트는 한국 IT/SI 관련 산업의 서비스업생산지수와 IT 직종 구인 수요를 전처리하고, 분석 질문 Q1~Q5에 필요한 그래프와 수치 요약을 생성한다.

## 2. 전체 처리 흐름

```text
원본 데이터 수집
  ↓
data/raw/ 저장
  ↓
src/preprocess.py 실행
  ↓
data/processed/ 분석용 데이터 생성
  ↓
src/analyze.py 실행
  ↓
images/ 그래프 생성 + analysis_metrics.md 생성
  ↓
REPORT.md 작성 및 제출
```

## 3. 데이터 관리 기능

### 3.1 원본 데이터 분리

원본 통계 파일은 `data/raw/` 폴더에 둔다. 라이선스 확인 전까지 원본 파일은 Git에 포함하지 않는다.

제외 대상:

```text
data/raw/*.csv
data/raw/*.xls
data/raw/*.xlsx
```

### 3.2 가공 데이터 분리

전처리 결과는 `data/processed/`에 저장한다. CSV 가공 파일도 Git에 포함하지 않는다.

제외 대상:

```text
data/processed/*.csv
data/processed/*.xls
data/processed/*.xlsx
```

단, 분석 수치 요약인 `data/processed/analysis_metrics.md`는 원자료가 아니므로 Git에 포함할 수 있다.

## 4. 전처리 기능

전처리 스크립트:

```text
src/preprocess.py
```

### 4.1 서비스업생산지수 전처리

기능:

- KOSIS 서비스업생산지수 CSV 자동 탐색
- cp949 인코딩으로 파일 읽기
- 월별 컬럼 자동 인식
- 분석 대상 업종 필터링
- 경상지수, 불변지수, 계절조정지수 추출
- wide format 데이터를 long format으로 변환
- 중복 행 검증 및 정리

출력:

```text
data/processed/service_production_long.csv
```

### 4.2 구인구직 데이터 전처리

기능:

- 고용행정통계 엑셀 파일 자동 탐색
- `.xls` 또는 `.xlsx` 확장자 파일의 OOXML 구조 직접 파싱
- 월별 구인인원, 구직건수, 취업건수 추출
- 2007/2018/2025 직종분류 연결
- 상위 IT 직종 전체와 소프트웨어 개발자 지표 생성
- 구인인원 / 구직건수 비율 계산

출력:

```text
data/processed/job_demand_long.csv
```

### 4.3 병합 데이터 생성

서비스업생산지수와 구인 수요를 월 단위로 병합한다.

출력:

```text
data/processed/merged_monthly.csv
```

## 5. 분석 및 시각화 기능

분석 스크립트:

```text
src/analyze.py
```

### 5.1 장기 추세 그래프

출력 이미지:

```text
images/01_service_trend_constant_index.png
```

기능:

- IT 관련 4개 업종의 불변지수 추세 표시
- 원자료 선과 12개월 이동평균선 표시
- 코로나19 참고 구간 표시

### 5.2 월별 계절성 그래프

출력 이미지:

```text
images/02_monthly_seasonality_by_industry.png
```

기능:

- 월별 값 / 해당 연도 평균 × 100 계산
- 업종별 평균 월별 계절비율 비교
- Q1, Q3 분석에 사용

### 5.3 경상지수와 불변지수 비교

출력 이미지:

```text
images/03_current_vs_constant_index.png
```

기능:

- SI 관련 업종의 경상지수와 불변지수 비교
- 명목 흐름과 실질 흐름의 차이를 확인

### 5.4 생산지수와 구인 수요 비교

출력 이미지:

```text
images/04_service_vs_job_demand_indexed.png
```

기능:

- 생산지수와 구인인원을 첫 달 100 기준으로 지수화
- 서로 다른 단위의 시계열을 비교
- Q4 분석에 사용

### 5.5 시차 상관 분석

출력 이미지:

```text
images/06_lag_correlation_service_vs_jobs.png
```

기능:

- -6개월부터 +6개월까지의 시차 상관 계산
- 구인수요가 생산지수보다 선행하는지 확인
- 생산지수가 구인수요보다 선행하는지 확인

시차 해석:

```text
lag < 0: 구인수요가 생산지수보다 선행
lag = 0: 동월 비교
lag > 0: 생산지수가 구인수요보다 선행
```

### 5.6 Seasonal Naive 예측

출력 이미지:

```text
images/05_seasonal_naive_forecast_error.png
```

기능:

- 전년동월 값을 예측값으로 사용
- 실제값과 예측값 비교
- 절대백분율오차 계산
- 예측이 크게 빗나간 달 확인

## 6. 수치 요약 생성 기능

분석 스크립트는 다음 파일을 생성한다.

```text
data/processed/analysis_metrics.md
```

포함 내용:

- 데이터 기간 및 행 수
- 3월 계절비율
- 장기 변화율
- 코로나19 참고 구간 최저값
- 업종별 계절성 표준편차
- 생산지수와 구인수요 상관계수
- 시차 상관 결과
- Seasonal Naive 예측오차 상위 월

## 7. 문서화 기능

프로젝트는 다음 문서를 포함한다.

| 문서 | 설명 |
|---|---|
| `README.md` | 프로젝트 개요 및 실행 방법 |
| `README_ja.md` | 일본어 프로젝트 개요 |
| `DATA_SOURCE.md` | 데이터 수집 안내 |
| `REPORT.md` | 분석 보고서 |
| `data/columns.md` | 컬럼 매핑 문서 |
| `ai-log.md` | AI 사용 로그 |
| `docs/` | 추가 기획 및 기능 설명 문서 |

## 8. 실행 명령 요약

전처리:

```zsh
python3 src/preprocess.py
```

분석:

```zsh
python3 src/analyze.py
```

## 9. 주요 제한사항

- 원본 통계 파일은 Git에 포함하지 않는다.
- 구인 수요 데이터는 직종분류 변경으로 인해 완전히 동일 정의의 장기 시계열이 아닐 수 있다.
- 구인인원/구직건수 비율은 공식 구인배율이 아니다.
- 본 프로젝트는 인과분석이 아니라 탐색적 시계열 분석이다.
